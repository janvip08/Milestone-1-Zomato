import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now run the backend
if __name__ == "__main__":
    # Change to phase4 directory and run main
    os.chdir("phase4")
    exec(open("main.py").read())
