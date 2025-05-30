"""
Main Flask API Server

This is the main entry point for the Flask API server that provides
backend services for the React WebUI.
"""

import os
import sys
from pathlib import Path

# Add the core module to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "m2_fake_sphere" / "src"))

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import time
from datetime import datetime

from routes.simulations import simulations_bp
from routes.metrics import metrics_bp
from routes.configurations import configurations_bp
from routes.auth import auth_bp
from websockets.simulation_events import setup_websocket_handlers


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'fake-sphere-secret-key-dev'
    app.config['CORS_HEADERS'] = 'Content-Type'
    
    # Enable CORS for all domains (development only)
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Register blueprints
    app.register_blueprint(simulations_bp, url_prefix='/api/simulations')
    app.register_blueprint(metrics_bp, url_prefix='/api/metrics')
    app.register_blueprint(configurations_bp, url_prefix='/api/configurations')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Setup WebSocket handlers
    setup_websocket_handlers(socketio)
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '0.1.0'
        })
    
    # System info endpoint
    @app.route('/api/system/info')
    def system_info():
        """Get system information."""
        return jsonify({
            'version': '0.1.0',
            'uptime': time.time(),  # Would calculate actual uptime
            'active_simulations': 2,  # Would get from simulation manager
            'total_requests_today': 15240,
            'system_load': {
                'cpu_percent': 45.2,
                'memory_percent': 68.1,
                'disk_percent': 32.8
            },
            'features': [
                'api_simulation',
                'database_ingestion',
                'real_time_monitoring',
                'metrics_collection'
            ]
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app, socketio


def start_background_tasks(socketio):
    """Start background tasks for real-time updates."""
    def emit_simulation_updates():
        """Emit periodic simulation updates."""
        while True:
            # Simulate real-time updates
            sample_update = {
                'timestamp': datetime.utcnow().isoformat(),
                'simulations': [
                    {
                        'id': 'sim_001',
                        'name': 'Petstore API',
                        'status': 'running',
                        'progress': 75.3,
                        'requests_completed': 1506,
                        'requests_per_second': 42.1,
                        'error_rate': 2.4
                    },
                    {
                        'id': 'sim_002',
                        'name': 'User Database',
                        'status': 'running',
                        'progress': 32.8,
                        'requests_completed': 656,
                        'requests_per_second': 12.8,
                        'error_rate': 0.1
                    }
                ]
            }
            
            socketio.emit('simulation_update', sample_update, namespace='/simulation')
            time.sleep(2)  # Update every 2 seconds
    
    def emit_metrics_updates():
        """Emit periodic metrics updates."""
        while True:
            import random
            
            sample_metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'system_metrics': {
                    'total_requests': random.randint(15200, 15300),
                    'requests_per_second': round(random.uniform(40, 50), 1),
                    'avg_response_time': random.randint(200, 300),
                    'error_rate': round(random.uniform(1.5, 3.0), 1),
                    'active_connections': random.randint(8, 15),
                    'memory_usage': round(random.uniform(65, 75), 1)
                },
                'endpoint_metrics': [
                    {
                        'endpoint': 'GET /api/pets',
                        'requests': random.randint(1200, 1300),
                        'avg_response_time': random.randint(180, 220),
                        'error_rate': round(random.uniform(1.0, 2.0), 1)
                    },
                    {
                        'endpoint': 'POST /api/pets',
                        'requests': random.randint(200, 250),
                        'avg_response_time': random.randint(280, 320),
                        'error_rate': round(random.uniform(2.0, 4.0), 1)
                    }
                ]
            }
            
            socketio.emit('metrics_update', sample_metrics, namespace='/metrics')
            time.sleep(5)  # Update every 5 seconds
    
    def emit_log_updates():
        """Emit periodic log updates."""
        while True:
            import random
            
            log_entries = [
                "Request completed: GET /api/pets/123 - 200 OK (245ms)",
                "Inserted 50 records into users table",
                "Authentication token refreshed",
                "Response time exceeding threshold: 1.2s",
                "Request completed: POST /api/pets - 201 Created (189ms)",
                "Memory usage: 2.1GB / Thread pool: 5/10 active",
                "Request failed: GET /api/orders/456 - 404 Not Found",
                "Processing table: product_categories (500/1000 records)",
                "Simulation milestone: 1000 requests completed",
                "Rate limit approaching: 95/100 requests per minute"
            ]
            
            levels = ["INFO", "WARNING", "ERROR", "SUCCESS", "DEBUG"]
            simulations = ["sim_001", "sim_002", "System"]
            
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': random.choice(levels),
                'simulation': random.choice(simulations),
                'message': random.choice(log_entries)
            }
            
            socketio.emit('log_update', log_entry, namespace='/logs')
            time.sleep(1)  # Update every second
    
    # Start background threads
    threading.Thread(target=emit_simulation_updates, daemon=True).start()
    threading.Thread(target=emit_metrics_updates, daemon=True).start()
    threading.Thread(target=emit_log_updates, daemon=True).start()


def main():
    """Main entry point for the API server."""
    app, socketio = create_app()
    
    # Start background tasks
    start_background_tasks(socketio)
    
    print("🚀 Starting Fake Sphere API Server...")
    print("📡 WebSocket support enabled")
    print("🌐 CORS enabled for development")
    print("🔗 Available at: http://localhost:5000")
    print("📊 API Documentation: http://localhost:5000/api/health")
    
    # Run the server
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=True,
        allow_unsafe_werkzeug=True  # For development only
    )


if __name__ == "__main__":
    main()