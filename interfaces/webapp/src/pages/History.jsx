import React from 'react';
import { History as HistoryIcon, Download, Trash2, Eye } from 'lucide-react';

const History = () => {
  // Mock data - in real app this would come from API
  const historyData = [
    {
      id: 'sim_001',
      name: 'Petstore API Test',
      type: 'api',
      status: 'completed',
      started_at: '2024-01-20T10:30:00Z',
      completed_at: '2024-01-20T11:15:00Z',
      total_requests: 2000,
      success_rate: 97.5,
      avg_response_time: 245
    },
    {
      id: 'sim_002',
      name: 'User Database Seed',
      type: 'database',
      status: 'completed',
      started_at: '2024-01-20T09:00:00Z',
      completed_at: '2024-01-20T09:45:00Z',
      total_requests: 5000,
      success_rate: 99.8,
      avg_response_time: 89
    },
    {
      id: 'sim_003',
      name: 'E-commerce API Load Test',
      type: 'api',
      status: 'failed',
      started_at: '2024-01-19T15:20:00Z',
      completed_at: '2024-01-19T15:35:00Z',
      total_requests: 856,
      success_rate: 45.2,
      avg_response_time: 1200
    }
  ];

  const getStatusBadge = (status) => {
    const baseClasses = 'px-2 py-1 text-xs font-semibold rounded-full';
    switch (status) {
      case 'completed':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'failed':
        return `${baseClasses} bg-red-100 text-red-800`;
      case 'stopped':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (start, end) => {
    const duration = new Date(end) - new Date(start);
    const minutes = Math.floor(duration / 60000);
    const seconds = Math.floor((duration % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Simulation History</h1>
          <p className="text-gray-400 mt-1">
            View and analyze past simulation results
          </p>
        </div>
        <div className="flex space-x-2 mt-4 sm:mt-0">
          <button className="btn btn-secondary">
            <Download className="w-4 h-4" />
            Export All
          </button>
          <button className="btn btn-danger">
            <Trash2 className="w-4 h-4" />
            Clear History
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="p-4 border-b border-slate-600">
          <div className="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search simulations..."
                className="form-input"
              />
            </div>
            <div className="flex space-x-2">
              <select className="form-select">
                <option value="all">All Types</option>
                <option value="api">API Simulation</option>
                <option value="database">Database Ingestion</option>
              </select>
              <select className="form-select">
                <option value="all">All Status</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="stopped">Stopped</option>
              </select>
            </div>
          </div>
        </div>

        {/* History Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-700 border-b border-slate-600">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Simulation
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Requests
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Success Rate
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-600">
              {historyData.map((simulation) => (
                <tr key={simulation.id} className="hover:bg-slate-700 transition-colors">
                  <td className="px-4 py-4">
                    <div>
                      <div className="font-medium text-white">{simulation.name}</div>
                      <div className="text-sm text-gray-400">
                        Started: {formatDateTime(simulation.started_at)}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-sm text-gray-300">
                      {simulation.type === 'api' ? 'API Simulation' : 'Database Ingestion'}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className={getStatusBadge(simulation.status)}>
                      {simulation.status}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-sm text-gray-300">
                      {formatDuration(simulation.started_at, simulation.completed_at)}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-sm text-gray-300">
                      {simulation.total_requests?.toLocaleString()}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center">
                      <span className={`text-sm font-medium ${
                        simulation.success_rate >= 95 ? 'text-green-400' :
                        simulation.success_rate >= 80 ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {simulation.success_rate}%
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex space-x-2">
                      <button className="btn btn-secondary text-xs">
                        <Eye className="w-3 h-3" />
                        View
                      </button>
                      <button className="btn btn-secondary text-xs">
                        <Download className="w-3 h-3" />
                        Export
                      </button>
                      <button className="btn btn-danger text-xs">
                        <Trash2 className="w-3 h-3" />
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-slate-600">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-400">
              Showing 1 to 3 of 3 results
            </div>
            <div className="flex space-x-2">
              <button className="btn btn-secondary text-xs" disabled>
                Previous
              </button>
              <button className="btn btn-secondary text-xs" disabled>
                Next
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-white">15</div>
            <div className="text-sm text-gray-400">Total Simulations</div>
          </div>
        </div>
        <div className="card p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">12</div>
            <div className="text-sm text-gray-400">Completed</div>
          </div>
        </div>
        <div className="card p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-400">2</div>
            <div className="text-sm text-gray-400">Failed</div>
          </div>
        </div>
        <div className="card p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-400">1</div>
            <div className="text-sm text-gray-400">Stopped</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default History;