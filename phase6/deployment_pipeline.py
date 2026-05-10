"""Deployment Pipeline: CI/CD configuration and environment management."""

from typing import Dict, Any, List, Optional, Union
import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import shutil
import platform


class Environment(Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class DeploymentStatus(Enum):
    """Deployment status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class DeploymentConfig:
    """Deployment configuration."""
    environment: Environment
    app_name: str
    version: str
    git_branch: str
    git_commit: str
    build_number: Optional[str]
    deploy_timestamp: datetime
    config_vars: Dict[str, Any]
    health_check_url: str
    rollback_enabled: bool
    auto_rollback: bool
    max_retries: int
    timeout_seconds: int


@dataclass
class DeploymentStep:
    """Individual deployment step."""
    step_id: str
    name: str
    command: str
    working_dir: str
    timeout_seconds: int
    retry_count: int
    max_retries: int
    status: DeploymentStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    output: str
    error: Optional[str]


class EnvironmentManager:
    """Manages different environment configurations."""
    
    def __init__(self, base_path: str = "c:\\Users\\Abhishek kapoor\\Milestone 1"):
        """
        Initialize environment manager.
        
        Args:
            base_path: Base path for the project
        """
        self.base_path = Path(base_path)
        self.environments = {}
        self.current_environment = None
        
        # Load environment configurations
        self._load_environments()
    
    def _load_environments(self) -> None:
        """Load environment configurations."""
        # Default environment configurations
        self.environments = {
            Environment.DEVELOPMENT: {
                "name": "development",
                "debug": True,
                "log_level": "DEBUG",
                "api_host": "localhost",
                "api_port": 8000,
                "streamlit_host": "localhost",
                "streamlit_port": 8501,
                "database_url": "sqlite:///dev.db",
                "cache_backend": "memory",
                "rate_limiting": {
                    "enabled": False,
                    "per_ip": {"requests": 1000, "window": 60}
                },
                "monitoring": {
                    "enabled": True,
                    "metrics_retention": 24
                }
            },
            Environment.STAGING: {
                "name": "staging",
                "debug": False,
                "log_level": "INFO",
                "api_host": "0.0.0.0",
                "api_port": 8000,
                "streamlit_host": "0.0.0.0",
                "streamlit_port": 8501,
                "database_url": "sqlite:///staging.db",
                "cache_backend": "sqlite",
                "rate_limiting": {
                    "enabled": True,
                    "per_ip": {"requests": 200, "window": 60}
                },
                "monitoring": {
                    "enabled": True,
                    "metrics_retention": 168  # 7 days
                }
            },
            Environment.PRODUCTION: {
                "name": "production",
                "debug": False,
                "log_level": "WARNING",
                "api_host": "0.0.0.0",
                "api_port": 8000,
                "streamlit_host": "0.0.0.0",
                "streamlit_port": 8501,
                "database_url": os.getenv("DATABASE_URL", "sqlite:///prod.db"),
                "cache_backend": "redis",
                "redis_host": os.getenv("REDIS_HOST", "localhost"),
                "redis_port": int(os.getenv("REDIS_PORT", 6379)),
                "rate_limiting": {
                    "enabled": True,
                    "per_ip": {"requests": 100, "window": 60},
                    "per_user": {"requests": 50, "window": 60}
                },
                "monitoring": {
                    "enabled": True,
                    "metrics_retention": 720  # 30 days
                }
            },
            Environment.TESTING: {
                "name": "testing",
                "debug": True,
                "log_level": "DEBUG",
                "api_host": "localhost",
                "api_port": 8001,
                "streamlit_host": "localhost",
                "streamlit_port": 8502,
                "database_url": "sqlite:///test.db",
                "cache_backend": "memory",
                "rate_limiting": {
                    "enabled": False
                },
                "monitoring": {
                    "enabled": False
                }
            }
        }
    
    def get_environment_config(self, env: Environment) -> Dict[str, Any]:
        """
        Get configuration for specific environment.
        
        Args:
            env: Environment
            
        Returns:
            Environment configuration
        """
        return self.environments.get(env, {})
    
    def set_environment(self, env: Environment) -> None:
        """
        Set current environment.
        
        Args:
            env: Environment to set
        """
        self.current_environment = env
        
        # Set environment variables
        config = self.get_environment_config(env)
        for key, value in config.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    env_var = f"{key.upper()}_{sub_key.upper()}"
                    os.environ[env_var] = str(sub_value)
            else:
                env_var = key.upper()
                os.environ[env_var] = str(value)
    
    def create_env_file(self, env: Environment, output_path: Optional[str] = None) -> str:
        """
        Create .env file for environment.
        
        Args:
            env: Environment
            output_path: Output path for .env file
            
        Returns:
            Path to created .env file
        """
        config = self.get_environment_config(env)
        
        if output_path is None:
            output_path = self.base_path / f".env.{env.value}"
        else:
            output_path = Path(output_path)
        
        # Flatten nested config
        flat_config = {}
        for key, value in config.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat_config[f"{key}_{sub_key}"] = sub_value
            else:
                flat_config[key] = value
        
        # Write .env file
        with open(output_path, 'w') as f:
            for key, value in flat_config.items():
                f.write(f"{key.upper()}={value}\n")
        
        return str(output_path)
    
    def validate_environment(self, env: Environment) -> tuple[bool, List[str]]:
        """
        Validate environment configuration.
        
        Args:
            env: Environment to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        config = self.get_environment_config(env)
        errors = []
        
        # Check required fields
        required_fields = ["name", "api_host", "api_port", "streamlit_port"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Check port conflicts
        api_port = config.get("api_port")
        streamlit_port = config.get("streamlit_port")
        if api_port == streamlit_port:
            errors.append("API and Streamlit ports cannot be the same")
        
        # Check port ranges
        for port_field in ["api_port", "streamlit_port"]:
            port = config.get(port_field)
            if port and (port < 1024 or port > 65535):
                errors.append(f"{port_field} must be between 1024 and 65535")
        
        # Check database URL for production
        if env == Environment.PRODUCTION:
            db_url = config.get("database_url", "")
            if "sqlite:///" in db_url:
                errors.append("Production should not use SQLite database")
        
        return len(errors) == 0, errors


class DeploymentPipeline:
    """CI/CD deployment pipeline."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize deployment pipeline.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config or self._get_default_config()
        self.environment_manager = EnvironmentManager()
        self.deployment_history = []
        self.current_deployment = None
        
        # Create deployment directories
        self._create_directories()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default pipeline configuration."""
        return {
            "base_path": str(Path.cwd()),
            "git_repo": "https://github.com/your-repo/restaurant-recommendation.git",
            "docker_registry": "your-registry.com",
            "app_name": "restaurant-recommendation",
            "health_check_timeout": 30,
            "rollback_timeout": 60,
            "max_retries": 3,
            "environments": ["development", "staging", "production"],
            "steps": {
                "pre_deploy": [
                    {"name": "Validate Environment", "command": "python -m phase6.deployment_pipeline validate_env"},
                    {"name": "Run Tests", "command": "python -m pytest tests/"},
                    {"name": "Security Scan", "command": "python -m phase6.security_middleware scan"}
                ],
                "deploy": [
                    {"name": "Build Application", "command": "python -m phase6.deployment_pipeline build"},
                    {"name": "Deploy Services", "command": "python -m phase6.deployment_pipeline deploy_services"},
                    {"name": "Health Check", "command": "python -m phase6.deployment_pipeline health_check"}
                ],
                "post_deploy": [
                    {"name": "Run Smoke Tests", "command": "python -m phase6.deployment_pipeline smoke_test"},
                    {"name": "Update Monitoring", "command": "python -m phase6.deployment_pipeline update_monitoring"}
                ]
            }
        }
    
    def _create_directories(self) -> None:
        """Create necessary directories."""
        directories = [
            "logs",
            "deployments",
            "backups",
            "configs",
            "scripts"
        ]
        
        for directory in directories:
            Path(self.config["base_path"]) / directory.mkdir(exist_ok=True)
    
    def get_git_info(self) -> Dict[str, str]:
        """Get git repository information."""
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, cwd=self.config["base_path"]
            )
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            
            # Get current commit
            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, cwd=self.config["base_path"]
            )
            commit = commit_result.stdout.strip() if commit_result.returncode == 0 else "unknown"
            
            # Get commit message
            message_result = subprocess.run(
                ["git", "log", "-1", "--pretty=%s"],
                capture_output=True, text=True, cwd=self.config["base_path"]
            )
            message = message_result.stdout.strip() if message_result.returncode == 0 else "unknown"
            
            return {
                "branch": branch,
                "commit": commit,
                "message": message
            }
            
        except Exception:
            return {
                "branch": "unknown",
                "commit": "unknown", 
                "message": "unknown"
            }
    
    def create_deployment_config(
        self,
        environment: Environment,
        version: Optional[str] = None
    ) -> DeploymentConfig:
        """
        Create deployment configuration.
        
        Args:
            environment: Target environment
            version: Version to deploy
            
        Returns:
            Deployment configuration
        """
        git_info = self.get_git_info()
        env_config = self.environment_manager.get_environment_config(environment)
        
        return DeploymentConfig(
            environment=environment,
            app_name=self.config["app_name"],
            version=version or git_info["commit"][:8],
            git_branch=git_info["branch"],
            git_commit=git_info["commit"],
            build_number=None,  # Would come from CI/CD system
            deploy_timestamp=datetime.now(),
            config_vars=env_config,
            health_check_url=f"http://{env_config['api_host']}:{env_config['api_port']}/health",
            rollback_enabled=True,
            auto_rollback=environment != Environment.DEVELOPMENT,
            max_retries=self.config["max_retries"],
            timeout_seconds=self.config["health_check_timeout"]
        )
    
    def run_deployment_step(self, step: DeploymentStep) -> DeploymentStep:
        """
        Run a single deployment step.
        
        Args:
            step: Deployment step to run
            
        Returns:
            Updated step with results
        """
        step.status = DeploymentStatus.RUNNING
        step.start_time = datetime.now()
        
        try:
            # Run the command
            result = subprocess.run(
                step.command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=step.working_dir,
                timeout=step.timeout_seconds
            )
            
            step.end_time = datetime.now()
            step.output = result.stdout
            
            if result.returncode == 0:
                step.status = DeploymentStatus.SUCCESS
            else:
                step.status = DeploymentStatus.FAILED
                step.error = result.stderr
            
        except subprocess.TimeoutExpired:
            step.status = DeploymentStatus.FAILED
            step.error = f"Command timed out after {step.timeout_seconds} seconds"
            step.end_time = datetime.now()
        
        except Exception as e:
            step.status = DeploymentStatus.FAILED
            step.error = str(e)
            step.end_time = datetime.now()
        
        return step
    
    def execute_deployment(self, deployment_config: DeploymentConfig) -> DeploymentConfig:
        """
        Execute deployment pipeline.
        
        Args:
            deployment_config: Deployment configuration
            
        Returns:
            Updated deployment configuration
        """
        self.current_deployment = deployment_config
        deployment_config.steps = []
        
        # Set environment
        self.environment_manager.set_environment(deployment_config.environment)
        
        # Run pre-deployment steps
        for step_config in self.config["steps"]["pre_deploy"]:
            step = DeploymentStep(
                step_id=f"pre_{step_config['name'].replace(' ', '_')}",
                name=step_config["name"],
                command=step_config["command"],
                working_dir=self.config["base_path"],
                timeout_seconds=300,
                retry_count=0,
                max_retries=deployment_config.max_retries,
                status=DeploymentStatus.PENDING,
                start_time=None,
                end_time=None,
                output="",
                error=None
            )
            
            # Run step with retries
            for attempt in range(step.max_retries + 1):
                step = self.run_deployment_step(step)
                if step.status == DeploymentStatus.SUCCESS:
                    break
                elif attempt < step.max_retries:
                    step.retry_count += 1
                    step.status = DeploymentStatus.PENDING
            
            deployment_config.steps.append(step)
            
            # Fail fast if pre-deployment step fails
            if step.status == DeploymentStatus.FAILED:
                deployment_config.status = DeploymentStatus.FAILED
                return deployment_config
        
        # Run deployment steps
        deployment_config.status = DeploymentStatus.RUNNING
        for step_config in self.config["steps"]["deploy"]:
            step = DeploymentStep(
                step_id=f"deploy_{step_config['name'].replace(' ', '_')}",
                name=step_config["name"],
                command=step_config["command"],
                working_dir=self.config["base_path"],
                timeout_seconds=deployment_config.timeout_seconds,
                retry_count=0,
                max_retries=deployment_config.max_retries,
                status=DeploymentStatus.PENDING,
                start_time=None,
                end_time=None,
                output="",
                error=None
            )
            
            # Run step with retries
            for attempt in range(step.max_retries + 1):
                step = self.run_deployment_step(step)
                if step.status == DeploymentStatus.SUCCESS:
                    break
                elif attempt < step.max_retries:
                    step.retry_count += 1
                    step.status = DeploymentStatus.PENDING
            
            deployment_config.steps.append(step)
            
            # Fail if deployment step fails
            if step.status == DeploymentStatus.FAILED:
                deployment_config.status = DeploymentStatus.FAILED
                if deployment_config.auto_rollback:
                    self.rollback_deployment(deployment_config)
                return deployment_config
        
        # Run post-deployment steps
        for step_config in self.config["steps"]["post_deploy"]:
            step = DeploymentStep(
                step_id=f"post_{step_config['name'].replace(' ', '_')}",
                name=step_config["name"],
                command=step_config["command"],
                working_dir=self.config["base_path"],
                timeout_seconds=300,
                retry_count=0,
                max_retries=deployment_config.max_retries,
                status=DeploymentStatus.PENDING,
                start_time=None,
                end_time=None,
                output="",
                error=None
            )
            
            # Run step with retries
            for attempt in range(step.max_retries + 1):
                step = self.run_deployment_step(step)
                if step.status == DeploymentStatus.SUCCESS:
                    break
                elif attempt < step.max_retries:
                    step.retry_count += 1
                    step.status = DeploymentStatus.PENDING
            
            deployment_config.steps.append(step)
        
        # Check final status
        failed_steps = [step for step in deployment_config.steps if step.status == DeploymentStatus.FAILED]
        if failed_steps:
            deployment_config.status = DeploymentStatus.FAILED
        else:
            deployment_config.status = DeploymentStatus.SUCCESS
        
        # Save to history
        self.deployment_history.append(deployment_config)
        
        return deployment_config
    
    def rollback_deployment(self, deployment_config: DeploymentConfig) -> bool:
        """
        Rollback deployment.
        
        Args:
            deployment_config: Deployment to rollback
            
        Returns:
            True if rollback successful
        """
        if not deployment_config.rollback_enabled:
            return False
        
        try:
            # Find previous successful deployment
            previous_deployments = [
                d for d in self.deployment_history[:-1]
                if d.environment == deployment_config.environment and d.status == DeploymentStatus.SUCCESS
            ]
            
            if not previous_deployments:
                return False
            
            previous_deployment = previous_deployments[-1]
            
            # Rollback logic would go here
            # For now, just log the rollback
            print(f"Rolling back to version: {previous_deployment.version}")
            
            # Update status
            deployment_config.status = DeploymentStatus.ROLLED_BACK
            
            return True
            
        except Exception:
            return False
    
    def validate_environment(self, environment: Environment) -> tuple[bool, List[str]]:
        """
        Validate environment setup.
        
        Args:
            environment: Environment to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        return self.environment_manager.validate_environment(environment)
    
    def build_application(self) -> bool:
        """
        Build application for deployment.
        
        Returns:
            True if build successful
        """
        try:
            # Install dependencies
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                capture_output=True, cwd=self.config["base_path"]
            )
            
            # Run tests
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-v"],
                capture_output=True, cwd=self.config["base_path"]
            )
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def deploy_services(self) -> bool:
        """
        Deploy application services.
        
        Returns:
            True if deployment successful
        """
        try:
            # This would contain the actual deployment logic
            # For now, just simulate deployment
            print("Deploying services...")
            
            # Start API server
            print("Starting API server...")
            
            # Start Streamlit app
            print("Starting Streamlit app...")
            
            return True
            
        except Exception:
            return False
    
    def health_check(self, url: str, timeout: int = 30) -> bool:
        """
        Perform health check.
        
        Args:
            url: Health check URL
            timeout: Timeout in seconds
            
        Returns:
            True if healthy
        """
        try:
            import requests
            
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def smoke_test(self) -> bool:
        """
        Run smoke tests.
        
        Returns:
            True if all tests pass
        """
        try:
            # Test API health
            api_healthy = self.health_check("http://localhost:8000/health")
            
            # Test basic recommendation
            import requests
            
            test_payload = {
                "preferences": {
                    "location": "Downtown",
                    "cuisine": "Italian",
                    "max_cost_for_two": 1000
                }
            }
            
            response = requests.post(
                "http://localhost:8000/recommend",
                json=test_payload,
                timeout=10
            )
            
            api_working = api_healthy and response.status_code == 200
            
            return api_working
            
        except Exception:
            return False
    
    def get_deployment_status(self, environment: Environment) -> Dict[str, Any]:
        """
        Get deployment status for environment.
        
        Args:
            environment: Environment to check
            
        Returns:
            Deployment status
        """
        env_deployments = [
            d for d in self.deployment_history
            if d.environment == environment
        ]
        
        if not env_deployments:
            return {"status": "no_deployments", "environment": environment.value}
        
        latest_deployment = env_deployments[-1]
        
        return {
            "environment": environment.value,
            "status": latest_deployment.status.value,
            "version": latest_deployment.version,
            "deploy_timestamp": latest_deployment.deploy_timestamp.isoformat(),
            "steps": [
                {
                    "name": step.name,
                    "status": step.status.value,
                    "retry_count": step.retry_count,
                    "duration": (step.end_time - step.start_time).total_seconds() if step.start_time and step.end_time else None
                }
                for step in latest_deployment.steps
            ]
        }
    
    def create_deployment_script(self, environment: Environment) -> str:
        """
        Create deployment script for environment.
        
        Args:
            environment: Target environment
            
        Returns:
            Deployment script content
        """
        script_content = f"""#!/bin/bash
# Deployment script for {environment.value} environment

set -e

echo "Starting deployment to {environment.value}..."

# Set environment
export ENVIRONMENT={environment.value}

# Validate environment
python -m phase6.deployment_pipeline validate_env

# Run tests
python -m pytest tests/ -v

# Deploy services
python -m phase6.deployment_pipeline deploy_services

# Health check
python -m phase6.deployment_pipeline health_check

# Run smoke tests
python -m phase6.deployment_pipeline smoke_test

echo "Deployment to {environment.value} completed successfully!"
"""
        
        return script_content


# Global instances
environment_manager = EnvironmentManager()
deployment_pipeline = DeploymentPipeline()
