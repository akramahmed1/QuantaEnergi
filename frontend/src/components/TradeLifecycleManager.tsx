import React, { useState, useEffect } from 'react';
import {
  captureTrade,
  validateTrade,
  generateConfirmation,
  allocateTrade,
  processSettlement,
  generateInvoice,
  processPayment,
  getTradeStatus,
  getUserTrades,
  cancelTrade,
  TradeCreate,
  TradeResponse,
  TradeStatusResponse,
  formatCurrency,
  formatDate,
  calculatePnL,
  calculatePnLPercentage
} from '../services/tradingApi';

interface TradeLifecycleManagerProps {
  userId?: string;
}

const TradeLifecycleManager: React.FC<TradeLifecycleManagerProps> = ({ userId = 'user123' }) => {
  // State management
  const [trades, setTrades] = useState<TradeResponse[]>([]);
  const [selectedTrade, setSelectedTrade] = useState<TradeResponse | null>(null);
  const [tradeStatus, setTradeStatus] = useState<TradeStatusResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'capture' | 'manage' | 'monitor'>('capture');

  // Form state for new trade
  const [newTrade, setNewTrade] = useState<TradeCreate>({
    trade_type: 'forward',
    commodity: 'crude_oil',
    quantity: 1000,
    price: 85.50,
    currency: 'USD',
    counterparty: 'CP001',
    delivery_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    delivery_location: 'Houston, TX',
    additional_terms: {}
  });

  // Load user trades on component mount
  useEffect(() => {
    loadUserTrades();
  }, []);

  const loadUserTrades = async () => {
    try {
      setLoading(true);
      const userTrades = await getUserTrades();
      setTrades(userTrades);
    } catch (err) {
      setError('Failed to load trades');
      console.error('Error loading trades:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTradeCapture = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const capturedTrade = await captureTrade(newTrade);
      setTrades(prev => [capturedTrade, ...prev]);
      
      // Reset form
      setNewTrade({
        trade_type: 'forward',
        commodity: 'crude_oil',
        quantity: 1000,
        price: 85.50,
        currency: 'USD',
        counterparty: 'CP001',
        delivery_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        delivery_location: 'Houston, TX',
        additional_terms: {}
      });
      
      alert('Trade captured successfully!');
    } catch (err) {
      setError('Failed to capture trade');
      console.error('Error capturing trade:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTradeAction = async (tradeId: string, action: string, data?: any) => {
    try {
      setLoading(true);
      setError(null);
      
      let result;
      switch (action) {
        case 'validate':
          result = await validateTrade(tradeId);
          setTradeStatus(result);
          break;
        case 'confirm':
          result = await generateConfirmation(tradeId);
          break;
        case 'allocate':
          result = await allocateTrade(tradeId, data || { account: 'ACC001', portfolio: 'PORT001' });
          break;
        case 'settle':
          result = await processSettlement(tradeId, data || { settlement_method: 'wire_transfer', bank_details: 'BANK001' });
          break;
        case 'invoice':
          result = await generateInvoice(tradeId);
          break;
        case 'payment':
          result = await processPayment(tradeId, data || { payment_method: 'credit_card', card_number: '****1234' });
          break;
        case 'cancel':
          result = await cancelTrade(tradeId);
          break;
        default:
          throw new Error('Unknown action');
      }
      
      // Refresh trades list
      await loadUserTrades();
      alert(`${action.charAt(0).toUpperCase() + action.slice(1)} completed successfully!`);
    } catch (err) {
      setError(`Failed to ${action} trade`);
      console.error(`Error ${action}ing trade:`, err);
    } finally {
      setLoading(false);
    }
  };

  const getTradeStatusColor = (status: string) => {
    const statusColors: Record<string, string> = {
      captured: 'bg-blue-100 text-blue-800',
      validated: 'bg-green-100 text-green-800',
      confirmed: 'bg-purple-100 text-purple-800',
      allocated: 'bg-indigo-100 text-indigo-800',
      settled: 'bg-emerald-100 text-emerald-800',
      invoiced: 'bg-amber-100 text-amber-800',
      paid: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
      failed: 'bg-red-100 text-red-800'
    };
    return statusColors[status] || 'bg-gray-100 text-gray-800';
  };

  const getTradeTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      spot: '⚡',
      forward: '📅',
      futures: '📊',
      options: '🎯',
      swap: '🔄',
      murabaha: '☪️',
      sukuk: '🏛️'
    };
    return icons[type] || '📋';
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Trade Lifecycle Management</h1>
        <p className="text-gray-600">Complete ETRM/CTRM trade lifecycle from capture to settlement</p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'capture', label: 'Capture Trade', icon: '➕' },
            { id: 'manage', label: 'Manage Trades', icon: '📋' },
            { id: 'monitor', label: 'Monitor Status', icon: '📊' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Trade Capture Tab */}
      {activeTab === 'capture' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Capture New Trade</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Trade Type</label>
              <select
                value={newTrade.trade_type}
                onChange={(e) => setNewTrade(prev => ({ ...prev, trade_type: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="spot">Spot</option>
                <option value="forward">Forward</option>
                <option value="futures">Futures</option>
                <option value="options">Options</option>
                <option value="swap">Swap</option>
                <option value="murabaha">Murabaha (Islamic)</option>
                <option value="sukuk">Sukuk (Islamic)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Commodity</label>
              <select
                value={newTrade.commodity}
                onChange={(e) => setNewTrade(prev => ({ ...prev, commodity: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="crude_oil">Crude Oil</option>
                <option value="natural_gas">Natural Gas</option>
                <option value="electricity">Electricity</option>
                <option value="renewables">Renewables</option>
                <option value="carbon_credits">Carbon Credits</option>
                <option value="lng">LNG</option>
                <option value="lpg">LPG</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
              <input
                type="number"
                value={newTrade.quantity}
                onChange={(e) => setNewTrade(prev => ({ ...prev, quantity: parseFloat(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="1000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Price</label>
              <input
                type="number"
                step="0.01"
                value={newTrade.price}
                onChange={(e) => setNewTrade(prev => ({ ...prev, price: parseFloat(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="85.50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Currency</label>
              <select
                value={newTrade.currency}
                onChange={(e) => setNewTrade(prev => ({ ...prev, currency: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="SAR">SAR</option>
                <option value="AED">AED</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Counterparty</label>
              <input
                type="text"
                value={newTrade.counterparty}
                onChange={(e) => setNewTrade(prev => ({ ...prev, counterparty: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="CP001"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Date</label>
              <input
                type="date"
                value={newTrade.delivery_date}
                onChange={(e) => setNewTrade(prev => ({ ...prev, delivery_date: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Location</label>
              <input
                type="text"
                value={newTrade.delivery_location}
                onChange={(e) => setNewTrade(prev => ({ ...prev, delivery_location: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Houston, TX"
              />
            </div>
          </div>

          <div className="mt-6">
            <button
              onClick={handleTradeCapture}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Capturing Trade...' : 'Capture Trade'}
            </button>
          </div>
        </div>
      )}

      {/* Trade Management Tab */}
      {activeTab === 'manage' && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold">Manage Trades</h2>
            <p className="text-sm text-gray-600 mt-1">View and manage your active trades</p>
          </div>
          
          {loading ? (
            <div className="p-6 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading trades...</p>
            </div>
          ) : trades.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              <p>No trades found. Capture a new trade to get started.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trade</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Details</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {trades.map((trade) => (
                    <tr key={trade.trade_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className="text-2xl mr-3">{getTradeTypeIcon(trade.trade_type || 'unknown')}</span>
                          <div>
                            <div className="text-sm font-medium text-gray-900">{trade.trade_id}</div>
                            <div className="text-sm text-gray-500">{formatDate(trade.timestamp)}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          <div>Type: {trade.trade_type || 'Unknown'}</div>
                          <div>Status: {trade.status}</div>
                          <div>Message: {trade.message}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getTradeStatusColor(trade.status)}`}>
                          {trade.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleTradeAction(trade.trade_id, 'validate')}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Validate
                          </button>
                          <button
                            onClick={() => handleTradeAction(trade.trade_id, 'confirm')}
                            className="text-green-600 hover:text-green-900"
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => handleTradeAction(trade.trade_id, 'allocate')}
                            className="text-purple-600 hover:text-purple-900"
                          >
                            Allocate
                          </button>
                          <button
                            onClick={() => handleTradeAction(trade.trade_id, 'settle')}
                            className="text-indigo-600 hover:text-indigo-900"
                          >
                            Settle
                          </button>
                          <button
                            onClick={() => handleTradeAction(trade.trade_id, 'cancel')}
                            className="text-red-600 hover:text-red-900"
                          >
                            Cancel
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Trade Monitoring Tab */}
      {activeTab === 'monitor' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Trade Status Monitoring</h2>
          
          {selectedTrade ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Trade: {selectedTrade.trade_id}</h3>
                <button
                  onClick={() => setSelectedTrade(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
              
              {tradeStatus ? (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium mb-2">Current Status: {tradeStatus.status}</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Trade ID:</span> {tradeStatus.trade_id}
                    </div>
                    <div>
                      <span className="font-medium">Timestamp:</span> {formatDate(tradeStatus.timestamp)}
                    </div>
                  </div>
                  {tradeStatus.details && Object.keys(tradeStatus.details).length > 0 && (
                    <div className="mt-4">
                      <h5 className="font-medium mb-2">Details:</h5>
                      <pre className="bg-white p-2 rounded text-xs overflow-auto">
                        {JSON.stringify(tradeStatus.details, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500 mb-4">Select a trade to view its status</p>
                  <button
                    onClick={() => handleTradeAction(selectedTrade.trade_id, 'validate')}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                  >
                    Check Status
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">Select a trade from the Manage Trades tab to monitor its status</p>
            </div>
          )}
        </div>
      )}

      {/* Summary Statistics */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <span className="text-2xl">📊</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Trades</p>
              <p className="text-2xl font-semibold text-gray-900">{trades.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <span className="text-2xl">✅</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Trades</p>
              <p className="text-2xl font-semibold text-gray-900">
                {trades.filter(t => !['settled', 'cancelled', 'failed'].includes(t.status)).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <span className="text-2xl">⏳</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-2xl font-semibold text-gray-900">
                {trades.filter(t => ['captured', 'validated'].includes(t.status)).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <span className="text-2xl">⚠️</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Issues</p>
              <p className="text-2xl font-semibold text-gray-900">
                {trades.filter(t => ['failed'].includes(t.status)).length}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradeLifecycleManager;
