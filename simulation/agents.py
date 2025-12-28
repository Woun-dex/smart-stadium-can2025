import random

def fan(env, fan_id, stadium, metrics):
    """
    Simulates a single fan's journey through the stadium.
    
    Journey: Parking (optional) -> Turnstile -> Concourse -> Vendor (optional) -> Seat
    """
    arrival_time = env.now
    
    # 40% of fans use parking (others use public transport/walk/rideshare)
    # 6000 parking / 68000 fans = ~9% max can park, but many arrive together
    uses_parking = random.random() < 0.40
    
    if uses_parking:
        # Try to get parking spot
        if stadium.parking.level > 0:
            yield stadium.parking.get(1)  # Take one parking spot
            metrics.log_parking_used()
            # Walk from parking to turnstile area (1-3 min)
            yield env.timeout(random.uniform(1, 3))
    
    # Queue at biometric turnstile (92 turnstiles shared across all fans)
    with stadium.turnstiles.request() as req:
        turnstile_start = env.now
        yield req
        wait_time = env.now - turnstile_start
        metrics.log_turnstile_wait(wait_time)
        
        # Biometric scan + ticket validation (modern systems: 1.5-2 seconds per fan)
        # 1.5-2 seconds = 0.025-0.033 minutes = 30-40 fans/min per turnstile
        yield env.timeout(random.uniform(0.025, 0.033))

    # Walk through concourse to section (1-3 minutes for large stadium)
    yield env.timeout(random.uniform(1, 3))

    # Some fans visit vendors before finding seat (8% chance - quick snack/drink)
    if random.random() < 0.03:
        with stadium.vendors.request() as v_req:
            vendor_start = env.now
            yield v_req
            vendor_wait = env.now - vendor_start
            metrics.log_vendor_wait(vendor_wait)
            
            # Service time at vendor (1-4 minutes: order, pay, receive)
            yield env.timeout(random.uniform(1, 4))
        # Note: vendor resource is automatically released when 'with' block exits

    # Walk to seat and find seat (0.5-1.5 minutes)
    yield env.timeout(random.uniform(0.5, 1.5))

    # Fan is now seated
    metrics.fans_completed += 1
    
    # === EXIT LOGIC AFTER MATCH ===
    # Match duration: 90 min regular time + 15 min halftime + injury time
    # Most fans stay until final whistle (~300 min from start = 180 kickoff + 120 match)
    # Some leave early (85th min onwards), most leave at full time
    match_end_time = 180 + 120  # 300 minutes (kickoff + match duration)
    
    # Wait until match end time (with some variation)
    # 10% leave 10-20 min early (traffic beaters)
    # 70% leave at full time (match_end_time ± 5 min)
    # 20% leave 5-15 min late (celebrations, bathroom, etc.)
    leave_decision = random.random()
    if leave_decision < 0.10:
        # Early leavers
        exit_time = match_end_time - random.uniform(10, 20)
    elif leave_decision < 0.80:
        # Normal exit (most fans)
        exit_time = match_end_time + random.uniform(-5, 5)
    else:
        # Late leavers
        exit_time = match_end_time + random.uniform(5, 15)
    
    # During match, some fans visit vendors at halftime (~t=225, which is kickoff+45min)
    halftime_start = 180 + 45  # t=225
    current_time = env.now
    
    # Only visit vendors at halftime if already seated before halftime and won't miss exit
    # 5% of fans visit vendors during halftime (most bought food before sitting)
    if current_time < halftime_start and random.random() < 0.0:
        # Wait until halftime
        yield env.timeout(halftime_start - current_time + random.uniform(0, 5))
        
        # Visit vendor during halftime
        with stadium.vendors.request() as v_req:
            vendor_start = env.now
            yield v_req
            vendor_wait = env.now - vendor_start
            metrics.log_vendor_wait(vendor_wait)
            yield env.timeout(random.uniform(2, 3))
    
    # Wait until exit time
    time_to_wait = max(0, exit_time - env.now)
    yield env.timeout(time_to_wait)
    
    # Exit through turnstiles (faster on exit - no ticket scan, just flow out)
    # Exit processing: 0.5-1 second per fan = 0.008-0.017 minutes = 60-120 fans/min per exit
    with stadium.turnstiles.request() as exit_req:
        exit_turnstile_start = env.now
        yield exit_req
        exit_wait = env.now - exit_turnstile_start
        metrics.log_exit_wait(exit_wait)
        
        # Quick exit through turnstile (0.008-0.017 min = 0.5-1 sec)
        yield env.timeout(random.uniform(0.008, 0.017))
    
    # If they parked, walk to car and leave (2-5 min to parking + exit)
    if uses_parking:
        yield env.timeout(random.uniform(2, 5))
        stadium.parking.put(1)  # Return parking spot
    
    # Fan has now exited the stadium
    metrics.fans_exited += 1
    