"""
Metrics API Routes

API endpoints for retrieving and analyzing simulation metrics.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random

metrics_bp = Blueprint('metrics', __name__)


@metrics_bp.route('/overview', methods=['GET'])
def get_metrics_overview():
    """Get high-level metrics overview."""
    time_period = request.args.get('period', '24h')
    
    # Simulate metrics based on time period
    if time_period == '1h':
        multiplier = 1
    elif time_period == '24h':
        multiplier = 24
    elif time_period == '7d':
        multiplier = 168
    else:  # 30d
        multiplier = 720
    
    base_requests = 1000 * multiplier
    
    return jsonify({
        'time_period': time_period,
        'summary': {
            'total_requests': base_requests + random.randint(-100, 100),
            'successful_requests': int((base_requests + random.randint(-100, 100)) * 0.97),
            'failed_requests': int((base_requests + random.randint(-100, 100)) * 0.03),
            'avg_response_time_ms': random.randint(200, 300),
            'min_response_time_ms': random.randint(50, 100),
            'max_response_time_ms': random.randint(800, 1200),
            'requests_per_second': round(random.uniform(40, 50), 2),
            'error_rate_percent': round(random.uniform(2.0, 4.0), 2),
            'uptime_percent': round(random.uniform(99.5, 99.9), 2)
        },
        'timestamp': datetime.utcnow().isoformat()
    })


@metrics_bp.route('/timeseries', methods=['GET'])
def get_timeseries_metrics():
    """Get time series metrics data."""
    metric_type = request.args.get('type', 'requests_per_second')
    time_period = request.args.get('period', '1h')
    resolution = request.args.get('resolution', 'minute')
    
    # Generate sample time series data
    if time_period == '1h':
        points = 60 if resolution == 'minute' else 3600
        start_time = datetime.utcnow() - timedelta(hours=1)
    elif time_period == '24h':
        points = 24 if resolution == 'hour' else 1440
        start_time = datetime.utcnow() - timedelta(days=1)
    else:
        points = 168 if resolution == 'hour' else 7
        start_time = datetime.utcnow() - timedelta(days=7)
    
    data_points = []
    for i in range(points):
        if resolution == 'minute':
            timestamp = start_time + timedelta(minutes=i)
        elif resolution == 'hour':
            timestamp = start_time + timedelta(hours=i)
        else:
            timestamp = start_time + timedelta(days=i)
        
        if metric_type == 'requests_per_second':
            value = round(random.uniform(30, 60), 2)
        elif metric_type == 'response_time':
            value = random.randint(150, 400)
        elif metric_type == 'error_rate':
            value = round(random.uniform(0.5, 5.0), 2)
        else:
            value = random.randint(1, 100)
        
        data_points.append({
            'timestamp': timestamp.isoformat(),
            'value': value
        })
    
    return jsonify({
        'metric_type': metric_type,
        'time_period': time_period,
        'resolution': resolution,
        'data_points': data_points,
        'total_points': len(data_points)
    })


@metrics_bp.route('/endpoints', methods=['GET'])
def get_endpoint_metrics():
    """Get per-endpoint performance metrics."""
    
    endpoints = [
        {
            'endpoint': 'GET /api/pets',
            'method': 'GET',
            'path': '/api/pets',
            'requests': random.randint(1200, 1400),
            'avg_response_time_ms': random.randint(150, 200),
            'min_response_time_ms': random.randint(80, 120),
            'max_response_time_ms': random.randint(400, 600),
            'success_rate_percent': round(random.uniform(97, 99), 2),
            'error_rate_percent': round(random.uniform(1, 3), 2),
            'p50_response_time': random.randint(160, 180),
            'p95_response_time': random.randint(300, 400),
            'p99_response_time': random.randint(500, 700)
        },
        {
            'endpoint': 'POST /api/pets',
            'method': 'POST',
            'path': '/api/pets',
            'requests': random.randint(200, 300),
            'avg_response_time_ms': random.randint(250, 350),
            'min_response_time_ms': random.randint(150, 200),
            'max_response_time_ms': random.randint(800, 1200),
            'success_rate_percent': round(random.uniform(95, 98), 2),
            'error_rate_percent': round(random.uniform(2, 5), 2),
            'p50_response_time': random.randint(280, 320),
            'p95_response_time': random.randint(500, 700),
            'p99_response_time': random.randint(900, 1100)
        },
        {
            'endpoint': 'GET /api/pets/{id}',
            'method': 'GET',
            'path': '/api/pets/{id}',
            'requests': random.randint(800, 1000),
            'avg_response_time_ms': random.randint(180, 250),
            'min_response_time_ms': random.randint(100, 150),
            'max_response_time_ms': random.randint(500, 800),
            'success_rate_percent': round(random.uniform(96, 99), 2),
            'error_rate_percent': round(random.uniform(1, 4), 2),
            'p50_response_time': random.randint(190, 230),
            'p95_response_time': random.randint(350, 450),
            'p99_response_time': random.randint(600, 750)
        },
        {
            'endpoint': 'PUT /api/pets/{id}',
            'method': 'PUT',
            'path': '/api/pets/{id}',
            'requests': random.randint(100, 200),
            'avg_response_time_ms': random.randint(300, 400),
            'min_response_time_ms': random.randint(200, 250),
            'max_response_time_ms': random.randint(1000, 1500),
            'success_rate_percent': round(random.uniform(94, 97), 2),
            'error_rate_percent': round(random.uniform(3, 6), 2),
            'p50_response_time': random.randint(320, 380),
            'p95_response_time': random.randint(600, 800),
            'p99_response_time': random.randint(1100, 1400)
        }
    ]
    
    return jsonify({
        'endpoints': endpoints,
        'total_endpoints': len(endpoints),
        'timestamp': datetime.utcnow().isoformat()
    })


@metrics_bp.route('/status-codes', methods=['GET'])
def get_status_code_distribution():
    """Get HTTP status code distribution."""
    
    total_requests = random.randint(2800, 3200)
    
    status_codes = [
        {
            'status_code': 200,
            'description': 'OK',
            'count': int(total_requests * 0.91),
            'percentage': 91.0
        },
        {
            'status_code': 201,
            'description': 'Created',
            'count': int(total_requests * 0.05),
            'percentage': 5.0
        },
        {
            'status_code': 400,
            'description': 'Bad Request',
            'count': int(total_requests * 0.015),
            'percentage': 1.5
        },
        {
            'status_code': 401,
            'description': 'Unauthorized',
            'count': int(total_requests * 0.01),
            'percentage': 1.0
        },
        {
            'status_code': 404,
            'description': 'Not Found',
            'count': int(total_requests * 0.008),
            'percentage': 0.8
        },
        {
            'status_code': 500,
            'description': 'Internal Server Error',
            'count': int(total_requests * 0.007),
            'percentage': 0.7
        }
    ]
    
    return jsonify({
        'status_codes': status_codes,
        'total_requests': total_requests,
        'timestamp': datetime.utcnow().isoformat()
    })


@metrics_bp.route('/errors', methods=['GET'])
def get_error_analysis():
    """Get detailed error analysis."""
    
    errors = [
        {
            'error_type': 'Timeout',
            'count': random.randint(25, 35),
            'percentage': round(random.uniform(30, 35), 1),
            'first_seen': (datetime.utcnow() - timedelta(hours=2, minutes=30)).isoformat(),
            'last_seen': (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
            'affected_endpoints': ['GET /api/pets', 'POST /api/pets'],
            'sample_message': 'Request timeout after 30 seconds'
        },
        {
            'error_type': 'Authentication Failed',
            'count': random.randint(18, 25),
            'percentage': round(random.uniform(20, 25), 1),
            'first_seen': (datetime.utcnow() - timedelta(hours=1, minutes=45)).isoformat(),
            'last_seen': (datetime.utcnow() - timedelta(minutes=12)).isoformat(),
            'affected_endpoints': ['POST /api/pets', 'PUT /api/pets/{id}'],
            'sample_message': 'Invalid or expired authentication token'
        },
        {
            'error_type': 'Rate Limited',
            'count': random.randint(15, 22),
            'percentage': round(random.uniform(18, 22), 1),
            'first_seen': (datetime.utcnow() - timedelta(hours=1, minutes=20)).isoformat(),
            'last_seen': (datetime.utcnow() - timedelta(minutes=8)).isoformat(),
            'affected_endpoints': ['GET /api/pets', 'GET /api/pets/{id}'],
            'sample_message': 'Rate limit exceeded: 100 requests per minute'
        },
        {
            'error_type': 'Not Found',
            'count': random.randint(10, 18),
            'percentage': round(random.uniform(12, 18), 1),
            'first_seen': (datetime.utcnow() - timedelta(hours=3)).isoformat(),
            'last_seen': (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            'affected_endpoints': ['GET /api/pets/{id}', 'PUT /api/pets/{id}'],
            'sample_message': 'Pet with ID 12345 not found'
        },
        {
            'error_type': 'Server Error',
            'count': random.randint(5, 12),
            'percentage': round(random.uniform(6, 12), 1),
            'first_seen': (datetime.utcnow() - timedelta(hours=4)).isoformat(),
            'last_seen': (datetime.utcnow() - timedelta(minutes=25)).isoformat(),
            'affected_endpoints': ['POST /api/pets', 'PUT /api/pets/{id}'],
            'sample_message': 'Internal server error: Database connection failed'
        }
    ]
    
    return jsonify({
        'errors': errors,
        'total_errors': sum(e['count'] for e in errors),
        'error_categories': len(errors),
        'timestamp': datetime.utcnow().isoformat()
    })


@metrics_bp.route('/performance', methods=['GET'])
def get_performance_summary():
    """Get performance summary and SLA compliance."""
    
    sla_targets = {
        'avg_response_time_ms': 500,
        'p95_response_time_ms': 1000,
        'p99_response_time_ms': 2000,
        'error_rate_percent': 5.0,
        'uptime_percent': 99.0
    }
    
    current_performance = {
        'avg_response_time_ms': random.randint(200, 350),
        'p50_response_time_ms': random.randint(180, 250),
        'p95_response_time_ms': random.randint(400, 600),
        'p99_response_time_ms': random.randint(700, 1200),
        'error_rate_percent': round(random.uniform(1.5, 4.5), 2),
        'uptime_percent': round(random.uniform(99.2, 99.9), 2),
        'throughput_rps': round(random.uniform(40, 55), 2),
        'concurrent_users': random.randint(8, 15),
        'memory_usage_mb': random.randint(1800, 2400),
        'cpu_usage_percent': round(random.uniform(45, 75), 1)
    }
    
    # Calculate SLA compliance
    sla_compliance = {}
    for metric, target in sla_targets.items():
        current_value = current_performance.get(metric, 0)
        if 'response_time' in metric:
            # Lower is better for response time
            compliant = current_value <= target
        elif 'error_rate' in metric:
            # Lower is better for error rate
            compliant = current_value <= target
        else:
            # Higher is better for uptime
            compliant = current_value >= target
        
        sla_compliance[metric] = {
            'target': target,
            'current': current_value,
            'compliant': compliant,
            'variance_percent': round(((current_value - target) / target) * 100, 2)
        }
    
    return jsonify({
        'performance': current_performance,
        'sla_targets': sla_targets,
        'sla_compliance': sla_compliance,
        'overall_health': 'good' if all(c['compliant'] for c in sla_compliance.values()) else 'warning',
        'timestamp': datetime.utcnow().isoformat()
    })


@metrics_bp.route('/export', methods=['POST'])
def export_metrics():
    """Export metrics data."""
    data = request.get_json()
    export_format = data.get('format', 'json')
    time_period = data.get('period', '24h')
    metrics = data.get('metrics', ['overview', 'endpoints', 'errors'])
    
    # In a real implementation, this would generate and return actual export files
    export_id = f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    return jsonify({
        'export_id': export_id,
        'format': export_format,
        'time_period': time_period,
        'metrics_included': metrics,
        'status': 'completed',
        'download_url': f'/api/metrics/downloads/{export_id}.{export_format}',
        'file_size_bytes': random.randint(1024, 10240),
        'created_at': datetime.utcnow().isoformat()
    })


@metrics_bp.route('/realtime', methods=['GET'])
def get_realtime_metrics():
    """Get real-time metrics for live monitoring."""
    
    # This would typically be served via WebSocket, but also available as REST
    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'current_rps': round(random.uniform(40, 50), 1),
        'active_connections': random.randint(8, 15),
        'response_time_ms': random.randint(200, 300),
        'error_rate_percent': round(random.uniform(1.5, 3.5), 1),
        'memory_usage_percent': round(random.uniform(65, 75), 1),
        'cpu_usage_percent': round(random.uniform(45, 65), 1),
        'queue_size': random.randint(0, 25),
        'cache_hit_rate_percent': round(random.uniform(85, 95), 1)
    })