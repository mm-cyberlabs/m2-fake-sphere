import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Common/Layout';
import Home from './pages/Home';
import Simulations from './pages/Simulations';
import Settings from './pages/Settings';
import History from './pages/History';
import { useAuthStore } from './stores/authStore';

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <Router>
      <div className="App">
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: 'var(--surface-bg)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border-color)',
            },
          }}
        />
        
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="simulations" element={<Simulations />} />
            <Route path="settings" element={<Settings />} />
            <Route path="history" element={<History />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </div>
    </Router>
  );
}

export default App;