"""
Stadium AI Dashboard - Enhanced Real-Time Monitoring
====================================================
Beautiful, responsive dashboard with ML control visualization.
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

# Page configuration
st.set_page_config(
    page_title="Stadium AI Control Center",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ ENHANCED CSS STYLING ============
st.markdown("""
<style>
    /* Main container */
    .main .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 100%; }
    
    /* Header styling */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-top: -10px;
    }
    
    /* Status alerts */
    .alert-critical {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        font-weight: bold;
        text-align: center;
        font-size: 1.1rem;
        box-shadow: 0 4px 20px rgba(255,65,108,0.4);
        animation: pulse 2s infinite;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: #333;
        padding: 1.2rem;
        border-radius: 12px;
        font-weight: bold;
        text-align: center;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(247,151,30,0.3);
    }
    
    .alert-ok {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        font-weight: bold;
        text-align: center;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(17,153,142,0.3);
    }
    
    /* Live badge */
    .live-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .live-dot {
        width: 10px;
        height: 10px;
        background: white;
        border-radius: 50%;
        margin-right: 8px;
        animation: blink 1s infinite;
    }
    
    /* ML Action cards - Minimal Design */
    .ml-action {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
        font-size: 0.9rem;
    }
    .ml-action-strong {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
    }
    .ml-action-exit {
        border-left-color: #8b5cf6;
        background: #faf5ff;
    }
    .ml-action-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 6px;
    }
    .ml-time { 
        background: #e2e8f0; 
        padding: 2px 8px; 
        border-radius: 4px; 
        font-size: 0.8rem;
        font-weight: 600;
        color: #475569;
    }
    .ml-badge {
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .ml-badge-moderate { background: #fef3c7; color: #92400e; }
    .ml-badge-strong { background: #fee2e2; color: #991b1b; }
    .ml-badge-entry { background: #dbeafe; color: #1e40af; }
    .ml-badge-exit { background: #ede9fe; color: #5b21b6; }
    .ml-details {
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 4px;
    }
    .ml-details b { color: #334155; }
    .ml-action-taken {
        background: #f1f5f9;
        padding: 6px 10px;
        border-radius: 6px;
        margin-top: 8px;
        font-size: 0.82rem;
        color: #475569;
    }
    
    /* Phase indicators */
    .phase-badge {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .phase-early { background: #e3f2fd; color: #1565c0; }
    .phase-building { background: #fff3e0; color: #e65100; }
    .phase-peak { background: #ffebee; color: #c62828; }
    .phase-match { background: #e8f5e9; color: #2e7d32; }
    .phase-exit { background: #f3e5f5; color: #7b1fa2; }
    
    /* Card containers */
    .stat-card {
        background: linear-gradient(145deg, #ffffff, #f5f5f5);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
    }
    
    /* Animations */
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 4px 20px rgba(255,65,108,0.4); }
        50% { box-shadow: 0 4px 30px rgba(255,65,108,0.7); }
        100% { box-shadow: 0 4px 20px rgba(255,65,108,0.4); }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #a8a8a8; }
</style>
""", unsafe_allow_html=True)

# ============ API & CONFIG ============
API_URL = "http://localhost:8000"

# Session state initialization
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 2
if 'sim_start_time' not in st.session_state:
    st.session_state.sim_start_time = None
if 'last_file_mod' not in st.session_state:
    st.session_state.last_file_mod = None


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


def get_phase_badge(time_min):
    """Get the current phase based on simulation time."""
    if time_min < 60:
        return '<span class="phase-badge phase-early">🌅 Early Arrivals</span>'
    elif time_min < 120:
        return '<span class="phase-badge phase-building">📈 Building Up</span>'
    elif time_min < 180:
        return '<span class="phase-badge phase-peak">🔥 Peak Rush</span>'
    elif time_min < 300:
        return '<span class="phase-badge phase-match">⚽ Match Time</span>'
    else:
        return '<span class="phase-badge phase-exit">🚪 Exit Flow</span>'


def get_alert_status(data):
    """Determine the current alert status based on queue and wait times."""
    if data is None or len(data) == 0:
        return "unknown", "⚪ Waiting for simulation data..."
    
    latest = data.iloc[-1]
    total_queue = latest.get('turnstile_queue', 0) + latest.get('security_queue', 0)
    total_wait = latest.get('avg_turnstile_wait', 0) + latest.get('avg_security_wait', 0)
    
    if total_queue > 8000 or total_wait > 25:
        return "critical", f"🚨 CRITICAL CONGESTION | Total Queue: {int(total_queue):,} fans | Wait: {total_wait:.1f} min"
    elif total_queue > 4000 or total_wait > 15:
        return "warning", f"⚠️ HIGH LOAD | Total Queue: {int(total_queue):,} fans | Wait: {total_wait:.1f} min"
    else:
        return "ok", f"✅ OPTIMAL FLOW | Total Queue: {int(total_queue):,} fans | Wait: {total_wait:.1f} min"


# ============ CHART FUNCTIONS ============
def create_queue_comparison_chart(data):
    """Create side-by-side queue comparison chart."""
    if data is None or len(data) == 0:
        return None
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('🔒 Security Queue', '🚪 Turnstile Queue'),
        horizontal_spacing=0.08
    )
    
    # Security queue
    if 'security_queue' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['time'], y=data['security_queue'],
            mode='lines', name='Security Queue',
            line=dict(color='#9b59b6', width=2.5),
            fill='tozeroy', fillcolor='rgba(155,89,182,0.2)'
        ), row=1, col=1)
    
    # Turnstile queue
    if 'turnstile_queue' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['time'], y=data['turnstile_queue'],
            mode='lines', name='Turnstile Queue',
            line=dict(color='#3498db', width=2.5),
            fill='tozeroy', fillcolor='rgba(52,152,219,0.2)'
        ), row=1, col=2)
        
        # Add current position marker
        if len(data) > 0:
            latest = data.iloc[-1]
            fig.add_trace(go.Scatter(
                x=[latest['time']], y=[latest['turnstile_queue']],
                mode='markers', marker=dict(size=14, color='#e74c3c', symbol='circle'),
                name='Current', showlegend=False
            ), row=1, col=2)
    
    fig.update_layout(
        height=300,
        showlegend=False,
        margin=dict(t=50, b=40, l=50, r=30),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(title_text='Time (min)', gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(title_text='Queue Size', gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def create_exit_queue_chart(data):
    """Create exit queue and wait time chart."""
    if data is None or len(data) == 0:
        return None
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('🚪 Exit Queue', '⏱️ Exit Wait Time'),
        horizontal_spacing=0.08
    )
    
    # Exit queue
    if 'exit_queue' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['time'], y=data['exit_queue'],
            mode='lines', name='Exit Queue',
            line=dict(color='#e74c3c', width=2.5),
            fill='tozeroy', fillcolor='rgba(231,76,60,0.2)'
        ), row=1, col=1)
    
    # Exit wait time
    if 'avg_exit_wait' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['time'], y=data['avg_exit_wait'],
            mode='lines', name='Exit Wait',
            line=dict(color='#f39c12', width=2.5),
            fill='tozeroy', fillcolor='rgba(243,156,18,0.2)'
        ), row=1, col=2)
        
        # Add critical line
        fig.add_hline(y=30, line_dash='dash', line_color='#d32f2f',
                      annotation_text='Critical', row=1, col=2)
    
    fig.update_layout(
        height=280,
        showlegend=False,
        margin=dict(t=50, b=40, l=50, r=30),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(title_text='Time (min)', gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def create_wait_time_gauge(current_wait, max_wait=35):
    """Create a gauge chart for total wait time."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current_wait,
        number={'suffix': ' min', 'font': {'size': 32, 'color': '#333'}},
        delta={'reference': 5, 'position': 'bottom', 'relative': False},
        title={'text': 'Total Wait Time', 'font': {'size': 16}},
        gauge={
            'axis': {'range': [0, max_wait], 'tickwidth': 2},
            'bar': {'color': '#667eea', 'thickness': 0.8},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': '#ddd',
            'steps': [
                {'range': [0, 5], 'color': '#c8e6c9'},
                {'range': [5, 10], 'color': '#fff9c4'},
                {'range': [10, 20], 'color': '#ffccbc'},
                {'range': [20, max_wait], 'color': '#ffcdd2'}
            ],
            'threshold': {
                'line': {'color': '#d32f2f', 'width': 4},
                'thickness': 0.8,
                'value': 20
            }
        }
    ))
    
    fig.update_layout(
        height=240,
        margin=dict(t=40, b=20, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig


def create_flow_rate_chart(data):
    """Create arrival and exit flow rate chart."""
    if data is None or 'arrival_rate' not in data.columns:
        return None
    
    fig = go.Figure()
    
    # Arrival rate
    fig.add_trace(go.Scatter(
        x=data['time'], y=data['arrival_rate'],
        mode='lines', name='Arrivals',
        line=dict(color='#2196f3', width=2.5),
        fill='tozeroy', fillcolor='rgba(33,150,243,0.15)'
    ))
    
    # Exit rate
    if 'exit_rate' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['time'], y=data['exit_rate'],
            mode='lines', name='Exits',
            line=dict(color='#f44336', width=2.5),
            fill='tozeroy', fillcolor='rgba(244,67,54,0.15)'
        ))
    
    # Kickoff line
    fig.add_vline(
        x=180, line_dash='dash', line_color='#4caf50', line_width=2,
        annotation_text='⚽ KICKOFF', annotation_position='top'
    )
    
    fig.update_layout(
        title={'text': '👥 Fan Flow Rate Over Time', 'font': {'size': 16}},
        xaxis_title='Time (min)',
        yaxis_title='Fans per minute',
        height=300,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def create_utilization_chart(data):
    """Create resource utilization bar chart."""
    if data is None or len(data) == 0:
        return None
    
    latest = data.iloc[-1]
    
    resources = ['Security', 'Turnstiles', 'Vendors', 'Exit Gates', 'Parking']
    utilizations = [
        latest.get('security_utilization', 0) * 100,
        latest.get('turnstile_utilization', 0) * 100,
        latest.get('vendor_utilization', 0) * 100,
        latest.get('exit_utilization', 0) * 100,
        latest.get('parking_utilization', 0) * 100
    ]
    
    # Color based on utilization level
    colors = []
    for u in utilizations:
        if u < 60:
            colors.append('#4caf50')  # Green
        elif u < 80:
            colors.append('#ff9800')  # Orange
        else:
            colors.append('#f44336')  # Red
    
    fig = go.Figure(go.Bar(
        y=resources,
        x=utilizations,
        orientation='h',
        marker_color=colors,
        text=[f'{u:.0f}%' for u in utilizations],
        textposition='inside',
        textfont=dict(color='white', size=13, family='Arial Black')
    ))
    
    # Add threshold line
    fig.add_vline(x=85, line_dash='dash', line_color='#d32f2f', line_width=2,
                  annotation_text='Capacity', annotation_position='top right')
    
    fig.update_layout(
        title={'text': '📊 Resource Utilization', 'font': {'size': 16}},
        xaxis=dict(range=[0, 100], title='Utilization %'),
        height=280,
        margin=dict(l=100),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_wait_trend_chart(data):
    """Create wait time trend chart."""
    if data is None or len(data) == 0:
        return None
    
    fig = go.Figure()
    
    # Security wait
    if 'avg_security_wait' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['time'], y=data['avg_security_wait'],
            mode='lines', name='Security Wait',
            line=dict(color='#9b59b6', width=2.5)
        ))
    
    # Turnstile wait
    if 'avg_turnstile_wait' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['time'], y=data['avg_turnstile_wait'],
            mode='lines', name='Turnstile Wait',
            line=dict(color='#3498db', width=2.5)
        ))
    
    # Target and critical lines
    fig.add_hline(y=10, line_dash='dot', line_color='#27ae60',
                  annotation_text='Target (10 min)', annotation_position='right')
    fig.add_hline(y=20, line_dash='dash', line_color='#e74c3c',
                  annotation_text='Critical (20 min)', annotation_position='right')
    
    fig.update_layout(
        title={'text': '⏱️ Wait Time Trends', 'font': {'size': 16}},
        xaxis_title='Time (min)',
        yaxis_title='Wait Time (min)',
        height=300,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def create_stadium_fill_chart(data):
    """Create stadium fill progression chart."""
    if data is None or 'fans_in_stadium' not in data.columns:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['time'], y=data['fans_in_stadium'],
        mode='lines', name='Fans in Stadium',
        line=dict(color='#667eea', width=3),
        fill='tozeroy', fillcolor='rgba(102,126,234,0.2)'
    ))
    
    # Capacity line
    capacity = data['fans_in_stadium'].max() * 1.1 if len(data) > 0 else 70000
    fig.add_hline(y=68000, line_dash='dash', line_color='#333',
                  annotation_text='Capacity: 68,000')
    
    fig.update_layout(
        title={'text': '🏟️ Stadium Fill Progress', 'font': {'size': 16}},
        xaxis_title='Time (min)',
        yaxis_title='Fans in Stadium',
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def generate_ml_actions(data):
    """Generate ML control actions with gate state tracking."""
    if data is None or len(data) < 10:
        return []
    
    actions = []
    kickoff_time = 180
    match_end_time = kickoff_time + 120  # t=300
    
    # Track gate states (starting values)
    security_gates = 30
    entry_gates = 20  # turnstiles
    exit_gates = 25
    vendors = 40
    
    # Check more frequently to catch exit spikes
    check_points = range(5, len(data), max(1, len(data)//50))
    
    for idx in check_points:
        row = data.iloc[idx]
        t = row['time']
        
        # Entry metrics
        sec_q = row.get('security_queue', 0)
        turn_q = row.get('turnstile_queue', 0)
        sec_wait = row.get('avg_security_wait', 0)
        turn_wait = row.get('avg_turnstile_wait', 0)
        entry_queue = sec_q + turn_q
        entry_wait = max(sec_wait, turn_wait)
        
        # Exit metrics
        exit_q = row.get('exit_queue', 0)
        exit_wait = row.get('avg_exit_wait', 0)
        
        # Risk calculations
        entry_risk = (min(entry_queue/5000, 1)*0.4 + min(entry_wait/15, 1)*0.5 + 
                     (0.1 if t < kickoff_time and kickoff_time-t < 60 else 0))
        exit_risk = (min(exit_q/2000, 1)*0.4 + min(exit_wait/10, 1)*0.5 + 
                    (0.2 if t > match_end_time - 30 else 0))
        
        is_exit_phase = t > kickoff_time + 90  # After halftime (t=270)
        
        # Priority: Check EXIT first if queue is building
        if exit_q > 500:  # Exit queue detected
            if exit_risk > 0.6:
                old_exits = exit_gates
                exit_gates = min(exit_gates + 10, 80)
                actions.append({
                    'time': t, 'type': 'STRONG', 'risk_type': 'EXIT',
                    'risk': exit_risk, 'queue': int(exit_q), 'wait': exit_wait,
                    'decision': f'+10 exit gates ({old_exits}->{exit_gates})',
                    'security': security_gates, 'entry': entry_gates, 'exit': exit_gates, 'vendors': vendors
                })
            elif exit_risk > 0.4:
                old_exits = exit_gates
                exit_gates = min(exit_gates + 5, 80)
                actions.append({
                    'time': t, 'type': 'MODERATE', 'risk_type': 'EXIT',
                    'risk': exit_risk, 'queue': int(exit_q), 'wait': exit_wait,
                    'decision': f'+5 exit gates ({old_exits}->{exit_gates})',
                    'security': security_gates, 'entry': entry_gates, 'exit': exit_gates, 'vendors': vendors
                })
        elif entry_queue > 500:  # Entry queue detected
            if entry_risk > 0.7:
                old_sec, old_vend = security_gates, vendors
                security_gates = min(security_gates + 5, 80)
                vendors = min(vendors + 10, 150)
                actions.append({
                    'time': t, 'type': 'STRONG', 'risk_type': 'ENTRY',
                    'risk': entry_risk, 'queue': int(entry_queue), 'wait': entry_wait,
                    'decision': f'Security {old_sec}->{security_gates}, Vendors {old_vend}->{vendors}',
                    'security': security_gates, 'entry': entry_gates, 'exit': exit_gates, 'vendors': vendors
                })
            elif entry_risk > 0.5:
                old_sec, old_vend = security_gates, vendors
                security_gates = min(security_gates + 3, 80)
                vendors = min(vendors + 5, 150)
                actions.append({
                    'time': t, 'type': 'MODERATE', 'risk_type': 'ENTRY',
                    'risk': entry_risk, 'queue': int(entry_queue), 'wait': entry_wait,
                    'decision': f'Security {old_sec}->{security_gates}, Vendors {old_vend}->{vendors}',
                    'security': security_gates, 'entry': entry_gates, 'exit': exit_gates, 'vendors': vendors
                })
    
    return actions


# ============ MAIN APPLICATION ============
def main():
    # Header
    st.markdown('<h1 class="main-header">🏟️ Stadium AI Control Center</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time Crowd Management & ML Control System</p>', unsafe_allow_html=True)
    
    # ============ SIDEBAR ============
    with st.sidebar:
        if st.session_state.auto_refresh:
            st.markdown('<div class="live-badge"><span class="live-dot"></span>LIVE MONITORING</div>', unsafe_allow_html=True)
        
        st.header("⚙️ Control Panel")
        
        # API Status
        api_status = check_api_status()
        if api_status:
            st.success("🟢 API Server Online")
        else:
            st.warning("🟡 API Offline - Using Local Mode")
        
        st.divider()
        
        # Display Settings
        st.subheader("🔄 Display Settings")
        st.session_state.auto_refresh = st.toggle("Auto Refresh", value=st.session_state.auto_refresh)
        st.session_state.refresh_interval = st.slider("Refresh Interval (sec)", 1, 10, 2)
        
        col1, col2 = st.columns(2)
        if col1.button("🔄 Refresh Now"):
            st.rerun()
        if col2.button("⏮️ Reset View"):
            st.session_state.sim_start_time = datetime.now()
            st.rerun()
        
        st.divider()
        
        # Simulation Controls
        st.subheader("🎮 Simulation Control")
        num_fans = st.slider("👥 Number of Fans", 20000, 80000, 68000, step=5000)
        enable_ml = st.toggle("🤖 Enable ML Control", value=True)
        
        if st.button("▶️ Run New Simulation", type="primary", use_container_width=True):
            with st.spinner("Running simulation..."):
                if api_status:
                    try:
                        response = requests.post(
                            f"{API_URL}/simulate",
                            json={"num_fans": num_fans, "enable_ml_control": enable_ml},
                            timeout=300
                        )
                        if response.status_code == 200:
                            st.success("✅ Simulation completed!")
                            st.session_state.sim_start_time = datetime.now()
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    # Run locally
                    import subprocess
                    cmd = ['python', 'simulation/run_simulation.py', '--fans', str(num_fans)]
                    if enable_ml:
                        cmd.append('--ml')
                    subprocess.run(cmd, cwd=Path(__file__).parent.parent)
                    st.success("✅ Simulation completed!")
                    st.session_state.sim_start_time = datetime.now()
                    time.sleep(1)
                    st.rerun()
        
        st.divider()
        st.caption("© Stadium AI v2.0 - Enhanced Dashboard")
    
    # ============ MAIN CONTENT ============
    # Load data
    full_data = load_simulation_data()
    
    if full_data is not None:
        data, sim_time = get_realtime_slice(full_data)
    else:
        data, sim_time = None, 0
    
    # Status Bar
    if data is not None and len(data) > 0:
        current_time = data.iloc[-1].get('time', 0)
        max_time = full_data['time'].max()
        progress = min(100, (current_time / max_time) * 100) if max_time > 0 else 0
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            hours = int(current_time) // 60
            mins = int(current_time) % 60
            st.markdown(f"**⏰ Simulation Time:** `T+{hours}h {mins:02d}m`")
        
        with col2:
            st.markdown(f"**Phase:** {get_phase_badge(current_time)}", unsafe_allow_html=True)
        
        with col3:
            st.progress(progress / 100, text=f"Progress: {progress:.0f}%")
    
    # Alert Banner
    status, message = get_alert_status(data)
    alert_class = 'alert-critical' if status == 'critical' else 'alert-warning' if status == 'warning' else 'alert-ok'
    st.markdown(f'<div class="{alert_class}">{message}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Key Metrics Row - Entry metrics
    if data is not None and len(data) > 0:
        latest = data.iloc[-1]
        
        st.markdown("**🔒 Entry Metrics**")
        m1, m2, m3, m4, m5 = st.columns(5)
        
        with m1:
            st.metric(
                "👥 In Stadium",
                f"{int(latest.get('fans_in_stadium', 0)):,}",
                delta=f"{latest.get('arrival_rate', 0):.0f}/min"
            )
        
        with m2:
            st.metric(
                "🔒 Security Q",
                f"{int(latest.get('security_queue', 0)):,}",
                delta=None
            )
        
        with m3:
            st.metric(
                "🚪 Turnstile Q",
                f"{int(latest.get('turnstile_queue', 0)):,}",
                delta=None
            )
        
        with m4:
            entry_wait = latest.get('avg_security_wait', 0) + latest.get('avg_turnstile_wait', 0)
            st.metric(
                "⏱️ Entry Wait",
                f"{entry_wait:.1f} min",
                delta=None
            )
        
        with m5:
            fill_pct = latest.get('fill_ratio', 0) * 100
            st.metric(
                "🏟️ Fill Rate",
                f"{fill_pct:.1f}%",
                delta=None
            )
        
        # Exit metrics row
        st.markdown("**🚪 Exit Metrics**")
        e1, e2, e3, e4, e5 = st.columns(5)
        
        with e1:
            st.metric(
                "🚶 Exited",
                f"{int(latest.get('fans_exited', 0)):,}",
                delta=f"{latest.get('exit_rate', 0):.0f}/min"
            )
        
        with e2:
            st.metric(
                "🚪 Exit Queue",
                f"{int(latest.get('exit_queue', 0)):,}",
                delta=None
            )
        
        with e3:
            st.metric(
                "⏱️ Exit Wait",
                f"{latest.get('avg_exit_wait', 0):.1f} min",
                delta=None
            )
        
        with e4:
            exit_util = latest.get('exit_utilization', 0) * 100
            st.metric(
                "📊 Exit Util",
                f"{exit_util:.0f}%",
                delta=None
            )
        
        with e5:
            exit_pct = latest.get('exit_progress', 0) * 100
            st.metric(
                "✅ Exit Progress",
                f"{exit_pct:.1f}%",
                delta=None
            )
    
    st.markdown("---")
    
    # Charts Section
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        # Queue comparison chart (Entry)
        queue_chart = create_queue_comparison_chart(data)
        if queue_chart:
            st.plotly_chart(queue_chart, use_container_width=True)
        
        # Exit queue chart
        exit_chart = create_exit_queue_chart(data)
        if exit_chart:
            st.plotly_chart(exit_chart, use_container_width=True)
        
        # Flow rate chart
        flow_chart = create_flow_rate_chart(data)
        if flow_chart:
            st.plotly_chart(flow_chart, use_container_width=True)
    
    with col_right:
        # Entry wait time gauge
        if data is not None and len(data) > 0:
            latest = data.iloc[-1]
            total_wait = latest.get('avg_security_wait', 0) + latest.get('avg_turnstile_wait', 0)
            gauge = create_wait_time_gauge(total_wait)
            st.plotly_chart(gauge, use_container_width=True)
        
        # Utilization chart
        util_chart = create_utilization_chart(data)
        if util_chart:
            st.plotly_chart(util_chart, use_container_width=True)
        
        # Stadium fill chart
        fill_chart = create_stadium_fill_chart(data)
        if fill_chart:
            st.plotly_chart(fill_chart, use_container_width=True)
    
    st.markdown("---")
    
    # Tabs for additional info
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 ML Control Actions", "📋 Data Table", "📊 Statistics", "ℹ️ About"])
    
    with tab1:
        st.subheader("ML Control Decision Log")
        
        if data is not None and len(data) > 0:
            actions = generate_ml_actions(data)
            
            if actions:
                entry_actions = [a for a in actions if a.get('risk_type') == 'ENTRY']
                exit_actions = [a for a in actions if a.get('risk_type') == 'EXIT']
                
                # Current gate states (from last action)
                last_action = actions[-1]
                st.markdown("##### 📊 Current Resource State")
                g1, g2, g3, g4 = st.columns(4)
                g1.metric("🔒 Security", last_action.get('security', 30))
                g2.metric("🚪 Entry Gates", last_action.get('entry', 20))
                g3.metric("🚶 Exit Gates", last_action.get('exit', 25))
                g4.metric("🏪 Vendors", last_action.get('vendors', 40))
                
                st.markdown("---")
                
                # Summary metrics
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Actions", len(actions))
                c2.metric("Entry", len(entry_actions))
                c3.metric("Exit", len(exit_actions))
                strong_count = len([a for a in actions if a['type'] == 'STRONG'])
                c4.metric("Critical", strong_count)
                
                st.markdown("---")
                
                # Display actions with gate state
                for action in reversed(actions[-12:]):
                    is_exit = action.get('risk_type') == 'EXIT'
                    is_strong = action['type'] == 'STRONG'
                    
                    card_class = 'ml-action'
                    if is_strong:
                        card_class += ' ml-action-strong'
                    if is_exit:
                        card_class += ' ml-action-exit'
                    
                    type_badge = 'ml-badge-strong' if is_strong else 'ml-badge-moderate'
                    phase_badge = 'ml-badge-exit' if is_exit else 'ml-badge-entry'
                    phase_icon = '🚪' if is_exit else '🔐'
                    
                    # Gate state display
                    gate_state = f"Sec:{action.get('security', '-')} | Entry:{action.get('entry', '-')} | Exit:{action.get('exit', '-')}"
                    
                    st.markdown(f'''
                    <div class="{card_class}">
                        <div class="ml-action-header">
                            <span class="ml-time">t={int(action["time"])}min</span>
                            <span class="ml-badge {type_badge}">{action["type"]}</span>
                            <span class="ml-badge {phase_badge}">{phase_icon} {action["risk_type"]}</span>
                        </div>
                        <div class="ml-details">
                            <b>Risk:</b> {action.get("risk", 0):.0%} | 
                            <b>Queue:</b> {action.get("queue", 0):,} | 
                            <b>Wait:</b> {action.get("wait", 0):.1f}min
                        </div>
                        <div class="ml-action-taken">→ {action.get("decision", "N/A")}</div>
                        <div style="font-size:0.75rem;color:#94a3b8;margin-top:4px">📊 {gate_state}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                st.success("✓ No interventions needed - System optimal")
        else:
            st.info("Run a simulation to see ML actions")
    
    with tab2:
        st.subheader("Simulation Data")
        if data is not None:
            display_cols = [
                'time', 'fans_in_stadium', 'security_queue', 'turnstile_queue',
                'avg_security_wait', 'avg_turnstile_wait', 'arrival_rate', 'exit_rate'
            ]
            available_cols = [c for c in display_cols if c in data.columns]
            st.dataframe(
                data[available_cols].tail(30).round(2),
                use_container_width=True,
                hide_index=True
            )
    
    with tab3:
        st.subheader("Simulation Statistics")
        if data is not None and len(data) > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Peak Security Queue", f"{int(data['security_queue'].max()):,}")
                st.metric("Avg Security Wait", f"{data['avg_security_wait'].mean():.1f} min")
            
            with col2:
                st.metric("Peak Turnstile Queue", f"{int(data['turnstile_queue'].max()):,}")
                st.metric("Avg Turnstile Wait", f"{data['avg_turnstile_wait'].mean():.1f} min")
            
            with col3:
                st.metric("Peak Arrival Rate", f"{data['arrival_rate'].max():.0f}/min")
                st.metric("Max Fans in Stadium", f"{int(data['fans_in_stadium'].max()):,}")
            
            with col4:
                st.metric("Max Total Wait", f"{(data['avg_security_wait'] + data['avg_turnstile_wait']).max():.1f} min")
                st.metric("Simulation Duration", f"{int(data['time'].max())} min")
    
    with tab4:
        st.subheader("About Stadium AI")
        st.markdown("""
        **Stadium AI Control Center** is an advanced real-time crowd management system 
        that uses machine learning to optimize fan flow and minimize wait times.
        
        **Features:**
        - 🔄 Real-time monitoring of queue lengths and wait times
        - 🤖 ML-based predictive control for capacity management
        - 📊 Comprehensive resource utilization tracking
        - ⚠️ Intelligent alert system for congestion events
        - 📈 Historical trend analysis and statistics
        
        **System Components:**
        - Security Screening: 60 lanes
        - Turnstile Gates: 40 gates  
        - Vendor Stations: 120 stations
        - Exit Gates: 40 gates
        - Stadium Capacity: 68,000 fans
        """)
    
    # Auto-refresh
    if st.session_state.auto_refresh:
        time.sleep(st.session_state.refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
