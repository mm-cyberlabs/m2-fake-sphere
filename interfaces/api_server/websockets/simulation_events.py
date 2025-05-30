"""
WebSocket Event Handlers for Simulation Updates

Real-time WebSocket handlers for simulation monitoring,
metrics updates, and log streaming.
"""

from flask_socketio import emit, join_room, leave_room, disconnect
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)


def setup_websocket_handlers(socketio):
    """Set up all WebSocket event handlers."""
    
    @socketio.on('connect', namespace='/simulation')
    def on_simulation_connect():
        """Handle client connection to simulation namespace."""
        logger.info('Client connected to simulation namespace')
        emit('connected', {
            'message': 'Connected to simulation updates',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @socketio.on('disconnect', namespace='/simulation')
    def on_simulation_disconnect():
        """Handle client disconnection from simulation namespace."""
        logger.info('Client disconnected from simulation namespace')
    
    @socketio.on('join_simulation', namespace='/simulation')
    def on_join_simulation(data):
        """Join a specific simulation room for targeted updates."""
        simulation_id = data.get('simulation_id')
        if simulation_id:
            join_room(simulation_id)
            emit('joined_simulation', {
                'simulation_id': simulation_id,
                'message': f'Joined simulation {simulation_id}',
                'timestamp': datetime.utcnow().isoformat()
            })
            logger.info(f'Client joined simulation room: {simulation_id}')
    
    @socketio.on('leave_simulation', namespace='/simulation')
    def on_leave_simulation(data):
        """Leave a specific simulation room."""
        simulation_id = data.get('simulation_id')
        if simulation_id:
            leave_room(simulation_id)
            emit('left_simulation', {
                'simulation_id': simulation_id,
                'message': f'Left simulation {simulation_id}',
                'timestamp': datetime.utcnow().isoformat()
            })
            logger.info(f'Client left simulation room: {simulation_id}')
    
    @socketio.on('request_simulation_status', namespace='/simulation')
    def on_request_simulation_status(data):
        """Handle request for current simulation status."""
        simulation_id = data.get('simulation_id')
        
        # In a real implementation, this would fetch actual simulation status
        sample_status = {
            'simulation_id': simulation_id or 'all',
            'simulations': [
                {
                    'id': 'sim_001',
                    'name': 'Petstore API',
                    'status': 'running',
                    'progress': 75.3,
                    'requests_completed': 1506,
                    'requests_per_second': 42.1,
                    'error_rate': 2.4,
                    'last_updated': datetime.utcnow().isoformat()
                }
            ],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        emit('simulation_status', sample_status)
    
    # Metrics namespace handlers
    @socketio.on('connect', namespace='/metrics')
    def on_metrics_connect():
        """Handle client connection to metrics namespace."""
        logger.info('Client connected to metrics namespace')
        emit('connected', {
            'message': 'Connected to metrics updates',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @socketio.on('disconnect', namespace='/metrics')
    def on_metrics_disconnect():
        """Handle client disconnection from metrics namespace."""
        logger.info('Client disconnected from metrics namespace')
    
    @socketio.on('subscribe_metrics', namespace='/metrics')
    def on_subscribe_metrics(data):
        """Subscribe to specific metric types."""
        metric_types = data.get('metric_types', ['all'])
        
        for metric_type in metric_types:
            join_room(f'metrics_{metric_type}')
        
        emit('subscribed_metrics', {
            'metric_types': metric_types,
            'message': f'Subscribed to metrics: {", ".join(metric_types)}',
            'timestamp': datetime.utcnow().isoformat()
        })
        logger.info(f'Client subscribed to metrics: {metric_types}')
    
    @socketio.on('unsubscribe_metrics', namespace='/metrics')
    def on_unsubscribe_metrics(data):
        """Unsubscribe from specific metric types."""
        metric_types = data.get('metric_types', [])
        
        for metric_type in metric_types:
            leave_room(f'metrics_{metric_type}')
        
        emit('unsubscribed_metrics', {
            'metric_types': metric_types,
            'message': f'Unsubscribed from metrics: {", ".join(metric_types)}',
            'timestamp': datetime.utcnow().isoformat()
        })
        logger.info(f'Client unsubscribed from metrics: {metric_types}')
    
    # Logs namespace handlers
    @socketio.on('connect', namespace='/logs')
    def on_logs_connect():
        """Handle client connection to logs namespace."""
        logger.info('Client connected to logs namespace')
        emit('connected', {
            'message': 'Connected to log streaming',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @socketio.on('disconnect', namespace='/logs')
    def on_logs_disconnect():
        """Handle client disconnection from logs namespace."""
        logger.info('Client disconnected from logs namespace')
    
    @socketio.on('set_log_filter', namespace='/logs')
    def on_set_log_filter(data):
        """Set log filtering criteria."""
        filters = {
            'level': data.get('level', 'ALL'),
            'simulation_id': data.get('simulation_id', 'ALL'),
            'search_text': data.get('search_text', ''),
            'max_lines': data.get('max_lines', 1000)
        }
        
        # Store filters in session or user preferences
        # For now, just acknowledge the filter change
        emit('log_filter_updated', {
            'filters': filters,
            'message': 'Log filters updated',
            'timestamp': datetime.utcnow().isoformat()
        })
        logger.info(f'Client updated log filters: {filters}')
    
    @socketio.on('request_log_history', namespace='/logs')
    def on_request_log_history(data):
        """Request historical log entries."""
        lines = data.get('lines', 100)
        
        # In a real implementation, this would fetch actual log history
        sample_history = [
            {
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'INFO',
                'simulation': 'sim_001',
                'message': 'Request completed: GET /api/pets/123 - 200 OK (245ms)'
            },
            {
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'SUCCESS',
                'simulation': 'sim_002',
                'message': 'Inserted 50 records into users table'
            }
        ]
        
        emit('log_history', {
            'logs': sample_history,
            'total_lines': len(sample_history),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # System namespace handlers
    @socketio.on('connect', namespace='/system')
    def on_system_connect():
        """Handle client connection to system namespace."""
        logger.info('Client connected to system namespace')
        emit('connected', {
            'message': 'Connected to system updates',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @socketio.on('disconnect', namespace='/system')
    def on_system_disconnect():
        """Handle client disconnection from system namespace."""
        logger.info('Client disconnected from system namespace')
    
    @socketio.on('request_system_status', namespace='/system')
    def on_request_system_status():
        """Handle request for system status."""
        import random
        
        system_status = {
            'status': 'healthy',
            'uptime_seconds': 86400,  # 24 hours
            'memory_usage_percent': round(random.uniform(60, 80), 1),
            'cpu_usage_percent': round(random.uniform(40, 70), 1),
            'disk_usage_percent': round(random.uniform(30, 50), 1),
            'active_simulations': 2,
            'total_requests_today': 15240,
            'network_status': 'online',
            'database_status': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        emit('system_status', system_status)
    
    # Error handler
    @socketio.on_error_default
    def default_error_handler(e):
        """Handle WebSocket errors."""
        logger.error(f'WebSocket error: {e}')
        emit('error', {
            'message': 'An error occurred',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    return socketio