import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Play, 
  Pause, 
  Square, 
  Trash2, 
  Eye, 
  Filter,
  Search,
  Globe,
  Database,
  Clock,
  TrendingUp,
  AlertCircle
} from 'lucide-react';
import { simulationsAPI } from '../services/api';
import toast from 'react-hot-toast';

const Simulations = () => {
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSimulation, setSelectedSimulation] = useState(null);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadSimulations();
  }, [filter]);

  const loadSimulations = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { status: filter } : {};
      const response = await simulationsAPI.getAll(params);
      setSimulations(response.data.simulations || []);
    } catch (error) {
      console.error('Error loading simulations:', error);
      toast.error('Failed to load simulations');
    } finally {
      setLoading(false);
    }
  };

  const handleSimulationAction = async (simulationId, action) => {
    try {
      switch (action) {
        case 'start':
          await simulationsAPI.start(simulationId);
          toast.success('Simulation started');
          break;
        case 'pause':
          await simulationsAPI.pause(simulationId);
          toast.success('Simulation paused');
          break;
        case 'resume':
          await simulationsAPI.resume(simulationId);
          toast.success('Simulation resumed');
          break;
        case 'stop':
          await simulationsAPI.stop(simulationId);
          toast.success('Simulation stopped');
          break;
        case 'delete':
          await simulationsAPI.delete(simulationId);
          toast.success('Simulation deleted');
          break;
        default:
          break;
      }
      loadSimulations();
    } catch (error) {
      console.error(`Error ${action}ing simulation:`, error);
      toast.error(`Failed to ${action} simulation`);
    }
  };

  const getStatusBadge = (status) => {
    const baseClasses = 'px-2 py-1 text-xs font-semibold rounded-full';
    switch (status) {
      case 'running':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'paused':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'completed':
        return `${baseClasses} bg-blue-100 text-blue-800`;
      case 'failed':
        return `${baseClasses} bg-red-100 text-red-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const getTypeIcon = (type) => {
    return type === 'api' ? Globe : Database;
  };

  const filteredSimulations = simulations.filter(simulation =>
    simulation.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    simulation.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (startTime, endTime) => {
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const duration = Math.floor((end - start) / 1000);
    
    const hours = Math.floor(duration / 3600);
    const minutes = Math.floor((duration % 3600) / 60);
    const seconds = duration % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    } else {
      return `${seconds}s`;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Simulations</h1>
          <p className="text-gray-400 mt-1">
            Manage your API simulations and database ingestions
          </p>
        </div>
        <button className="btn btn-primary mt-4 sm:mt-0">
          <Plus className="w-4 h-4" />
          New Simulation
        </button>
      </div>

      {/* Filters and Search */}
      <div className="card">
        <div className="p-4 border-b border-slate-600">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0 sm:space-x-4">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search simulations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="form-input pl-10"
              />
            </div>

            {/* Filter */}
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="form-select"
              >
                <option value="all">All Status</option>
                <option value="running">Running</option>
                <option value="paused">Paused</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>
        </div>

        {/* Simulations List */}
        <div className="p-4">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="spinner"></div>
            </div>
          ) : filteredSimulations.length === 0 ? (
            <div className="text-center py-8">
              <Database className="w-12 h-12 text-gray-500 mx-auto mb-4" />
              <p className="text-gray-400 mb-4">
                {searchTerm ? 'No simulations found matching your search' : 'No simulations found'}
              </p>
              <button className="btn btn-primary">
                <Plus className="w-4 h-4" />
                Create Your First Simulation
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredSimulations.map((simulation) => {
                const TypeIcon = getTypeIcon(simulation.type);
                
                return (
                  <div 
                    key={simulation.id}
                    className="bg-slate-700 rounded-lg border border-slate-600 p-4 hover:border-slate-500 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4 flex-1">
                        <div className="p-2 bg-slate-600 rounded-lg">
                          <TypeIcon className="w-6 h-6 text-blue-400" />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="text-lg font-medium text-white truncate">
                              {simulation.name}
                            </h3>
                            <span className={getStatusBadge(simulation.status)}>
                              {simulation.status}
                            </span>
                          </div>
                          
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <p className="text-gray-400">Type</p>
                              <p className="text-white">
                                {simulation.type === 'api' ? 'API Simulation' : 'Database Ingestion'}
                              </p>
                            </div>
                            <div>
                              <p className="text-gray-400">Progress</p>
                              <p className="text-white">
                                {simulation.progress?.progress_percent?.toFixed(1) || 0}%
                              </p>
                            </div>
                            <div>
                              <p className="text-gray-400">Requests</p>
                              <p className="text-white">
                                {simulation.progress?.current_requests || 0} / {simulation.progress?.target_requests || 0}
                              </p>
                            </div>
                            <div>
                              <p className="text-gray-400">Started</p>
                              <p className="text-white">
                                {simulation.started_at ? formatDateTime(simulation.started_at) : 'Not started'}
                              </p>
                            </div>
                          </div>

                          {/* Progress Bar */}
                          {simulation.status === 'running' && (
                            <div className="mt-3">
                              <div className="w-full bg-slate-600 rounded-full h-2">
                                <div 
                                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                                  style={{ width: `${simulation.progress?.progress_percent || 0}%` }}
                                ></div>
                              </div>
                            </div>
                          )}

                          {/* Metrics for running simulations */}
                          {simulation.status === 'running' && simulation.progress && (
                            <div className="grid grid-cols-3 gap-4 mt-3 text-sm">
                              <div className="flex items-center space-x-2">
                                <TrendingUp className="w-4 h-4 text-green-400" />
                                <span className="text-gray-400">RPS:</span>
                                <span className="text-white">{simulation.progress.requests_per_second}</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Clock className="w-4 h-4 text-blue-400" />
                                <span className="text-gray-400">Avg:</span>
                                <span className="text-white">{simulation.progress.avg_response_time}ms</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <AlertCircle className="w-4 h-4 text-red-400" />
                                <span className="text-gray-400">Errors:</span>
                                <span className="text-white">{simulation.progress.error_count}</span>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center space-x-2 ml-4">
                        <button 
                          className="btn btn-secondary"
                          onClick={() => setSelectedSimulation(simulation)}
                        >
                          <Eye className="w-4 h-4" />
                        </button>

                        {simulation.status === 'running' && (
                          <>
                            <button 
                              className="btn btn-warning"
                              onClick={() => handleSimulationAction(simulation.id, 'pause')}
                            >
                              <Pause className="w-4 h-4" />
                            </button>
                            <button 
                              className="btn btn-danger"
                              onClick={() => handleSimulationAction(simulation.id, 'stop')}
                            >
                              <Square className="w-4 h-4" />
                            </button>
                          </>
                        )}

                        {simulation.status === 'paused' && (
                          <button 
                            className="btn btn-success"
                            onClick={() => handleSimulationAction(simulation.id, 'resume')}
                          >
                            <Play className="w-4 h-4" />
                          </button>
                        )}

                        {simulation.status === 'created' && (
                          <button 
                            className="btn btn-success"
                            onClick={() => handleSimulationAction(simulation.id, 'start')}
                          >
                            <Play className="w-4 h-4" />
                          </button>
                        )}

                        {['completed', 'failed', 'stopped'].includes(simulation.status) && (
                          <button 
                            className="btn btn-danger"
                            onClick={() => handleSimulationAction(simulation.id, 'delete')}
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Simulation Details Modal */}
      {selectedSimulation && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div 
              className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
              onClick={() => setSelectedSimulation(null)}
            ></div>
            
            <div className="relative bg-slate-800 rounded-lg max-w-2xl w-full max-h-screen overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-white">
                    Simulation Details
                  </h2>
                  <button 
                    onClick={() => setSelectedSimulation(null)}
                    className="text-gray-400 hover:text-white"
                  >
                    ×
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium text-white mb-2">Basic Information</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-400">Name</p>
                        <p className="text-white">{selectedSimulation.name}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Type</p>
                        <p className="text-white">
                          {selectedSimulation.type === 'api' ? 'API Simulation' : 'Database Ingestion'}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400">Status</p>
                        <span className={getStatusBadge(selectedSimulation.status)}>
                          {selectedSimulation.status}
                        </span>
                      </div>
                      <div>
                        <p className="text-gray-400">Created</p>
                        <p className="text-white">{formatDateTime(selectedSimulation.created_at)}</p>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-medium text-white mb-2">Configuration</h3>
                    <div className="bg-slate-700 rounded-lg p-4">
                      <pre className="text-sm text-gray-300 overflow-x-auto">
                        {JSON.stringify(selectedSimulation.configuration, null, 2)}
                      </pre>
                    </div>
                  </div>

                  {selectedSimulation.progress && (
                    <div>
                      <h3 className="font-medium text-white mb-2">Progress</h3>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-400">Completion</p>
                          <p className="text-white">{selectedSimulation.progress.progress_percent?.toFixed(1)}%</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Requests</p>
                          <p className="text-white">
                            {selectedSimulation.progress.current_requests} / {selectedSimulation.progress.target_requests}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-400">Rate</p>
                          <p className="text-white">{selectedSimulation.progress.requests_per_second} RPS</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Errors</p>
                          <p className="text-white">{selectedSimulation.progress.error_count}</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Simulations;