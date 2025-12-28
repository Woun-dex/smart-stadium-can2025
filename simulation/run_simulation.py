from env import create_env
from resources import StadiumResources
from arrival import arrival_process
from metrics import MetricsCollector

def run_simulation():
    env = create_env()
    stadium = StadiumResources(env)
    metrics = MetricsCollector(env, stadium, stadium_capacity=68000, kickoff_time=180)

    # Start the arrival process
    env.process(arrival_process(env, stadium, metrics))
    
    # Start the periodic snapshot collector (every 1 minute for ML granularity)
    env.process(metrics.periodic_snapshot(interval=1))

    # Run long enough for all fans to arrive, watch match, and exit
    # Arrival: ~180 min | Match: 120 min | Exit: ~30 min
    # Total: ~330 min, run to 450 to allow halftime vendor visits + exit
    env.run(until=450)
    
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, '..', 'data', 'raw', 'stadium_simulation.csv')
    metrics.save_to_csv(output_path)
    print(f"\n=== Simulation Complete ===")
    print(f"Total fans arrived: {metrics.fans_arrived}")
    print(f"Total fans seated: {metrics.fans_completed}")
    print(f"Total fans exited: {metrics.fans_exited}")
    print(f"Fans remaining in stadium: {metrics.fans_completed - metrics.fans_exited}")
    
    

if __name__ == "__main__":
    run_simulation()