"""
Stadium AI - Dashboard startup script.

Run with: python run_dashboard.py
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    dashboard_path = Path(__file__).parent / 'dashboard' / 'app.py'
    
    print("🚀 Starting Stadium AI Dashboard...")
    print("📊 Open: http://localhost:8501")
    print("📖 API must be running on http://localhost:8000")
    print("-" * 50)
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(dashboard_path),
        "--server.port=8501"
    ])
