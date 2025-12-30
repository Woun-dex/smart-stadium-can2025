"""
ML Model Loading Utilities.

Provides functions to load trained models for:
- Crowd flow prediction
- Queue time prediction  
- Anomaly detection
"""

import os
import joblib
from pathlib import Path


def get_models_dir():
    """Get the models directory path."""
    current_dir = Path(__file__).parent
    models_dir = current_dir.parent / 'models'
    return models_dir


def load_all_models():
    """
    Load all trained ML models.
    
    Returns:
    --------
    dict : Dictionary containing loaded models
        - 'crowd': Crowd flow prediction model
        - 'queue': Queue time prediction model
        - 'anomaly': Anomaly detection model
        
    Raises:
    -------
    FileNotFoundError : If models directory or files don't exist
    """
    models_dir = get_models_dir()
    
    # Check if models directory exists
    if not models_dir.exists():
        models_dir.mkdir(parents=True, exist_ok=True)
        raise FileNotFoundError(
            f"Models directory created at {models_dir}. "
            "Please train models first using the training notebooks."
        )
    
    models = {}
    
    # Load crowd model
    crowd_path = models_dir / 'crowd_model.pkl'
    if crowd_path.exists():
        models['crowd'] = joblib.load(crowd_path)
    else:
        models['crowd'] = None
        print(f"Warning: Crowd model not found at {crowd_path}")
    
    # Load queue model
    queue_path = models_dir / 'queue_model.pkl'
    if queue_path.exists():
        models['queue'] = joblib.load(queue_path)
    else:
        models['queue'] = None
        print(f"Warning: Queue model not found at {queue_path}")
    
    # Load anomaly model
    anomaly_path = models_dir / 'anomaly_model.pkl'
    if anomaly_path.exists():
        models['anomaly'] = joblib.load(anomaly_path)
    else:
        models['anomaly'] = None
        print(f"Warning: Anomaly model not found at {anomaly_path}")
    
    return models


def save_model(model, name):
    """
    Save a trained model.
    
    Parameters:
    -----------
    model : object
        Trained model to save
    name : str
        Model name ('crowd', 'queue', or 'anomaly')
    """
    models_dir = get_models_dir()
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = models_dir / f'{name}_model.pkl'
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")


def model_exists(name):
    """
    Check if a model file exists.
    
    Parameters:
    -----------
    name : str
        Model name ('crowd', 'queue', or 'anomaly')
        
    Returns:
    --------
    bool : True if model file exists
    """
    models_dir = get_models_dir()
    model_path = models_dir / f'{name}_model.pkl'
    return model_path.exists()


def get_model_info():
    """
    Get information about available models.
    
    Returns:
    --------
    dict : Information about each model
    """
    models_dir = get_models_dir()
    
    info = {}
    for name in ['crowd', 'queue', 'anomaly']:
        model_path = models_dir / f'{name}_model.pkl'
        if model_path.exists():
            stat = model_path.stat()
            info[name] = {
                'exists': True,
                'path': str(model_path),
                'size_mb': stat.st_size / (1024 * 1024),
                'modified': stat.st_mtime,
            }
        else:
            info[name] = {'exists': False, 'path': str(model_path)}
    
    return info

