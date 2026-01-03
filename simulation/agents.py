"""
Stadium Fan Agent - Simulates individual fan journey through stadium
====================================================================
Realistic queuing model with proper wait time accumulation.

NEW REALISTIC BEHAVIORS:
- Group arrivals with coordination
- VIP fast-track lanes
- Bathroom visits (pre-match, halftime, post-match)
- Multiple concession visits
- Merchandise shopping
- Realistic exit timing (early leavers, post-celebration lingering)
- Dynamic behavior based on match events
"""
import random


def fan_group(env, fan_id, stadium, metrics, group_size):
    """
    Fan arriving in a group - stays together through journey.
    Groups take slightly longer at vendors and coordinate movements.
    """
    arrival_time = env.now
    
    # Log phase
    if hasattr(metrics, 'log_time_phase'):
        metrics.log_time_phase(env.now)
    
    # Parking (60% of groups drive)
    uses_parking = random.random() < 0.60
    
    if uses_parking and stadium.parking.level > 0:
        yield stadium.parking.get(1)
        metrics.log_parking_used()
        yield env.timeout(random.uniform(3, 7))  # Groups take longer
    
    # Security - groups may split across lanes
    with stadium.security.request() as sec_req:
        security_queue_start = env.now
        yield sec_req
        security_wait = env.now - security_queue_start
        metrics.log_security_wait(security_wait)
        
        # Groups take slightly longer (bags, kids)
        screening_time = random.uniform(0.1, 0.2)
        yield env.timeout(screening_time)
    
    # Turnstile - each person scans individually
    with stadium.turnstiles.request() as gate_req:
        turnstile_queue_start = env.now
        yield gate_req
        turnstile_wait = env.now - turnstile_queue_start
        metrics.log_turnstile_wait(turnstile_wait)
        
        base_service = random.uniform(0.083, 0.125)
        service_factor = getattr(stadium, 'turnstile_service_factor', 1.0)
        actual_service = base_service / service_factor
        yield env.timeout(actual_service * group_size * 0.8)  # Slight efficiency
    
    # Groups often stop at concessions (70% vs 20% individuals)
    if random.random() < 0.70:
        yield env.timeout(random.uniform(2, 5))  # Navigate to vendor
        
        with stadium.vendors.request() as v_req:
            vendor_queue_start = env.now
            yield v_req
            vendor_wait = env.now - vendor_queue_start
            metrics.log_vendor_wait(vendor_wait)
            
            # Groups take longer (multiple orders)
            yield env.timeout(random.uniform(1.5, 3.0))
    
    # Bathroom stop (30% of groups)
    if random.random() < 0.30:
        yield env.timeout(random.uniform(3, 6))
    
    # Find seats
    yield env.timeout(random.uniform(1.0, 2.5))
    
    metrics.fans_completed += 1
    
    # Watch match and exit
    match_end_time = 290
    
    # Groups tend to leave earlier or later together
    exit_decision = random.random()
    if exit_decision < 0.12:  # 12% early exit (families with kids)
        exit_time = match_end_time - random.uniform(15, 25)
    elif exit_decision < 0.75:
        exit_time = match_end_time + random.uniform(0, 15)
    else:
        exit_time = match_end_time + random.uniform(15, 35)  # Stay longer
    
    yield env.timeout(max(0, exit_time - env.now))
    
    # Exit
    with stadium.exit_gates.request() as exit_req:
        exit_queue_start = env.now
        yield exit_req
        exit_wait = env.now - exit_queue_start
        metrics.log_exit_wait(exit_wait)
        
        exit_service = random.uniform(0.033, 0.067)
        yield env.timeout(exit_service * group_size * 0.7)
    
    if uses_parking:
        yield env.timeout(random.uniform(4, 8))
        stadium.parking.put(1)
    
    metrics.fans_exited += 1


def vip_fan(env, fan_id, stadium, metrics):
    """
    VIP fan with fast-track access.
    Skips most queues, has access to premium lounges.
    """
    arrival_time = env.now
    
    if hasattr(metrics, 'log_time_phase'):
        metrics.log_time_phase(env.now)
    
    # VIP parking (reserved)
    if stadium.parking.level > 0:
        yield stadium.parking.get(1)
        metrics.log_parking_used()
        yield env.timeout(random.uniform(1, 2))  # Closer parking
    
    # Express security (minimal wait)
    with stadium.security.request() as sec_req:
        security_queue_start = env.now
        yield sec_req
        security_wait = env.now - security_queue_start
        metrics.log_security_wait(security_wait * 0.3)  # Fast-track
        
        yield env.timeout(random.uniform(0.05, 0.1))  # Quick screening
    
    # Express turnstile
    with stadium.turnstiles.request() as gate_req:
        turnstile_queue_start = env.now
        yield gate_req
        turnstile_wait = env.now - turnstile_queue_start
        metrics.log_turnstile_wait(turnstile_wait * 0.2)  # VIP lane
        
        yield env.timeout(random.uniform(0.04, 0.08))  # Fast entry
    
    # VIP lounge visit (80% of VIPs)
    if random.random() < 0.80:
        yield env.timeout(random.uniform(10, 20))  # Lounge time
    
    # Minimal walking
    yield env.timeout(random.uniform(0.5, 1.5))
    
    metrics.fans_completed += 1
    
    # VIPs tend to stay full match
    match_end_time = 290
    exit_time = match_end_time + random.uniform(5, 20)
    
    yield env.timeout(max(0, exit_time - env.now))
    
    # VIP exit (separate gates)
    with stadium.exit_gates.request() as exit_req:
        exit_queue_start = env.now
        yield exit_req
        exit_wait = env.now - exit_queue_start
        metrics.log_exit_wait(exit_wait * 0.3)
        
        yield env.timeout(random.uniform(0.02, 0.05))
    
    if stadium.parking.level < stadium.MAX_PARKING:
        yield env.timeout(random.uniform(2, 4))
        stadium.parking.put(1)
    
    metrics.fans_exited += 1


