# 🏟️ Stadium AI - Intelligent Crowd Management System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)
![SimPy](https://img.shields.io/badge/SimPy-4.0+-2c3e50?style=for-the-badge)
![ML](https://img.shields.io/badge/ML-Powered-00d4aa?style=for-the-badge&logo=tensorflow&logoColor=white)

**AI-Powered Stadium Crowd Management & Congestion Prevention System**

*Real-time monitoring • ML Risk Prediction • Proactive Control • Beautiful Dashboard*

[Features](#-features) • [Quick Start](#-quick-start) • [Dashboard](#-dashboard) • [ML System](#-ml-system) • [API](#-api-reference)

</div>

---

## 📋 Overview

**Stadium AI** is a comprehensive crowd management solution that combines discrete-event simulation, machine learning, and real-time visualization to help stadium operators prevent congestion and optimize fan experience.

### The Problem

Large stadium events face critical challenges:
- **Entry Congestion**: 68,000 fans arriving in 2-3 hours creates massive queues
- **Exit Crush**: Post-match surge can be dangerous without proper management
- **Resource Inefficiency**: Static resource allocation wastes capacity during low periods
- **Reactive Management**: Most systems only respond after problems occur

### Our Solution

Stadium AI provides:
- **Predictive Risk Assessment**: ML models predict congestion 10-15 minutes ahead
- **Proactive Control**: Automatic resource scaling before problems occur
- **Real-Time Monitoring**: Beautiful dashboard with live metrics and alerts
- **Simulation Engine**: Test scenarios before real events

---

## ✨ Features

### 🔮 ML-Powered Predictions
- **Entry Risk Prediction**: Queue size, wait time, time-to-critical estimates
- **Exit Risk Prediction**: Post-match surge forecasting
- **Confidence Scoring**: Know how reliable each prediction is
- **Trend Analysis**: Detect patterns before they become problems

### 🎛️ Intelligent Control
- **Automatic Gate Scaling**: Open/close entry and exit gates based on demand
- **Security Lane Management**: Add lanes during peak periods
- **Vendor Optimization**: Scale concession stands dynamically
- **Queue Redirection**: Distribute load across available resources

### 📊 Real-Time Dashboard
- **Live Risk Gauges**: Visual entry/exit risk indicators
- **Queue Monitoring**: Track all queues in real-time
- **Wait Time Trends**: Historical and predicted wait times
- **Actionable Recommendations**: Clear guidance for operators

### 🧪 Simulation Engine
- **Discrete-Event Simulation**: Realistic fan behavior modeling
- **Configurable Parameters**: Test different scenarios
- **ML Control Mode**: Compare baseline vs ML-controlled operations
- **Comprehensive Metrics**: Detailed output for analysis

---

## 🚀 Quick Start


### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/can_stadium_AI.git
cd can_stadium_AI

# Install dependencies
pip install -r api/requirements.txt

# Additional ML dependencies
pip install scikit-learn xgboost plotly
```

### Running the System

#### Option 1: Quick Start (Dashboard Only)
```bash
python run_dashboard.py
```
Open http://localhost:8501 in your browser.

#### Option 2: Full System (API + Dashboard)
```bash
# Terminal 1: Start the API server
python run_api.py

# Terminal 2: Start the dashboard
python run_dashboard.py
```

#### Option 3: Windows Batch File
```bash
start_app.bat
```

---

## 📺 Dashboard

The Streamlit dashboard provides a comprehensive control center for stadium operations.

### Main Features

| Section | Description |
|---------|-------------|
| **Status Bar** | Current simulation time, event phase, progress |
| **Alert Banner** | Real-time status (OPTIMAL/WARNING/CRITICAL) |
| **Risk Gauges** | Visual entry and exit congestion risk |
| **Predictions** | ML-predicted queue sizes and wait times |
| **Recommendations** | Actionable suggestions with expected improvement |
| **Queue Charts** | Entry and exit queue trends over time |
| **Wait Time Trends** | Historical wait times with critical thresholds |
| **Flow Rate** | Fan arrival and exit rates |
| **ML Actions Log** | Record of all automated interventions |

### Event Phases

The system recognizes five distinct phases:

| Phase | Time | Description |
|-------|------|-------------|
| 🌅 Early Arrivals | t < 60 | Light traffic, early fans arriving |
| 📈 Building Up | 60 ≤ t < 120 | Moderate traffic, queues forming |
| 🔥 Peak Rush | 120 ≤ t < 180 | Heavy traffic, maximum congestion risk |
| ⚽ Match Time | 180 ≤ t < 300 | Match in progress, minimal entry flow |
| 🚪 Exit Flow | t ≥ 300 | Post-match exit surge |

### Risk Levels

| Level | Score | Action Required |
|-------|-------|-----------------|
| 🟢 LOW | < 35% | Normal operations |
| 🟡 MODERATE | 35-55% | Monitor closely |
| 🟠 HIGH | 55-75% | Proactive intervention recommended |
| 🔴 CRITICAL | > 75% | Immediate action required |

---

## 🤖 ML System

### Risk Prediction Model

The `StadiumRiskPredictor` class provides real-time congestion forecasting:

```python
from ml.risk_predictor import StadiumRiskPredictor

predictor = StadiumRiskPredictor(kickoff_time=180)

entry_pred, exit_pred = predictor.predict_risk(
    current_time=150,
    security_queue=500,
    turnstile_queue=800,
    exit_queue=0,
    avg_security_wait=3.5,
    avg_turnstile_wait=5.2,
    avg_exit_wait=0,
    arrival_rate=400,
    exit_rate=0,
    fans_in_stadium=35000
)

print(f"Entry Risk: {entry_pred.risk_score:.0%} ({entry_pred.risk_level.value})")
print(f"Exit Risk: {exit_pred.risk_score:.0%} ({exit_pred.risk_level.value})")
```

### Prediction Output

Each prediction includes:
- **risk_score**: Float 0-1 indicating congestion probability
- **risk_level**: Categorical (LOW/MODERATE/HIGH/CRITICAL)
- **predicted_wait**: Expected wait time if no action taken
- **predicted_queue**: Expected queue size
- **confidence**: Model confidence in the prediction
- **time_to_critical**: Minutes until critical threshold (entry only)

### Recommendation System

The model also generates actionable recommendations:

```python
recommendations = predictor.get_recommendations(entry_pred, exit_pred, current_resources)

for rec in recommendations:
    print(f"[{rec.priority.upper()}] {rec.description}")
    print(f"  Expected improvement: {rec.expected_improvement:.0f}%")
```

### Additional ML Models

| Model | Purpose | Algorithm |
|-------|---------|-----------|
| `crowd_model.py` | Predict fans in stadium | Random Forest |
| `queue_model.py` | Predict wait times | XGBoost |
| `anomaly_model.py` | Detect unusual patterns | Isolation Forest |
| `risk_predictor.py` | Real-time risk scoring | Rule-based + ML hybrid |

---

## 🎮 Simulation

### Running Simulations

#### Basic Simulation
```bash
python simulation/run_simulation.py
```

#### Custom Parameters
```bash
python simulation/run_simulation.py --fans 68000 --security 30 --turnstiles 20 --exits 25 --ml
```

#### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--fans` | 68000 | Number of fans to simulate |
| `--security` | 30 | Initial security lanes |
| `--turnstiles` | 20 | Initial entry turnstiles |
| `--exits` | 25 | Initial exit gates |
| `--ml` | False | Enable ML control system |

### Simulation Components

```
simulation/
├── env.py          # SimPy environment setup
├── resources.py    # Stadium resources (gates, security, etc.)
├── arrival.py      # Fan arrival patterns
├── agents.py       # Fan behavior agents
├── metrics.py      # Metrics collection
├── control.py      # ML control policies
└── run_simulation.py  # Main entry point
```

### Output Metrics

Simulations output comprehensive CSV data including:
- Queue lengths (security, turnstile, exit)
- Wait times (average, max)
- Flow rates (arrival, completion, exit)
- Resource utilization
- Stadium occupancy

---

## 🔌 API Reference

### Endpoints

#### GET `/status`
Check API server status.

```bash
curl http://localhost:8000/status
```

#### POST `/simulate`
Run a new simulation.

```bash
curl -X POST http://localhost:8000/simulate -H "Content-Type: application/json" -d '{"num_fans": 68000, "enable_ml_control": true}'
```

#### GET `/metrics`
Get current simulation metrics.

```bash
curl http://localhost:8000/metrics
```

---

## 🛠️ Configuration

### Environment Variables

```bash
# API Configuration
API_HOST=localhost
API_PORT=8000

# Dashboard Configuration  
DASHBOARD_PORT=8501

# Simulation Defaults
DEFAULT_FANS=68000
KICKOFF_TIME=180
```

### ML Thresholds

Edit `ml/config.py` to adjust model parameters:

```python
PREDICTION_HORIZON_CROWD = 15   # minutes ahead
PREDICTION_HORIZON_QUEUE = 10
CONGESTION_THRESHOLD = 500      # queue size
```

---

## 🧪 Development

### Running Tests
```bash
python -m pytest tests/
```

### Training Models
```bash
cd ml
python crowd_model.py
python queue_model.py
python anomaly_model.py
```

### Jupyter Notebooks
```bash
jupyter notebook notebook/
```


<div align="center">

</div>
