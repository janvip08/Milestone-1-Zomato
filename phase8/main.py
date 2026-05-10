"""
Phase 8: Main Orchestrator
Main entry point for Phase 8 Streamlit Cloud Production Deployment
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any

# Import Phase 8 modules
from streamlit_cloud_deployer import StreamlitCloudDeployer
from cicd_pipeline import CICDPipeline
from production_monitor import ProductionMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase8Orchestrator:
    """Main orchestrator for Phase 8 deployment operations"""
    
    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.github_repo = os.getenv('GITHUB_REPO', 'janvip08/Milestone-1-Zomato')
        self.version = os.getenv('APP_VERSION', '1.0.0')
        
        # Initialize Phase 8 components
        self.deployer = StreamlitCloudDeployer()
        self.pipeline = CICDPipeline()
        self.monitor = ProductionMonitor()
        
    def run_deployment_pipeline(self) -> Dict[str, Any]:
        """Run complete deployment pipeline"""
        logger.info("Starting Phase 8 deployment pipeline...")
        
        results = {
            'pipeline_start': datetime.now().isoformat(),
            'environment': self.environment,
            'version': self.version
        }
        
        try:
            # Step 1: Create CI/CD pipeline
            logger.info("Step 1: Creating CI/CD pipeline...")
            pipeline_result = self.pipeline.create_github_workflow()
            results['cicd_pipeline'] = pipeline_result
            
            # Step 2: Create deployment configurations
            logger.info("Step 2: Creating deployment configurations...")
            config_result = self.deployer.deploy_to_streamlit_cloud()
            results['deployment_config'] = config_result
            
            # Step 3: Setup monitoring
            logger.info("Step 3: Setting up monitoring...")
            monitor_result = self.monitor.generate_monitoring_dashboard()
            results['monitoring_setup'] = monitor_result
            
            # Step 4: Create deployment package
            logger.info("Step 4: Creating deployment package...")
            package_result = self.create_deployment_package()
            results['deployment_package'] = package_result
            
            results['pipeline_status'] = 'success'
            results['completion_time'] = datetime.now().isoformat()
            
            logger.info("Phase 8 deployment pipeline completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Phase 8 deployment pipeline failed: {str(e)}")
            results['pipeline_status'] = 'error'
            results['error'] = str(e)
            results['completion_time'] = datetime.now().isoformat()
            return results
    
    def create_deployment_package(self) -> Dict[str, Any]:
        """Create deployment package with all necessary files"""
        package_files = [
            'streamlit_cloud_deployer.py',
            'cicd_pipeline.py',
            'production_monitor.py',
            'requirements.txt',
            'README.md'
        ]
        
        # Create deployment package directory
        package_dir = 'deployment_package'
        os.makedirs(package_dir, exist_ok=True)
        
        # Copy files to package directory
        import shutil
        for file in package_files:
            if os.path.exists(file):
                shutil.copy2(file, f'{package_dir}/{file}')
        
        # Create package manifest
        manifest = {
            'package_name': 'phase8-streamlit-deployment',
            'version': self.version,
            'environment': self.environment,
            'created_at': datetime.now().isoformat(),
            'files': package_files,
            'dependencies': [
                'python>=3.9',
                'streamlit>=1.28.0',
                'requests>=2.28.0'
            ],
            'deployment_targets': [
                'streamlit_cloud',
                'github_actions',
                'monitoring'
            ]
        }
        
        with open(f'{package_dir}/manifest.json', 'w') as f:
            import json
            json.dump(manifest, f, indent=2)
        
        return {
            'status': 'success',
            'package_directory': package_dir,
            'total_files': len(package_files),
            'manifest_created': True
        }
    
    def run_health_checks(self) -> Dict[str, Any]:
        """Run comprehensive health checks"""
        logger.info("Running Phase 8 health checks...")
        
        health_results = {
            'check_start': datetime.now().isoformat(),
            'environment': self.environment
        }
        
        try:
            # Check Streamlit deployment
            streamlit_health = self.monitor.check_streamlit_health()
            health_results['streamlit_health'] = streamlit_health.__dict__ if hasattr(streamlit_health, '__dict__') else {}
            
            # Check API health
            api_health = self.monitor.check_api_health()
            health_results['api_health'] = api_health.__dict__ if hasattr(api_health, '__dict__') else {}
            
            # Check integration health
            integration_health = self.monitor.check_integration_health()
            health_results['integration_health'] = integration_health
            
            # Overall health status
            all_healthy = (
                streamlit_health.status == 'healthy' and
                api_health.status == 'healthy' and
                integration_health.get('integration_test', {}).get('success', False)
            )
            
            health_results['overall_health'] = {
                'status': 'healthy' if all_healthy else 'degraded',
                'timestamp': datetime.now().isoformat(),
                'components': {
                    'streamlit': streamlit_health.status,
                    'api': api_health.status,
                    'integration': integration_health.get('integration_test', {}).get('success', False)
                }
            }
            
            health_results['health_check_status'] = 'success'
            
        except Exception as e:
            logger.error(f"Health checks failed: {str(e)}")
            health_results['health_check_status'] = 'error'
            health_results['error'] = str(e)
        
        return health_results
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get current deployment status"""
        return {
            'phase': 8,
            'name': 'Streamlit Cloud Production Deployment',
            'environment': self.environment,
            'version': self.version,
            'timestamp': datetime.now().isoformat(),
            'components': {
                'streamlit_cloud_deployer': 'ready',
                'cicd_pipeline': 'ready',
                'production_monitor': 'ready'
            },
            'status': 'ready_for_deployment',
            'next_steps': [
                'Run deployment pipeline: python phase8/main.py deploy',
                'Test deployment: python phase8/main.py health-check',
                'Monitor production: python phase8/main.py monitor'
            ]
        }

def main():
    """Main entry point for Phase 8"""
    orchestrator = Phase8Orchestrator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "deploy":
            result = orchestrator.run_deployment_pipeline()
            print(json.dumps(result, indent=2))
            
        elif command == "health-check":
            result = orchestrator.run_health_checks()
            print(json.dumps(result, indent=2))
            
        elif command == "status":
            result = orchestrator.get_deployment_status()
            print(json.dumps(result, indent=2))
            
        else:
            print("❌ Unknown command")
            print("Available commands: deploy, health-check, status")
    else:
        print("🚀 Phase 8: Streamlit Cloud Production Deployment")
        print("Commands: deploy, health-check, status")
        print("Example: python phase8/main.py deploy")
        
        # Show current status
        status = orchestrator.get_deployment_status()
        print(json.dumps(status, indent=2))

if __name__ == "__main__":
    main()