def fan(env, fan_id, stadium, metrics):
    """
    Simulates a single fan's journey through the stadium.
    
    Journey: Arrival -> Parking (optional) -> Security -> Turnstile -> 
             Concourse -> Vendor (optional) -> Bathroom (optional) ->
             Merchandise (optional) -> Seat -> Watch Match -> 
             Halftime activities -> Exit
    
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
        # Walk from parking to entry area (variable distance)
        yield env.timeout(random.uniform(2, 6))
    
    # =====================
    # SECURITY SCREENING
    # =====================
    with stadium.security.request() as sec_req:
        security_queue_start = env.now
        yield sec_req
        security_wait = env.now - security_queue_start
        metrics.log_security_wait(security_wait)
        
        # Security screening: 5-10 seconds (walk-through metal detector)
        # Some fans trigger alarms (10% take longer)
        if random.random() < 0.10:
            screening_time = random.uniform(0.3, 0.6)  # Manual check
        else:
            screening_time = random.uniform(0.083, 0.167)
        yield env.timeout(screening_time)
    
    # =====================
    # TURNSTILE ENTRY
    # =====================
    queue_length = len(stadium.turnstiles.queue) + stadium.turnstiles.count
    expected_wait = queue_length * 0.1
    if hasattr(metrics, 'log_future_wait'):
        metrics.log_future_wait(expected_wait)
    
    with stadium.turnstiles.request() as gate_req:
        turnstile_queue_start = env.now
        yield gate_req
        turnstile_wait = env.now - turnstile_queue_start
        metrics.log_turnstile_wait(turnstile_wait)
        
        # Biometric scan + ticket validation: 5-7.5 seconds
        # Some tickets fail (5% need assistance)
        if random.random() < 0.05:
            base_service = random.uniform(0.3, 0.5)  # Technical issue
        else:
            base_service = random.uniform(0.083, 0.125)
        
        service_factor = getattr(stadium, 'turnstile_service_factor', 1.0)
        actual_service = base_service / service_factor
        yield env.timeout(actual_service)
    
    # =====================
    # CONCOURSE ACTIVITIES
    # =====================
    
    # Navigate concourse
    yield env.timeout(random.uniform(1.5, 4))
    
    # Bathroom visit (25% before seating)
    if random.random() < 0.25:
        yield env.timeout(random.uniform(2, 5))  # Bathroom queue + use
    
    # Merchandise shop (15% buy souvenirs)
    if random.random() < 0.15:
        yield env.timeout(random.uniform(3, 8))  # Browse and purchase
    
    # =====================
    # VENDOR VISIT (30% before seating - increased)
    # =====================
    if random.random() < 0.30:
        with stadium.vendors.request() as v_req:
            vendor_queue_start = env.now
            yield v_req
            vendor_wait = env.now - vendor_queue_start
            metrics.log_vendor_wait(vendor_wait)
            
            # Service time at vendor (0.5-2 minutes)
            yield env.timeout(random.uniform(0.5, 2.0))
    
    # =====================
    # FIND SEAT
    # =====================
    yield env.timeout(random.uniform(0.5, 2.0))
    
    # Fan is now seated
    metrics.fans_completed += 1
    
    # =====================
    # WATCH MATCH & ACTIVITIES
    # =====================
    match_end_time = 290  # Full time at ~t=290
    halftime_start = 225  # Halftime at t=225
    halftime_end = 240    # Second half starts
    
    # -------- HALFTIME ACTIVITIES --------
    if env.now < halftime_start:
        # Wait until halftime
        yield env.timeout(max(0, halftime_start - env.now + random.uniform(0, 3)))
        
        halftime_activity = random.random()
        
        if halftime_activity < 0.35:  # 35% visit vendor at halftime
            with stadium.vendors.request() as v_req:
                vendor_start = env.now
                yield v_req
                metrics.log_vendor_wait(env.now - vendor_start)
                yield env.timeout(random.uniform(1.5, 3.0))
        
        elif halftime_activity < 0.55:  # 20% bathroom break
            yield env.timeout(random.uniform(3, 6))
        
        # Return to seat before second half
        if env.now < halftime_end:
            yield env.timeout(max(0, halftime_end - env.now + random.uniform(-2, 5)))
    
    # -------- EXIT TIMING DECISION --------
    exit_decision = random.random()
    
    if exit_decision < 0.05:  # 5% leave very early (emergency, bored)
        exit_time = match_end_time - random.uniform(30, 45)
    elif exit_decision < 0.13:  # 8% beat the traffic
        exit_time = match_end_time - random.uniform(10, 20)
    elif exit_decision < 0.80:  # 67% leave soon after final whistle
        exit_time = match_end_time + random.uniform(0, 15)
    elif exit_decision < 0.95:  # 15% linger (celebrate, avoid crowds)
        exit_time = match_end_time + random.uniform(15, 30)
    else:  # 5% stay very late (cleanup crew, celebration)
        exit_time = match_end_time + random.uniform(30, 50)
    
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
    