"""
Stadium AI - API startup script.

Run with: python run_api.py
"""

import uvicorn
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'simulation'))
sys.path.insert(0, str(project_root / 'ml'))
sys.path.insert(0, str(project_root / 'api'))

if __name__ == "__main__":
    print("🚀 Starting Stadium AI API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("📊 Dashboard: Run 'streamlit run dashboard/app.py' in another terminal")
    print("-" * 50)
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
