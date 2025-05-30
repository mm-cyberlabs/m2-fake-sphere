import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Database, 
  Globe, 
  TrendingUp, 
  Clock, 
  AlertCircle,
  CheckCircle,
  XCircle,
  Play,
  Pause,
  Square
} from 'lucide-react';
import { simulationsAPI, metricsAPI } from '../services/api';
import webSocketService from '../services/websocket';

const Home = () => {
  const [stats, setStats] = useState({
    active_simulations: 0,
    completed_simulations: 0,
    total_requests_today: 0,
    avg_requests_per_second: 0,
  });
  const [simulations, setSimulations] = useState([]);
  const [metrics, setMetrics] = useState({
    total_requests: 0,
    requests_per_second: 0,
    avg_response_time: 0,
    error_rate: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    setupWebSocketConnections();
    
    return () => {
      webSocketService.disconnectAll();
    };
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsResponse, simulationsResponse, metricsResponse] = await Promise.all([
        simulationsAPI.getStats(),
        simulationsAPI.getAll({ status: 'running' }),
        metricsAPI.getOverview('24h')
      ]);

      setStats(statsResponse.data);
      setSimulations(simulationsResponse.data.simulations || []);
      setMetrics(metricsResponse.data.summary || {});
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocketConnections = () => {
    // Connect to simulation updates
    webSocketService.connectToSimulations();
    webSocketService.subscribeToSimulation(null, (data) => {
      if (data.simulations) {
        setSimulations(data.simulations);
      }
    });

    // Connect to metrics updates
    webSocketService.connectToMetrics();
    webSocketService.subscribeToMetrics(['all'], (data) => {
      if (data.system_metrics) {
        setMetrics(data.system_metrics);
      }
    });
  };

  const handleSimulationAction = async (simulationId, action) => {
    try {
      switch (action) {
        case 'start':
          await simulationsAPI.start(simulationId);
          break;
        case 'pause':
          await simulationsAPI.pause(simulationId);
          break;
        case 'stop':
          await simulationsAPI.stop(simulationId);
          break;
        default:
          break;
      }
      // Refresh simulations list
      loadDashboardData();
    } catch (error) {
      console.error(`Error ${action}ing simulation:`, error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'paused':
        return <Pause className="w-5 h-5 text-yellow-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'text-green-500';
      case 'paused':
        return 'text-yellow-500';
      case 'failed':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white mb-2">
          Welcome to Fake Sphere
        </h1>
        <p className="text-gray-400">
          Monitor and control your API simulations and database ingestions
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="futuristic-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">Active Simulations</p>
              <p className="text-2xl font-bold text-white">{stats.active_simulations}</p>
            </div>
            <Activity className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="futuristic-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">Requests Today</p>
              <p className="text-2xl font-bold text-white">{stats.total_requests_today?.toLocaleString()}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="futuristic-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">Avg RPS</p>
              <p className="text-2xl font-bold text-white">{metrics.requests_per_second}</p>
            </div>
            <Globe className="w-8 h-8 text-purple-500" />
          </div>
        </div>

        <div className="futuristic-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">Error Rate</p>
              <p className="text-2xl font-bold text-white">{metrics.error_rate}%</p>
            </div>
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
        </div>
      </div>

      {/* Active Simulations */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Active Simulations</h2>
          <button className="btn btn-primary">
            <Play className="w-4 h-4" />
            New Simulation
          </button>
        </div>
        
        <div className="card-content">
          {simulations.length === 0 ? (
            <div className="text-center py-8">
              <Activity className="w-12 h-12 text-gray-500 mx-auto mb-4" />
              <p className="text-gray-400 mb-4">No active simulations</p>
              <button className="btn btn-primary">
                Start Your First Simulation
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {simulations.map((simulation) => (
                <div 
                  key={simulation.id} 
                  className="bg-slate-700 rounded-lg p-4 border border-slate-600"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(simulation.status)}
                      <div>
                        <h3 className="font-medium text-white">{simulation.name}</h3>
                        <p className="text-sm text-gray-400">
                          {simulation.type === 'api' ? 'API Simulation' : 'Database Ingestion'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`text-sm font-medium ${getStatusColor(simulation.status)}`}>
                        {simulation.status?.toUpperCase()}
                      </span>
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div className="mb-3">
                    <div className="flex justify-between text-sm text-gray-400 mb-1">
                      <span>Progress</span>
                      <span>{simulation.progress?.progress_percent?.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-600 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${simulation.progress?.progress_percent || 0}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Metrics */}
                  <div className="grid grid-cols-3 gap-4 mb-3">
                    <div>
                      <p className="text-xs text-gray-400">Requests</p>
                      <p className="text-sm font-medium text-white">
                        {simulation.progress?.current_requests || 0}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400">RPS</p>
                      <p className="text-sm font-medium text-white">
                        {simulation.progress?.requests_per_second || 0}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400">Errors</p>
                      <p className="text-sm font-medium text-white">
                        {simulation.progress?.error_count || 0}
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex space-x-2">
                    {simulation.status === 'running' && (
                      <>
                        <button 
                          className="btn btn-secondary text-xs"
                          onClick={() => handleSimulationAction(simulation.id, 'pause')}
                        >
                          <Pause className="w-3 h-3" />
                          Pause
                        </button>
                        <button 
                          className="btn btn-danger text-xs"
                          onClick={() => handleSimulationAction(simulation.id, 'stop')}
                        >
                          <Square className="w-3 h-3" />
                          Stop
                        </button>
                      </>
                    )}
                    {simulation.status === 'paused' && (
                      <button 
                        className="btn btn-success text-xs"
                        onClick={() => handleSimulationAction(simulation.id, 'start')}
                      >
                        <Play className="w-3 h-3" />
                        Resume
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">API Simulation</h3>
          </div>
          <div className="card-content">
            <p className="text-gray-400 mb-4">
              Generate synthetic API traffic using Swagger specifications
            </p>
            <button className="btn btn-primary w-full">
              <Globe className="w-4 h-4" />
              Start API Simulation
            </button>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Database Ingestion</h3>
          </div>
          <div className="card-content">
            <p className="text-gray-400 mb-4">
              Generate synthetic data directly into your database
            </p>
            <button className="btn btn-primary w-full">
              <Database className="w-4 h-4" />
              Start DB Ingestion
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;