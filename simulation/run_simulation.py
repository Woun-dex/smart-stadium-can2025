"""
Stadium Simulation Runner
=========================
Main entry point for running stadium crowd simulations.
"""
import os
import sys
import random
import simpy

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from env import create_env
from resources import StadiumResources
from arrival import arrival_process, create_arrival_process
from metrics import MetricsCollector
from control import decide_action, apply_action, apply_action_with_details


def run_simulation(save_csv=True, verbose=True):
    """
    Run a single stadium simulation with default parameters.
    Returns the MetricsCollector for analysis.
    """
    print("\n" + "="*60)
    print("STADIUM SIMULATION - Starting")
    print("="*60)
    
    env = create_env()
    stadium = StadiumResources(env)
    metrics = MetricsCollector(env, stadium, stadium_capacity=68000, kickoff_time=180)
    
    print(f"\nConfiguration:")
    print(f"  - Stadium Capacity: 68,000 fans")
    print(f"  - Security Lanes: {stadium.active_security}")
    print(f"  - Entry Turnstiles: {stadium.active_turnstiles}")
    print(f"  - Vendors: {stadium.active_vendors}")
    print(f"  - Exit Gates: {stadium.active_exit_gates}")
    print(f"  - Parking Spots: {stadium.parking.capacity}")
    print(f"  - Kickoff Time: t=180 min")
    print("-"*60)

    # Start the arrival process
    env.process(arrival_process(env, stadium, metrics))
    
    # Start the periodic snapshot collector
    env.process(metrics.periodic_snapshot(interval=1))

    # Run simulation (450 min = full event including exit)
    env.run(until=450)
    
    if save_csv:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '..', 'data', 'raw', 'stadium_simulation.csv')
        metrics.save_to_csv(output_path)
    
    if verbose:
        print(f"\n" + "="*60)
        print("SIMULATION COMPLETE")
        print("="*60)
        print(f"Total fans arrived: {metrics.fans_arrived:,}")
        print(f"Total fans seated: {metrics.fans_completed:,}")
        print(f"Total fans exited: {metrics.fans_exited:,}")
        print(f"Remaining in stadium: {metrics.fans_completed - metrics.fans_exited:,}")
        
        # Print wait time statistics
        if metrics.all_security_waits:
            print(f"\n--- Wait Time Statistics ---")
            print(f"Security Wait: avg={sum(metrics.all_security_waits)/len(metrics.all_security_waits):.2f} min, "
                  f"max={max(metrics.all_security_waits):.2f} min")
        if metrics.all_turnstile_waits:
            print(f"Turnstile Wait: avg={sum(metrics.all_turnstile_waits)/len(metrics.all_turnstile_waits):.2f} min, "
                  f"max={max(metrics.all_turnstile_waits):.2f} min")
        if metrics.all_vendor_waits:
            print(f"Vendor Wait: avg={sum(metrics.all_vendor_waits)/len(metrics.all_vendor_waits):.2f} min, "
                  f"max={max(metrics.all_vendor_waits):.2f} min")
        if metrics.all_exit_waits:
            print(f"Exit Wait: avg={sum(metrics.all_exit_waits)/len(metrics.all_exit_waits):.2f} min, "
                  f"max={max(metrics.all_exit_waits):.2f} min")
    
    return metrics


