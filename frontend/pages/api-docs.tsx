/**
 * QuantaEnergi API Documentation Page
 * Interactive Swagger UI with Live API Testing
 */

import { NextPage } from 'next';
import Head from 'next/head';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { 
  CodeBracketIcon, 
  DocumentTextIcon, 
  PlayIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const ApiDocs: NextPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [apiStatus, setApiStatus] = useState('online');

  useEffect(() => {
    // Check API status
    const checkApiStatus = async () => {
      try {
        const response = await fetch('/api/v1/health');
        setApiStatus(response.ok ? 'online' : 'offline');
      } catch (error) {
        setApiStatus('offline');
      }
    };
    
    checkApiStatus();
    const interval = setInterval(checkApiStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const apiEndpoints = [
    {
      category: 'Authentication',
      endpoints: [
        { method: 'POST', path: '/v1/auth/register', description: 'Register new user' },
        { method: 'POST', path: '/v1/auth/login', description: 'User login' },
        { method: 'POST', path: '/v1/auth/refresh', description: 'Refresh access token' },
        { method: 'POST', path: '/v1/auth/logout', description: 'User logout' },
        { method: 'GET', path: '/v1/auth/me', description: 'Get user profile' }
      ]
    },
    {
      category: 'Trading',
      endpoints: [
        { method: 'POST', path: '/v1/trades/execute', description: 'Execute trade' },
        { method: 'GET', path: '/v1/trades/history', description: 'Get trade history' },
        { method: 'GET', path: '/v1/trades/positions', description: 'Get current positions' },
        { method: 'POST', path: '/v1/trades/cancel', description: 'Cancel trade order' }
      ]
    },
    {
      category: 'AGI Trading',
      endpoints: [
        { method: 'POST', path: '/v1/agi/predictions', description: 'Get AGI market predictions' },
        { method: 'POST', path: '/v1/agi/strategies', description: 'Generate trading strategies' },
        { method: 'GET', path: '/v1/agi/performance', description: 'Get AGI performance metrics' }
      ]
    },
    {
      category: 'Quantum Optimization',
      endpoints: [
        { method: 'POST', path: '/v1/quantum/optimize', description: 'Quantum portfolio optimization' },
        { method: 'POST', path: '/v1/quantum/risk', description: 'Quantum risk assessment' },
        { method: 'GET', path: '/v1/quantum/status', description: 'Get quantum computing status' }
      ]
    },
    {
      category: 'Risk Management',
      endpoints: [
        { method: 'GET', path: '/v1/risk/var', description: 'Calculate Value at Risk' },
        { method: 'POST', path: '/v1/risk/stress', description: 'Run stress tests' },
        { method: 'GET', path: '/v1/risk/limits', description: 'Get risk limits' },
        { method: 'POST', path: '/v1/risk/limits', description: 'Update risk limits' }
      ]
    },
    {
      category: 'Market Data',
      endpoints: [
        { method: 'GET', path: '/v1/market/prices', description: 'Get real-time prices' },
        { method: 'GET', path: '/v1/market/volumes', description: 'Get trading volumes' },
        { method: 'GET', path: '/v1/market/news', description: 'Get market news' }
      ]
    }
  ];

  const codeExamples = {
    python: `# Python SDK Example
import quantaenergi

# Initialize client
client = quantaenergi.Client(
    api_key="your_api_key",
    environment="production"
)

# Get AGI prediction
prediction = client.agi.get_prediction(
    asset="WTI_Crude",
    timeframe="1h"
)
print(f"Predicted price: ${prediction.price}")
print(f"Confidence: {prediction.confidence}")

# Execute trade
trade = client.trading.execute_trade(
    asset="WTI_Crude",
    side="buy",
    quantity=100,
    price=85.50
)
print(f"Trade ID: {trade.id}")`,

    javascript: `// JavaScript SDK Example
import { QuantaEnergiClient } from '@quantaenergi/sdk';

// Initialize client
const client = new QuantaEnergiClient({
  apiKey: 'your_api_key',
  environment: 'production'
});

// Get AGI prediction
const prediction = await client.agi.getPrediction({
  asset: 'WTI_Crude',
  timeframe: '1h'
});
console.log(\`Predicted price: $\${prediction.price}\`);
console.log(\`Confidence: \${prediction.confidence}\`);

// Execute trade
const trade = await client.trading.executeTrade({
  asset: 'WTI_Crude',
  side: 'buy',
  quantity: 100,
  price: 85.50
});
console.log(\`Trade ID: \${trade.id}\`);`,

    curl: `# cURL Examples

# Get AGI Prediction
curl -X POST "https://api.quantaenergi.com/v1/agi/predictions" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "asset": "WTI_Crude",
    "timeframe": "1h",
    "features": ["price", "volume", "sentiment"]
  }'

# Execute Trade
curl -X POST "https://api.quantaenergi.com/v1/trades/execute" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "asset": "WTI_Crude",
    "side": "buy",
    "quantity": 100,
    "price": 85.50,
    "order_type": "limit"
  }'

# Quantum Portfolio Optimization
curl -X POST "https://api.quantaenergi.com/v1/quantum/optimize" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "assets": ["WTI", "Brent", "Gas"],
    "constraints": {
      "max_risk": 0.15,
      "sharia_compliant": true
    }
  }'`
  };

  const getMethodColor = (method: string) => {
    switch (method) {
      case 'GET': return 'bg-green-100 text-green-800';
      case 'POST': return 'bg-blue-100 text-blue-800';
      case 'PUT': return 'bg-yellow-100 text-yellow-800';
      case 'DELETE': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <>
      <Head>
        <title>API Documentation - QuantaEnergi</title>
        <meta name="description" content="Comprehensive API documentation for QuantaEnergi ETRM platform with interactive examples and live testing." />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center">
                <Link href="/" className="text-2xl font-bold text-gray-900">
                  <span className="text-green-600">Quanta</span>Energi
                </Link>
                <span className="ml-4 text-gray-500">API Documentation</span>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <div className={`w-2 h-2 rounded-full mr-2 ${apiStatus === 'online' ? 'bg-green-400' : 'bg-red-400'}`}></div>
                  <span className="text-sm text-gray-600">
                    API {apiStatus === 'online' ? 'Online' : 'Offline'}
                  </span>
                </div>
                <Link href="/" className="text-gray-600 hover:text-gray-900">
                  Back to Home
                </Link>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-sm border p-6 sticky top-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Documentation</h3>
                <nav className="space-y-2">
                  <button
                    onClick={() => setActiveTab('overview')}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      activeTab === 'overview' 
                        ? 'bg-green-100 text-green-700' 
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    Overview
                  </button>
                  <button
                    onClick={() => setActiveTab('endpoints')}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      activeTab === 'endpoints' 
                        ? 'bg-green-100 text-green-700' 
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    API Endpoints
                  </button>
                  <button
                    onClick={() => setActiveTab('examples')}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      activeTab === 'examples' 
                        ? 'bg-green-100 text-green-700' 
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    Code Examples
                  </button>
                  <button
                    onClick={() => setActiveTab('swagger')}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      activeTab === 'swagger' 
                        ? 'bg-green-100 text-green-700' 
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    Interactive API
                  </button>
                </nav>
              </div>
            </div>

            {/* Main Content */}
            <div className="lg:col-span-3">
              {activeTab === 'overview' && (
                <div className="space-y-8">
                  <div className="bg-white rounded-lg shadow-sm border p-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-4">QuantaEnergi API</h1>
                    <p className="text-lg text-gray-600 mb-6">
                      The QuantaEnergi API provides programmatic access to our revolutionary ETRM platform. 
                      Build powerful trading applications with AI predictions, quantum optimization, and blockchain transparency.
                    </p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                      <div className="text-center p-6 bg-green-50 rounded-lg">
                        <CodeBracketIcon className="h-8 w-8 text-green-600 mx-auto mb-2" />
                        <h3 className="font-semibold text-gray-900">RESTful API</h3>
                        <p className="text-sm text-gray-600">Complete CRUD operations for all trading functions</p>
                      </div>
                      <div className="text-center p-6 bg-blue-50 rounded-lg">
                        <PlayIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                        <h3 className="font-semibold text-gray-900">Real-time WebSockets</h3>
                        <p className="text-sm text-gray-600">Live market data and trade notifications</p>
                      </div>
                      <div className="text-center p-6 bg-purple-50 rounded-lg">
                        <DocumentTextIcon className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                        <h3 className="font-semibold text-gray-900">Interactive Docs</h3>
                        <p className="text-sm text-gray-600">Test APIs directly in your browser</p>
                      </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Base URL</h3>
                      <div className="bg-gray-900 rounded-md p-4">
                        <code className="text-green-400">https://api.quantaenergi.com</code>
                      </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Authentication</h3>
                      <p className="text-gray-600 mb-4">
                        All API requests require authentication using JWT tokens. Include your token in the Authorization header:
                      </p>
                      <div className="bg-gray-900 rounded-md p-4">
                        <code className="text-green-400">Authorization: Bearer YOUR_JWT_TOKEN</code>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'endpoints' && (
                <div className="space-y-8">
                  <div className="bg-white rounded-lg shadow-sm border p-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-6">API Endpoints</h1>
                    
                    {apiEndpoints.map((category, categoryIndex) => (
                      <div key={categoryIndex} className="mb-8">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">{category.category}</h2>
                        <div className="space-y-3">
                          {category.endpoints.map((endpoint, endpointIndex) => (
                            <div key={endpointIndex} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                              <div className="flex items-center space-x-4">
                                <span className={`px-2 py-1 rounded text-xs font-medium ${getMethodColor(endpoint.method)}`}>
                                  {endpoint.method}
                                </span>
                                <code className="text-sm font-mono text-gray-900">{endpoint.path}</code>
                              </div>
                              <span className="text-sm text-gray-600">{endpoint.description}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'examples' && (
                <div className="space-y-8">
                  <div className="bg-white rounded-lg shadow-sm border p-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-6">Code Examples</h1>
                    
                    <div className="space-y-8">
                      <div>
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Python SDK</h2>
                        <div className="bg-gray-900 rounded-lg p-6 overflow-x-auto">
                          <pre className="text-sm text-gray-300">
                            <code>{codeExamples.python}</code>
                          </pre>
                        </div>
                      </div>

                      <div>
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">JavaScript SDK</h2>
                        <div className="bg-gray-900 rounded-lg p-6 overflow-x-auto">
                          <pre className="text-sm text-gray-300">
                            <code>{codeExamples.javascript}</code>
                          </pre>
                        </div>
                      </div>

                      <div>
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">cURL Examples</h2>
                        <div className="bg-gray-900 rounded-lg p-6 overflow-x-auto">
                          <pre className="text-sm text-gray-300">
                            <code>{codeExamples.curl}</code>
                          </pre>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'swagger' && (
                <div className="space-y-8">
                  <div className="bg-white rounded-lg shadow-sm border p-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-6">Interactive API Testing</h1>
                    
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                      <div className="flex items-center">
                        <CheckCircleIcon className="h-5 w-5 text-blue-600 mr-2" />
                        <span className="text-blue-800 font-medium">Live API Available</span>
                      </div>
                      <p className="text-blue-700 mt-2">
                        Test our APIs directly in your browser with our interactive Swagger UI.
                      </p>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Swagger UI</h3>
                      <p className="text-gray-600 mb-4">
                        Our interactive API documentation allows you to test endpoints directly from your browser.
                      </p>
                      <div className="bg-gray-900 rounded-lg p-6 text-center">
                        <div className="text-gray-300 mb-4">
                          <svg className="h-12 w-12 mx-auto mb-2" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                          </svg>
                        </div>
                        <p className="text-gray-400 mb-4">Interactive Swagger UI</p>
                        <a 
                          href="/api/v1/openapi.json" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                          <PlayIcon className="h-4 w-4 mr-2" />
                          Open Swagger UI
                        </a>
                      </div>
                    </div>

                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mt-6">
                      <div className="flex items-center">
                        <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 mr-2" />
                        <span className="text-yellow-800 font-medium">Authentication Required</span>
                      </div>
                      <p className="text-yellow-700 mt-2">
                        To test protected endpoints, you'll need to authenticate first. Use the "Authorize" button in Swagger UI.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ApiDocs;
