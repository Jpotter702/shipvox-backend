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
    port = int(os.getenv("PORT", "10000"))  # Use Render's PORT env var or default to 10000
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
# Load environment variables
# Start FastAPI server with uvicorn
