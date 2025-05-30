"""
Simulation Engine Orchestrator

This module orchestrates the entire API simulation process including:
- Configuration management and user interaction
- Multi-threaded request execution
- Authentication handling
- Progress monitoring and control
- Real-time status reporting
"""

import json
import yaml
import time
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import requests
from urllib.parse import urljoin
import os

from .swagger_parser import SwaggerParser
from .request_generator import RequestGenerator
from .metrics_collector import MetricsCollector


@dataclass
class SimulationConfig:
    """Configuration for API simulation."""
    simulation_name: str
    api_source: str  # URL or file path to Swagger spec
    environment: str  # dev, staging, production
    target_requests: int
    concurrent_threads: int
    request_delay_ms: int
    auth_config: Dict[str, Any]
    output_directory: str
    include_endpoints: List[str] = None  # Specific endpoints to test
    exclude_endpoints: List[str] = None  # Endpoints to skip
    custom_headers: Dict[str, str] = None


@dataclass
class SimulationStatus:
    """Current simulation status."""
    simulation_id: str
    status: str  # starting, running, paused, completed, failed
    progress_percent: float
    current_requests: int
    target_requests: int
    elapsed_time_seconds: float
    estimated_remaining_seconds: float
    current_rps: float  # requests per second
    error_count: int
    last_error: Optional[str] = None


class ControlFile:
    """Manages simulation control through file-based coordination."""
    
    def __init__(self, simulation_id: str, control_directory: str = "./data/simulations/active"):
        self.simulation_id = simulation_id
        self.control_directory = Path(control_directory)
        self.control_directory.mkdir(parents=True, exist_ok=True)
        self.control_file_path = self.control_directory / f"{simulation_id}_control.json"
        self._lock = threading.Lock()
        
        # Initialize control file
        self._write_control_data({
            'simulation_id': simulation_id,
            'status': 'initializing',
            'created_at': time.time(),
            'updated_at': time.time(),
            'should_stop': False,
            'should_pause': False,
            'current_requests': 0,
            'target_requests': 0,
            'error_count': 0
        })
    
    def _write_control_data(self, data: Dict[str, Any]) -> None:
        """Write control data to file."""
        with self._lock:
            with open(self.control_file_path, 'w') as f:
                json.dump(data, f, indent=2)
    
    def _read_control_data(self) -> Dict[str, Any]:
        """Read control data from file."""
        with self._lock:
            if self.control_file_path.exists():
                with open(self.control_file_path, 'r') as f:
                    return json.load(f)
            return {}
    
    def update_status(self, status: str, **kwargs) -> None:
        """Update simulation status."""
        data = self._read_control_data()
        data['status'] = status
        data['updated_at'] = time.time()
        data.update(kwargs)
        self._write_control_data(data)
    
    def update_progress(self, current_requests: int, error_count: int = None) -> None:
        """Update simulation progress."""
        data = self._read_control_data()
        data['current_requests'] = current_requests
        data['updated_at'] = time.time()
        if error_count is not None:
            data['error_count'] = error_count
        self._write_control_data(data)
    
    def should_stop(self) -> bool:
        """Check if simulation should stop."""
        data = self._read_control_data()
        return data.get('should_stop', False)
    
    def should_pause(self) -> bool:
        """Check if simulation should pause."""
        data = self._read_control_data()
        return data.get('should_pause', False)
    
    def request_stop(self) -> None:
        """Request simulation to stop."""
        data = self._read_control_data()
        data['should_stop'] = True
        data['updated_at'] = time.time()
        self._write_control_data(data)
    
    def request_pause(self) -> None:
        """Request simulation to pause."""
        data = self._read_control_data()
        data['should_pause'] = True
        data['updated_at'] = time.time()
        self._write_control_data(data)
    
    def resume(self) -> None:
        """Resume paused simulation."""
        data = self._read_control_data()
        data['should_pause'] = False
        data['updated_at'] = time.time()
        self._write_control_data(data)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status from control file."""
        return self._read_control_data()
    
    def cleanup(self) -> None:
        """Clean up control file."""
        if self.control_file_path.exists():
            self.control_file_path.unlink()


class AuthenticationHandler:
    """Handles various authentication schemes."""
    
    def __init__(self, auth_config: Dict[str, Any]):
        self.auth_config = auth_config
        self.auth_type = auth_config.get('type', 'none')
        self._token_cache = {}
        
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for requests."""
        if self.auth_type == 'bearer':
            token = self._get_bearer_token()
            if token:
                return {'Authorization': f'Bearer {token}'}
        elif self.auth_type == 'api_key':
            api_key = self.auth_config.get('api_key')
            header_name = self.auth_config.get('header_name', 'X-API-Key')
            if api_key:
                return {header_name: api_key}
        elif self.auth_type == 'basic':
            # Basic auth would be handled by requests.auth
            pass
        
        return {}
    
    def _get_bearer_token(self) -> Optional[str]:
        """Get or refresh bearer token."""
        # Check if we have a cached valid token
        cached_token = self._token_cache.get('access_token')
        expires_at = self._token_cache.get('expires_at', 0)
        
        if cached_token and time.time() < expires_at:
            return cached_token
        
        # Get new token
        token_url = self.auth_config.get('token_url')
        client_id = self.auth_config.get('client_id')
        client_secret = self.auth_config.get('client_secret')
        
        if not all([token_url, client_id, client_secret]):
            return self.auth_config.get('static_token')  # Fallback to static token
        
        try:
            response = requests.post(token_url, data={
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret
            })
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)
            
            if access_token:
                self._token_cache = {
                    'access_token': access_token,
                    'expires_at': time.time() + expires_in - 60  # Refresh 1 minute early
                }
                return access_token
                
        except Exception as e:
            print(f"Error getting bearer token: {e}")
        
        return None


