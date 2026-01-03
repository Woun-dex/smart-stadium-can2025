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


def arrival_process(env, stadium, metrics):
    """
    Generates fan arrivals with time-varying rates.
    Default process for backward compatibility.
    """
    yield from create_arrival_process(env, stadium, metrics, TOTAL_FANS)


def create_arrival_process(env, stadium, metrics, total_fans=68000):
    """
    Generate arrivals calibrated for 68,000 fans by t=180 (kickoff).
    Rates are designed to exceed bottleneck capacity and create realistic queues.
    """
    fan_id = 0
    vip_count = int(total_fans * 0.05)  # 5% VIP
    scale_factor = total_fans / TOTAL_FANS
    
    # Realistic arrival factors (recalculated per simulation)
    weather_factor = random.uniform(0.98, 1.02)  # Minimal weather variation
    traffic_factor = random.uniform(0.98, 1.02)  # Minimal traffic variation
    rivalry_game = random.random() < 0.3  # 30% chance of rivalry
    rivalry_boost = 1.1 if rivalry_game else 1.0
    
    while fan_id < total_fans:
        t = env.now
        
        # IMPORTANT: These rates are calibrated so 68,000 fans arrive by t=180 (kickoff)
        # Average needed: 378 fans/min over 180 minutes
        # Peak rates exceed bottleneck capacity (250 fans/min) to create realistic queues
        
        if t < 30:
            # Very early (first 30 min) - light traffic
            # 150 fans/min × 30 min = 4,500 fans (6.6%)
            # Season ticket holders, early birds, tailgaters
            rate = 150 * scale_factor * weather_factor
            
        elif 30 <= t < 60:
            # Early arrivals building up
            # 250 fans/min × 30 min = 7,500 fans (11%)
            # Matches system capacity - minimal queues
            rate = 250 * scale_factor * weather_factor
            
        elif 60 <= t < 90:
            # Moderate buildup (2h before kickoff)
            # 350 fans/min × 30 min = 10,500 fans (15.4%)
            # Public transport arrivals start - exceeds capacity
            rate = 350 * scale_factor * traffic_factor * rivalry_boost
            
            # Simulate bus/train arrival spike
            if int(t) % 15 == 0:  # Every 15 mins
                rate *= 1.3  # 30% spike from public transport
            
        elif 90 <= t < 120:
            # PEAK RUSH (1.5h to 1h before kickoff)
            # 500 fans/min × 30 min = 15,000 fans (22%)
            # 2× bottleneck capacity - major congestion
            rate = 500 * scale_factor * traffic_factor * rivalry_boost
            
            if int(t) % 10 == 0:  # More frequent arrivals
                rate *= 1.4
            
        elif 120 <= t < 150:
            # Sustained rush (1h to 30min before)
            # 550 fans/min × 30 min = 16,500 fans (24.3%)
            # Maximum congestion period
            rate = 550 * scale_factor * traffic_factor * rivalry_boost
            
            if int(t) % 10 == 0:
                rate *= 1.35
            
        elif 150 <= t < 180:
            # Final rush before kickoff
            # 450 fans/min × 30 min = 13,500 fans (19.9%)
            # Last-minute arrivals rushing to get in
            rate = 450 * scale_factor * rivalry_boost * 1.1
            
        elif 180 <= t < 200:
            # Just after kickoff (latecomers)
            # 25 fans/min × 20 min = 500 fans (0.7%)
            rate = 25 * scale_factor
            
        else:
            # Very late / match in progress
            # 2 fans/min (stragglers, technical issues)
            rate = 2 * scale_factor
        
        # Ensure minimum rate
        rate = max(1, rate)
        
        # Generate fans based on rate - batch arrivals for efficiency
        # Wait a small interval (0.1 min = 6 seconds) and generate appropriate number
        interval = 0.1  # minutes (6 seconds)
        num_fans = max(1, int(random.gauss(rate * interval, rate * interval * 0.3)))
        
        for _ in range(num_fans):
            if fan_id >= total_fans:
                break
                
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
        
        # Wait for next batch
        yield env.timeout(interval)


def get_arrival_rate_info():
    return {
        'total_fans': 68000,
        'arrival_window': 180, 
        'phases': [
            {'name': 'Very Early', 'start': 0, 'end': 30, 'rate': 150, 'fans': 4500, 'pct': 6.6},
            {'name': 'Early', 'start': 30, 'end': 60, 'rate': 250, 'fans': 7500, 'pct': 11.0},
            {'name': 'Moderate', 'start': 60, 'end': 90, 'rate': 350, 'fans': 10500, 'pct': 15.4},
            {'name': 'Peak Rush', 'start': 90, 'end': 120, 'rate': 500, 'fans': 15000, 'pct': 22.1},
            {'name': 'Sustained Rush', 'start': 120, 'end': 150, 'rate': 550, 'fans': 16500, 'pct': 24.3},
            {'name': 'Final Rush', 'start': 150, 'end': 180, 'rate': 450, 'fans': 13500, 'pct': 19.9},
            {'name': 'Latecomers', 'start': 180, 'end': 200, 'rate': 25, 'fans': 500, 'pct': 0.7},
        ],
        'expected_by_kickoff': 67500,  
        'bottleneck_capacity': 250,  
    }