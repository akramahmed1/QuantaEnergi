import React, { useState, useEffect, useRef } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { 
  Button, 
  Input, 
  Textarea, 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Brain, 
  Zap, 
  Shield, 
  Globe,
  MessageSquare,
  Send,
  RefreshCw
} from 'lucide-react';

// Register Chart.js components
Chart.register(...registerables);

interface MarketData {
  timestamp: string;
  price: number;
  volume: number;
  volatility: number;
}

interface AGIPrediction {
  id: string;
  timestamp: string;
  prediction: number;
  confidence: number;
  strategy: string;
  reasoning: string;
}

interface QuantumOptimization {
  id: string;
  timestamp: string;
  optimalWeights: number[];
  expectedReturn: number;
  risk: number;
  sharpeRatio: number;
  speedup: number;
}

interface TradingMessage {
  id: string;
  timestamp: string;
  type: 'user' | 'agi' | 'system';
  content: string;
  confidence?: number;
  strategy?: string;
}

const TradingDashboard: React.FC = () => {
  // State management
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [agiPredictions, setAgiPredictions] = useState<AGIPrediction[]>([]);
  const [quantumOptimizations, setQuantumOptimizations] = useState<QuantumOptimization[]>([]);
  const [tradingMessages, setTradingMessages] = useState<TradingMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [selectedAsset, setSelectedAsset] = useState('WTI_Crude');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connecting');
  
  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // WebSocket connection for real-time data
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        // Mock WebSocket connection - in production, connect to real WebSocket
        setConnectionStatus('connecting');
        
        // Simulate connection
        setTimeout(() => {
          setConnectionStatus('connected');
          // Mock real-time data updates
          startMockDataUpdates();
        }, 1000);
        
      } catch (error) {
        console.error('WebSocket connection failed:', error);
        setConnectionStatus('disconnected');
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Mock real-time data updates
  const startMockDataUpdates = () => {
    const interval = setInterval(() => {
      // Update market data
      const newMarketData: MarketData = {
        timestamp: new Date().toISOString(),
        price: 75.5 + Math.random() * 10,
        volume: 1000000 + Math.random() * 500000,
        volatility: 0.02 + Math.random() * 0.01
      };
      
      setMarketData(prev => [...prev.slice(-19), newMarketData]);
      
      // Update AGI predictions
      if (Math.random() > 0.7) {
        const newPrediction: AGIPrediction = {
          id: `pred_${Date.now()}`,
          timestamp: new Date().toISOString(),
          prediction: 75.5 + Math.random() * 10,
          confidence: 0.7 + Math.random() * 0.3,
          strategy: ['Momentum', 'Mean Reversion', 'Breakout'][Math.floor(Math.random() * 3)],
          reasoning: 'AI analysis suggests potential price movement based on market sentiment and technical indicators.'
        };
        setAgiPredictions(prev => [...prev.slice(-9), newPrediction]);
      }
      
      // Update quantum optimizations
      if (Math.random() > 0.8) {
        const newOptimization: QuantumOptimization = {
          id: `opt_${Date.now()}`,
          timestamp: new Date().toISOString(),
          optimalWeights: [0.3, 0.25, 0.2, 0.15, 0.1],
          expectedReturn: 0.08 + Math.random() * 0.04,
          risk: 0.12 + Math.random() * 0.03,
          sharpeRatio: 0.6 + Math.random() * 0.4,
          speedup: 5 + Math.random() * 5
        };
        setQuantumOptimizations(prev => [...prev.slice(-4), newOptimization]);
      }
    }, 2000);

    return () => clearInterval(interval);
  };

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [tradingMessages]);

  // Send message to AGI
  const sendMessage = async () => {
    if (!newMessage.trim()) return;

    const userMessage: TradingMessage = {
      id: `msg_${Date.now()}`,
      timestamp: new Date().toISOString(),
      type: 'user',
      content: newMessage
    };

    setTradingMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setIsLoading(true);

    try {
      // Mock AGI response - in production, call real AGI API
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const agiResponse: TradingMessage = {
        id: `msg_${Date.now() + 1}`,
        timestamp: new Date().toISOString(),
        type: 'agi',
        content: `Based on your question about "${newMessage}", I recommend analyzing the current market conditions and considering a diversified approach. The quantum optimization suggests optimal portfolio weights, and our risk metrics indicate moderate volatility.`,
        confidence: 0.85,
        strategy: 'Balanced Portfolio'
      };

      setTradingMessages(prev => [...prev, agiResponse]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Chart data preparation
  const priceChartData = {
    labels: marketData.map(d => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [{
      label: 'Price',
      data: marketData.map(d => d.price),
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4
    }]
  };

  const volumeChartData = {
    labels: marketData.map(d => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [{
      label: 'Volume',
      data: marketData.map(d => d.volume),
      backgroundColor: 'rgba(34, 197, 94, 0.8)'
    }]
  };

  const quantumWeightsData = {
    labels: ['WTI', 'Brent', 'Natural Gas', 'Heating Oil', 'Gasoline'],
    datasets: [{
      data: quantumOptimizations[0]?.optimalWeights || [0.2, 0.2, 0.2, 0.2, 0.2],
      backgroundColor: [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 205, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)'
      ]
    }]
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            QuantaEnergi Trading Dashboard
          </h1>
          <div className="flex items-center gap-4">
            <Badge variant={connectionStatus === 'connected' ? 'default' : 'destructive'}>
              <Activity className="w-4 h-4 mr-1" />
              {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
            </Badge>
            <Badge variant="outline">
              <Brain className="w-4 h-4 mr-1" />
              AGI Active
            </Badge>
            <Badge variant="outline">
              <Zap className="w-4 h-4 mr-1" />
              Quantum Ready
            </Badge>
          </div>
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Market Data Chart */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Real-Time Market Data
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <Line 
                  data={priceChartData} 
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: true }
                    },
                    scales: {
                      y: { beginAtZero: false }
                    }
                  }} 
                />
              </div>
            </CardContent>
          </Card>

          {/* Quantum Optimization */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                Quantum Portfolio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <Doughnut 
                  data={quantumWeightsData} 
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom' }
                    }
                  }} 
                />
              </div>
              {quantumOptimizations[0] && (
                <div className="mt-4 space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Expected Return:</span>
                    <span className="text-sm font-medium">
                      {(quantumOptimizations[0].expectedReturn * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Risk:</span>
                    <span className="text-sm font-medium">
                      {(quantumOptimizations[0].risk * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Sharpe Ratio:</span>
                    <span className="text-sm font-medium">
                      {quantumOptimizations[0].sharpeRatio.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Speedup:</span>
                    <span className="text-sm font-medium">
                      {quantumOptimizations[0].speedup.toFixed(1)}x
                    </span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* AGI Chat and Volume Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* AGI Trading Chat */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                AGI Trading Assistant
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 overflow-y-auto border rounded-lg p-4 mb-4 bg-gray-50">
                {tradingMessages.map((message) => (
                  <div
                    key={message.id}
                    className={`mb-3 p-3 rounded-lg ${
                      message.type === 'user' 
                        ? 'bg-blue-100 ml-8' 
                        : message.type === 'agi'
                        ? 'bg-green-100 mr-8'
                        : 'bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs text-gray-500">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                      {message.confidence && (
                        <Badge variant="outline" className="text-xs">
                          {(message.confidence * 100).toFixed(0)}% confidence
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm">{message.content}</p>
                    {message.strategy && (
                      <Badge variant="secondary" className="mt-1 text-xs">
                        {message.strategy}
                      </Badge>
                    )}
                  </div>
                ))}
                {isLoading && (
                  <div className="flex items-center gap-2 text-gray-500">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span className="text-sm">AGI is thinking...</span>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
              
              <div className="flex gap-2">
                <Input
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Ask AGI about trading strategies, market analysis..."
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  disabled={isLoading}
                />
                <Button 
                  onClick={sendMessage} 
                  disabled={isLoading || !newMessage.trim()}
                  size="sm"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Volume Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingDown className="w-5 h-5" />
                Trading Volume
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <Bar 
                  data={volumeChartData} 
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false }
                    },
                    scales: {
                      y: { beginAtZero: true }
                    }
                  }} 
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Asset Selection and Controls */}
        <div className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="w-5 h-5" />
                Trading Controls
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium">Asset:</label>
                  <Select value={selectedAsset} onValueChange={setSelectedAsset}>
                    <SelectTrigger className="w-40">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="WTI_Crude">WTI Crude</SelectItem>
                      <SelectItem value="Brent_Crude">Brent Crude</SelectItem>
                      <SelectItem value="Natural_Gas">Natural Gas</SelectItem>
                      <SelectItem value="Heating_Oil">Heating Oil</SelectItem>
                      <SelectItem value="Gasoline">Gasoline</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <Button variant="outline" size="sm">
                  <RefreshCw className="w-4 h-4 mr-1" />
                  Refresh Data
                </Button>
                
                <Button variant="outline" size="sm">
                  <Shield className="w-4 h-4 mr-1" />
                  Risk Check
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default TradingDashboard;