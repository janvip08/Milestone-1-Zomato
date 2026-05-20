import os
import sys
import logging
from pathlib import Path

# Add the project root to the sys.path so phase2/phase3 imports work
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from phase4.api_server import create_app

# Resolve data path relative to this script
data_path = project_root / "data" / "processed" / "restaurants.csv"

# Fetch Groq API Key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    logging.warning("GROQ_API_KEY environment variable is not set. Please set it in production.")
    groq_api_key = "dummy-key-for-startup"

# Create the ASGI application instance
app = create_app(groq_api_key=groq_api_key, data_path=str(data_path))
