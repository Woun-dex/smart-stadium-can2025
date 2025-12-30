"""
AFCON 2025 Morocco - Stadium Simulation API
Flask backend to run SimPy simulations for the React dashboard
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import simpy
import random
import math

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Stadium configurations
STADIUMS = {
    'prince-moulay-abdellah': {'name': 'Prince Moulay Abdellah Stadium', 'city': 'Rabat', 'capacity': 69500},
    'complexe-olympique-rabat': {'name': 'Complexe Sportif Prince Moulay Abdellah Olympic Stadium', 'city': 'Rabat', 'capacity': 21000},
    'prince-heritier-rabat': {'name': 'Complexe Sportif Prince Heritier Moulay El Hassan', 'city': 'Rabat', 'capacity': 22000},
    'el-barid-rabat': {'name': 'Stade El Barid', 'city': 'Rabat', 'capacity': 18000},
    'grand-agadir': {'name': 'Grande Stade d\'Agadir', 'city': 'Agadir', 'capacity': 45480},
    'complexe-fes': {'name': 'Complexe Sportif de Fes', 'city': 'Fes', 'capacity': 45000},
    'grand-marrakech': {'name': 'Grande Stade de Marrakech', 'city': 'Marrakech', 'capacity': 45240},
    'mohammed-v-casa': {'name': 'Stade Mohammed V', 'city': 'Casablanca', 'capacity': 67000},
    'grand-tangier': {'name': 'Grande Stade de Tangier', 'city': 'Tangier', 'capacity': 68000}
}


def get_stadium_resources(capacity):
    """Calculate resource counts based on stadium capacity"""
    ratio = capacity / 50000
    return {
        'security_gates': max(20, round(30 * ratio)),
        'turnstiles': max(15, round(25 * ratio)),
        'vendors': max(30, round(50 * ratio)),
        'exit_gates': max(20, round(30 * ratio))
    }


@app.route('/api/stadiums', methods=['GET'])
def get_stadiums():
    """Get list of all stadiums"""
    return jsonify(list(STADIUMS.values()))


@app.route('/api/simulate', methods=['POST'])
def run_simulation():
    """Run a stadium simulation"""
    try:
        data = request.json
        stadium = data.get('stadium', {})
        num_fans = data.get('fans', 40000)
        resources = data.get('resources', {})
        ml_enabled = data.get('mlEnabled', True)
        
        stadium_id = stadium.get('id', 'grand-marrakech')
        capacity = stadium.get('capacity', 45000)
        
        # Get resources
        if not resources:
            resources = get_stadium_resources(capacity)
        
        security_gates = resources.get('securityGates', 30)
        turnstiles = resources.get('turnstiles', 20)
        vendors = resources.get('vendors', 40)
        exit_gates = resources.get('exitGates', 25)
        
        # Run simulation
        result = run_stadium_simulation(
            num_fans=num_fans,
            security_gates=security_gates,
            turnstiles=turnstiles,
            vendors=vendors,
            exit_gates=exit_gates,
            ml_enabled=ml_enabled
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def run_stadium_simulation(num_fans, security_gates, turnstiles, vendors, exit_gates, ml_enabled):
    """Run the actual SimPy simulation"""
    import simpy
    
    # Simulation parameters
    KICKOFF_TIME = 180  # 3 hours from start
    MATCH_DURATION = 120  # 2 hours
    SIM_DURATION = 360  # 6 hours total
    
    env = simpy.Environment()
    
    # Create resources
    security = simpy.Resource(env, capacity=security_gates)
    turnstile = simpy.Resource(env, capacity=turnstiles)
    vendor = simpy.Resource(env, capacity=vendors)
    exit_res = simpy.Resource(env, capacity=exit_gates)
    
    # Metrics collection
    metrics = {
        'timeseries': [],
        'wait_times': {
            'security': [], 'turnstile': [], 'exit': [], 'vendor': []
        },
        'queues': {
            'security': [], 'turnstile': [], 'exit': [], 'vendor': []
        },
        'inside_stadium': 0,
        'total_entered': 0,
        'total_exited': 0
    }
    
    # ML control actions
    ml_actions = []
    current_resources = {
        'security': security_gates,
        'entry': turnstiles,
        'exit': exit_gates,
        'vendors': vendors
    }
    
    def fan_process(fan_id, arrival_time):
        """Process a single fan through the stadium"""
        nonlocal metrics
        
        yield env.timeout(arrival_time)
        
        # Security check
        sec_start = env.now
        with security.request() as req:
            yield req
            sec_wait = env.now - sec_start
            metrics['wait_times']['security'].append(sec_wait)
            yield env.timeout(random.uniform(0.3, 0.8))  # Service time
        
        # Turnstile
        turn_start = env.now
        with turnstile.request() as req:
            yield req
            turn_wait = env.now - turn_start
            metrics['wait_times']['turnstile'].append(turn_wait)
            yield env.timeout(random.uniform(0.1, 0.3))
        
        metrics['inside_stadium'] += 1
        metrics['total_entered'] += 1
        
        # Vendor visit (30% chance before match)
        if random.random() < 0.3 and env.now < KICKOFF_TIME:
            vend_start = env.now
            with vendor.request() as req:
                yield req
                vend_wait = env.now - vend_start
                metrics['wait_times']['vendor'].append(vend_wait)
                yield env.timeout(random.uniform(0.5, 2))
        
        # Wait for match end
        if env.now < KICKOFF_TIME + MATCH_DURATION:
            yield env.timeout(KICKOFF_TIME + MATCH_DURATION - env.now + random.uniform(0, 30))
        
        # Exit
        exit_start = env.now
        with exit_res.request() as req:
            yield req
            exit_wait = env.now - exit_start
            metrics['wait_times']['exit'].append(exit_wait)
            yield env.timeout(random.uniform(0.2, 0.5))
        
        metrics['inside_stadium'] -= 1
        metrics['total_exited'] += 1
    
    def metrics_collector():
        """Collect metrics at regular intervals"""
        while True:
            t = env.now
            
            sec_waits = metrics['wait_times']['security'][-100:] if metrics['wait_times']['security'] else [0]
            turn_waits = metrics['wait_times']['turnstile'][-100:] if metrics['wait_times']['turnstile'] else [0]
            exit_waits = metrics['wait_times']['exit'][-100:] if metrics['wait_times']['exit'] else [0]
            vend_waits = metrics['wait_times']['vendor'][-100:] if metrics['wait_times']['vendor'] else [0]
            
            metrics['timeseries'].append({
                'time': round(t),
                'security_queue': len(security.queue),
                'turnstile_queue': len(turnstile.queue),
                'exit_queue': len(exit_res.queue),
                'vendor_queue': len(vendor.queue),
                'avg_security_wait': round(sum(sec_waits) / len(sec_waits), 2),
                'avg_turnstile_wait': round(sum(turn_waits) / len(turn_waits), 2),
                'avg_exit_wait': round(sum(exit_waits) / len(exit_waits), 2),
                'avg_vendor_wait': round(sum(vend_waits) / len(vend_waits), 2),
                'inside_stadium': metrics['inside_stadium'],
                'total_entered': metrics['total_entered'],
                'total_exited': metrics['total_exited']
            })
            
            yield env.timeout(1)
    
    def ml_control():
        """ML crowd control process"""
        nonlocal ml_actions, current_resources
        
        while True:
            yield env.timeout(5)  # Check every 5 minutes
            
            if not ml_enabled:
                continue
            
            t = env.now
            entry_queue = len(security.queue) + len(turnstile.queue)
            exit_queue = len(exit_res.queue)
            
            # Recent waits
            sec_waits = metrics['wait_times']['security'][-50:] if metrics['wait_times']['security'] else [0]
            exit_waits = metrics['wait_times']['exit'][-50:] if metrics['wait_times']['exit'] else [0]
            
            avg_sec_wait = sum(sec_waits) / len(sec_waits)
            avg_exit_wait = sum(exit_waits) / len(exit_waits)
            
            # Risk calculations
            entry_risk = min(entry_queue / 5000, 1) * 0.4 + min(avg_sec_wait / 15, 1) * 0.5
            exit_risk = min(exit_queue / 2000, 1) * 0.4 + min(avg_exit_wait / 10, 1) * 0.5
            
            # Exit actions
            if exit_queue > 500 and exit_risk > 0.4:
                old_exit = current_resources['exit']
                increment = 10 if exit_risk > 0.6 else 5
                current_resources['exit'] = min(current_resources['exit'] + increment, 80)
                
                ml_actions.append({
                    'time': round(t),
                    'type': 'STRONG' if exit_risk > 0.6 else 'MODERATE',
                    'riskType': 'EXIT',
                    'risk': round(exit_risk, 2),
                    'queue': exit_queue,
                    'decision': f'+{increment} exit gates ({old_exit}→{current_resources["exit"]})',
                    'security': current_resources['security'],
                    'entry': current_resources['entry'],
                    'exit': current_resources['exit'],
                    'vendors': current_resources['vendors']
                })
                
            # Entry actions
            elif entry_queue > 500 and entry_risk > 0.5:
                old_sec = current_resources['security']
                old_vend = current_resources['vendors']
                
                if entry_risk > 0.7:
                    current_resources['security'] = min(current_resources['security'] + 5, 80)
                    current_resources['vendors'] = min(current_resources['vendors'] + 10, 150)
                else:
                    current_resources['security'] = min(current_resources['security'] + 3, 80)
                    current_resources['vendors'] = min(current_resources['vendors'] + 5, 150)
                
                ml_actions.append({
                    'time': round(t),
                    'type': 'STRONG' if entry_risk > 0.7 else 'MODERATE',
                    'riskType': 'ENTRY',
                    'risk': round(entry_risk, 2),
                    'queue': entry_queue,
                    'decision': f'Security {old_sec}→{current_resources["security"]}, Vendors {old_vend}→{current_resources["vendors"]}',
                    'security': current_resources['security'],
                    'entry': current_resources['entry'],
                    'exit': current_resources['exit'],
                    'vendors': current_resources['vendors']
                })
    
    # Generate arrivals - peak before kickoff
    arrival_times = []
    for i in range(num_fans):
        # Gaussian distribution peaking at 60 min before kickoff
        peak = KICKOFF_TIME - 60
        spread = 45
        t = random.gauss(peak, spread)
        t = max(0, min(t, KICKOFF_TIME - 5))  # Clamp to valid range
        arrival_times.append(t)
    
    arrival_times.sort()
    
    # Start processes
    for i, arrival_time in enumerate(arrival_times):
        env.process(fan_process(i, arrival_time))
    
    env.process(metrics_collector())
    env.process(ml_control())
    
    # Run simulation
    env.run(until=SIM_DURATION)
    
    # Calculate summary stats
    timeseries = metrics['timeseries']
    all_sec_waits = metrics['wait_times']['security']
    all_turn_waits = metrics['wait_times']['turnstile']
    all_exit_waits = metrics['wait_times']['exit']
    
    avg_sec = sum(all_sec_waits) / len(all_sec_waits) if all_sec_waits else 0
    avg_turn = sum(all_turn_waits) / len(all_turn_waits) if all_turn_waits else 0
    avg_exit = sum(all_exit_waits) / len(all_exit_waits) if all_exit_waits else 0
    
    max_entry_q = max(r['security_queue'] + r['turnstile_queue'] for r in timeseries)
    max_exit_q = max(r['exit_queue'] for r in timeseries)
    
    return {
        'timeseries': timeseries,
        'actions': ml_actions,
        'summary': {
            'totalFans': num_fans,
            'avgSecurityWait': round(avg_sec, 1),
            'avgTurnstileWait': round(avg_turn, 1),
            'avgExitWait': round(avg_exit, 1),
            'maxEntryQueue': max_entry_q,
            'maxExitQueue': max_exit_q,
            'totalActions': len(ml_actions)
        },
        'resources': {
            'initial': {
                'securityGates': security_gates,
                'turnstiles': turnstiles,
                'exitGates': exit_gates,
                'vendors': vendors
            },
            'final': current_resources
        }
    }


if __name__ == '__main__':
    print("Starting AFCON 2025 Stadium Simulation API...")
    print("Access the API at http://localhost:5000")
    app.run(debug=True, port=5000)
