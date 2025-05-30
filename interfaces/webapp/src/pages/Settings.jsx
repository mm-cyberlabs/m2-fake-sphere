import React from 'react';
import { Settings as SettingsIcon, User, Shield, Bell, Database } from 'lucide-react';

const Settings = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-gray-400 mt-1">
          Configure your Fake Sphere preferences and system settings
        </p>
      </div>

      {/* Settings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Settings */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center space-x-2">
              <User className="w-5 h-5 text-blue-400" />
              <h2 className="card-title">User Settings</h2>
            </div>
          </div>
          <div className="card-content space-y-4">
            <div className="form-group">
              <label className="form-label">Username</label>
              <input type="text" className="form-input" defaultValue="admin" />
            </div>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input type="email" className="form-input" defaultValue="admin@fakesphere.dev" />
            </div>
            <div className="form-group">
              <label className="form-label">Role</label>
              <select className="form-select" defaultValue="admin">
                <option value="admin">Administrator</option>
                <option value="operator">Operator</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>
            <button className="btn btn-primary">Save Changes</button>
          </div>
        </div>

        {/* Security Settings */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center space-x-2">
              <Shield className="w-5 h-5 text-green-400" />
              <h2 className="card-title">Security</h2>
            </div>
          </div>
          <div className="card-content space-y-4">
            <div className="form-group">
              <label className="form-label">Current Password</label>
              <input type="password" className="form-input" />
            </div>
            <div className="form-group">
              <label className="form-label">New Password</label>
              <input type="password" className="form-input" />
            </div>
            <div className="form-group">
              <label className="form-label">Confirm Password</label>
              <input type="password" className="form-input" />
            </div>
            <button className="btn btn-primary">Update Password</button>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center space-x-2">
              <Bell className="w-5 h-5 text-yellow-400" />
              <h2 className="card-title">Notifications</h2>
            </div>
          </div>
          <div className="card-content space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-white">Simulation Completion</p>
                <p className="text-sm text-gray-400">Get notified when simulations complete</p>
              </div>
              <input type="checkbox" className="form-checkbox" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-white">Error Alerts</p>
                <p className="text-sm text-gray-400">Receive alerts for simulation errors</p>
              </div>
              <input type="checkbox" className="form-checkbox" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-white">System Maintenance</p>
                <p className="text-sm text-gray-400">Updates about system maintenance</p>
              </div>
              <input type="checkbox" className="form-checkbox" />
            </div>
            <button className="btn btn-primary">Save Preferences</button>
          </div>
        </div>

        {/* System Settings */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center space-x-2">
              <SettingsIcon className="w-5 h-5 text-purple-400" />
              <h2 className="card-title">System</h2>
            </div>
          </div>
          <div className="card-content space-y-4">
            <div className="form-group">
              <label className="form-label">Default Theme</label>
              <select className="form-select" defaultValue="dark">
                <option value="dark">Dark</option>
                <option value="light">Light</option>
                <option value="auto">Auto</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Time Zone</label>
              <select className="form-select" defaultValue="UTC">
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
                <option value="Europe/London">London</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Auto-refresh Interval</label>
              <select className="form-select" defaultValue="5">
                <option value="1">1 second</option>
                <option value="5">5 seconds</option>
                <option value="10">10 seconds</option>
                <option value="30">30 seconds</option>
              </select>
            </div>
            <button className="btn btn-primary">Apply Settings</button>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center space-x-2">
            <Database className="w-5 h-5 text-cyan-400" />
            <h2 className="card-title">System Information</h2>
          </div>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="font-medium text-white mb-2">Version</h3>
              <p className="text-gray-400">Fake Sphere v0.1.0</p>
            </div>
            <div>
              <h3 className="font-medium text-white mb-2">Uptime</h3>
              <p className="text-gray-400">2 days, 14 hours</p>
            </div>
            <div>
              <h3 className="font-medium text-white mb-2">Last Updated</h3>
              <p className="text-gray-400">2 hours ago</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;