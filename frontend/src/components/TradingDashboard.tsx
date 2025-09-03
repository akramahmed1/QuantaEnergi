import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { getPredictions, getPortfolioData, getMarketData } from '../services/api';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface TradingData {
  timestamp: string;
  price: number;
  volume: number;
  commodity: string;
}

interface PortfolioPosition {
  commodity: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercentage: number;
}

interface AGIPrediction {
  timestamp: string;
  predictedPrice: number;
  confidence: number;
  strategy: string;
}

const TradingDashboard: React.FC = () => {
  // State management
  const [predictions, setPredictions] = useState<AGIPrediction[]>([]);
  const [portfolioData, setPortfolioData] = useState<PortfolioPosition[]>([]);
  const [marketData, setMarketData] = useState<TradingData[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('Connecting...');
  const [selectedCommodity, setSelectedCommodity] = useState('crude_oil');
  const [timeframe, setTimeframe] = useState('1D');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // WebSocket connection
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        // TODO: Replace with real WebSocket endpoint
        const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
        const websocket = new WebSocket(wsUrl);

        websocket.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);
          setConnectionStatus('Connected');
          setError(null);
        };

        websocket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
          } catch (err) {
            console.error('Failed to parse WebSocket message:', err);
          }
        };

        websocket.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);
          setConnectionStatus('Disconnected');
          // Attempt to reconnect after 5 seconds
          setTimeout(connectWebSocket, 5000);
        };

        websocket.onerror = (error) => {
          console.error('WebSocket error:', error);
          setError('WebSocket connection failed');
          setIsConnected(false);
          setConnectionStatus('Error');
        };

        setWs(websocket);

        return () => {
          websocket.close();
        };
      } catch (err) {
        console.error('Failed to create WebSocket:', err);
        setError('Failed to establish WebSocket connection');
      }
    };

    connectWebSocket();
  }, []);

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((data: any) => {
    if (data.type === 'market_update') {
      setMarketData(prev => [...prev, data.data].slice(-100)); // Keep last 100 data points
    } else if (data.type === 'prediction_update') {
      setPredictions(prev => [...prev, data.data].slice(-50)); // Keep last 50 predictions
    } else if (data.type === 'portfolio_update') {
      setPortfolioData(data.data);
    }
  }, []);

  // Fetch initial data
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        
        // Fetch AGI predictions
        const predictionsData = await getPredictions();
        setPredictions(predictionsData.predictions || []);

        // Fetch portfolio data
        const portfolio = await getPortfolioData();
        setPortfolioData(portfolio.positions || []);

        // Fetch market data
        const market = await getMarketData();
        setMarketData(market.data || []);

        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch initial data:', err);
        setError('Failed to load trading data');
        setLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  // Chart data preparation
  const priceChartData = useMemo(() => ({
    labels: marketData.map(d => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'Market Price',
        data: marketData.map(d => d.price),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'AGI Prediction',
        data: predictions.map(p => p.predictedPrice),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        fill: false,
        tension: 0.4,
        borderDash: [5, 5],
      },
    ],
  }), [marketData, predictions]);

  const volumeChartData = useMemo(() => ({
    labels: marketData.map(d => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'Trading Volume',
        data: marketData.map(d => d.volume),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgb(54, 162, 235)',
        borderWidth: 1,
      },
    ],
  }), [marketData]);

  const portfolioChartData = useMemo(() => ({
    labels: portfolioData.map(p => p.commodity),
    datasets: [
      {
        label: 'Portfolio Value',
        data: portfolioData.map(p => p.quantity * p.currentPrice),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
        ],
        borderWidth: 2,
      },
    ],
  }), [portfolioData]);

  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'QuantaEnergi Trading Dashboard',
      },
    },
    scales: {
      y: {
        beginAtZero: false,
      },
    },
  };

  // Calculate portfolio metrics
  const portfolioMetrics = useMemo(() => {
    const totalValue = portfolioData.reduce((sum, pos) => sum + (pos.quantity * pos.currentPrice), 0);
    const totalPnL = portfolioData.reduce((sum, pos) => sum + pos.pnl, 0);
    const totalPnLPercentage = totalValue > 0 ? (totalPnL / totalValue) * 100 : 0;
    
    return {
      totalValue,
      totalPnL,
      totalPnLPercentage,
      positionCount: portfolioData.length,
    };
  }, [portfolioData]);

  // Handle commodity selection
  const handleCommodityChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCommodity(event.target.value);
  };

  // Handle timeframe change
  const handleTimeframeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setTimeframe(event.target.value);
  };

  // Render loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
        <span className="ml-4 text-lg">Loading trading dashboard...</span>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="trading-dashboard bg-gray-50 min-h-screen p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          QuantaEnergi Trading Dashboard
        </h1>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-600">{connectionStatus}</span>
          </div>
          <span className="text-sm text-gray-500">
            Last updated: {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Controls */}
      <div className="mb-6 flex flex-wrap gap-4">
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Commodity:</label>
          <select
            value={selectedCommodity}
            onChange={handleCommodityChange}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm"
          >
            <option value="crude_oil">Crude Oil</option>
            <option value="natural_gas">Natural Gas</option>
            <option value="electricity">Electricity</option>
            <option value="coal">Coal</option>
            <option value="renewables">Renewables</option>
          </select>
        </div>
        
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Timeframe:</label>
          <select
            value={timeframe}
            onChange={handleTimeframeChange}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm"
          >
            <option value="1H">1 Hour</option>
            <option value="1D">1 Day</option>
            <option value="1W">1 Week</option>
            <option value="1M">1 Month</option>
          </select>
        </div>
      </div>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Portfolio Value</h3>
          <p className="text-3xl font-bold text-blue-600">
            ${portfolioMetrics.totalValue.toLocaleString()}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Total P&L</h3>
          <p className={`text-3xl font-bold ${portfolioMetrics.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            ${portfolioMetrics.totalPnL.toLocaleString()}
          </p>
          <p className={`text-sm ${portfolioMetrics.totalPnLPercentage >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {portfolioMetrics.totalPnLPercentage.toFixed(2)}%
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Positions</h3>
          <p className="text-3xl font-bold text-purple-600">{portfolioMetrics.positionCount}</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">AGI Confidence</h3>
          <p className="text-3xl font-bold text-orange-600">
            {predictions.length > 0 ? (predictions[predictions.length - 1]?.confidence * 100).toFixed(1) : 0}%
          </p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Price Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Price & Predictions</h3>
          <div className="h-80">
            <Line data={priceChartData} options={chartOptions} />
          </div>
        </div>

        {/* Volume Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Trading Volume</h3>
          <div className="h-80">
            <Bar data={volumeChartData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Portfolio Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Portfolio Distribution</h3>
          <div className="h-80">
            <Doughnut data={portfolioChartData} options={chartOptions} />
          </div>
        </div>

        {/* Positions Table */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Current Positions</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Commodity</th>
                  <th className="text-left py-2">Quantity</th>
                  <th className="text-left py-2">Avg Price</th>
                  <th className="text-left py-2">Current</th>
                  <th className="text-left py-2">P&L</th>
                </tr>
              </thead>
              <tbody>
                {portfolioData.map((position, index) => (
                  <tr key={index} className="border-b">
                    <td className="py-2 capitalize">{position.commodity.replace('_', ' ')}</td>
                    <td className="py-2">{position.quantity.toLocaleString()}</td>
                    <td className="py-2">${position.avgPrice.toFixed(2)}</td>
                    <td className="py-2">${position.currentPrice.toFixed(2)}</td>
                    <td className={`py-2 ${position.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ${position.pnl.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* AGI Predictions */}
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">AGI Trading Predictions</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">Timestamp</th>
                <th className="text-left py-2">Predicted Price</th>
                <th className="text-left py-2">Confidence</th>
                <th className="text-left py-2">Strategy</th>
              </tr>
            </thead>
            <tbody>
              {predictions.slice(-10).reverse().map((prediction, index) => (
                <tr key={index} className="border-b">
                  <td className="py-2">{new Date(prediction.timestamp).toLocaleString()}</td>
                  <td className="py-2">${prediction.predictedPrice.toFixed(2)}</td>
                  <td className="py-2">{(prediction.confidence * 100).toFixed(1)}%</td>
                  <td className="py-2">{prediction.strategy}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center text-sm text-gray-500">
        <p>QuantaEnergi Trading Platform - Powered by Advanced AI & Quantum Computing</p>
        <p className="mt-1">Real-time data updates via WebSocket • AGI-powered predictions • Islamic-compliant trading</p>
      </div>
    </div>
  );
};

export default TradingDashboard;