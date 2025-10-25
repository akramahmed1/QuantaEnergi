import React, { useState, useEffect } from 'react';
import './App.css';

// Types
interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

interface Trade {
  id: string;
  asset: string;
  quantity: number;
  price: number;
  side: string;
  status: string;
  timestamp: string;
  trader_id: string;
}

interface PortfolioPosition {
  asset: string;
  quantity: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
}

// API Service
class ETMRApiService {
  private baseUrl = 'http://localhost:8000';
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    };

    const response = await fetch(url, { ...options, headers });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  async login(username: string, password: string): Promise<LoginResponse> {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async logout(): Promise<void> {
    return this.request('/auth/logout', { method: 'POST' });
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    return this.request('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });
  }

  async getTrades(): Promise<Trade[]> {
    return this.request('/trading/trades');
  }

  async createTrade(asset: string, quantity: number, price: number, side: string): Promise<Trade> {
    return this.request('/trading/trades', {
      method: 'POST',
      body: JSON.stringify({ asset, quantity, price, side }),
    });
  }

  async updateTrade(tradeId: string, status: string): Promise<void> {
    return this.request(`/trading/trades/${tradeId}`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  async getRiskMetrics(): Promise<any> {
    return this.request('/risk/metrics');
  }

  async getPortfolioOverview(): Promise<any> {
    return this.request('/portfolio/overview');
  }

  async getAnalyticsPerformance(): Promise<any> {
    return this.request('/analytics/performance');
  }

  async getComplianceStatus(): Promise<any> {
    return this.request('/compliance/status');
  }

  async getDashboardStats(): Promise<any> {
    return this.request('/dashboard/stats');
  }
}

const apiService = new ETMRApiService();

// Main App Component
const App: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Dashboard Data
  const [dashboardStats, setDashboardStats] = useState<any>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [portfolio, setPortfolio] = useState<any>(null);
  const [riskMetrics, setRiskMetrics] = useState<any>(null);

  // Login Form
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });

  // Password Change Form
  const [passwordForm, setPasswordForm] = useState({ 
    currentPassword: '', 
    newPassword: '', 
    confirmPassword: '' 
  });

  // New Trade Form
  const [tradeForm, setTradeForm] = useState({
    asset: '',
    quantity: 0,
    price: 0,
    side: 'buy'
  });

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const userData = localStorage.getItem('user_data');
    
    if (token && userData) {
      apiService.setToken(token);
      setUser(JSON.parse(userData));
      setIsLoggedIn(true);
      loadDashboardData();
    }
  }, []);

  const loadDashboardData = async () => {
    try {
      const [stats, tradesData, portfolioData, riskData] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.getTrades(),
        apiService.getPortfolioOverview(),
        apiService.getRiskMetrics()
      ]);

      setDashboardStats(stats);
      setTrades(tradesData);
      setPortfolio(portfolioData);
      setRiskMetrics(riskData);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await apiService.login(loginForm.username, loginForm.password);
      
      apiService.setToken(response.access_token);
      setUser(response.user);
      setIsLoggedIn(true);
      
      localStorage.setItem('auth_token', response.access_token);
      localStorage.setItem('user_data', JSON.stringify(response.user));
      
      await loadDashboardData();
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await apiService.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      apiService.setToken('');
      setUser(null);
      setIsLoggedIn(false);
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    try {
      await apiService.changePassword(passwordForm.currentPassword, passwordForm.newPassword);
      setError('');
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
      alert('Password changed successfully');
    } catch (err: any) {
      setError(err.message || 'Password change failed');
    }
  };

  const handleCreateTrade = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.createTrade(
        tradeForm.asset,
        tradeForm.quantity,
        tradeForm.price,
        tradeForm.side
      );
      setTradeForm({ asset: '', quantity: 0, price: 0, side: 'buy' });
      await loadDashboardData();
      alert('Trade created successfully');
    } catch (err: any) {
      setError(err.message || 'Trade creation failed');
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <h1>QuantaEnergi ETRM/CTRM</h1>
            <p>Enterprise Energy Trading Platform</p>
          </div>
          
          <form onSubmit={handleLogin} className="login-form">
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                value={loginForm.username}
                onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                required
              />
            </div>
            
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                required
              />
            </div>
            
            {error && <div className="error-message">{error}</div>}
            
            <button type="submit" className="login-btn" disabled={loading}>
              {loading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>
          
          <div className="login-footer">
            <h4>Demo Credentials</h4>
            <p><strong>Admin:</strong> admin / QuantaEnergi2024!</p>
            <p><strong>Trader:</strong> trader / trader123</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-left">
          <h1>QuantaEnergi ETRM/CTRM</h1>
          <span className="version">v2.0.0</span>
        </div>
        <div className="header-center">
          <div className="user-info">
            <span className="user-name">Welcome, {user?.username}</span>
            <span className="user-role">{user?.role}</span>
          </div>
        </div>
        <div className="header-right">
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      {/* Navigation */}
      <nav className="app-nav">
        {['dashboard', 'trading', 'portfolio', 'risk', 'analytics', 'compliance', 'settings'].map(tab => (
          <button
            key={tab}
            className={`nav-item ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </nav>

      {/* Main Content */}
      <main className="app-main">
        {activeTab === 'dashboard' && (
          <div className="dashboard">
            <h2>Dashboard</h2>
            {dashboardStats && (
              <div className="stats-grid">
                <div className="stat-card">
                  <h3>Total Trades</h3>
                  <div className="stat-value">{dashboardStats.total_trades}</div>
                </div>
                <div className="stat-card">
                  <h3>Total Volume</h3>
                  <div className="stat-value">${dashboardStats.total_volume?.toLocaleString()}</div>
                </div>
                <div className="stat-card">
                  <h3>Total P&L</h3>
                  <div className="stat-value">${dashboardStats.total_pnl?.toLocaleString()}</div>
                </div>
                <div className="stat-card">
                  <h3>Risk Exposure</h3>
                  <div className="stat-value">${dashboardStats.risk_exposure?.toLocaleString()}</div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'trading' && (
          <div className="trading">
            <h2>Trading Desk</h2>
            
            <div className="trading-forms">
              <form onSubmit={handleCreateTrade} className="trade-form">
                <h3>Create New Trade</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label>Asset</label>
                    <input
                      type="text"
                      value={tradeForm.asset}
                      onChange={(e) => setTradeForm({ ...tradeForm, asset: e.target.value })}
                      placeholder="e.g., ELEC_SPOT"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Quantity</label>
                    <input
                      type="number"
                      value={tradeForm.quantity}
                      onChange={(e) => setTradeForm({ ...tradeForm, quantity: Number(e.target.value) })}
                      required
                    />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>Price</label>
                    <input
                      type="number"
                      step="0.01"
                      value={tradeForm.price}
                      onChange={(e) => setTradeForm({ ...tradeForm, price: Number(e.target.value) })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Side</label>
                    <select
                      value={tradeForm.side}
                      onChange={(e) => setTradeForm({ ...tradeForm, side: e.target.value })}
                    >
                      <option value="buy">Buy</option>
                      <option value="sell">Sell</option>
                    </select>
                  </div>
                </div>
                <button type="submit" className="submit-btn">Create Trade</button>
              </form>
            </div>

            <div className="trades-table">
              <h3>Recent Trades</h3>
              <table>
                <thead>
                  <tr>
                    <th>Asset</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Side</th>
                    <th>Status</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.map(trade => (
                    <tr key={trade.id}>
                      <td>{trade.asset}</td>
                      <td>{trade.quantity}</td>
                      <td>${trade.price}</td>
                      <td className={trade.side}>{trade.side}</td>
                      <td className={trade.status}>{trade.status}</td>
                      <td>{new Date(trade.timestamp).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'portfolio' && (
          <div className="portfolio">
            <h2>Portfolio Management</h2>
            {portfolio && (
              <div className="portfolio-overview">
                <div className="portfolio-stats">
                  <div className="stat">
                    <label>Total Value</label>
                    <span>${portfolio.total_value?.toLocaleString()}</span>
                  </div>
                  <div className="stat">
                    <label>Total P&L</label>
                    <span>${portfolio.total_pnl?.toLocaleString()}</span>
                  </div>
                  <div className="stat">
                    <label>Risk Exposure</label>
                    <span>${portfolio.risk_exposure?.toLocaleString()}</span>
                  </div>
                </div>
                
                <div className="positions-table">
                  <h3>Positions</h3>
                  <table>
                    <thead>
                      <tr>
                        <th>Asset</th>
                        <th>Quantity</th>
                        <th>Current Price</th>
                        <th>Market Value</th>
                        <th>Unrealized P&L</th>
                      </tr>
                    </thead>
                    <tbody>
                      {portfolio.positions?.map((position: PortfolioPosition, index: number) => (
                        <tr key={index}>
                          <td>{position.asset}</td>
                          <td>{position.quantity}</td>
                          <td>${position.current_price}</td>
                          <td>${position.market_value?.toLocaleString()}</td>
                          <td className={position.unrealized_pnl >= 0 ? 'positive' : 'negative'}>
                            ${position.unrealized_pnl?.toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'risk' && (
          <div className="risk">
            <h2>Risk Management</h2>
            {riskMetrics && (
              <div className="risk-metrics">
                <div className="risk-card">
                  <h3>Value at Risk (VaR)</h3>
                  <div className="risk-value">${riskMetrics.var_95?.toLocaleString()}</div>
                  <div className="risk-label">95% Confidence</div>
                </div>
                <div className="risk-card">
                  <h3>Expected Shortfall</h3>
                  <div className="risk-value">${riskMetrics.expected_shortfall?.toLocaleString()}</div>
                  <div className="risk-label">99% Confidence</div>
                </div>
                <div className="risk-card">
                  <h3>Sharpe Ratio</h3>
                  <div className="risk-value">{riskMetrics.sharpe_ratio}</div>
                  <div className="risk-label">Risk-Adjusted Return</div>
                </div>
                <div className="risk-card">
                  <h3>Max Drawdown</h3>
                  <div className="risk-value">{(riskMetrics.max_drawdown * 100).toFixed(2)}%</div>
                  <div className="risk-label">Maximum Loss</div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="analytics">
            <h2>Analytics & Reporting</h2>
            <div className="analytics-content">
              <div className="chart-placeholder">
                <h3>Performance Analytics</h3>
                <p>Advanced analytics and reporting features will be displayed here.</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'compliance' && (
          <div className="compliance">
            <h2>Compliance & Reporting</h2>
            <div className="compliance-content">
              <div className="compliance-status">
                <h3>Compliance Status</h3>
                <div className="status-grid">
                  <div className="status-item">
                    <span className="status-label">Regulatory Compliance</span>
                    <span className="status-value compliant">Compliant</span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Risk Limits</span>
                    <span className="status-value compliant">Within Limits</span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Audit Trail</span>
                    <span className="status-value compliant">Complete</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="settings">
            <h2>Settings</h2>
            
            <div className="settings-section">
              <h3>Change Password</h3>
              <form onSubmit={handlePasswordChange} className="password-form">
                <div className="form-group">
                  <label>Current Password</label>
                  <input
                    type="password"
                    value={passwordForm.currentPassword}
                    onChange={(e) => setPasswordForm({ ...passwordForm, currentPassword: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>New Password</label>
                  <input
                    type="password"
                    value={passwordForm.newPassword}
                    onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Confirm New Password</label>
                  <input
                    type="password"
                    value={passwordForm.confirmPassword}
                    onChange={(e) => setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })}
                    required
                  />
                </div>
                <button type="submit" className="submit-btn">Change Password</button>
              </form>
            </div>

            {error && <div className="error-message">{error}</div>}
          </div>
        )}
      </main>
    </div>
  );
};

export default App;