

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'simulation'))
sys.path.insert(0, str(PROJECT_ROOT / 'ml'))

# Import project modules
from load_models import load_all_models, get_model_info, model_exists

# Create FastAPI app
app = FastAPI(
    title="Stadium AI API",
    description="ML-powered stadium operations management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
models = None
simulation_results = {}
live_metrics = {
    "time": 0,
    "fans_in_stadium": 0,
    "turnstile_queue": 0,
    "arrival_rate": 0,
    "avg_turnstile_wait": 0,
    "fill_ratio": 0,
    "last_updated": None
}


# =====================
# REQUEST/RESPONSE MODELS
# =====================

class CrowdPredictionRequest(BaseModel):
    
    time: float = Field(..., description="Current time in minutes from stadium opening")
    fans_arrived: int = Field(..., ge=0, description="Number of fans who have arrived")
    arrival_rate: float = Field(..., ge=0, description="Current arrival rate (fans/min)")
    turnstile_queue: int = Field(..., ge=0, description="Current turnstile queue length")
    fill_ratio: float = Field(..., ge=0, le=1, description="Stadium fill ratio (0-1)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "time": 120,
                "fans_arrived": 45000,
                "arrival_rate": 800,
                "turnstile_queue": 250,
                "fill_ratio": 0.65
            }
        }


class CrowdPredictionResponse(BaseModel):
    predicted_arrival_rate: float
    predicted_queue_in_5min: int
    confidence: float
    risk_level: str
    recommended_action: str


class QueuePredictionRequest(BaseModel):
    turnstile_queue: int = Field(..., ge=0, description="Current turnstile queue length")
    arrival_rate: float = Field(..., ge=0, description="Current arrival rate")
    turnstile_utilization: float = Field(..., ge=0, le=1, description="Turnstile utilization")
    time_to_kickoff: float = Field(..., description="Minutes until kickoff")
    
    class Config:
        json_schema_extra = {
            "example": {
                "turnstile_queue": 200,
                "arrival_rate": 600,
                "turnstile_utilization": 0.85,
                "time_to_kickoff": 30
            }
        }


class QueuePredictionResponse(BaseModel):
    predicted_wait_time: float
    predicted_queue_growth: float
    congestion_risk: float
    alert_level: str


class SimulationRequest(BaseModel):
    num_fans: int = Field(default=68000, ge=1000, le=100000, description="Number of fans")
    num_turnstiles: int = Field(default=92, ge=10, le=200, description="Number of turnstiles")
    num_vendors: int = Field(default=80, ge=10, le=200, description="Number of vendors")
    parking_spots: int = Field(default=6000, ge=0, le=20000, description="Parking spots")
    enable_ml_control: bool = Field(default=False, description="Enable ML control")
    random_seed: int = Field(default=42, description="Random seed for reproducibility")
    
    class Config:
        json_schema_extra = {
            "example": {
                "num_fans": 68000,
                "num_turnstiles": 92,
                "num_vendors": 80,
                "parking_spots": 6000,
                "enable_ml_control": True,
                "random_seed": 42
            }
        }


class SimulationResponse(BaseModel):
    simulation_id: str
    status: str
    fans_completed: int
    fans_exited: int
    avg_turnstile_wait: float
    max_turnstile_wait: float
    avg_vendor_wait: float
    total_time_minutes: float
    ml_interventions: int


class StatusResponse(BaseModel):
    status: str
    version: str
    models_loaded: bool
    available_models: Dict[str, bool]
    timestamp: str


# =====================
# STARTUP EVENT
# =====================

@app.on_event("startup")
async def load_models_on_startup():
    global models
    try:
        models = load_all_models()
        print("ML models loaded successfully")
    except Exception as e:
        print(f"Could not load models: {e}")
        models = {'crowd': None, 'queue': None, 'anomaly': None}


# =====================
# ENDPOINTS
# =====================

@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Stadium AI API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/status", response_model=StatusResponse, tags=["Health"])
async def get_status():
    model_info = get_model_info()
    return StatusResponse(
        status="operational",
        version="1.0.0",
        models_loaded=models is not None,
        available_models={
            'crowd': model_info.get('crowd', {}).get('exists', False),
            'queue': model_info.get('queue', {}).get('exists', False),
            'anomaly': model_info.get('anomaly', {}).get('exists', False),
        },
        timestamp=datetime.now().isoformat()
    )


@app.get("/models", tags=["Models"])
async def get_models_info():
    """Get detailed information about loaded models."""
    return get_model_info()


