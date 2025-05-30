"""
Simulation Management Routes

API endpoints for managing API simulations and database ingestions.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import uuid
import random

simulations_bp = Blueprint('simulations', __name__)

# Mock simulation data store (in production, this would be a database)
SIMULATIONS = {
    'sim_001': {
        'id': 'sim_001',
        'name': 'Petstore API Simulation',
        'type': 'api',
        'status': 'running',
        'created_at': (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
        'started_at': (datetime.utcnow() - timedelta(minutes=14)).isoformat(),
        'configuration': {
            'api_source': 'https://petstore.swagger.io/v2/swagger.json',
            'environment': 'staging',
            'total_requests': 2000,
            'concurrent_threads': 5,
            'request_delay_ms': 100
        },
        'progress': {
            'current_requests': 1506,
            'target_requests': 2000,
            'progress_percent': 75.3,
            'requests_per_second': 42.1,
            'avg_response_time': 245,
            'error_rate': 2.4,
            'error_count': 36
        }
    },
    'sim_002': {
        'id': 'sim_002',
        'name': 'User Database Ingestion',
        'type': 'database',
        'status': 'running',
        'created_at': (datetime.utcnow() - timedelta(minutes=6)).isoformat(),
        'started_at': (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
        'configuration': {
            'database_type': 'postgresql',
            'host': 'localhost',
            'database': 'userapp_dev',
            'schema': 'public',
            'records_per_table': 1000,
            'preserve_data': False
        },
        'progress': {
            'current_requests': 656,
            'target_requests': 2000,
            'progress_percent': 32.8,
            'requests_per_second': 12.8,
            'avg_response_time': 89,
            'error_rate': 0.1,
            'error_count': 1
        }
    }
}


@simulations_bp.route('/', methods=['GET'])
def get_simulations():
    """Get all simulations with optional filtering."""
    status_filter = request.args.get('status')
    type_filter = request.args.get('type')
    
    simulations = list(SIMULATIONS.values())
    
    # Apply filters
    if status_filter:
        simulations = [s for s in simulations if s['status'] == status_filter]
    if type_filter:
        simulations = [s for s in simulations if s['type'] == type_filter]
    
    return jsonify({
        'simulations': simulations,
        'total': len(simulations),
        'timestamp': datetime.utcnow().isoformat()
    })


@simulations_bp.route('/<simulation_id>', methods=['GET'])
def get_simulation(simulation_id):
    """Get a specific simulation by ID."""
    simulation = SIMULATIONS.get(simulation_id)
    
    if not simulation:
        return jsonify({'error': 'Simulation not found'}), 404
    
    return jsonify(simulation)


@simulations_bp.route('/', methods=['POST'])
def create_simulation():
    """Create a new simulation."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['name', 'type', 'configuration']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    simulation_id = str(uuid.uuid4())[:8]
    
    simulation = {
        'id': simulation_id,
        'name': data['name'],
        'type': data['type'],
        'status': 'created',
        'created_at': datetime.utcnow().isoformat(),
        'started_at': None,
        'completed_at': None,
        'configuration': data['configuration'],
        'progress': {
            'current_requests': 0,
            'target_requests': data['configuration'].get('total_requests', 1000),
            'progress_percent': 0.0,
            'requests_per_second': 0.0,
            'avg_response_time': 0,
            'error_rate': 0.0,
            'error_count': 0
        }
    }
    
    SIMULATIONS[simulation_id] = simulation
    
    return jsonify(simulation), 201


@simulations_bp.route('/<simulation_id>/start', methods=['POST'])
def start_simulation(simulation_id):
    """Start a simulation."""
    simulation = SIMULATIONS.get(simulation_id)
    
    if not simulation:
        return jsonify({'error': 'Simulation not found'}), 404
    
    if simulation['status'] in ['running', 'completed']:
        return jsonify({'error': f'Cannot start simulation in {simulation["status"]} state'}), 400
    
    simulation['status'] = 'running'
    simulation['started_at'] = datetime.utcnow().isoformat()
    
    return jsonify(simulation)


@simulations_bp.route('/<simulation_id>/stop', methods=['POST'])
def stop_simulation(simulation_id):
    """Stop a simulation."""
    simulation = SIMULATIONS.get(simulation_id)
    
    if not simulation:
        return jsonify({'error': 'Simulation not found'}), 404
    
    if simulation['status'] not in ['running', 'paused']:
        return jsonify({'error': f'Cannot stop simulation in {simulation["status"]} state'}), 400
    
    simulation['status'] = 'stopped'
    simulation['completed_at'] = datetime.utcnow().isoformat()
    
    return jsonify(simulation)


