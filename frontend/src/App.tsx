import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './index.css';
import Login from './pages/Login';
import Signup from './pages/Signup';
import DisruptiveFeatures from './pages/DisruptiveFeatures';
import ProtectedRoute from './components/ProtectedRoute';
import TradingDashboard from './components/TradingDashboard';
import Optimization from './pages/Optimization';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/features" element={<DisruptiveFeatures />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <TradingDashboard />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/optimization"
            element={
              <ProtectedRoute>
                <Optimization />
              </ProtectedRoute>
            }
          />

          {/* Default redirects */}
          <Route path="/" element={<Navigate to="/features" replace />} />
          <Route path="*" element={<Navigate to="/features" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