def run_match_simulation(
    num_fans=68000,
    num_security=30,
    num_turnstiles=20,
    num_vendors=40,
    num_exits=25,
    parking_spots=6000,
    random_seed=42,
    enable_ml_control=False,
    ml_models=None,
    intervention_threshold=10,
    verbose=False
):
    """
    Run stadium simulation with configurable parameters.
    Used for baseline vs ML comparison experiments.
    """
    # Set random seed for reproducibility
    random.seed(random_seed)
    
    # Create environment
    env = create_env()
    
    # Create stadium with custom parameters
    stadium = StadiumResources(env)
    
    # Override resource capacities
    stadium.active_security = num_security
    stadium.security = simpy.Resource(env, capacity=num_security)
    
    stadium.active_turnstiles = num_turnstiles
    stadium.turnstiles = simpy.Resource(env, capacity=num_turnstiles)
    
    stadium.active_vendors = num_vendors
    stadium.vendors = simpy.Resource(env, capacity=num_vendors)
    
    stadium.active_exit_gates = num_exits
    stadium.exit_gates = simpy.Resource(env, capacity=num_exits)
    
    stadium.parking = simpy.Container(env, init=parking_spots, capacity=parking_spots)
    
    # Create metrics collector
    metrics = MetricsCollector(env, stadium, stadium_capacity=num_fans, kickoff_time=180)
    
    # Additional tracking lists for evaluation
    metrics.turnstile_waits = metrics.all_turnstile_waits
    metrics.vendor_waits = metrics.all_vendor_waits
    metrics.exit_waits = metrics.all_exit_waits
    metrics.security_waits = metrics.all_security_waits
    metrics.queue_lengths = []
    metrics.control_actions = []
    
    # Start arrival process with custom fan count
    env.process(create_arrival_process(env, stadium, metrics, total_fans=num_fans))
    
    # Start metrics collection
    env.process(metrics.periodic_snapshot(interval=1))
    
    # ML Control Process (if enabled)
    if enable_ml_control and ml_models is not None:
        env.process(ml_control_process(
            env, stadium, metrics, ml_models, 
            intervention_threshold, verbose
        ))
    
    # Queue length tracking process
    env.process(queue_tracking_process(env, stadium, metrics))
    
    # Run simulation
    env.run(until=450)
    
    return metrics


def ml_control_process(env, stadium, metrics, ml_models, threshold, verbose=False):
    """
    ML-driven control process that monitors and adjusts stadium resources.
    Monitors ENTRY (security + turnstile) and EXIT congestion.
    Runs every 2 minutes during the simulation for faster response.
    """
    print("\n" + "="*60)
    print("ML CONTROL SYSTEM ACTIVATED")
    print("="*60)
    print(f"   Entry thresholds: Queue>5000, Wait>{threshold}min")
    print(f"   Exit thresholds: Queue>3000, Wait>15min")
    print(f"   Risk levels: MODERATE>0.5, STRONG>0.7")
    print("="*60 + "\n")
    
    while True:
        yield env.timeout(2)  # Check every 2 minutes for faster response
        
        # ========== ENTRY RISK CALCULATION ==========
        entry_queue = len(stadium.turnstiles.queue) + len(stadium.security.queue)
        
        # Calculate average entry wait from recent data
        recent_window = 30
        if len(metrics.all_turnstile_waits) >= recent_window:
            avg_entry_wait = sum(metrics.all_turnstile_waits[-recent_window:]) / recent_window
        elif metrics.all_turnstile_waits:
            avg_entry_wait = sum(metrics.all_turnstile_waits) / len(metrics.all_turnstile_waits)
        else:
            avg_entry_wait = 0
        
        # ========== EXIT RISK CALCULATION ==========
        exit_queue = len(stadium.exit_gates.queue)
        
        # Calculate average exit wait from recent data
        if len(metrics.all_exit_waits) >= recent_window:
            avg_exit_wait = sum(metrics.all_exit_waits[-recent_window:]) / recent_window
        elif metrics.all_exit_waits:
            avg_exit_wait = sum(metrics.all_exit_waits) / len(metrics.all_exit_waits)
        else:
            avg_exit_wait = 0
        
        try:
            # ========== ENTRY RISK SCORE ==========
            entry_queue_risk = min(1.0, entry_queue / 5000)
            entry_wait_risk = min(1.0, avg_entry_wait / threshold)
            
            # Time-based risk (higher risk closer to kickoff for entry)
            entry_time_risk = 0
            if env.now < metrics.kickoff_time:
                time_remaining = metrics.kickoff_time - env.now
                if time_remaining < 30:
                    entry_time_risk = 0.3
                elif time_remaining < 60:
                    entry_time_risk = 0.1
            
            entry_risk = (entry_queue_risk * 0.4) + (entry_wait_risk * 0.5) + (entry_time_risk * 0.1)
            
            # ========== EXIT RISK SCORE (More aggressive) ==========
            exit_queue_risk = min(1.0, exit_queue / 1500)  # Lower threshold - 1500 is concerning
            exit_wait_risk = min(1.0, avg_exit_wait / 10)   # 10 min is critical exit wait
            
            # Time-based risk (higher risk after match ends)
            exit_time_risk = 0
            match_end_time = metrics.kickoff_time + 120  # ~2 hours after kickoff
            if env.now > match_end_time:
                time_since_end = env.now - match_end_time
                if time_since_end < 30:
                    exit_time_risk = 0.5  # Very high urgency right after match
                elif time_since_end < 60:
                    exit_time_risk = 0.3
                else:
                    exit_time_risk = 0.1
            elif env.now > metrics.kickoff_time + 90:  # Halftime onwards
                exit_time_risk = 0.15
            
            exit_risk = (exit_queue_risk * 0.35) + (exit_wait_risk * 0.45) + (exit_time_risk * 0.2)
            
            # ========== DETERMINE PHASE & RISK TYPE ==========
            is_exit_phase = env.now > metrics.kickoff_time + 90  # After halftime
            
            # Prioritize exit when fans are leaving (after halftime or exit queue forming)
            if is_exit_phase and exit_queue > 50:
                # During exit phase, always prioritize exit if there's a queue
                predicted_risk = exit_risk
                risk_type = "EXIT"
                current_queue = exit_queue
                current_wait = avg_exit_wait
            elif exit_risk > entry_risk and exit_queue > 50:
                predicted_risk = exit_risk
                risk_type = "EXIT"
                current_queue = exit_queue
                current_wait = avg_exit_wait
            else:
                predicted_risk = entry_risk
                risk_type = "ENTRY"
                current_queue = entry_queue
                current_wait = avg_entry_wait
            
            # Lower thresholds for faster action
            if predicted_risk > 0.7:
                action = "STRONG"
            elif predicted_risk > 0.5:
                action = "MODERATE"
            else:
                action = "NONE"
            
            # ========== APPLY ACTION & LOG ==========
            if action != "NONE":
                action_details = apply_action_with_details(action, stadium, risk_type)
                
                metrics.control_actions.append({
                    'time': env.now,
                    'action': action,
                    'risk_type': risk_type,
                    'risk': predicted_risk,
                    'entry_queue': entry_queue,
                    'exit_queue': exit_queue,
                    'entry_wait': avg_entry_wait,
                    'exit_wait': avg_exit_wait,
                    'details': action_details
                })
                
                # Always print ML actions (this is the real-time feedback)
                icon = "!!" if action == "STRONG" else "**"
                type_icon = "[EXIT]" if risk_type == "EXIT" else "[ENTRY]"
                print(f"\n{icon} ML ACTION t={env.now:.0f}min | {action} {type_icon}")
                print(f"   Risk: {predicted_risk:.2f} | Queue: {current_queue:,} | Wait: {current_wait:.1f}min")
                print(f"   -> {action_details}")
                
            elif int(env.now) % 30 == 0:  # Status update every 30 min
                phase = "EXIT" if is_exit_phase else "ENTRY"
                print(f"-- ML STATUS t={env.now:.0f}min | Phase: {phase} | Entry Risk: {entry_risk:.2f} | Exit Risk: {exit_risk:.2f}")
                    
        except Exception as e:
            print(f"[ML Control] Error: {e}")


