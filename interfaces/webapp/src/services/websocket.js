import { io } from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.connections = {};
    this.baseUrl = process.env.REACT_APP_WS_BASE_URL || 'http://localhost:5000';
  }

  connect(namespace) {
    if (this.connections[namespace]) {
      return this.connections[namespace];
    }

    const socket = io(`${this.baseUrl}${namespace}`, {
      transports: ['websocket', 'polling'],
      timeout: 20000,
      forceNew: true,
    });

    // Connection event handlers
    socket.on('connect', () => {
      console.log(`Connected to ${namespace} namespace`);
    });

    socket.on('disconnect', (reason) => {
      console.log(`Disconnected from ${namespace} namespace:`, reason);
      if (reason === 'io server disconnect') {
        // Server disconnected the socket, reconnect manually
        socket.connect();
      }
    });

    socket.on('connect_error', (error) => {
      console.error(`Connection error for ${namespace}:`, error);
    });

    this.connections[namespace] = socket;
    return socket;
  }

  disconnect(namespace) {
    if (this.connections[namespace]) {
      this.connections[namespace].disconnect();
      delete this.connections[namespace];
    }
  }

  disconnectAll() {
    Object.keys(this.connections).forEach(namespace => {
      this.disconnect(namespace);
    });
  }

  // Simulation WebSocket methods
  connectToSimulations() {
    const socket = this.connect('/simulation');
    
    socket.on('connected', (data) => {
      console.log('Simulation WebSocket connected:', data);
    });

    return socket;
  }

  subscribeToSimulation(simulationId, callback) {
    const socket = this.connections['/simulation'];
    if (!socket) {
      throw new Error('Simulation WebSocket not connected');
    }

    socket.emit('join_simulation', { simulation_id: simulationId });
    socket.on('simulation_update', callback);
    
    return () => {
      socket.emit('leave_simulation', { simulation_id: simulationId });
      socket.off('simulation_update', callback);
    };
  }

  requestSimulationStatus(simulationId = null) {
    const socket = this.connections['/simulation'];
    if (!socket) return;

    socket.emit('request_simulation_status', { simulation_id: simulationId });
  }

  // Metrics WebSocket methods
  connectToMetrics() {
    const socket = this.connect('/metrics');
    
    socket.on('connected', (data) => {
      console.log('Metrics WebSocket connected:', data);
    });

    return socket;
  }

  subscribeToMetrics(metricTypes = ['all'], callback) {
    const socket = this.connections['/metrics'];
    if (!socket) {
      throw new Error('Metrics WebSocket not connected');
    }

    socket.emit('subscribe_metrics', { metric_types: metricTypes });
    socket.on('metrics_update', callback);
    
    return () => {
      socket.emit('unsubscribe_metrics', { metric_types: metricTypes });
      socket.off('metrics_update', callback);
    };
  }

  // Logs WebSocket methods
  connectToLogs() {
    const socket = this.connect('/logs');
    
    socket.on('connected', (data) => {
      console.log('Logs WebSocket connected:', data);
    });

    return socket;
  }

  subscribeToLogs(callback) {
    const socket = this.connections['/logs'];
    if (!socket) {
      throw new Error('Logs WebSocket not connected');
    }

    socket.on('log_update', callback);
    
    return () => {
      socket.off('log_update', callback);
    };
  }

  setLogFilter(filters) {
    const socket = this.connections['/logs'];
    if (!socket) return;

    socket.emit('set_log_filter', filters);
  }

  requestLogHistory(lines = 100) {
    const socket = this.connections['/logs'];
    if (!socket) return;

    socket.emit('request_log_history', { lines });
  }

  // System WebSocket methods
  connectToSystem() {
    const socket = this.connect('/system');
    
    socket.on('connected', (data) => {
      console.log('System WebSocket connected:', data);
    });

    return socket;
  }

  requestSystemStatus() {
    const socket = this.connections['/system'];
    if (!socket) return;

    socket.emit('request_system_status');
  }

  subscribeToSystemUpdates(callback) {
    const socket = this.connections['/system'];
    if (!socket) {
      throw new Error('System WebSocket not connected');
    }

    socket.on('system_status', callback);
    
    return () => {
      socket.off('system_status', callback);
    };
  }
}

// Create singleton instance
const webSocketService = new WebSocketService();

export default webSocketService;