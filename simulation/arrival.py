"""
Fan Arrival Process - Time-varying arrival patterns
====================================================
Generates realistic fan arrivals that CREATE QUEUES.

Key insight: To have meaningful wait times, arrival rate must EXCEED
service capacity at peak times.

Service capacity:
- 60 security lanes × 6 fans/min = 360 fans/min max
- 25 turnstiles × 10 fans/min = 250 fans/min max (THE BOTTLENECK!)

So we need arrival rates that exceed 250 fans/min to create turnstile queues.
Peak arrivals of 400-500/min will create realistic 5-15 minute waits.
"""
import random
from agents import fan, fan_group, vip_fan

TOTAL_FANS = 68000  # Full stadium capacity

# Realistic arrival factors
WEATHER_FACTOR = random.uniform(0.9, 1.1)  # Weather affects timing (rain = early)
TRAFFIC_FACTOR = random.uniform(0.95, 1.05)  # Traffic delays
RIVALRY_GAME = random.random() < 0.3  # 30% chance of rivalry (higher demand)


def arrival_process(env, stadium, metrics):
    """
    Generates fan arrivals with time-varying rates.
    Default process for backward compatibility.
    """
    yield from create_arrival_process(env, stadium, metrics, TOTAL_FANS)


def create_arrival_process(env, stadium, metrics, total_fans=68000):
    """
    Generates fan arrivals with time-varying rates.
    
    Time units = minutes. Stadium opens 3 hours before kickoff (t=0).
    Kickoff is at t=180.
    
    Arrival distribution designed to create REALISTIC QUEUES:
    - 68,000 fans need to arrive in ~180 minutes
    - Average rate needed: 378 fans/min
    - Peak rate: 450-550 fans/min (exceeds 250 capacity, creates queues)
    
    NEW REALISTIC FEATURES:
    - Group arrivals (families, friends)
    - VIP fast-track arrivals
    - Weather and traffic effects
    - Public transport arrival spikes
    """
    fan_id = 0
    vip_count = int(total_fans * 0.05)  # 5% VIP
    scale_factor = total_fans / TOTAL_FANS
    
    rivalry_boost = 1.15 if RIVALRY_GAME else 1.0
    
    while fan_id < total_fans:
        t = env.now
        
        # Arrival rates calibrated to CREATE QUEUES
        # System can handle ~250 fans/min through turnstiles
        # Rates > 250 will create backlogs
        
        if t < 30:
            # Very early (first 30 min) - light traffic
            # Season ticket holders, early birds, tailgaters
            rate = 150 * scale_factor * WEATHER_FACTOR
            
        elif 30 <= t < 60:
            # Early arrivals building up
            # ~250 fans/min × 30 min = 7,500 fans (11%)
            # Matches capacity - no queue yet
            rate = 250 * scale_factor * WEATHER_FACTOR
            
        elif 60 <= t < 90:
            # Moderate buildup (2h before kickoff)
            # Public transport arrivals start
            rate = 350 * scale_factor * TRAFFIC_FACTOR * rivalry_boost
            
            # Simulate bus/train arrival spike
            if int(t) % 15 == 0:  # Every 15 mins
                rate *= 1.3  # 30% spike from public transport
            
        elif 90 <= t < 120:
            # PEAK RUSH (1.5h to 1h before kickoff)
            # Multiple public transport arrivals
            rate = 500 * scale_factor * TRAFFIC_FACTOR * rivalry_boost
            
            if int(t) % 10 == 0:  # More frequent arrivals
                rate *= 1.4
            
        elif 120 <= t < 150:
            # Sustained rush (1h to 30min before)
            # Maximum congestion period
            rate = 550 * scale_factor * TRAFFIC_FACTOR * rivalry_boost
            
            if int(t) % 10 == 0:
                rate *= 1.35
            
        elif 150 <= t < 180:
            # Final rush before kickoff
            # Last-minute arrivals, people rushing
            rate = 450 * scale_factor * rivalry_boost * 1.1
            
        elif 180 <= t < 200:
            # Just after kickoff (latecomers)
            rate = 25 * scale_factor
            
        else:
            # Very late / match in progress
            rate = 2 * scale_factor
        
        # Ensure minimum rate
        rate = max(1, rate)
        
        # Generate inter-arrival time (exponential distribution)
        inter_arrival = random.expovariate(rate)
        yield env.timeout(inter_arrival)
        
        # Decide arrival type
        arrival_type = random.random()
        
        if arrival_type < 0.15:  # 15% arrive in groups (2-6 people)
            group_size = random.choices([2, 3, 4, 5, 6], weights=[30, 35, 20, 10, 5])[0]
            group_size = min(group_size, total_fans - fan_id)
            
            # Spawn group with slight delays
            for i in range(group_size):
                if fan_id < total_fans:
                    is_vip = fan_id < vip_count
                    if is_vip:
                        env.process(vip_fan(env, fan_id, stadium, metrics))
                    else:
                        env.process(fan_group(env, fan_id, stadium, metrics, group_size))
                    metrics.fans_arrived += 1
                    fan_id += 1
                    if i < group_size - 1:  # Small delay between group members
                        yield env.timeout(random.uniform(0.05, 0.15))
        
        elif arrival_type < 0.20:  # 5% VIP arrivals (fast-track)
            if fan_id < vip_count:
                env.process(vip_fan(env, fan_id, stadium, metrics))
            else:
                env.process(fan(env, fan_id, stadium, metrics))
            metrics.fans_arrived += 1
            fan_id += 1
        
        else:  # 80% regular individual arrivals
            is_vip = fan_id < vip_count
            if is_vip:
                env.process(vip_fan(env, fan_id, stadium, metrics))
            else:
                env.process(fan(env, fan_id, stadium, metrics))
            metrics.fans_arrived += 1
            fan_id += 1


def get_arrival_rate_info():
    """Returns information about arrival rate distribution."""
    return {
        'phases': [
            {'name': 'Very Early', 'start': 0, 'end': 30, 'rate': 100, 'pct': 4.4},
            {'name': 'Early', 'start': 30, 'end': 60, 'rate': 200, 'pct': 8.8},
            {'name': 'Moderate', 'start': 60, 'end': 90, 'rate': 400, 'pct': 17.6},
            {'name': 'Peak Rush', 'start': 90, 'end': 120, 'rate': 700, 'pct': 30.9},
            {'name': 'Sustained', 'start': 120, 'end': 150, 'rate': 600, 'pct': 26.5},
            {'name': 'Pre-Kickoff', 'start': 150, 'end': 180, 'rate': 250, 'pct': 11.0},
            {'name': 'Latecomers', 'start': 180, 'end': 200, 'rate': 25, 'pct': 0.7},
        ],
        'total_expected': TOTAL_FANS,
        'peak_rate': 700,
        'bottleneck': 'turnstiles (200 fans/min capacity)',
    }