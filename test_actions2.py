import pandas as pd

def generate_ml_actions(data):
    if data is None or len(data) < 10:
        return []
    
    actions = []
    kickoff_time = 180
    match_end_time = kickoff_time + 120
    
    security_gates = 30
    entry_gates = 20
    exit_gates = 25
    vendors = 40
    
    # More frequent sampling
    check_points = range(5, len(data), max(1, len(data)//50))
    
    for idx in check_points:
        row = data.iloc[idx]
        t = row["time"]
        
        sec_q = row.get("security_queue", 0)
        turn_q = row.get("turnstile_queue", 0)
        entry_queue = sec_q + turn_q
        entry_wait = max(row.get("avg_security_wait", 0), row.get("avg_turnstile_wait", 0))
        
        exit_q = row.get("exit_queue", 0)
        exit_wait = row.get("avg_exit_wait", 0)
        
        entry_risk = min(entry_queue/5000, 1)*0.4 + min(entry_wait/15, 1)*0.5
        exit_risk = min(exit_q/2000, 1)*0.4 + min(exit_wait/10, 1)*0.5 + (0.2 if t > match_end_time-30 else 0)
        
        # Priority: EXIT first if queue building
        if exit_q > 500:
            if exit_risk > 0.4:
                old = exit_gates
                exit_gates = min(exit_gates + (10 if exit_risk > 0.6 else 5), 80)
                actions.append({
                    "time": t, "type": "STRONG" if exit_risk > 0.6 else "MODERATE", 
                    "risk_type": "EXIT", "exit_q": exit_q, "exit": exit_gates
                })
        elif entry_queue > 500:
            if entry_risk > 0.5:
                security_gates = min(security_gates + (5 if entry_risk > 0.7 else 3), 80)
                vendors = min(vendors + (10 if entry_risk > 0.7 else 5), 150)
                actions.append({
                    "time": t, "type": "STRONG" if entry_risk > 0.7 else "MODERATE", 
                    "risk_type": "ENTRY", "queue": entry_queue, "sec": security_gates, "vend": vendors
                })
    
    return actions

data = pd.read_csv("data/raw/stadium_simulation.csv")
actions = generate_ml_actions(data)

print(f"Total actions: {len(actions)}")
print(f"  ENTRY actions: {len([a for a in actions if a['risk_type']=='ENTRY'])}")
print(f"  EXIT actions: {len([a for a in actions if a['risk_type']=='EXIT'])}")

print("\n=== ENTRY ACTIONS (first 5) ===")
for a in [x for x in actions if x["risk_type"]=="ENTRY"][:5]:
    print(f"  t={a['time']}: {a['type']} | Queue={a['queue']} | Sec->{a['sec']} Vend->{a['vend']}")

print("\n=== EXIT ACTIONS ===")
for a in [x for x in actions if x["risk_type"]=="EXIT"]:
    print(f"  t={a['time']}: {a['type']} | ExitQ={a['exit_q']} | Exit->{a['exit']}")
