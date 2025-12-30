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
from agents import fan

TOTAL_FANS = 68000  # Full stadium capacity


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
    """
    fan_id = 0
    scale_factor = total_fans / TOTAL_FANS
    
    while fan_id < total_fans:
        t = env.now
        
        # Arrival rates calibrated to CREATE QUEUES
        # System can handle ~250 fans/min through turnstiles
        # Rates > 250 will create backlogs
        
        if t < 30:
            # Very early (first 30 min) - light traffic
            # ~150 fans/min × 30 min = 4,500 fans (6.6%)
            rate = 150 * scale_factor
            
        elif 30 <= t < 60:
            # Early arrivals building up
            # ~250 fans/min × 30 min = 7,500 fans (11%)
            # Matches capacity - no queue yet
            rate = 250 * scale_factor
            
        elif 60 <= t < 90:
            # Moderate buildup (2h before kickoff)
            # ~350 fans/min × 30 min = 10,500 fans (15.4%)
            # Exceeds capacity - queues start forming
            rate = 350 * scale_factor
            
        elif 90 <= t < 120:
            # PEAK RUSH (1.5h to 1h before kickoff)
            # ~500 fans/min × 30 min = 15,000 fans (22%)
            # 2× capacity - significant queues!
            rate = 500 * scale_factor
            
        elif 120 <= t < 150:
            # Sustained rush (1h to 30min before)
            # ~550 fans/min × 30 min = 16,500 fans (24.3%)
            # Peak congestion
            rate = 550 * scale_factor
            
        elif 150 <= t < 180:
            # Final rush before kickoff
            # ~450 fans/min × 30 min = 13,500 fans (19.9%)
            rate = 450 * scale_factor
            
        elif 180 <= t < 200:
            # Just after kickoff (latecomers)
            # ~25 fans/min × 20 min = 500 fans (0.7%)
            rate = 25 * scale_factor
            
        else:
            # Very late / match in progress
            rate = 2 * scale_factor
        
        # Ensure minimum rate
        rate = max(1, rate)
        
        # Generate inter-arrival time (exponential distribution)
        inter_arrival = random.expovariate(rate)
        yield env.timeout(inter_arrival)
        
        # Spawn fan process
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