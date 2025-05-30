"""
Metrics Collector for API Response Tracking

This module collects and manages comprehensive metrics during API simulation including:
- Request/response timing data
- HTTP status codes and response analysis
- Error tracking and categorization
- Performance statistics
- Real-time metrics aggregation
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from threading import Lock
import os


@dataclass
class RequestMetric:
    """Individual request metric data."""
    timestamp: str
    simulation_id: str
    endpoint_path: str
    http_method: str
    target_host: str
    target_port: int
    request_url: str
    request_size_bytes: int
    request_start_time: float
    request_end_time: float
    response_time_ms: float
    status_code: int
    response_size_bytes: int
    response_message: str
    error_message: Optional[str] = None
    auth_type: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class SimulationSummary:
    """Summary statistics for a simulation."""
    simulation_id: str
    start_time: str
    end_time: Optional[str]
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    requests_per_second: float
    error_rate_percent: float
    status_code_distribution: Dict[int, int]
    endpoint_statistics: Dict[str, Dict[str, Any]]


class MetricsCollector:
    """Collects and manages API simulation metrics."""
    
    def __init__(self, simulation_id: str, output_directory: str = None):
        self.simulation_id = simulation_id
        self.output_directory = output_directory or "./data/metrics"
        self.metrics: List[RequestMetric] = []
        self.lock = Lock()
        self.simulation_start_time = time.time()
        self.simulation_end_time: Optional[float] = None
        
        # Ensure output directory exists
        os.makedirs(self.output_directory, exist_ok=True)
    
    def record_request(self, 
                      endpoint_path: str,
                      http_method: str,
                      target_host: str,
                      target_port: int,
                      request_url: str,
                      request_size_bytes: int,
                      request_start_time: float,
                      request_end_time: float,
                      status_code: int,
                      response_size_bytes: int,
                      response_message: str,
                      error_message: Optional[str] = None,
                      auth_type: Optional[str] = None,
                      request_id: Optional[str] = None) -> None:
        """
        Record metrics for a single API request.
        
        Args:
            endpoint_path: The API endpoint path
            http_method: HTTP method (GET, POST, etc.)
            target_host: Target server hostname
            target_port: Target server port
            request_url: Full request URL
            request_size_bytes: Size of request payload
            request_start_time: Request start timestamp
            request_end_time: Request completion timestamp
            status_code: HTTP response status code
            response_size_bytes: Size of response payload
            response_message: Response status message
            error_message: Error message if request failed
            auth_type: Authentication type used
            request_id: Unique request identifier
        """
        response_time_ms = (request_end_time - request_start_time) * 1000
        
        metric = RequestMetric(
            timestamp=datetime.fromtimestamp(request_start_time, timezone.utc).isoformat(),
            simulation_id=self.simulation_id,
            endpoint_path=endpoint_path,
            http_method=http_method,
            target_host=target_host,
            target_port=target_port,
            request_url=request_url,
            request_size_bytes=request_size_bytes,
            request_start_time=request_start_time,
            request_end_time=request_end_time,
            response_time_ms=response_time_ms,
            status_code=status_code,
            response_size_bytes=response_size_bytes,
            response_message=response_message,
            error_message=error_message,
            auth_type=auth_type,
            request_id=request_id
        )
        
        with self.lock:
            self.metrics.append(metric)
    
    def get_current_statistics(self) -> Dict[str, Any]:
        """Get real-time statistics for current simulation."""
        with self.lock:
            if not self.metrics:
                return {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'avg_response_time_ms': 0,
                    'requests_per_second': 0,
                    'error_rate_percent': 0
                }
            
            total_requests = len(self.metrics)
            successful_requests = len([m for m in self.metrics if 200 <= m.status_code < 300])
            failed_requests = total_requests - successful_requests
            
            response_times = [m.response_time_ms for m in self.metrics]
            avg_response_time = sum(response_times) / len(response_times)
            
            elapsed_time = time.time() - self.simulation_start_time
            requests_per_second = total_requests / elapsed_time if elapsed_time > 0 else 0
            
            error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'avg_response_time_ms': round(avg_response_time, 2),
                'min_response_time_ms': round(min(response_times), 2),
                'max_response_time_ms': round(max(response_times), 2),
                'requests_per_second': round(requests_per_second, 2),
                'error_rate_percent': round(error_rate, 2),
                'elapsed_time_seconds': round(elapsed_time, 2)
            }
    
    def get_status_code_distribution(self) -> Dict[int, int]:
        """Get distribution of HTTP status codes."""
        with self.lock:
            distribution = {}
            for metric in self.metrics:
                distribution[metric.status_code] = distribution.get(metric.status_code, 0) + 1
            return distribution
    
    def get_endpoint_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get per-endpoint statistics."""
        with self.lock:
            endpoint_stats = {}
            
            for metric in self.metrics:
                endpoint_key = f"{metric.http_method} {metric.endpoint_path}"
                
                if endpoint_key not in endpoint_stats:
                    endpoint_stats[endpoint_key] = {
                        'total_requests': 0,
                        'successful_requests': 0,
                        'failed_requests': 0,
                        'response_times': [],
                        'status_codes': {}
                    }
                
                stats = endpoint_stats[endpoint_key]
                stats['total_requests'] += 1
                stats['response_times'].append(metric.response_time_ms)
                
                if 200 <= metric.status_code < 300:
                    stats['successful_requests'] += 1
                else:
                    stats['failed_requests'] += 1
                
                stats['status_codes'][metric.status_code] = stats['status_codes'].get(metric.status_code, 0) + 1
            
            # Calculate derived statistics
            for endpoint_key, stats in endpoint_stats.items():
                response_times = stats['response_times']
                if response_times:
                    stats['avg_response_time_ms'] = round(sum(response_times) / len(response_times), 2)
                    stats['min_response_time_ms'] = round(min(response_times), 2)
                    stats['max_response_time_ms'] = round(max(response_times), 2)
                else:
                    stats['avg_response_time_ms'] = 0
                    stats['min_response_time_ms'] = 0
                    stats['max_response_time_ms'] = 0
                
                stats['error_rate_percent'] = round(
                    (stats['failed_requests'] / stats['total_requests'] * 100) 
                    if stats['total_requests'] > 0 else 0, 2
                )
                
                # Remove raw response times from output to reduce size
                del stats['response_times']
            
            return endpoint_stats
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """Analyze errors and failure patterns."""
        with self.lock:
            error_analysis = {
                'total_errors': 0,
                'error_by_status_code': {},
                'error_by_endpoint': {},
                'error_messages': {},
                'common_errors': []
            }
            
            for metric in self.metrics:
                if metric.status_code >= 400 or metric.error_message:
                    error_analysis['total_errors'] += 1
                    
                    # Group by status code
                    status_key = str(metric.status_code)
                    error_analysis['error_by_status_code'][status_key] = \
                        error_analysis['error_by_status_code'].get(status_key, 0) + 1
                    
                    # Group by endpoint
                    endpoint_key = f"{metric.http_method} {metric.endpoint_path}"
                    error_analysis['error_by_endpoint'][endpoint_key] = \
                        error_analysis['error_by_endpoint'].get(endpoint_key, 0) + 1
                    
                    # Track error messages
                    if metric.error_message:
                        error_analysis['error_messages'][metric.error_message] = \
                            error_analysis['error_messages'].get(metric.error_message, 0) + 1
            
            # Identify most common errors
            if error_analysis['error_messages']:
                common_errors = sorted(
                    error_analysis['error_messages'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]  # Top 5 most common errors
                error_analysis['common_errors'] = [
                    {'message': msg, 'count': count} for msg, count in common_errors
                ]
            
            return error_analysis
    
    def finish_simulation(self) -> SimulationSummary:
        """Mark simulation as finished and generate final summary."""
        self.simulation_end_time = time.time()
        
        with self.lock:
            if not self.metrics:
                return SimulationSummary(
                    simulation_id=self.simulation_id,
                    start_time=datetime.fromtimestamp(self.simulation_start_time, timezone.utc).isoformat(),
                    end_time=datetime.fromtimestamp(self.simulation_end_time, timezone.utc).isoformat(),
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                    avg_response_time_ms=0,
                    min_response_time_ms=0,
                    max_response_time_ms=0,
                    requests_per_second=0,
                    error_rate_percent=0,
                    status_code_distribution={},
                    endpoint_statistics={}
                )
            
            total_requests = len(self.metrics)
            successful_requests = len([m for m in self.metrics if 200 <= m.status_code < 300])
            failed_requests = total_requests - successful_requests
            
            response_times = [m.response_time_ms for m in self.metrics]
            avg_response_time = sum(response_times) / len(response_times)
            
            elapsed_time = self.simulation_end_time - self.simulation_start_time
            requests_per_second = total_requests / elapsed_time if elapsed_time > 0 else 0
            
            error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
            
            return SimulationSummary(
                simulation_id=self.simulation_id,
                start_time=datetime.fromtimestamp(self.simulation_start_time, timezone.utc).isoformat(),
                end_time=datetime.fromtimestamp(self.simulation_end_time, timezone.utc).isoformat(),
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                avg_response_time_ms=round(avg_response_time, 2),
                min_response_time_ms=round(min(response_times), 2),
                max_response_time_ms=round(max(response_times), 2),
                requests_per_second=round(requests_per_second, 2),
                error_rate_percent=round(error_rate, 2),
                status_code_distribution=self.get_status_code_distribution(),
                endpoint_statistics=self.get_endpoint_statistics()
            )
    
    def export_metrics(self, include_raw_data: bool = True) -> str:
        """
        Export metrics to JSON file.
        
        Args:
            include_raw_data: Whether to include individual request metrics
            
        Returns:
            Path to exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simulation_{self.simulation_id}_{timestamp}.json"
        filepath = os.path.join(self.output_directory, filename)
        
        export_data = {
            'simulation_summary': asdict(self.finish_simulation()),
            'status_code_distribution': self.get_status_code_distribution(),
            'endpoint_statistics': self.get_endpoint_statistics(),
            'error_analysis': self.get_error_analysis(),
            'export_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        if include_raw_data:
            with self.lock:
                export_data['raw_metrics'] = [asdict(metric) for metric in self.metrics]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def get_metrics_count(self) -> int:
        """Get current number of collected metrics."""
        with self.lock:
            return len(self.metrics)
    
    def clear_metrics(self) -> None:
        """Clear all collected metrics (useful for testing)."""
        with self.lock:
            self.metrics.clear()
            self.simulation_start_time = time.time()
            self.simulation_end_time = None