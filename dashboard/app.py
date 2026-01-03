"""
Stadium AI Control Center - Professional Dashboard
===================================================
Real-time crowd monitoring, ML predictions, and intelligent control system.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ml.risk_predictor import StadiumRiskPredictor, RiskLevel
except ImportError:
    StadiumRiskPredictor = None

# Page configuration
st.set_page_config(
    page_title="🏟️ STADIUM CONTROL CENTER",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ CONTROL ROOM STYLING ============
st.markdown("""
<style>
    /* Dark control room theme */
    .stApp {
        background: linear-gradient(180deg, #0a0e1a 0%, #121827 100%);
    }
    
    /* Main container - fullscreen */
    .main .block-container { 
        padding: 0.5rem 1rem; 
        max-width: 100%; 
    }
    
    /* Header - Large control room style */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00d4ff 0%, #0080ff 50%, #0040ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 0.3rem;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 4px;
        text-shadow: 0 0 40px rgba(0,212,255,0.5);
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #60a5fa;
        text-align: center;
        margin-top: -10px;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Status cards - Dark control room */
    .status-card {
        background: rgba(15,23,42,0.8);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 0 30px rgba(0,212,255,0.15), inset 0 0 60px rgba(0,100,255,0.05);
        border: 2px solid rgba(0,212,255,0.3);
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Alert banners - Large control room displays */
    .alert-critical {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        font-weight: 900;
        text-align: center;
        font-size: 1.8rem;
        box-shadow: 0 0 50px rgba(220,38,38,0.8), inset 0 0 30px rgba(255,0,0,0.2);
        animation: pulse-critical 1.5s infinite;
        border: 3px solid #ff0000;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
        color: #000;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        font-weight: 900;
        text-align: center;
        font-size: 1.8rem;
        box-shadow: 0 0 50px rgba(245,158,11,0.6), inset 0 0 30px rgba(255,200,0,0.2);
        border: 3px solid #fbbf24;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    .alert-ok {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        font-weight: 900;
        text-align: center;
        font-size: 1.8rem;
        box-shadow: 0 0 50px rgba(16,185,129,0.6), inset 0 0 30px rgba(0,255,150,0.2);
        border: 3px solid #10b981;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    /* Live badge - Control room style */
    .live-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #dc2626, #ff0000);
        color: white;
        padding: 0.6rem 1.5rem;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: 900;
        margin-bottom: 1rem;
        box-shadow: 0 0 30px rgba(255,0,0,0.8);
        border: 2px solid #ff0000;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .live-dot {
        width: 12px;
        height: 12px;
        background: white;
        border-radius: 50%;
        margin-right: 10px;
        animation: blink 1s infinite;
        box-shadow: 0 0 15px rgba(255,255,255,0.9);
    }
    
    /* Risk indicator - Large displays */
    .risk-indicator {
        display: inline-block;
        padding: 8px 18px;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 0 20px currentColor;
    }
    .risk-low { background: #10b981; color: white; }
    .risk-moderate { background: #fbbf24; color: #000; }
    .risk-high { background: #f97316; color: white; }
    .risk-critical { background: #dc2626; color: white; animation: pulse-critical 1s infinite; border: 2px solid #ff0000; }
    
    /* Prediction card - Dark theme */
    .prediction-card {
        background: rgba(15,23,42,0.9);
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 5px solid #00d4ff;
        margin: 0.8rem 0;
        box-shadow: 0 0 30px rgba(0,212,255,0.3), inset 0 0 40px rgba(0,100,255,0.1);
        color: #e2e8f0;
    }
    
    .prediction-card.exit {
        border-left-color: #a855f7;
        box-shadow: 0 0 30px rgba(168,85,247,0.3), inset 0 0 40px rgba(168,85,247,0.1);
    }
    
    .prediction-card.critical {
        border-left-color: #dc2626;
        background: rgba(40,0,0,0.9);
        box-shadow: 0 0 40px rgba(220,38,38,0.5), inset 0 0 40px rgba(255,0,0,0.15);
    }
    
    /* Recommendation card - Dark control room */
    .recommendation {
        background: rgba(15,23,42,0.8);
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0;
        border-left: 5px solid #00d4ff;
        box-shadow: 0 0 20px rgba(0,212,255,0.25);
        color: #e2e8f0;
        font-size: 1.05rem;
    }
    
    .recommendation.urgent {
        border-left-color: #dc2626;
        background: rgba(40,0,0,0.8);
        box-shadow: 0 0 30px rgba(220,38,38,0.4);
        animation: pulse-critical 2s infinite;
    }
    
    .recommendation.high {
        border-left-color: #f59e0b;
        background: rgba(40,30,0,0.8);
        box-shadow: 0 0 25px rgba(245,158,11,0.3);
    }
    
    /* Resource state - Digital display style */
    .resource-state {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 1.2rem;
        background: rgba(0,20,40,0.8);
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid rgba(0,212,255,0.3);
        box-shadow: 0 0 15px rgba(0,212,255,0.15);
    }
    
    .resource-value {
        font-size: 1.8rem;
        font-weight: 900;
        color: #00d4ff;
        text-shadow: 0 0 10px rgba(0,212,255,0.8);
        font-family: 'Courier New', monospace;
    }
    
    /* Phase indicators - High visibility */
    .phase-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: 900;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 0 20px currentColor;
        border: 2px solid currentColor;
    }
    .phase-early { background: rgba(59,130,246,0.2); color: #60a5fa; border-color: #3b82f6; }
    .phase-building { background: rgba(251,191,36,0.2); color: #fbbf24; border-color: #f59e0b; }
    .phase-peak { background: rgba(239,68,68,0.2); color: #ff6b6b; border-color: #dc2626; animation: pulse-critical 2s infinite; }
    .phase-match { background: rgba(16,185,129,0.2); color: #10b981; border-color: #059669; }
    .phase-exit { background: rgba(168,85,247,0.2); color: #a855f7; border-color: #8b5cf6; }
    
    /* ML Action log - Dark theme */
    .ml-action {
        background: rgba(15,23,42,0.8);
        border-left: 5px solid #00d4ff;
        padding: 12px 16px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
        font-size: 1rem;
        color: #e2e8f0;
        box-shadow: 0 0 15px rgba(0,212,255,0.2);
    }
    
    .ml-action.strong {
        background: rgba(40,0,0,0.8);
        border-left-color: #dc2626;
        box-shadow: 0 0 25px rgba(220,38,38,0.3);
    }
    
    .ml-action.exit-action {
        border-left-color: #a855f7;
        background: rgba(30,15,40,0.8);
        box-shadow: 0 0 15px rgba(168,85,247,0.2);
    }
    
    .ml-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 900;
        text-transform: uppercase;
        margin-right: 8px;
        border: 1px solid currentColor;
        letter-spacing: 1px;
    }
    
    .ml-badge-moderate { background: rgba(251,191,36,0.3); color: #fbbf24; border-color: #f59e0b; }
    .ml-badge-strong { background: rgba(220,38,38,0.3); color: #ff6b6b; border-color: #dc2626; }
    .ml-badge-entry { background: rgba(59,130,246,0.3); color: #60a5fa; border-color: #3b82f6; }
    .ml-badge-exit { background: rgba(168,85,247,0.3); color: #a855f7; border-color: #8b5cf6; }
    
    /* Animations - Control room style */
    @keyframes blink {
        0%, 50% { opacity: 1; transform: scale(1); }
        51%, 100% { opacity: 0.4; transform: scale(0.9); }
    }
    
    @keyframes pulse-critical {
        0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 40px currentColor; }
        50% { opacity: 0.9; transform: scale(1.02); box-shadow: 0 0 60px currentColor; }
    }
    
    /* Custom scrollbar - Dark theme */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: rgba(15,23,42,0.5); border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.4); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.6); }
    
    /* Streamlit overrides - Dark theme */
    .stMetric { background: rgba(15,23,42,0.6); padding: 1rem; border-radius: 10px; border: 1px solid rgba(0,212,255,0.2); }
    .stMetric label { color: #60a5fa !important; font-size: 1rem !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 1px; }
    .stMetric [data-testid="stMetricValue"] { color: #00d4ff !important; font-size: 2rem !important; font-weight: 900 !important; text-shadow: 0 0 15px rgba(0,212,255,0.6); }
    .stMetric [data-testid="stMetricDelta"] { color: #10b981 !important; font-weight: 700 !important; }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] { background: rgba(15,23,42,0.8); border-radius: 10px; padding: 0.5rem; }
    .stTabs [data-baseweb="tab"] { color: #60a5fa; font-weight: 700; font-size: 1.1rem; }
    .stTabs [data-baseweb="tab-highlight"] { background: #00d4ff; }
    
    /* Dataframe styling */
    .stDataFrame { background: rgba(15,23,42,0.8); border-radius: 10px; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============ API & CONFIG ============
API_URL = "http://localhost:8000"

# Initialize session state
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 2
if 'sim_start_time' not in st.session_state:
    st.session_state.sim_start_time = None
if 'last_file_mod' not in st.session_state:
    st.session_state.last_file_mod = None
if 'predictor' not in st.session_state:
    st.session_state.predictor = StadiumRiskPredictor() if StadiumRiskPredictor else None


# ============ HELPER FUNCTIONS ============
def check_api_status():
    """Check if the API server is running."""
    try:
        response = requests.get(f"{API_URL}/status", timeout=2)
        return response.status_code == 200
    except:
        return False


def load_simulation_data():
    """Load simulation data from CSV file."""
    data_path = Path(__file__).parent.parent / 'data' / 'raw' / 'stadium_simulation.csv'
    if data_path.exists():
        current_mod = data_path.stat().st_mtime
        if st.session_state.last_file_mod != current_mod:
            st.session_state.last_file_mod = current_mod
            st.session_state.sim_start_time = datetime.now()
        return pd.read_csv(data_path)
    return None


def get_realtime_slice(data):
    """Get data slice for real-time playback effect."""
    if data is None or len(data) == 0:
        return data, 0
    
    if st.session_state.sim_start_time is None:
        st.session_state.sim_start_time = datetime.now()
    
    elapsed = (datetime.now() - st.session_state.sim_start_time).total_seconds()
    sim_time = min(elapsed * 3, data['time'].max())  # 3x playback speed
    return data[data['time'] <= sim_time].copy(), sim_time


def get_phase_info(time_min):
    """Get the current phase based on simulation time."""
    if time_min < 60:
        return 'early', '🌅 Early Arrivals', 'phase-early'
    elif time_min < 120:
        return 'building', '📈 Building Up', 'phase-building'
    elif time_min < 180:
        return 'peak', '🔥 Peak Rush', 'phase-peak'
    elif time_min < 300:
        return 'match', '⚽ Match Time', 'phase-match'
    else:
        return 'exit', '🚪 Exit Flow', 'phase-exit'


def get_predictions(data):
    """Get ML predictions for current state."""
    if data is None or len(data) == 0 or st.session_state.predictor is None:
        return None, None, None
    
    latest = data.iloc[-1]
    predictor = st.session_state.predictor
    
    entry_pred, exit_pred = predictor.predict_risk(
        current_time=latest.get('time', 0),
        security_queue=int(latest.get('security_queue', 0)),
        turnstile_queue=int(latest.get('turnstile_queue', 0)),
        exit_queue=int(latest.get('exit_queue', 0)),
        avg_security_wait=latest.get('avg_security_wait', 0),
        avg_turnstile_wait=latest.get('avg_turnstile_wait', 0),
        avg_exit_wait=latest.get('avg_exit_wait', 0),
        arrival_rate=latest.get('arrival_rate', 0),
        exit_rate=latest.get('exit_rate', 0),
        fans_in_stadium=int(latest.get('fans_in_stadium', 0))
    )
    
    # Get current resource state (use values from data if available)
    resources = {
        'active_security': int(latest.get('active_security', 30)),
        'max_security': 80,
        'active_turnstiles': int(latest.get('active_turnstiles', 20)),
        'max_turnstiles': 60,
        'active_exit_gates': int(latest.get('active_exit_gates', 25)),
        'max_exit_gates': 60,
        'active_vendors': int(latest.get('active_vendors', 40)),
        'max_vendors': 150
    }
    
    recommendations = predictor.get_recommendations(entry_pred, exit_pred, resources)
    
    return entry_pred, exit_pred, recommendations


def get_alert_status(data, entry_pred=None, exit_pred=None):
    """Determine the current alert status."""
    if data is None or len(data) == 0:
        return "unknown", "⚪ Waiting for simulation data..."
    
    # Use ML predictions if available
    if entry_pred and exit_pred:
        max_risk = max(entry_pred.risk_score, exit_pred.risk_score)
        primary = "EXIT" if exit_pred.risk_score > entry_pred.risk_score else "ENTRY"
        
        if max_risk >= 0.75:
            return "critical", f"🚨 CRITICAL {primary} CONGESTION | Risk: {max_risk:.0%} | Immediate action required"
        elif max_risk >= 0.55:
            return "warning", f"⚠️ HIGH {primary} LOAD | Risk: {max_risk:.0%} | Monitoring closely"
        else:
            return "ok", f"✅ OPTIMAL FLOW | Entry: {entry_pred.risk_score:.0%} | Exit: {exit_pred.risk_score:.0%}"
    
    # Fallback to raw data
    latest = data.iloc[-1]
    total_queue = latest.get('turnstile_queue', 0) + latest.get('security_queue', 0)
    total_wait = latest.get('avg_turnstile_wait', 0) + latest.get('avg_security_wait', 0)
    
    if total_queue > 5000 or total_wait > 25:
        return "critical", f"🚨 CRITICAL | Queue: {int(total_queue):,} | Wait: {total_wait:.1f} min"
    elif total_queue > 3000 or total_wait > 15:
        return "warning", f"⚠️ WARNING | Queue: {int(total_queue):,} | Wait: {total_wait:.1f} min"
    else:
        return "ok", f"✅ OPTIMAL | Queue: {int(total_queue):,} | Wait: {total_wait:.1f} min"


# ============ CHART FUNCTIONS ============
def create_risk_gauge(entry_risk, exit_risk):
    """Create dual risk gauge chart."""
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
        subplot_titles=['Entry Risk', 'Exit Risk']
    )
    
    # Entry risk gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=entry_risk * 100,
        number={'suffix': '%', 'font': {'size': 28}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': '#3b82f6'},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': '#e2e8f0',
            'steps': [
                {'range': [0, 35], 'color': '#d1fae5'},
                {'range': [35, 55], 'color': '#fef3c7'},
                {'range': [55, 75], 'color': '#fed7aa'},
                {'range': [75, 100], 'color': '#fecaca'}
            ],
            'threshold': {
                'line': {'color': '#dc2626', 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ), row=1, col=1)
    
    # Exit risk gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=exit_risk * 100,
        number={'suffix': '%', 'font': {'size': 28}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': '#8b5cf6'},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': '#e2e8f0',
            'steps': [
                {'range': [0, 35], 'color': '#d1fae5'},
                {'range': [35, 55], 'color': '#fef3c7'},
                {'range': [55, 75], 'color': '#fed7aa'},
                {'range': [75, 100], 'color': '#fecaca'}
            ],
            'threshold': {
                'line': {'color': '#dc2626', 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ), row=1, col=2)
    
    fig.update_layout(
        height=220,
        margin=dict(t=40, b=20, l=30, r=30),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_queue_chart(data):
    """Create queue comparison chart."""
    if data is None or len(data) == 0:
        return None
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('🔒 Entry Queues', '🚪 Exit Queue'),
        horizontal_spacing=0.1
    )
    
    # Entry queues (stacked)
    if 'security_queue' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['time'], y=data['security_queue'],
            mode='lines', name='Security',
            line=dict(color='#8b5cf6', width=2),
            fill='tozeroy', fillcolor='rgba(139,92,246,0.2)'
        ), row=1, col=1)
    
    if 'turnstile_queue' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['time'], y=data['turnstile_queue'],
            mode='lines', name='Turnstile',
            line=dict(color='#3b82f6', width=2),
            fill='tozeroy', fillcolor='rgba(59,130,246,0.2)'
        ), row=1, col=1)
    
    # Exit queue
    if 'exit_queue' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['time'], y=data['exit_queue'],
            mode='lines', name='Exit',
            line=dict(color='#ef4444', width=2.5),
            fill='tozeroy', fillcolor='rgba(239,68,68,0.2)'
        ), row=1, col=2)
        
        # Add current marker
        if len(data) > 0:
            latest = data.iloc[-1]
            fig.add_trace(go.Scatter(
                x=[latest['time']], y=[latest['exit_queue']],
                mode='markers',
                marker=dict(size=12, color='#dc2626', symbol='circle'),
                name='Current', showlegend=False
            ), row=1, col=2)
    
    # Add kickoff line
    fig.add_vline(x=180, line_dash='dash', line_color='#22c55e', line_width=2, row=1, col=1)
    fig.add_vline(x=180, line_dash='dash', line_color='#22c55e', line_width=2, row=1, col=2)
    
    fig.update_layout(
        height=280,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(t=50, b=40, l=50, r=30),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(title_text='Time (min)', gridcolor='rgba(0,0,0,0.08)')
    fig.update_yaxes(title_text='Queue Size', gridcolor='rgba(0,0,0,0.08)')
    
    return fig


def create_wait_time_chart(data):
    """Create wait time trend chart."""
    if data is None or len(data) == 0:
        return None
    
    fig = go.Figure()
    
    # Entry wait (combined)
    if 'avg_security_wait' in data.columns and 'avg_turnstile_wait' in data.columns:
        entry_wait = data['avg_security_wait'] + data['avg_turnstile_wait']
        fig.add_trace(go.Scatter(
            x=data['time'], y=entry_wait,
            mode='lines', name='Entry Wait',
            line=dict(color='#3b82f6', width=2.5),
            fill='tozeroy', fillcolor='rgba(59,130,246,0.15)'
        ))
    
    # Exit wait
    if 'avg_exit_wait' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['time'], y=data['avg_exit_wait'],
            mode='lines', name='Exit Wait',
            line=dict(color='#8b5cf6', width=2.5),
            fill='tozeroy', fillcolor='rgba(139,92,246,0.15)'
        ))
    
    # Critical lines
    fig.add_hline(y=15, line_dash='dot', line_color='#f59e0b', annotation_text='Warning (15min)')
    fig.add_hline(y=25, line_dash='dash', line_color='#dc2626', annotation_text='Critical (25min)')
    
    fig.update_layout(
        title={'text': '⏱️ Wait Time Trends', 'font': {'size': 16}},
        xaxis_title='Time (min)',
        yaxis_title='Wait Time (min)',
        height=280,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(gridcolor='rgba(0,0,0,0.08)')
    fig.update_yaxes(gridcolor='rgba(0,0,0,0.08)')
    
    return fig


def create_flow_chart(data):
    """Create arrival/exit flow chart."""
    if data is None or 'arrival_rate' not in data.columns:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['time'], y=data['arrival_rate'],
        mode='lines', name='Arrivals',
        line=dict(color='#22c55e', width=2),
        fill='tozeroy', fillcolor='rgba(34,197,94,0.15)'
    ))
    
    if 'exit_rate' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['time'], y=data['exit_rate'],
            mode='lines', name='Exits',
            line=dict(color='#ef4444', width=2),
            fill='tozeroy', fillcolor='rgba(239,68,68,0.15)'
        ))
    
    # Kickoff marker
    fig.add_vline(x=180, line_dash='dash', line_color='#22c55e', line_width=2,
                  annotation_text='⚽ Kickoff', annotation_position='top')
    
    fig.update_layout(
        title={'text': '👥 Fan Flow Rate', 'font': {'size': 16}},
        xaxis_title='Time (min)',
        yaxis_title='Fans/min',
        height=250,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_stadium_fill_chart(data):
    """Create stadium fill chart."""
    if data is None or 'fans_in_stadium' not in data.columns:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['time'], y=data['fans_in_stadium'],
        mode='lines', name='In Stadium',
        line=dict(color='#3b82f6', width=3),
        fill='tozeroy', fillcolor='rgba(59,130,246,0.2)'
    ))
    
    # Capacity line
    fig.add_hline(y=68000, line_dash='dash', line_color='#6b7280',
                  annotation_text='Capacity: 68,000')
    
    fig.update_layout(
        title={'text': '🏟️ Stadium Occupancy', 'font': {'size': 16}},
        xaxis_title='Time (min)',
        yaxis_title='Fans',
        height=250,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def generate_ml_actions(data):
    """Generate ML control actions with proper tracking."""
    if data is None or len(data) < 10:
        return []
    
    actions = []
    kickoff_time = 180
    match_end_time = kickoff_time + 120
    
    # Check for capacity columns
    has_capacity_data = ('active_security' in data.columns and 
                         'active_turnstiles' in data.columns and 
                         'active_exit_gates' in data.columns)
    
    # Initialize gate states
    if has_capacity_data:
        security_gates = int(data.iloc[0].get('active_security', 30))
        entry_gates = int(data.iloc[0].get('active_turnstiles', 20))
        exit_gates = int(data.iloc[0].get('active_exit_gates', 25))
        vendors = int(data.iloc[0].get('active_vendors', 40))
    else:
        security_gates = 30
        entry_gates = 20
        exit_gates = 25
        vendors = 40
    
    check_points = range(5, len(data), max(1, len(data)//50))
    
    for idx in check_points:
        row = data.iloc[idx]
        t = row['time']
        
        # Metrics
        sec_q = row.get('security_queue', 0)
        turn_q = row.get('turnstile_queue', 0)
        entry_queue = sec_q + turn_q
        entry_wait = row.get('avg_security_wait', 0) + row.get('avg_turnstile_wait', 0)
        exit_q = row.get('exit_queue', 0)
        exit_wait = row.get('avg_exit_wait', 0)
        
        # Risk scores
        entry_risk = (min(entry_queue/5000, 1)*0.4 + min(entry_wait/15, 1)*0.5 + 
                     (0.1 if t < kickoff_time and kickoff_time-t < 60 else 0))
        exit_risk = (min(exit_q/2000, 1)*0.4 + min(exit_wait/10, 1)*0.5 + 
                    (0.2 if t > match_end_time - 30 else 0))
        
        if has_capacity_data and idx > 0:
            # Read actual changes from data
            security_gates = int(row.get('active_security', security_gates))
            entry_gates = int(row.get('active_turnstiles', entry_gates))
            exit_gates = int(row.get('active_exit_gates', exit_gates))
            vendors = int(row.get('active_vendors', vendors))
            
            prev_row = data.iloc[idx-1]
            prev_security = int(prev_row.get('active_security', security_gates))
            prev_entry = int(prev_row.get('active_turnstiles', entry_gates))
            prev_exit = int(prev_row.get('active_exit_gates', exit_gates))
            prev_vendors = int(prev_row.get('active_vendors', vendors))
            
            if exit_gates != prev_exit:
                actions.append({
                    'time': t, 'type': 'STRONG' if exit_risk > 0.6 else 'MODERATE',
                    'risk_type': 'EXIT', 'risk': exit_risk, 'queue': int(exit_q),
                    'wait': exit_wait, 'decision': f'Exit gates {prev_exit}→{exit_gates}',
                    'security': security_gates, 'entry': entry_gates, 
                    'exit': exit_gates, 'vendors': vendors
                })
            elif security_gates != prev_security or entry_gates != prev_entry or vendors != prev_vendors:
                changes = []
                if security_gates != prev_security:
                    changes.append(f'Security {prev_security}→{security_gates}')
                if entry_gates != prev_entry:
                    changes.append(f'Entry {prev_entry}→{entry_gates}')
                if vendors != prev_vendors:
                    changes.append(f'Vendors {prev_vendors}→{vendors}')
                
                actions.append({
                    'time': t, 'type': 'STRONG' if entry_risk > 0.7 else 'MODERATE',
                    'risk_type': 'ENTRY', 'risk': entry_risk, 'queue': int(entry_queue),
                    'wait': entry_wait, 'decision': ', '.join(changes),
                    'security': security_gates, 'entry': entry_gates,
                    'exit': exit_gates, 'vendors': vendors
                })
        else:
            # Synthetic actions based on risk
            if exit_q > 500 and exit_risk > 0.4:
                old_exits = exit_gates
                increase = 10 if exit_risk > 0.6 else 5
                exit_gates = min(exit_gates + increase, 80)
                actions.append({
                    'time': t, 'type': 'STRONG' if exit_risk > 0.6 else 'MODERATE',
                    'risk_type': 'EXIT', 'risk': exit_risk, 'queue': int(exit_q),
                    'wait': exit_wait, 'decision': f'+{increase} exit gates ({old_exits}→{exit_gates})',
                    'security': security_gates, 'entry': entry_gates,
                    'exit': exit_gates, 'vendors': vendors
                })
            elif entry_queue > 500 and entry_risk > 0.5:
                old_sec, old_vend = security_gates, vendors
                sec_inc = 5 if entry_risk > 0.7 else 3
                vend_inc = 10 if entry_risk > 0.7 else 5
                security_gates = min(security_gates + sec_inc, 80)
                vendors = min(vendors + vend_inc, 150)
                actions.append({
                    'time': t, 'type': 'STRONG' if entry_risk > 0.7 else 'MODERATE',
                    'risk_type': 'ENTRY', 'risk': entry_risk, 'queue': int(entry_queue),
                    'wait': entry_wait,
                    'decision': f'Security {old_sec}→{security_gates}, Vendors {old_vend}→{vendors}',
                    'security': security_gates, 'entry': entry_gates,
                    'exit': exit_gates, 'vendors': vendors
                })
    
    return actions


# ============ MAIN APPLICATION ============
def main():
    # Header - Control Room Style
    st.markdown('<h1 class="main-header">🏟️ STADIUM CONTROL CENTER</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">⚡ MISSION CRITICAL OPERATIONS ⚡ ML-POWERED CROWD MANAGEMENT ⚡ LIVE MONITORING SYSTEM</p>', unsafe_allow_html=True)
    
    # ============ LOAD DATA FIRST ============
    full_data = load_simulation_data()
    
    if full_data is not None:
        data, sim_time = get_realtime_slice(full_data)
    else:
        data, sim_time = None, 0
    
    # ============ SIDEBAR - CONTROL PANEL ============
    with st.sidebar:
        if st.session_state.auto_refresh:
            st.markdown('<div class="live-badge"><span class="live-dot"></span>LIVE</div>', unsafe_allow_html=True)
        
        st.markdown("## ⚙️ CONTROL PANEL")
        
        # API Status
        api_status = check_api_status()
        if api_status:
            st.success("🟢 API ONLINE", icon="✅")
        else:
            st.info("🔵 LOCAL MODE", icon="💻")
        
        st.divider()
        
        # Settings
        st.markdown("### 🔄 DISPLAY SETTINGS")
        st.session_state.auto_refresh = st.toggle("♻️ Auto Refresh", value=st.session_state.auto_refresh)
        st.session_state.refresh_interval = st.slider("⏱️ Update Interval (s)", 1, 10, 2)
        
        col1, col2 = st.columns(2)
        if col1.button("🔄 REFRESH", use_container_width=True):
            st.rerun()
        if col2.button("⏮️ RESET", use_container_width=True):
            st.session_state.sim_start_time = datetime.now()
            st.session_state.predictor = StadiumRiskPredictor() if StadiumRiskPredictor else None
            st.rerun()
        
        st.divider()
        
        # Simulation
        st.markdown("### 🎮 SIMULATION CONTROL")
        num_fans = st.slider("👥 Total Fans", 20000, 80000, 68000, step=5000)
        enable_ml = st.toggle("🤖 ML Control System", value=True, help="Enable AI-powered resource management")
        
        if st.button("▶️ RUN SIMULATION", type="primary", use_container_width=True):
            with st.spinner("🔄 Running simulation..."):
                if api_status:
                    try:
                        response = requests.post(
                            f"{API_URL}/simulate",
                            json={"num_fans": num_fans, "enable_ml_control": enable_ml},
                            timeout=300
                        )
                        if response.status_code == 200:
                            st.success("✅ SIMULATION COMPLETE!")
                            st.session_state.sim_start_time = datetime.now()
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    import subprocess
                    cmd = ['python', 'simulation/run_simulation.py', '--fans', str(num_fans)]
                    if enable_ml:
                        cmd.append('--ml')
                    subprocess.run(cmd, cwd=Path(__file__).parent.parent)
                    st.success("✅ SIMULATION COMPLETE!")
                    st.session_state.sim_start_time = datetime.now()
                    time.sleep(1)
                    st.rerun()
        
        st.divider()
        
        # System info
        st.markdown("### 📊 SYSTEM STATUS")
        if data is not None and len(data) > 0:
            st.metric("📊 Data Points", f"{len(data):,}")
            st.metric("⏱️ Sim Time", f"{int(sim_time)} min")
        
        st.divider()
        st.caption("⚡ STADIUM AI v3.0")
        st.caption("🔒 CONTROL ROOM MODE")
    
    # ============ MAIN CONTENT ============
    # Get predictions
    entry_pred, exit_pred, recommendations = get_predictions(data)
    
    # Status Bar - Large control room displays
    if data is not None and len(data) > 0:
        latest = data.iloc[-1]
        current_time = latest.get('time', 0)
        max_time = full_data['time'].max()
        progress = min(100, (current_time / max_time) * 100) if max_time > 0 else 0
        
        phase_id, phase_label, phase_class = get_phase_info(current_time)
        
        st.markdown("")
        c1, c2, c3, c4 = st.columns([1, 1, 2, 1])
        with c1:
            hours, mins = int(current_time) // 60, int(current_time) % 60
            st.markdown(f"<div style='text-align:center;'><div style='font-size:0.9rem;color:#60a5fa;font-weight:700;'>ELAPSED TIME</div><div style='font-size:2rem;color:#00d4ff;font-weight:900;text-shadow:0 0 15px rgba(0,212,255,0.6);'>T+{hours}h {mins:02d}m</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div style='text-align:center;padding-top:1rem;'><span class='phase-badge {phase_class}'>{phase_label}</span></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div style='padding-top:1.5rem;'></div>", unsafe_allow_html=True)
            st.progress(progress / 100, text=f"OPERATION PROGRESS: {progress:.0f}%")
        with c4:
            total_fans = int(latest.get('fans_in_stadium', 0))
            st.markdown(f"<div style='text-align:center;'><div style='font-size:0.9rem;color:#60a5fa;font-weight:700;'>STADIUM</div><div style='font-size:2rem;color:#10b981;font-weight:900;text-shadow:0 0 15px rgba(16,185,129,0.6);'>{total_fans:,}</div></div>", unsafe_allow_html=True)
    
    # Alert Banner
    status, message = get_alert_status(data, entry_pred, exit_pred)
    alert_class = 'alert-critical' if status == 'critical' else 'alert-warning' if status == 'warning' else 'alert-ok'
    st.markdown(f'<div class="{alert_class}">{message}</div>', unsafe_allow_html=True)
    
    st.markdown("")
    
    # ============ PREDICTIONS ROW ============
    if entry_pred and exit_pred:
        st.markdown("")
        st.markdown("<h2 style='color:#00d4ff;text-align:center;font-size:2rem;text-transform:uppercase;letter-spacing:3px;text-shadow:0 0 20px rgba(0,212,255,0.6);'>🔮 ML RISK PREDICTIONS</h2>", unsafe_allow_html=True)
        st.markdown("")
        
        pred_col1, pred_col2, pred_col3 = st.columns([1, 1, 1])
        
        with pred_col1:
            # Risk gauges
            gauge_fig = create_risk_gauge(entry_pred.risk_score, exit_pred.risk_score)
            st.plotly_chart(gauge_fig, use_container_width=True)
        
        with pred_col2:
            # Entry prediction details
            entry_level_class = f"risk-{entry_pred.risk_level.value}"
            st.markdown(f"""
            <div class="prediction-card {'critical' if entry_pred.risk_level.value == 'critical' else ''}">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <strong>🔒 Entry Risk</strong>
                    <span class="risk-indicator {entry_level_class}">{entry_pred.risk_level.value}</span>
                </div>
                <div style="font-size:0.9rem;color:#64748b;">
                    <div>📊 Predicted Queue: <b>{entry_pred.predicted_queue:,}</b></div>
                    <div>⏱️ Predicted Wait: <b>{entry_pred.predicted_wait:.1f} min</b></div>
                    <div>🎯 Confidence: <b>{entry_pred.confidence:.0%}</b></div>
                    {f'<div>⚠️ Time to Critical: <b>{entry_pred.time_to_critical:.0f} min</b></div>' if entry_pred.time_to_critical else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with pred_col3:
            # Exit prediction details
            exit_level_class = f"risk-{exit_pred.risk_level.value}"
            st.markdown(f"""
            <div class="prediction-card exit {'critical' if exit_pred.risk_level.value == 'critical' else ''}">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <strong>🚪 Exit Risk</strong>
                    <span class="risk-indicator {exit_level_class}">{exit_pred.risk_level.value}</span>
                </div>
                <div style="font-size:0.9rem;color:#64748b;">
                    <div>📊 Predicted Queue: <b>{exit_pred.predicted_queue:,}</b></div>
                    <div>⏱️ Predicted Wait: <b>{exit_pred.predicted_wait:.1f} min</b></div>
                    <div>🎯 Confidence: <b>{exit_pred.confidence:.0%}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Recommendations
        if recommendations:
            st.markdown("**💡 Recommended Actions:**")
            for rec in recommendations[:3]:
                priority_class = "urgent" if rec.priority == "urgent" else "high" if rec.priority == "high" else ""
                st.markdown(f"""
                <div class="recommendation {priority_class}">
                    <div style="display:flex;justify-content:space-between;">
                        <span>{rec.description}</span>
                        <span style="color:#64748b;font-size:0.8rem;">↑{rec.expected_improvement:.0f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============ METRICS ROW ============
    if data is not None and len(data) > 0:
        latest = data.iloc[-1]
        
        st.markdown("")
        st.markdown("<h2 style='color:#00d4ff;text-align:center;font-size:2rem;text-transform:uppercase;letter-spacing:3px;text-shadow:0 0 20px rgba(0,212,255,0.6);'>📊 REAL-TIME METRICS</h2>", unsafe_allow_html=True)
        st.markdown("")
        
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        
        with m1:
            st.metric("👥 In Stadium", f"{int(latest.get('fans_in_stadium', 0)):,}",
                     delta=f"{latest.get('arrival_rate', 0):.0f}/min")
        with m2:
            st.metric("🔒 Entry Queue", f"{int(latest.get('security_queue', 0) + latest.get('turnstile_queue', 0)):,}")
        with m3:
            entry_wait = latest.get('avg_security_wait', 0) + latest.get('avg_turnstile_wait', 0)
            st.metric("⏱️ Entry Wait", f"{entry_wait:.1f} min")
        with m4:
            st.metric("🚪 Exit Queue", f"{int(latest.get('exit_queue', 0)):,}")
        with m5:
            st.metric("⏱️ Exit Wait", f"{latest.get('avg_exit_wait', 0):.1f} min")
        with m6:
            fill_pct = latest.get('fill_ratio', 0) * 100
            st.metric("🏟️ Fill", f"{fill_pct:.1f}%")
    
    # ============ CHARTS ============
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        queue_chart = create_queue_chart(data)
        if queue_chart:
            st.plotly_chart(queue_chart, use_container_width=True)
        
        wait_chart = create_wait_time_chart(data)
        if wait_chart:
            st.plotly_chart(wait_chart, use_container_width=True)
    
    with col_right:
        flow_chart = create_flow_chart(data)
        if flow_chart:
            st.plotly_chart(flow_chart, use_container_width=True)
        
        fill_chart = create_stadium_fill_chart(data)
        if fill_chart:
            st.plotly_chart(fill_chart, use_container_width=True)
    
    # ============ TABS ============
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["🤖 ML Actions", "📋 Data", "📊 Statistics"])
    
    with tab1:
        if data is not None and len(data) > 0:
            actions = generate_ml_actions(data)
            
            if actions:
                # Current resource state
                last_action = actions[-1]
                st.markdown("<h3 style='color:#00d4ff;text-transform:uppercase;letter-spacing:2px;'>📊 CURRENT RESOURCE ALLOCATION</h3>", unsafe_allow_html=True)
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("🔒 SECURITY", last_action.get('security', 30))
                r2.metric("🚪 ENTRY GATES", last_action.get('entry', 20))
                r3.metric("🚶 EXIT GATES", last_action.get('exit', 25))
                r4.metric("🏪 VENDORS", last_action.get('vendors', 40))
                
                st.markdown("---")
                
                # Stats
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Actions", len(actions))
                c2.metric("Entry", len([a for a in actions if a.get('risk_type') == 'ENTRY']))
                c3.metric("Exit", len([a for a in actions if a.get('risk_type') == 'EXIT']))
                c4.metric("Critical", len([a for a in actions if a['type'] == 'STRONG']))
                
                st.markdown("---")
                
                # Action log
                for action in reversed(actions[-10:]):
                    is_exit = action.get('risk_type') == 'EXIT'
                    is_strong = action['type'] == 'STRONG'
                    
                    card_class = 'ml-action'
                    if is_strong:
                        card_class += ' strong'
                    if is_exit:
                        card_class += ' exit-action'
                    
                    type_badge = 'ml-badge-strong' if is_strong else 'ml-badge-moderate'
                    phase_badge = 'ml-badge-exit' if is_exit else 'ml-badge-entry'
                    
                    st.markdown(f'''
                    <div class="{card_class}">
                        <div style="margin-bottom:6px;">
                            <span class="ml-badge {type_badge}">{action["type"]}</span>
                            <span class="ml-badge {phase_badge}">{action.get("risk_type", "ENTRY")}</span>
                            <span style="color:#64748b;font-size:0.85rem;">t={int(action["time"])}min</span>
                        </div>
                        <div style="font-size:0.9rem;">
                            Risk: <b>{action.get("risk", 0):.0%}</b> | 
                            Queue: <b>{action.get("queue", 0):,}</b> | 
                            Wait: <b>{action.get("wait", 0):.1f}min</b>
                        </div>
                        <div style="background:#f1f5f9;padding:6px 10px;border-radius:6px;margin-top:8px;font-size:0.85rem;">
                            → {action.get("decision", "N/A")}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                st.success("✓ System optimal - No interventions needed")
        else:
            st.info("Run a simulation to see ML actions")
    
    with tab2:
        if data is not None:
            cols = ['time', 'fans_in_stadium', 'security_queue', 'turnstile_queue',
                   'exit_queue', 'avg_security_wait', 'avg_turnstile_wait', 'avg_exit_wait',
                   'arrival_rate', 'exit_rate']
            available = [c for c in cols if c in data.columns]
            st.dataframe(data[available].tail(30).round(2), use_container_width=True, hide_index=True)
    
    with tab3:
        if data is not None and len(data) > 0:
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                st.metric("Peak Entry Queue", f"{int(data['security_queue'].max() + data['turnstile_queue'].max()):,}")
                st.metric("Avg Entry Wait", f"{(data['avg_security_wait'] + data['avg_turnstile_wait']).mean():.1f} min")
            
            with c2:
                st.metric("Peak Exit Queue", f"{int(data['exit_queue'].max()):,}")
                st.metric("Avg Exit Wait", f"{data['avg_exit_wait'].mean():.1f} min")
            
            with c3:
                st.metric("Peak Arrivals", f"{data['arrival_rate'].max():.0f}/min")
                st.metric("Max Fans", f"{int(data['fans_in_stadium'].max()):,}")
            
            with c4:
                st.metric("Max Total Wait", f"{(data['avg_security_wait'] + data['avg_turnstile_wait']).max():.1f} min")
                st.metric("Duration", f"{int(data['time'].max())} min")
    
    # Auto-refresh
    if st.session_state.auto_refresh:
        time.sleep(st.session_state.refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
