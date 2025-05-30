"""
Configuration Management Routes

API endpoints for managing simulation configurations and templates.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import uuid

configurations_bp = Blueprint('configurations', __name__)

# Mock configuration templates store
TEMPLATES = {
    'api_petstore': {
        'id': 'api_petstore',
        'name': 'Petstore API Template',
        'type': 'api',
        'description': 'Standard REST API testing template using Petstore',
        'category': 'public_apis',
        'created_at': '2024-01-15T10:30:00Z',
        'updated_at': '2024-01-20T14:20:00Z',
        'configuration': {
            'api_source': 'https://petstore.swagger.io/v2/swagger.json',
            'environment': 'staging',
            'total_requests': 1000,
            'concurrent_threads': 5,
            'request_delay_ms': 100,
            'auth_config': {'type': 'none'},
            'custom_headers': {},
            'include_endpoints': [],
            'exclude_endpoints': []
        }
    },
    'db_postgresql': {
        'id': 'db_postgresql',
        'name': 'PostgreSQL Database Template',
        'type': 'database',
        'description': 'PostgreSQL database ingestion template',
        'category': 'databases',
        'created_at': '2024-01-10T09:15:00Z',
        'updated_at': '2024-01-18T16:45:00Z',
        'configuration': {
            'database_type': 'postgresql',
            'host': 'localhost',
            'port': 5432,
            'database': 'testdb',
            'schema': 'public',
            'records_per_table': 1000,
            'preserve_data': False,
            'generate_relationships': True,
            'batch_size': 100
        }
    }
}

# Mock saved configurations
SAVED_CONFIGS = {}


@configurations_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get all configuration templates."""
    category_filter = request.args.get('category')
    type_filter = request.args.get('type')
    
    templates = list(TEMPLATES.values())
    
    # Apply filters
    if category_filter:
        templates = [t for t in templates if t['category'] == category_filter]
    if type_filter:
        templates = [t for t in templates if t['type'] == type_filter]
    
    return jsonify({
        'templates': templates,
        'total': len(templates),
        'categories': list(set(t['category'] for t in TEMPLATES.values())),
        'types': list(set(t['type'] for t in TEMPLATES.values()))
    })


@configurations_bp.route('/templates/<template_id>', methods=['GET'])
def get_template(template_id):
    """Get a specific template by ID."""
    template = TEMPLATES.get(template_id)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    return jsonify(template)


@configurations_bp.route('/templates', methods=['POST'])
def create_template():
    """Create a new configuration template."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['name', 'type', 'configuration']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    template_id = data.get('id', str(uuid.uuid4())[:8])
    
    template = {
        'id': template_id,
        'name': data['name'],
        'type': data['type'],
        'description': data.get('description', ''),
        'category': data.get('category', 'custom'),
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat(),
        'configuration': data['configuration']
    }
    
    TEMPLATES[template_id] = template
    
    return jsonify(template), 201


@configurations_bp.route('/templates/<template_id>', methods=['PUT'])
def update_template(template_id):
    """Update an existing template."""
    template = TEMPLATES.get(template_id)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields
    template['name'] = data.get('name', template['name'])
    template['description'] = data.get('description', template['description'])
    template['category'] = data.get('category', template['category'])
    template['configuration'] = data.get('configuration', template['configuration'])
    template['updated_at'] = datetime.utcnow().isoformat()
    
    return jsonify(template)


@configurations_bp.route('/templates/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a template."""
    template = TEMPLATES.get(template_id)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    # Don't allow deletion of system templates
    if template['category'] in ['public_apis', 'databases', 'system']:
        return jsonify({'error': 'Cannot delete system templates'}), 403
    
    del TEMPLATES[template_id]
    
    return '', 204


