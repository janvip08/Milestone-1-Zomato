"""Main entry point and examples for Phase 4 Application Layer."""

import os
import sys
import argparse
import logging
from typing import Dict, Any

from app_orchestrator import create_phase4_app, Phase4App
from .groq_provider import create_groq_config, GroqProvider


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def example_api_usage():
    """Example of using the API programmatically."""
    print("=== API Usage Example ===\n")
    
    # Get API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("Error: GROQ_API_KEY environment variable not set")
        return
    
    # Create app
    app = create_phase4_app(groq_api_key)
    
    # Test preferences
    preferences = {
        "location": "Downtown",
        "cuisine": "Italian",
        "min_rating": 4.0,
        "max_cost_for_two": 1000,
        "occasion": "date night"
    }
    
    print(f"Getting recommendations for: {preferences}")
    
    try:
        # Generate recommendations
        result = app.generate_recommendations_complete(
            preferences,
            response_type="recommendation",
            max_recommendations=3
        )
        
        # Display results
        print("\nRecommendations:")
        recommendations = result.get("recommendations", [])
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec.get('restaurant_name', 'Unknown')}")
            print(f"   Match Score: {rec.get('match_score', 0)*100:.1f}%")
            print(f"   Price: {rec.get('price_indication', 'N/A')}")
            print(f"   Best for: {rec.get('best_for', 'N/A')}")
            
            if rec.get('reasons'):
                print("   Reasons:")
                for reason in rec['reasons']:
                    print(f"   • {reason}")
        
        # Show metadata
        metadata = result.get("pipeline_metadata", {})
        print(f"\nGenerated in {metadata.get('response_time_ms', 0)}ms")
        print(f"Used {metadata.get('candidates_used', 0)} of {metadata.get('total_candidates', 0)} candidates")
        
    except Exception as e:
        print(f"Error: {e}")


def example_groq_provider():
    """Example of using Groq provider directly."""
    print("\n=== Groq Provider Example ===\n")
    
    # Get API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("Error: GROQ_API_KEY environment variable not set")
        return
    
    # Create Groq config
    config = create_groq_config(
        api_key=groq_api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.7
    )
    
    # Create provider
    provider = GroqProvider(config)
    
    print("Testing Groq connection...")
    
    try:
        # Test connection
        if provider.test_connection():
            print("✅ Groq connection successful")
        else:
            print("❌ Groq connection failed")
            return
        
        # Show available models
        models = provider.list_available_models()
        print(f"\nAvailable models:")
        for model, description in models.items():
            print(f"  • {model}: {description}")
        
        # Generate response
        print("\nGenerating test response...")
        prompt = "List 3 popular Italian dishes with brief descriptions."
        system_prompt = "You are a helpful culinary expert."
        
        response = provider.generate_response(prompt, system_prompt)
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_system_status():
    """Example of checking system status."""
    print("\n=== System Status Example ===\n")
    
    # Get API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("Error: GROQ_API_KEY environment variable not set")
        return
    
    # Create app
    app = create_phase4_app(groq_api_key)
    
    # Get system status
    status = app.get_system_status()
    
    print(f"System Status: {status['status']}")
    print(f"Timestamp: {status['timestamp']}")
    
    print("\nComponents:")
    for component, info in status['components'].items():
        comp_status = info.get('status', 'unknown')
        print(f"  • {component}: {comp_status}")
        
        if isinstance(info, dict) and 'restaurants_loaded' in info:
            print(f"    Restaurants: {info['restaurants_loaded']}")
        elif isinstance(info, dict) and 'url' in info:
            print(f"    URL: {info['url']}")


def example_end_to_end_test():
    """Example of running end-to-end test."""
    print("\n=== End-to-End Test Example ===\n")
    
    # Get API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("Error: GROQ_API_KEY environment variable not set")
        return
    
    # Create app
    app = create_phase4_app(groq_api_key)
    
    print("Running end-to-end test...")
    
    # Run test
    success = app.test_end_to_end()
    
    if success:
        print("✅ End-to-end test passed!")
    else:
        print("❌ End-to-end test failed!")
        print("Check the logs for details.")


def run_api_server_example():
    """Example of running the API server."""
    print("\n=== API Server Example ===\n")
    
    # Get API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("Error: GROQ_API_KEY environment variable not set")
        print("Set GROQ_API_KEY environment variable and try again.")
        return
    
    print("Starting API server...")
    print("The server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    
    # Create and run app
    app = create_phase4_app(groq_api_key)
    app.run_api_server(debug=True)


def run_streamlit_example():
    """Example of running the Streamlit app."""
    print("\n=== Streamlit App Example ===\n")
    
    print("Starting Streamlit application...")
    print("The app will be available at: http://localhost:8501")
    print("\nMake sure the API server is running on http://localhost:8000")
    print("Press Ctrl+C to stop the app")
    
    # Import and run Streamlit
    from .presentation_layer import create_streamlit_app
    create_streamlit_app()


def run_cli_example():
    """Example of running CLI interface."""
    print("\n=== CLI Interface Example ===\n")
    
    print("Starting CLI interface...")
    print("You can also use command-line arguments:")
    print("  python -m phase4.main --location Downtown --cuisine Italian")
    print("  python -m phase4.main --status")
    print("\nPress Ctrl+C to exit")
    
    # Import and run CLI
    from .cli_interface import main as cli_main
    cli_main()


def main():
    """Main entry point for Phase 4 examples."""
    parser = argparse.ArgumentParser(
        description="Phase 4 Application Layer Examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m phase4.main api-example      # API usage example
  python -m phase4.main groq-example      # Groq provider example
  python -m phase4.main status            # System status
  python -m phase4.main test              # End-to-end test
  python -m phase4.main api-server        # Run API server
  python -m phase4.main streamlit         # Run Streamlit app
  python -m phase4.main cli               # Run CLI interface
        """
    )
    
    parser.add_argument(
        "command",
        choices=[
            "api-example",
            "groq-example", 
            "status",
            "test",
            "api-server",
            "streamlit",
            "cli"
        ],
        help="Command to run"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Run command
    if args.command == "api-example":
        example_api_usage()
    elif args.command == "groq-example":
        example_groq_provider()
    elif args.command == "status":
        example_system_status()
    elif args.command == "test":
        example_end_to_end_test()
    elif args.command == "api-server":
        run_api_server_example()
    elif args.command == "streamlit":
        run_streamlit_example()
    elif args.command == "cli":
        run_cli_example()
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
