import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

df = pd.read_csv("../data/processed/stadium_features.csv")

FEATURES = [
    "arrival_rate",
    "net_flow_rate",
    "turnstile_utilization",
    "turnstile_queue",
    "fans_in_stadium"
]

X = df[FEATURES]

model = IsolationForest(
    n_estimators=200,
    contamination=0.02,
    random_state=42
)

df["anomaly"] = model.fit_predict(X)

anomalies = df[df["anomaly"] == -1]

print(f"🚨 Detected {len(anomalies)} anomalies")

joblib.dump(model, "../models/anomaly_model.pkl")
anomalies.to_csv("../data/processed/anomalies.csv", index=False)

print("✅ Anomaly model saved")
