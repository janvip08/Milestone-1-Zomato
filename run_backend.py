import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now run the phase4 main
from phase4.main import main

if __name__ == "__main__":
    main()
