import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now run backend
if __name__ == "__main__":
    # Change to phase4 directory and run main
    os.chdir("phase4")
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            code = f.read()
            exec(code)
    except Exception as e:
        print(f"Error running backend: {e}")
        sys.exit(1)