@simulations_bp.route('/<simulation_id>/pause', methods=['POST'])
def pause_simulation(simulation_id):
    """Pause a simulation."""
    simulation = SIMULATIONS.get(simulation_id)
    
    if not simulation:
        return jsonify({'error': 'Simulation not found'}), 404
    
    if simulation['status'] != 'running':
        return jsonify({'error': f'Cannot pause simulation in {simulation["status"]} state'}), 400
    
    simulation['status'] = 'paused'
    
    return jsonify(simulation)


@simulations_bp.route('/<simulation_id>/resume', methods=['POST'])
def resume_simulation(simulation_id):
    """Resume a paused simulation."""
    simulation = SIMULATIONS.get(simulation_id)
    
    if not simulation:
        return jsonify({'error': 'Simulation not found'}), 404
    
    if simulation['status'] != 'paused':
        return jsonify({'error': f'Cannot resume simulation in {simulation["status"]} state'}), 400
    
    simulation['status'] = 'running'
    
    return jsonify(simulation)


@simulations_bp.route('/<simulation_id>', methods=['DELETE'])
def delete_simulation(simulation_id):
    """Delete a simulation."""
    simulation = SIMULATIONS.get(simulation_id)
    
    if not simulation:
        return jsonify({'error': 'Simulation not found'}), 404
    
    if simulation['status'] == 'running':
        return jsonify({'error': 'Cannot delete running simulation. Stop it first.'}), 400
    
    del SIMULATIONS[simulation_id]
    
    return '', 204


@simulations_bp.route('/<simulation_id>/progress', methods=['GET'])
def get_simulation_progress(simulation_id):
    """Get detailed progress for a simulation."""
    simulation = SIMULATIONS.get(simulation_id)
    
    if not simulation:
        return jsonify({'error': 'Simulation not found'}), 404
    
    # Simulate real-time progress updates
    if simulation['status'] == 'running':
        progress = simulation['progress']
        progress['current_requests'] = min(
            progress['target_requests'],
            progress['current_requests'] + random.randint(1, 10)
        )
        progress['progress_percent'] = (
            progress['current_requests'] / progress['target_requests'] * 100
        )
        progress['requests_per_second'] = round(random.uniform(40, 50), 1)
        progress['avg_response_time'] = random.randint(200, 300)
        progress['error_rate'] = round(random.uniform(1.5, 3.5), 1)
    
    return jsonify({
        'simulation_id': simulation_id,
        'progress': simulation['progress'],
        'status': simulation['status'],
        'timestamp': datetime.utcnow().isoformat()
    })


@simulations_bp.route('/templates', methods=['GET'])
def get_simulation_templates():
    """Get available simulation templates."""
    templates = [
        {
            'id': 'api_petstore',
            'name': 'Petstore API Template',
            'type': 'api',
            'description': 'Standard REST API testing template using Petstore',
            'configuration': {
                'api_source': 'https://petstore.swagger.io/v2/swagger.json',
                'environment': 'staging',
                'total_requests': 1000,
                'concurrent_threads': 5,
                'request_delay_ms': 100,
                'auth_config': {'type': 'none'}
            }
        },
        {
            'id': 'db_postgresql',
            'name': 'PostgreSQL Database Template',
            'type': 'database',
            'description': 'PostgreSQL database ingestion template',
            'configuration': {
                'database_type': 'postgresql',
                'host': 'localhost',
                'port': 5432,
                'database': 'testdb',
                'schema': 'public',
                'records_per_table': 1000,
                'preserve_data': False
            }
        },
        {
            'id': 'api_ecommerce',
            'name': 'E-commerce API Template',
            'type': 'api',
            'description': 'E-commerce API simulation with authentication',
            'configuration': {
                'api_source': '/path/to/ecommerce-api.yaml',
                'environment': 'staging',
                'total_requests': 5000,
                'concurrent_threads': 10,
                'request_delay_ms': 50,
                'auth_config': {
                    'type': 'bearer',
                    'token_url': 'https://api.example.com/auth/token'
                }
            }
        }
    ]
    
    return jsonify({
        'templates': templates,
        'total': len(templates)
    })


@simulations_bp.route('/stats', methods=['GET'])
def get_simulation_stats():
    """Get overall simulation statistics."""
    active_count = len([s for s in SIMULATIONS.values() if s['status'] == 'running'])
    completed_count = len([s for s in SIMULATIONS.values() if s['status'] == 'completed'])
    total_requests = sum(s['progress']['current_requests'] for s in SIMULATIONS.values())
    
    return jsonify({
        'total_simulations': len(SIMULATIONS),
        'active_simulations': active_count,
        'completed_simulations': completed_count,
        'failed_simulations': 0,  # Would calculate from actual data
        'total_requests_processed': total_requests,
        'total_requests_today': 15240,  # Would calculate from actual data
        'avg_requests_per_second': 42.3,  # Would calculate from actual data
        'system_uptime_hours': 24.5,  # Would calculate from actual data
        'timestamp': datetime.utcnow().isoformat()
    })