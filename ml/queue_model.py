import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
import joblib

df = pd.read_csv("../data/processed/stadium_features.csv")

TARGET = "avg_turnstile_wait"

FEATURES = [
    "arrival_rate", "arrival_rate_lag1", "arrival_rate_ma5",
    "turnstiles_in_use", "turnstile_utilization",
    "turnstile_queue", "fans_in_stadium",
    "fill_ratio", "time_phase"
]

X = df[FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

model = XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror"
)

model.fit(X_train, y_train)

preds = model.predict(X_test)
rmse = mean_squared_error(y_test, preds, squared=False)

print(f"Queue RMSE: {rmse:.2f}")

joblib.dump(model, "../models/queue_model.pkl")
print("✅ Queue time model saved")
