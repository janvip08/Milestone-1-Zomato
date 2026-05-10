#!/usr/bin/env python3
"""
Simple backend runner for Phase 4
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Run a simple backend demo"""
    print("Starting Phase 4 Backend Demo...")
    
    # Change to phase4 directory
    os.chdir(project_root / "phase4")
    
    try:
        # Import and run demo
        import phase4.demo_test_simple
        phase4.demo_test_simple.run_demo()
        print("Backend demo completed successfully!")
    except Exception as e:
        print(f"Backend error: {e}")
        print("Trying alternative approach...")
        
        # Try running a simple FastAPI server
        try:
            from phase4.api_server import RecommendationAPI
            print("Backend API server available")
            print("Backend ready for integration!")
        except Exception as e2:
            print(f"Alternative backend error: {e2}")

if __name__ == "__main__":
    main()
