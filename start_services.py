#!/usr/bin/env python3
"""
Script to start both backend and frontend services
"""
import sys
import os
import subprocess
import time
from pathlib import Path

def start_backend():
    """Start the backend service"""
    print("Starting backend service...")
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    # Try to run a simple backend demo
    try:
        os.chdir("phase4")
        # Import and run a simple demo
        import phase4.demo_test_simple
        phase4.demo_test_simple.run_demo()
        return True
    except Exception as e:
        print(f"Backend error: {e}")
        return False

def start_frontend():
    """Start the frontend service"""
    print("Starting frontend service...")
    
    # Change to frontend directory
    project_root = Path(__file__).parent
    frontend_dir = project_root / "phase7"
    os.chdir(frontend_dir)
    
    try:
        # Try to start Next.js development server
        node_path = "C:\\Program Files\\nodejs\\node.exe"
        npm_path = "C:\\Program Files\\nodejs\\npm.cmd"
        
        # Use npm to run dev server
        result = subprocess.run([npm_path, "run", "dev"], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        if result.returncode == 0:
            print("Frontend started successfully!")
            return True
        else:
            print(f"Frontend error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Frontend error: {e}")
        return False

if __name__ == "__main__":
    print("Starting Phase 7 services...")
    
    # Start backend
    backend_success = start_backend()
    
    # Start frontend
    frontend_success = start_frontend()
    
    if backend_success and frontend_success:
        print("✅ Both services started successfully!")
        print("Backend: Running Phase 4 demo")
        print("Frontend: http://localhost:3000")
    else:
        print("❌ Some services failed to start")
        print(f"Backend: {'✅' if backend_success else '❌'}")
        print(f"Frontend: {'✅' if frontend_success else '❌'}")