class SimulationEngine:
    """Main simulation engine that orchestrates the entire process."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.simulation_id = str(uuid.uuid4())
        self.swagger_parser = SwaggerParser()
        self.request_generator = RequestGenerator()
        self.metrics_collector = MetricsCollector(self.simulation_id, config.output_directory)
        self.control_file = ControlFile(self.simulation_id)
        self.auth_handler = AuthenticationHandler(config.auth_config)
        
        self.status_callbacks: List[Callable[[SimulationStatus], None]] = []
        self.start_time = None
        self.is_running = False
        
    def add_status_callback(self, callback: Callable[[SimulationStatus], None]) -> None:
        """Add callback for status updates."""
        self.status_callbacks.append(callback)
    
    def _notify_status_change(self, status: SimulationStatus) -> None:
        """Notify all registered callbacks of status change."""
        for callback in self.status_callbacks:
            try:
                callback(status)
            except Exception as e:
                print(f"Error in status callback: {e}")
    
    def initialize(self) -> bool:
        """Initialize the simulation by loading and parsing the API specification."""
        try:
            self.control_file.update_status('loading_specification')
            
            # Load Swagger specification
            if not self.swagger_parser.load_specification(self.config.api_source):
                raise Exception(f"Failed to load API specification from {self.config.api_source}")
            
            self.control_file.update_status('analyzing_endpoints')
            
            # Filter endpoints if specified
            endpoints = self.swagger_parser.get_endpoints()
            if self.config.include_endpoints:
                endpoints = [ep for ep in endpoints if any(inc in ep['path'] for inc in self.config.include_endpoints)]
            if self.config.exclude_endpoints:
                endpoints = [ep for ep in endpoints if not any(exc in ep['path'] for exc in self.config.exclude_endpoints)]
            
            if not endpoints:
                raise Exception("No endpoints available for simulation after filtering")
            
            self.filtered_endpoints = endpoints
            self.control_file.update_status('ready', target_requests=self.config.target_requests)
            
            return True
            
        except Exception as e:
            self.control_file.update_status('failed', error_message=str(e))
            return False
    
    def start_simulation(self) -> bool:
        """Start the API simulation."""
        if not hasattr(self, 'filtered_endpoints'):
            if not self.initialize():
                return False
        
        try:
            self.start_time = time.time()
            self.is_running = True
            self.control_file.update_status('running')
            
            # Create thread pool for concurrent requests
            with ThreadPoolExecutor(max_workers=self.config.concurrent_threads) as executor:
                # Submit all requests
                future_to_request = {}
                
                for i in range(self.config.target_requests):
                    if self.control_file.should_stop():
                        break
                    
                    # Select random endpoint
                    import random
                    endpoint = random.choice(self.filtered_endpoints)
                    
                    # Submit request to thread pool
                    future = executor.submit(self._execute_single_request, endpoint, i)
                    future_to_request[future] = i
                    
                    # Add delay between request submissions if configured
                    if self.config.request_delay_ms > 0:
                        time.sleep(self.config.request_delay_ms / 1000.0)
                
                # Wait for all requests to complete
                completed_requests = 0
                error_count = 0
                
                for future in as_completed(future_to_request):
                    if self.control_file.should_stop():
                        # Cancel remaining futures
                        for remaining_future in future_to_request:
                            if not remaining_future.done():
                                remaining_future.cancel()
                        break
                    
                    # Check for pause
                    while self.control_file.should_pause() and not self.control_file.should_stop():
                        time.sleep(1)
                    
                    try:
                        result = future.result()
                        if not result:
                            error_count += 1
                    except Exception as e:
                        error_count += 1
                        print(f"Request execution error: {e}")
                    
                    completed_requests += 1
                    
                    # Update progress
                    self.control_file.update_progress(completed_requests, error_count)
                    
                    # Update status callback
                    self._update_status_callback(completed_requests, error_count)
            
            # Finalize simulation
            self.is_running = False
            final_status = 'completed' if not self.control_file.should_stop() else 'stopped'
            self.control_file.update_status(final_status)
            
            return True
            
        except Exception as e:
            self.is_running = False
            self.control_file.update_status('failed', error_message=str(e))
            return False
    
    def _execute_single_request(self, endpoint: Dict[str, Any], request_number: int) -> bool:
        """Execute a single API request."""
        request_start_time = time.time()
        request_id = f"{self.simulation_id}_{request_number}"
        
        try:
            # Generate request data
            request_data = self.request_generator.generate_request_data(endpoint)
            
            # Build URL
            base_url = self.swagger_parser.get_base_url()
            path = endpoint['path']
            
            # Replace path parameters
            for param_name, param_value in request_data['path_params'].items():
                path = path.replace(f"{{{param_name}}}", str(param_value))
            
            url = urljoin(base_url, path.lstrip('/'))
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': f'FakeSphere-Simulator/{self.simulation_id}'
            }
            headers.update(self.auth_handler.get_auth_headers())
            headers.update(request_data['headers'])
            if self.config.custom_headers:
                headers.update(self.config.custom_headers)
            
            # Calculate request size
            request_body = json.dumps(request_data['body']) if request_data['body'] else None
            request_size = len(request_body.encode('utf-8')) if request_body else 0
            
            # Make HTTP request
            response = requests.request(
                method=endpoint['method'],
                url=url,
                params=request_data['query_params'],
                data=request_body,
                headers=headers,
                timeout=30
            )
            
            request_end_time = time.time()
            
            # Calculate response size
            response_size = len(response.content) if response.content else 0
            
            # Record metrics
            self.metrics_collector.record_request(
                endpoint_path=endpoint['path'],
                http_method=endpoint['method'],
                target_host=requests.utils.urlparse(base_url).hostname,
                target_port=requests.utils.urlparse(base_url).port or (443 if base_url.startswith('https') else 80),
                request_url=url,
                request_size_bytes=request_size,
                request_start_time=request_start_time,
                request_end_time=request_end_time,
                status_code=response.status_code,
                response_size_bytes=response_size,
                response_message=response.reason,
                auth_type=self.auth_handler.auth_type,
                request_id=request_id
            )
            
            return True
            
        except Exception as e:
            request_end_time = time.time()
            
            # Record error metrics
            self.metrics_collector.record_request(
                endpoint_path=endpoint['path'],
                http_method=endpoint['method'],
                target_host="unknown",
                target_port=0,
                request_url=url if 'url' in locals() else "unknown",
                request_size_bytes=0,
                request_start_time=request_start_time,
                request_end_time=request_end_time,
                status_code=0,
                response_size_bytes=0,
                response_message="Request failed",
                error_message=str(e),
                auth_type=self.auth_handler.auth_type,
                request_id=request_id
            )
            
            return False
    
    def _update_status_callback(self, completed_requests: int, error_count: int) -> None:
        """Update status and notify callbacks."""
        if not self.start_time:
            return
        
        elapsed_time = time.time() - self.start_time
        progress_percent = (completed_requests / self.config.target_requests) * 100
        
        remaining_requests = self.config.target_requests - completed_requests
        current_rps = completed_requests / elapsed_time if elapsed_time > 0 else 0
        estimated_remaining_seconds = remaining_requests / current_rps if current_rps > 0 else 0
        
        status = SimulationStatus(
            simulation_id=self.simulation_id,
            status='running',
            progress_percent=round(progress_percent, 2),
            current_requests=completed_requests,
            target_requests=self.config.target_requests,
            elapsed_time_seconds=round(elapsed_time, 2),
            estimated_remaining_seconds=round(estimated_remaining_seconds, 2),
            current_rps=round(current_rps, 2),
            error_count=error_count
        )
        
        self._notify_status_change(status)
    
    def get_current_status(self) -> SimulationStatus:
        """Get current simulation status."""
        control_data = self.control_file.get_status()
        
        if not self.start_time:
            elapsed_time = 0
            current_rps = 0
            estimated_remaining = 0
        else:
            elapsed_time = time.time() - self.start_time
            completed_requests = control_data.get('current_requests', 0)
            current_rps = completed_requests / elapsed_time if elapsed_time > 0 else 0
            remaining_requests = self.config.target_requests - completed_requests
            estimated_remaining = remaining_requests / current_rps if current_rps > 0 else 0
        
        progress_percent = (control_data.get('current_requests', 0) / self.config.target_requests) * 100
        
        return SimulationStatus(
            simulation_id=self.simulation_id,
            status=control_data.get('status', 'unknown'),
            progress_percent=round(progress_percent, 2),
            current_requests=control_data.get('current_requests', 0),
            target_requests=self.config.target_requests,
            elapsed_time_seconds=round(elapsed_time, 2),
            estimated_remaining_seconds=round(estimated_remaining, 2),
            current_rps=round(current_rps, 2),
            error_count=control_data.get('error_count', 0)
        )
    
    def stop_simulation(self) -> None:
        """Request simulation to stop."""
        self.control_file.request_stop()
    
    def pause_simulation(self) -> None:
        """Request simulation to pause."""
        self.control_file.request_pause()
    
    def resume_simulation(self) -> None:
        """Resume paused simulation."""
        self.control_file.resume()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        return self.metrics_collector.get_current_statistics()
    
    def export_results(self) -> str:
        """Export simulation results to file."""
        return self.metrics_collector.export_metrics()
    
    def cleanup(self) -> None:
        """Clean up simulation resources."""
        self.control_file.cleanup()
    
    @classmethod
    def create_from_interactive_config(cls) -> 'SimulationEngine':
        """Create simulation engine through interactive configuration."""
        print("🔥 Fake Sphere API Simulation Configuration")
        print("=" * 50)
        
        # Collect basic configuration
        simulation_name = input("Simulation name: ").strip()
        api_source = input("Swagger/OpenAPI URL or file path: ").strip()
        environment = input("Environment (dev/staging/production) [dev]: ").strip() or "dev"
        target_requests = int(input("Number of requests to generate [100]: ") or "100")
        concurrent_threads = int(input("Concurrent threads [5]: ") or "5")
        request_delay_ms = int(input("Delay between requests (ms) [0]: ") or "0")
        
        # Authentication configuration
        print("\nAuthentication Configuration:")
        auth_type = input("Auth type (none/bearer/api_key/basic) [none]: ").strip() or "none"
        
        auth_config = {'type': auth_type}
        if auth_type == 'bearer':
            token_url = input("Token URL (or leave empty for static token): ").strip()
            if token_url:
                auth_config.update({
                    'token_url': token_url,
                    'client_id': input("Client ID: ").strip(),
                    'client_secret': input("Client Secret: ").strip()
                })
            else:
                auth_config['static_token'] = input("Static Bearer Token: ").strip()
        elif auth_type == 'api_key':
            auth_config.update({
                'api_key': input("API Key: ").strip(),
                'header_name': input("Header name [X-API-Key]: ").strip() or "X-API-Key"
            })
        
        # Output configuration
        output_directory = input("Output directory [./data/metrics]: ").strip() or "./data/metrics"
        
        config = SimulationConfig(
            simulation_name=simulation_name,
            api_source=api_source,
            environment=environment,
            target_requests=target_requests,
            concurrent_threads=concurrent_threads,
            request_delay_ms=request_delay_ms,
            auth_config=auth_config,
            output_directory=output_directory
        )
        
        return cls(config)