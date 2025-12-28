import csv

class MetricsCollector:
    """
    ML-optimized metrics collector for stadium simulation.
    Tracks turnstile queues, vendor usage, parking, and fan flow.
    """
    
    def __init__(self, env, stadium, stadium_capacity=68000, kickoff_time=180):
        self.env = env
        self.stadium = stadium
        self.stadium_capacity = stadium_capacity
        self.kickoff_time = kickoff_time  
        
        # Resource capacities for normalization
        self.turnstile_capacity = stadium.turnstiles.capacity  # 92 turnstiles
        self.vendor_capacity = stadium.vendors.capacity  # 45 vendors
        self.parking_capacity = stadium.parking.capacity  # 6000 spots
        
        # Tracking for rate calculations
        self.prev_arrived = 0
        self.prev_completed = 0
        self.prev_time = 0
        
        # Wait times (recent interval - cleared each snapshot)
        self.recent_turnstile_waits = []
        self.recent_vendor_waits = []
        self.recent_exit_waits = []
        
        # Rolling history for lag features
        self.arrival_rate_history = []
        self.queue_history = []
        
        # Counters
        self.fans_arrived = 0
        self.fans_completed = 0
        self.fans_exited = 0
        self.parking_used = 0

        self.rows = []

    def log_turnstile_wait(self, t):
        """Log wait time at turnstile."""
        self.recent_turnstile_waits.append(t)
    
    def log_vendor_wait(self, t):
        """Log wait time at vendor."""
        self.recent_vendor_waits.append(t)
    
    def log_exit_wait(self, t):
        """Log wait time at exit."""
        self.recent_exit_waits.append(t)
    
    def log_parking_used(self):
        """Log parking spot taken."""
        self.parking_used += 1
    
    def periodic_snapshot(self, interval=1):
        """Generator that takes periodic snapshots (1 min for ML granularity)."""
        while True:
            yield self.env.timeout(interval)
            self._take_snapshot()
    
    def _take_snapshot(self):
        """Capture ML-optimized features."""
        now = self.env.now
        dt = now - self.prev_time if self.prev_time > 0 else 1
        
        # === RATE FEATURES (fans per minute) ===
        arrival_rate = (self.fans_arrived - self.prev_arrived) / dt
        completion_rate = (self.fans_completed - self.prev_completed) / dt
        prev_exited = getattr(self, 'prev_exited', 0)
        exit_rate = (self.fans_exited - prev_exited) / dt
        net_flow_rate = arrival_rate - exit_rate  # Positive = stadium filling, negative = emptying
        
        # === QUEUE FEATURES ===
        turnstile_queue = len(self.stadium.turnstiles.queue)
        vendor_queue = len(self.stadium.vendors.queue)
        
        # === UTILIZATION FEATURES (0-1 normalized) ===
        turnstile_utilization = self.stadium.turnstiles.count / self.turnstile_capacity
        vendor_utilization = self.stadium.vendors.count / self.vendor_capacity
        parking_utilization = 1 - (self.stadium.parking.level / self.parking_capacity)
        
        # === PROGRESS FEATURES ===
        fill_ratio = self.fans_completed / self.stadium_capacity  # 0 to 1
        arrival_progress = self.fans_arrived / self.stadium_capacity
        exit_progress = self.fans_exited / self.stadium_capacity
        fans_in_stadium = self.fans_completed - self.fans_exited  # Currently in seats
        fans_in_system = self.fans_arrived - self.fans_exited  # Total in venue (queues + seated)
        
        # === TIME FEATURES ===
        time_to_kickoff = max(0, self.kickoff_time - now)
        is_pre_match = 1 if now < self.kickoff_time else 0
        time_phase = self._get_time_phase(now)  # Categorical: early/rush/late
        
        # === WAIT TIME FEATURES ===
        avg_turnstile_wait = self.avg(self.recent_turnstile_waits)
        max_turnstile_wait = max(self.recent_turnstile_waits) if self.recent_turnstile_waits else 0
        avg_vendor_wait = self.avg(self.recent_vendor_waits)
        avg_exit_wait = self.avg(self.recent_exit_waits)
        max_exit_wait = max(self.recent_exit_waits) if self.recent_exit_waits else 0
        
        # Estimated wait for new arrival (queue / throughput)
        # Each turnstile processes 30-40 fans/min (biometric systems)
        # Average processing time: 0.029 min (1.75 sec)
        # Throughput: 92 turnstiles × 35 fans/min = 3,220 fans/min
        throughput_per_min = self.turnstile_capacity * 35
        est_wait = turnstile_queue / throughput_per_min if throughput_per_min > 0 else 0
        
        # === LAG FEATURES (for sequence models) ===
        self.arrival_rate_history.append(arrival_rate)
        self.queue_history.append(turnstile_queue)
        
        # Keep last 10 periods
        if len(self.arrival_rate_history) > 10:
            self.arrival_rate_history.pop(0)
            self.queue_history.pop(0)
        
        arrival_rate_lag1 = self.arrival_rate_history[-2] if len(self.arrival_rate_history) >= 2 else 0
        arrival_rate_lag5 = self.arrival_rate_history[-6] if len(self.arrival_rate_history) >= 6 else 0
        queue_lag1 = self.queue_history[-2] if len(self.queue_history) >= 2 else 0
        queue_delta = turnstile_queue - queue_lag1  # Queue change from last period
        
        # === ROLLING AVERAGES ===
        arrival_rate_ma5 = self.avg(self.arrival_rate_history[-5:]) if self.arrival_rate_history else 0
        
        # === BUILD ROW ===
        row = {
            # Time features
            'time': round(now, 1),
            'time_to_kickoff': round(time_to_kickoff, 1),
            'is_pre_match': is_pre_match,
            'time_phase': time_phase,
            
            # Count features
            'fans_arrived': self.fans_arrived,
            'fans_completed': self.fans_completed,
            'fans_exited': self.fans_exited,
            'fans_in_stadium': fans_in_stadium,
            'fans_in_system': fans_in_system,
            
            # Progress features (normalized 0-1)
            'fill_ratio': round(fill_ratio, 4),
            'arrival_progress': round(arrival_progress, 4),
            'exit_progress': round(exit_progress, 4),
            
            # Rate features
            'arrival_rate': round(arrival_rate, 2),
            'completion_rate': round(completion_rate, 2),
            'exit_rate': round(exit_rate, 2),
            'net_flow_rate': round(net_flow_rate, 2),
            
            # Queue features
            'turnstile_queue': turnstile_queue,
            'vendor_queue': vendor_queue,
            'queue_delta': queue_delta,
            
            # Utilization features (normalized 0-1)
            'turnstile_utilization': round(turnstile_utilization, 4),
            'vendor_utilization': round(vendor_utilization, 4),
            'parking_utilization': round(parking_utilization, 4),
            
            # Wait time features
            'avg_turnstile_wait': round(avg_turnstile_wait, 2),
            'max_turnstile_wait': round(max_turnstile_wait, 2),
            'est_wait_new_arrival': round(est_wait, 2),
            'avg_vendor_wait': round(avg_vendor_wait, 2),
            'avg_exit_wait': round(avg_exit_wait, 2),
            'max_exit_wait': round(max_exit_wait, 2),
            
            # Lag features (for time series models)
            'arrival_rate_lag1': round(arrival_rate_lag1, 2),
            'arrival_rate_lag5': round(arrival_rate_lag5, 2),
            'arrival_rate_ma5': round(arrival_rate_ma5, 2),
            
            # Resource levels
            'turnstiles_in_use': self.stadium.turnstiles.count,
            'vendors_in_use': self.stadium.vendors.count,
            'parking_free': self.stadium.parking.level,
        }
        self.rows.append(row)
        
        # Update previous values
        self.prev_arrived = self.fans_arrived
        self.prev_completed = self.fans_completed
        self.prev_exited = self.fans_exited
        self.prev_time = now
        
        # Clear recent waits
        self.recent_turnstile_waits = []
        self.recent_vendor_waits = []
        self.recent_exit_waits = []
        
        # Print condensed progress
        if int(now) % 10 == 0:  # Print every 10 min
            print(f"t={now:>5.0f} | In Stadium: {fans_in_stadium:>6} | "
                  f"Exited: {self.fans_exited:>6} | Queue: {turnstile_queue:>5} | "
                  f"Arr: {arrival_rate:>4.0f}/min | Exit: {exit_rate:>4.0f}/min")
    
    def _get_time_phase(self, t):
        """Categorize time into phases (useful for ML)."""
        if t < 60:
            return 0  # Early - light traffic
        elif t < 120:
            return 1  # Building - moderate
        elif t < 180:
            return 2  # Rush - heavy traffic
        elif t < 240:
            return 3  # Peak/Kickoff
        else:
            return 4  # Post-rush - clearing

    def avg(self, lst):
        return sum(lst) / len(lst) if lst else 0.0
    
    def save_to_csv(self, filename='stadium_simulation.csv'):
        if not self.rows:
            print("No data to save!")
            return
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.rows[0].keys())
            writer.writeheader()
            writer.writerows(self.rows)
        print(f"Saved {len(self.rows)} rows to {filename}")
        
        # Print feature summary
        print(f"\n=== ML Dataset Summary ===")
        print(f"Samples: {len(self.rows)}")
        print(f"Features: {len(self.rows[0].keys())}")
        print(f"Time range: 0 - {self.rows[-1]['time']} min")
        print(f"\nFeature categories:")
        print(f"  - Time features: time, time_to_kickoff, is_pre_match, time_phase")
        print(f"  - Count features: fans_arrived, fans_completed, fans_in_system")
        print(f"  - Progress features: fill_ratio, arrival_progress")
        print(f"  - Rate features: arrival_rate, completion_rate, net_flow_rate")
        print(f"  - Queue features: turnstile_queue, vendor_queue, queue_delta")
        print(f"  - Utilization: turnstile_utilization, vendor_utilization, parking_utilization")
        print(f"  - Wait times: avg_turnstile_wait, max_turnstile_wait, est_wait_new_arrival")
        print(f"  - Lag features: arrival_rate_lag1/lag5/ma5")
        print(f"  - Resources: turnstiles_in_use, vendors_in_use, parking_free")