def queue_tracking_process(env, stadium, metrics):
    """Track queue lengths over time for analysis."""
    while True:
        yield env.timeout(1)  # Every minute
        total_queue = len(stadium.security.queue) + len(stadium.turnstiles.queue)
        metrics.queue_lengths.append({
            'time': env.now,
            'security_queue': len(stadium.security.queue),
            'turnstile_queue': len(stadium.turnstiles.queue),
            'total_entry_queue': total_queue,
            'exit_queue': len(stadium.exit_gates.queue),
        })


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Stadium Simulation')
    parser.add_argument('--fans', type=int, default=68000, help='Number of fans')
    parser.add_argument('--security', type=int, default=30, help='Security lanes')
    parser.add_argument('--turnstiles', type=int, default=20, help='Entry turnstiles')
    parser.add_argument('--exits', type=int, default=25, help='Exit gates')
    parser.add_argument('--ml', action='store_true', help='Enable ML control')
    args = parser.parse_args()
    
    if args.fans != 68000 or args.security != 30 or args.turnstiles != 20 or args.exits != 25 or args.ml:
        # Run with custom parameters
        metrics = run_match_simulation(
            num_fans=args.fans,
            num_security=args.security,
            num_turnstiles=args.turnstiles,
            num_exits=args.exits,
            enable_ml_control=args.ml,
            ml_models={'dummy': True} if args.ml else None,
            verbose=True
        )
        # Save to CSV
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '..', 'data', 'raw', 'stadium_simulation.csv')
        metrics.save_to_csv(output_path)
    else:
        metrics = run_simulation(save_csv=True, verbose=True)