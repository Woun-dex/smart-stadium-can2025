import pandas as pd 
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import  mean_absolute_error    
from sklearn.ensemble import RandomForestRegressor
import joblib
from config import *

df = pd.read_csv("../data/processed/stadium_clean.csv")

TARGET = "fans_in_stadium"

FEATURES = [
    "time_to_kickoff", "is_pre_match", "time_phase",
    "arrival_rate", "completion_rate", "exit_rate", "net_flow_rate",
    "arrival_rate_lag1", "arrival_rate_lag5", "arrival_rate_ma5",
    "turnstile_utilization", "parking_utilization",
    "fill_ratio", "arrival_progress", "exit_progress"
]

X = df[FEATURES]
y = df[TARGET]

X_train , X_test , y_train , y_test = train_test_split(X , y , test_size = 0.2 , shuffle = False)

baseline_pred = np.full_like(y_test , y_train.mean())

baseline_mae = mean_absolute_error(y_test , baseline_pred)

model = RandomForestRegressor(
    n_estimators=300 , 
    random_state=RANDOM_SEED,
    max_depth=15,
    n_jobs=-1
)
model.fit(X_train , y_train)
preds = model.predict(X_test)
mae = mean_absolute_error(y_test , preds)
print(f"Baseline MAE: {baseline_mae:.2f}")
print(f"Model MAE: {mae:.2f}")

assert mae < baseline_mae , "Model did not outperform baseline!"

joblib.dump(model, "../models/crowd_model.pkl")
print("Model saved ")
