import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run Phase 4
try:
    from phase4.main import main
    main()
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying to run Phase 4 directly...")
    
    # Try running a simple demo
    os.chdir("phase4")
    import phase4.demo_test_simple
    phase4.demo_test_simple.run_demo()
except Exception as e:
    print(f"Error running Phase 4: {e}")
    sys.exit(1)