@app.get("/metrics/live", tags=["Metrics"])
async def get_live_metrics():
    """
    Get real-time metrics from the most recent simulation data.
    Reads from the CSV to provide up-to-date metrics.
    """
    try:
        data_path = PROJECT_ROOT / 'data' / 'raw' / 'stadium_simulation.csv'
        if data_path.exists():
            df = pd.read_csv(data_path)
            if len(df) > 0:
                latest = df.iloc[-1]
                return {
                    "time": float(latest.get('time', 0)),
                    "fans_in_stadium": int(latest.get('fans_in_stadium', 0)),
                    "turnstile_queue": int(latest.get('turnstile_queue', 0)),
                    "arrival_rate": float(latest.get('arrival_rate', 0)),
                    "avg_turnstile_wait": float(latest.get('avg_turnstile_wait', 0)),
                    "fill_ratio": float(latest.get('fill_ratio', 0)),
                    "turnstile_utilization": float(latest.get('turnstile_utilization', 0)),
                    "vendor_utilization": float(latest.get('vendor_utilization', 0)),
                    "parking_utilization": float(latest.get('parking_utilization', 0)),
                    "total_records": len(df),
                    "max_time": float(df['time'].max()),
                    "last_updated": datetime.now().isoformat(),
                    "status": "live"
                }
    except Exception as e:
        pass
    
    return {
        "status": "no_data",
        "message": "No simulation data available",
        "last_updated": datetime.now().isoformat()
    }


@app.get("/metrics/history", tags=["Metrics"])
async def get_metrics_history(limit: int = 100):
    """
    Get historical metrics from simulation data.
    """
    try:
        data_path = PROJECT_ROOT / 'data' / 'raw' / 'stadium_simulation.csv'
        if data_path.exists():
            df = pd.read_csv(data_path)
            # Return last N records
            records = df.tail(limit).to_dict('records')
            return {
                "records": records,
                "count": len(records),
                "total_available": len(df),
                "last_updated": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"records": [], "count": 0}


@app.post("/predict/crowd", response_model=CrowdPredictionResponse, tags=["Predictions"])
async def predict_crowd(request: CrowdPredictionRequest):
    """
    Predict crowd flow for the next time period.
    
    Returns predictions for:
    - Expected arrival rate
    - Queue length in 5 minutes
    - Risk level and recommended action
    """
    # Build feature vector
    features = np.array([[
        request.time,
        request.fans_arrived,
        request.arrival_rate,
        request.turnstile_queue,
        request.fill_ratio
    ]])
    
    # Use model if available, otherwise use heuristic
    if models and models.get('crowd') is not None:
        try:
            prediction = models['crowd'].predict(features)[0]
            predicted_rate = float(prediction)
        except Exception as e:
            # Fallback to heuristic
            predicted_rate = estimate_arrival_rate(request.time)
    else:
        predicted_rate = estimate_arrival_rate(request.time)
    
    # Calculate queue prediction (simple physics model)
    throughput = 92 * 35  # 92 turnstiles × 35 fans/min
    queue_change = (predicted_rate - throughput) * 5  # 5 minute window
    predicted_queue = max(0, request.turnstile_queue + queue_change)
    
    # Calculate risk level
    risk = min(1.0, request.turnstile_queue / 500)  # 500 = high queue threshold
    
    if risk > 0.8:
        risk_level = "CRITICAL"
        action = "Open all turnstiles, add vendors, enable redirection"
    elif risk > 0.6:
        risk_level = "HIGH"
        action = "Add 10 vendors, throttle entry slightly"
    elif risk > 0.4:
        risk_level = "MODERATE"
        action = "Add 5 vendors, monitor closely"
    else:
        risk_level = "LOW"
        action = "Normal operations"
    
    return CrowdPredictionResponse(
        predicted_arrival_rate=round(predicted_rate, 1),
        predicted_queue_in_5min=int(predicted_queue),
        confidence=0.85 if models and models.get('crowd') else 0.6,
        risk_level=risk_level,
        recommended_action=action
    )


