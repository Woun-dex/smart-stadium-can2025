"""
Stadium Fan Agent - Simulates individual fan journey through stadium
====================================================================
Realistic queuing model with proper wait time accumulation.
"""
import random


def fan(env, fan_id, stadium, metrics):
    """
    Simulates a single fan's journey through the stadium.
    
    Journey: Arrival -> Parking (optional) -> Security -> Turnstile -> 
             Concourse -> Vendor (optional) -> Seat -> Watch Match -> Exit
    
    All times in minutes.
    """
    arrival_time = env.now
    
    # Log current phase for ML
    if hasattr(metrics, 'log_time_phase'):
        metrics.log_time_phase(env.now)
    
    # =====================
    # PARKING (40% of fans)
    # =====================
    uses_parking = random.random() < 0.40
    
    if uses_parking and stadium.parking.level > 0:
        yield stadium.parking.get(1)
        metrics.log_parking_used()
        # Walk from parking to entry area
        yield env.timeout(random.uniform(2, 5))
    
    # =====================
    # SECURITY SCREENING
    # =====================
    # All fans go through security before turnstiles
    # Modern walk-through scanners: 5-10 seconds per person
    # = 0.083 to 0.167 minutes
    with stadium.security.request() as sec_req:
        security_queue_start = env.now
        yield sec_req
        security_wait = env.now - security_queue_start
        metrics.log_security_wait(security_wait)
        
        # Security screening: 5-10 seconds (walk-through metal detector)
        screening_time = random.uniform(0.083, 0.167)
        yield env.timeout(screening_time)
    
    # =====================
    # TURNSTILE ENTRY
    # =====================
    # Queue at biometric turnstile - THIS IS THE MAIN BOTTLENECK
    queue_length = len(stadium.turnstiles.queue) + stadium.turnstiles.count
    expected_wait = queue_length * 0.1  # Rough estimate
    if hasattr(metrics, 'log_future_wait'):
        metrics.log_future_wait(expected_wait)
    
    with stadium.turnstiles.request() as gate_req:
        turnstile_queue_start = env.now
        yield gate_req
        turnstile_wait = env.now - turnstile_queue_start
        metrics.log_turnstile_wait(turnstile_wait)
        
        # Biometric scan + ticket validation: 5-7.5 seconds
        # (0.083 - 0.125 minutes) = ~8-12 fans/min per turnstile
        base_service = random.uniform(0.083, 0.125)
        service_factor = getattr(stadium, 'turnstile_service_factor', 1.0)
        actual_service = base_service / service_factor
        yield env.timeout(actual_service)
    
    # =====================
    # CONCOURSE WALK
    # =====================
    yield env.timeout(random.uniform(2, 4))
    
    # =====================
    # VENDOR VISIT (20% of fans before seating)
    # =====================
    if random.random() < 0.20:
        with stadium.vendors.request() as v_req:
            vendor_queue_start = env.now
            yield v_req
            vendor_wait = env.now - vendor_queue_start
            metrics.log_vendor_wait(vendor_wait)
            
            # Service time at vendor (0.5-1.5 minutes)
            yield env.timeout(random.uniform(0.5, 1.5))
    
    # =====================
    # FIND SEAT
    # =====================
    yield env.timeout(random.uniform(0.5, 1.5))
    
    # Fan is now seated
    metrics.fans_completed += 1
    
    # =====================
    # WATCH MATCH & EXIT
    # =====================
    match_end_time = 290  # Full time at ~t=290
    
    # Decide exit timing
    exit_decision = random.random()
    if exit_decision < 0.08:
        exit_time = match_end_time - random.uniform(10, 20)
    elif exit_decision < 0.85:
        exit_time = match_end_time + random.uniform(0, 10)
    else:
        exit_time = match_end_time + random.uniform(10, 25)
    
    # Halftime vendor visit (10% of seated fans)
    halftime_start = 225
    if env.now < halftime_start and random.random() < 0.10:
        yield env.timeout(max(0, halftime_start - env.now + random.uniform(0, 5)))
        
        with stadium.vendors.request() as v_req:
            vendor_start = env.now
            yield v_req
            metrics.log_vendor_wait(env.now - vendor_start)
            yield env.timeout(random.uniform(1.5, 2.5))
    
    # Wait until exit time
    yield env.timeout(max(0, exit_time - env.now))
    
    # =====================
    # EXIT THROUGH GATES
    # =====================
    with stadium.exit_gates.request() as exit_req:
        exit_queue_start = env.now
        yield exit_req
        exit_wait = env.now - exit_queue_start
        metrics.log_exit_wait(exit_wait)
        
        # Exit: 2-4 seconds per person (0.033 - 0.067 minutes)
        exit_service = random.uniform(0.033, 0.067)
        yield env.timeout(exit_service)
    
    # Return to parking if applicable
    if uses_parking:
        yield env.timeout(random.uniform(3, 6))
        stadium.parking.put(1)
    
    # Fan has exited
    metrics.fans_exited += 1
    