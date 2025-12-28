import random
from agents import fan

TOTAL_FANS = 68000  # Full stadium capacity

def arrival_process(env, stadium, metrics):
    """
    Generates fan arrivals with time-varying rates.
    
    Time units = minutes. Stadium opens 3 hours before kickoff.
    
    Capacity calculation:
    - 92 turnstiles, each processing 30-40 fans/min (modern biometric systems)
    - Max throughput: 92 × 35 (avg) = 3,220 fans/min (theoretical)
    - Realistic sustainable: ~2,500 fans/min with moderate queuing
    - Target: 68,000 fans in 90-120 minutes with realistic flow
    """
    fan_id = 0

    while fan_id < TOTAL_FANS:
        t = env.now

        # Arrival rates (fans per minute) - realistic for major stadium
        if t < 60:
            # First hour - early arrivals (6,000 fans)
            rate = 100
        elif 60 <= t < 90:
            # Building up (15,000 fans)
            rate = 500
        elif 90 <= t < 120:
            # Peak rush 30 min before kickoff (30,000 fans)
            rate = 1000
        elif 120 <= t < 150:
            # Final rush to kickoff (15,000 fans)
            rate = 500
        elif 150 <= t < 180:
            # Just before/at kickoff (2,000 fans)
            rate = 67
        else:
            # Late arrivals (stragglers)
            rate = 10
        
        inter_arrival = random.expovariate(rate)
        yield env.timeout(inter_arrival)
        
        env.process(fan(env, fan_id, stadium, metrics))
        metrics.fans_arrived += 1
        fan_id += 1