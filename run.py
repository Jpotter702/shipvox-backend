# Run"""Run script for ShipVox application."""
import os
import sys
from dotenv import load_dotenv
import uvicorn

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
# Load environment variables
# Start FastAPI server with uvicorn