@configurations_bp.route('/validate', methods=['POST'])
def validate_configuration():
    """Validate a configuration."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No configuration provided'}), 400
    
    config_type = data.get('type')
    configuration = data.get('configuration', {})
    
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'suggestions': []
    }
    
    # Validate based on type
    if config_type == 'api':
        validation_result = validate_api_configuration(configuration)
    elif config_type == 'database':
        validation_result = validate_database_configuration(configuration)
    else:
        validation_result['valid'] = False
        validation_result['errors'].append('Unknown configuration type')
    
    return jsonify(validation_result)


def validate_api_configuration(config):
    """Validate API configuration."""
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'suggestions': []
    }
    
    # Required fields
    required_fields = ['api_source', 'total_requests']
    for field in required_fields:
        if field not in config or not config[field]:
            result['errors'].append(f'Missing required field: {field}')
            result['valid'] = False
    
    # Validate numeric fields
    if 'total_requests' in config:
        try:
            total_requests = int(config['total_requests'])
            if total_requests <= 0:
                result['errors'].append('Total requests must be greater than 0')
                result['valid'] = False
            elif total_requests > 100000:
                result['warnings'].append('Very high request count may impact performance')
        except (ValueError, TypeError):
            result['errors'].append('Total requests must be a valid number')
            result['valid'] = False
    
    if 'concurrent_threads' in config:
        try:
            threads = int(config['concurrent_threads'])
            if threads <= 0 or threads > 50:
                result['warnings'].append('Recommended thread count is between 1-50')
        except (ValueError, TypeError):
            result['errors'].append('Concurrent threads must be a valid number')
            result['valid'] = False
    
    # Validate API source
    if 'api_source' in config:
        api_source = config['api_source']
        if not (api_source.startswith('http') or api_source.endswith(('.json', '.yaml', '.yml'))):
            result['warnings'].append('API source should be a URL or file path ending in .json, .yaml, or .yml')
    
    # Suggestions
    if config.get('request_delay_ms', 0) == 0:
        result['suggestions'].append('Consider adding a small delay between requests to be more realistic')
    
    if not config.get('auth_config', {}).get('type'):
        result['suggestions'].append('Configure authentication if your API requires it')
    
    return result


def validate_database_configuration(config):
    """Validate database configuration."""
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'suggestions': []
    }
    
    # Required fields
    required_fields = ['database_type', 'host', 'database']
    for field in required_fields:
        if field not in config or not config[field]:
            result['errors'].append(f'Missing required field: {field}')
            result['valid'] = False
    
    # Validate port
    if 'port' in config:
        try:
            port = int(config['port'])
            if port <= 0 or port > 65535:
                result['errors'].append('Port must be between 1 and 65535')
                result['valid'] = False
        except (ValueError, TypeError):
            result['errors'].append('Port must be a valid number')
            result['valid'] = False
    
    # Validate records per table
    if 'records_per_table' in config:
        try:
            records = int(config['records_per_table'])
            if records <= 0:
                result['errors'].append('Records per table must be greater than 0')
                result['valid'] = False
            elif records > 1000000:
                result['warnings'].append('Very high record count may take a long time to generate')
        except (ValueError, TypeError):
            result['errors'].append('Records per table must be a valid number')
            result['valid'] = False
    
    # Suggestions
    if not config.get('schema'):
        result['suggestions'].append('Specify a schema name for better control over data generation')
    
    if config.get('preserve_data', True):
        result['warnings'].append('Preserving existing data may lead to constraint violations')
    
    return result


@configurations_bp.route('/test-connection', methods=['POST'])
def test_connection():
    """Test database or API connection."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No configuration provided'}), 400
    
    config_type = data.get('type')
    configuration = data.get('configuration', {})
    
    # Simulate connection testing
    if config_type == 'database':
        return test_database_connection(configuration)
    elif config_type == 'api':
        return test_api_connection(configuration)
    else:
        return jsonify({'error': 'Unknown configuration type'}), 400


def test_database_connection(config):
    """Test database connection."""
    # In a real implementation, this would actually test the connection
    import random
    import time
    
    # Simulate connection test delay
    time.sleep(1)
    
    # Simulate success/failure
    success = random.choice([True, True, True, False])  # 75% success rate
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Database connection successful',
            'details': {
                'host': config.get('host'),
                'database': config.get('database'),
                'server_version': '14.5',
                'available_schemas': ['public', 'users', 'products'],
                'total_tables': random.randint(10, 50),
                'connection_time_ms': random.randint(50, 200)
            },
            'timestamp': datetime.utcnow().isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Database connection failed',
            'error': 'Connection timeout after 30 seconds',
            'suggestions': [
                'Check if the database server is running',
                'Verify host and port are correct',
                'Ensure credentials are valid',
                'Check firewall settings'
            ],
            'timestamp': datetime.utcnow().isoformat()
        }), 400


def test_api_connection(config):
    """Test API connection."""
    # In a real implementation, this would actually test the API
    import random
    import time
    
    # Simulate API test delay
    time.sleep(0.5)
    
    # Simulate success/failure
    success = random.choice([True, True, False])  # 67% success rate
    
    if success:
        return jsonify({
            'success': True,
            'message': 'API connection successful',
            'details': {
                'api_source': config.get('api_source'),
                'specification_version': '3.0.1',
                'total_endpoints': random.randint(15, 50),
                'authentication_required': random.choice([True, False]),
                'response_time_ms': random.randint(100, 500),
                'available_methods': ['GET', 'POST', 'PUT', 'DELETE']
            },
            'timestamp': datetime.utcnow().isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'message': 'API connection failed',
            'error': 'Unable to fetch Swagger specification',
            'suggestions': [
                'Check if the API URL is correct',
                'Verify the Swagger specification is valid',
                'Ensure the API server is running',
                'Check authentication requirements'
            ],
            'timestamp': datetime.utcnow().isoformat()
        }), 400


@configurations_bp.route('/saved', methods=['GET'])
def get_saved_configurations():
    """Get saved configurations."""
    return jsonify({
        'configurations': list(SAVED_CONFIGS.values()),
        'total': len(SAVED_CONFIGS)
    })


@configurations_bp.route('/saved', methods=['POST'])
def save_configuration():
    """Save a configuration."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No configuration provided'}), 400
    
    config_id = str(uuid.uuid4())[:8]
    
    saved_config = {
        'id': config_id,
        'name': data.get('name', f'Configuration {config_id}'),
        'type': data.get('type'),
        'configuration': data.get('configuration'),
        'created_at': datetime.utcnow().isoformat(),
        'last_used': None
    }
    
    SAVED_CONFIGS[config_id] = saved_config
    
    return jsonify(saved_config), 201


@configurations_bp.route('/saved/<config_id>', methods=['DELETE'])
def delete_saved_configuration(config_id):
    """Delete a saved configuration."""
    if config_id not in SAVED_CONFIGS:
        return jsonify({'error': 'Configuration not found'}), 404
    
    del SAVED_CONFIGS[config_id]
    return '', 204