@app.post("/predict/queue", response_model=QueuePredictionResponse, tags=["Predictions"])
async def predict_queue(request: QueuePredictionRequest):
    """
    Predict queue wait times.
    
    Returns predictions for:
    - Expected wait time
    - Queue growth rate
    - Congestion risk
    """
    # Build feature vector
    features = np.array([[
        request.turnstile_queue,
        request.arrival_rate,
        request.turnstile_utilization,
        request.time_to_kickoff
    ]])
    
    # Use model if available
    if models and models.get('queue') is not None:
        try:
            prediction = models['queue'].predict(features)[0]
            predicted_wait = float(prediction)
        except Exception:
            predicted_wait = estimate_wait_time(request.turnstile_queue)
    else:
        predicted_wait = estimate_wait_time(request.turnstile_queue)
    
    # Calculate queue growth (arrival - throughput)
    throughput = 92 * 35 * request.turnstile_utilization
    queue_growth = request.arrival_rate - throughput
    
    # Calculate congestion risk
    risk = min(1.0, (predicted_wait / 15))  # 15 min = max acceptable wait
    
    if risk > 0.8:
        alert = "🔴 CRITICAL"
    elif risk > 0.6:
        alert = "🟠 HIGH"
    elif risk > 0.4:
        alert = "🟡 MODERATE"
    else:
        alert = "🟢 LOW"
    
    return QueuePredictionResponse(
        predicted_wait_time=round(predicted_wait, 2),
        predicted_queue_growth=round(queue_growth, 1),
        congestion_risk=round(risk, 2),
        alert_level=alert
    )


@app.post("/simulate", response_model=SimulationResponse, tags=["Simulation"])
async def run_simulation_endpoint(request: SimulationRequest):
    """
    Run a stadium simulation with the specified parameters.
    
    This endpoint runs a complete match day simulation and returns
    key performance metrics.
    """
    try:
        # Import simulation module
        from run_simulation import run_match_simulation
        
        # Run simulation
        metrics = run_match_simulation(
            num_fans=request.num_fans,
            num_turnstiles=request.num_turnstiles,
            num_vendors=request.num_vendors,
            parking_spots=request.parking_spots,
            random_seed=request.random_seed,
            enable_ml_control=request.enable_ml_control,
            ml_models=models if request.enable_ml_control else None,
            verbose=False
        )
        
        # Generate simulation ID
        sim_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.random_seed}"
        
        # Calculate metrics
        avg_turnstile = np.mean(metrics.turnstile_waits) if metrics.turnstile_waits else 0
        max_turnstile = np.max(metrics.turnstile_waits) if metrics.turnstile_waits else 0
        avg_vendor = np.mean(metrics.vendor_waits) if metrics.vendor_waits else 0
        ml_actions = len(metrics.control_actions) if hasattr(metrics, 'control_actions') else 0
        
        # Store results
        simulation_results[sim_id] = metrics
        
        return SimulationResponse(
            simulation_id=sim_id,
            status="completed",
            fans_completed=metrics.fans_completed,
            fans_exited=metrics.fans_exited,
            avg_turnstile_wait=round(avg_turnstile, 2),
            max_turnstile_wait=round(max_turnstile, 2),
            avg_vendor_wait=round(avg_vendor, 2),
            total_time_minutes=450,
            ml_interventions=ml_actions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@app.get("/simulate/{simulation_id}", tags=["Simulation"])
async def get_simulation_results(simulation_id: str):
    """Get detailed results for a completed simulation."""
    if simulation_id not in simulation_results:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    metrics = simulation_results[simulation_id]
    
    return {
        "simulation_id": simulation_id,
        "fans_completed": metrics.fans_completed,
        "fans_exited": metrics.fans_exited,
        "turnstile_waits": {
            "mean": np.mean(metrics.turnstile_waits) if metrics.turnstile_waits else 0,
            "max": np.max(metrics.turnstile_waits) if metrics.turnstile_waits else 0,
            "min": np.min(metrics.turnstile_waits) if metrics.turnstile_waits else 0,
        },
        "vendor_waits": {
            "mean": np.mean(metrics.vendor_waits) if metrics.vendor_waits else 0,
            "max": np.max(metrics.vendor_waits) if metrics.vendor_waits else 0,
        },
        "queue_lengths": metrics.queue_lengths[-50:] if hasattr(metrics, 'queue_lengths') else [],
        "control_actions": metrics.control_actions if hasattr(metrics, 'control_actions') else [],
    }


# =====================
# HELPER FUNCTIONS
# =====================

def estimate_arrival_rate(time: float) -> float:
    """Estimate arrival rate based on time (heuristic fallback)."""
    if time < 60:
        return 100
    elif time < 90:
        return 500
    elif time < 120:
        return 1000
    elif time < 150:
        return 500
    elif time < 180:
        return 67
    else:
        return 10


def estimate_wait_time(queue_length: int) -> float:
    """Estimate wait time based on queue length (heuristic fallback)."""
    throughput = 92 * 35  # fans per minute
    return queue_length / throughput


# =====================
# RUN SERVER
# =====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
