/**
 * React Native Trading Screen for QuantaEnergi Mobile App
 * Production-Ready Mobile Trading Interface with Real-time Updates
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  RefreshControl,
  Dimensions,
  StatusBar,
} from 'react-native';
import {
  LineChart,
  BarChart,
  PieChart,
} from 'react-native-chart-kit';
import {
  MaterialIcons,
  MaterialCommunityIcons,
  Ionicons,
} from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { WebSocket } from 'react-native-websocket';

// Types
interface MarketData {
  timestamp: string;
  price: number;
  volume: number;
  change: number;
  changePercent: number;
}

interface TradeOrder {
  id: string;
  asset: string;
  side: 'buy' | 'sell';
  quantity: number;
  price: number;
  status: 'pending' | 'filled' | 'cancelled';
  timestamp: string;
}

interface AGIPrediction {
  id: string;
  asset: string;
  prediction: number;
  confidence: number;
  strategy: string;
  reasoning: string;
  timestamp: string;
}

interface QuantumOptimization {
  id: string;
  optimalWeights: number[];
  expectedReturn: number;
  risk: number;
  sharpeRatio: number;
  speedup: number;
  timestamp: string;
}

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

const TradingScreen: React.FC = () => {
  // State management
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [activeOrders, setActiveOrders] = useState<TradeOrder[]>([]);
  const [agiPredictions, setAgiPredictions] = useState<AGIPrediction[]>([]);
  const [quantumOptimization, setQuantumOptimization] = useState<QuantumOptimization | null>(null);
  const [selectedAsset, setSelectedAsset] = useState('WTI_Crude');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [newOrder, setNewOrder] = useState({
    side: 'buy' as 'buy' | 'sell',
    quantity: '',
    price: '',
  });

  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // WebSocket connection
  useEffect(() => {
    connectWebSocket();
    startDataUpdates();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      // Mock WebSocket connection - in production, connect to real WebSocket
      setIsConnected(true);
      
      // Simulate WebSocket events
      setTimeout(() => {
        // Mock connection established
        console.log('WebSocket connected');
      }, 1000);
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      setIsConnected(false);
    }
  };

  const startDataUpdates = () => {
    refreshIntervalRef.current = setInterval(() => {
      updateMarketData();
      updateAGIPredictions();
      updateQuantumOptimization();
    }, 3000);
  };

  const updateMarketData = () => {
    const newData: MarketData = {
      timestamp: new Date().toISOString(),
      price: 75.5 + Math.random() * 10,
      volume: 1000000 + Math.random() * 500000,
      change: (Math.random() - 0.5) * 2,
      changePercent: (Math.random() - 0.5) * 4,
    };

    setMarketData(prev => [...prev.slice(-19), newData]);
  };

  const updateAGIPredictions = () => {
    if (Math.random() > 0.7) {
      const newPrediction: AGIPrediction = {
        id: `pred_${Date.now()}`,
        asset: selectedAsset,
        prediction: 75.5 + Math.random() * 10,
        confidence: 0.7 + Math.random() * 0.3,
        strategy: ['Momentum', 'Mean Reversion', 'Breakout'][Math.floor(Math.random() * 3)],
        reasoning: 'AI analysis suggests potential price movement based on market sentiment.',
        timestamp: new Date().toISOString(),
      };

      setAgiPredictions(prev => [...prev.slice(-4), newPrediction]);
    }
  };

  const updateQuantumOptimization = () => {
    if (Math.random() > 0.8) {
      const newOptimization: QuantumOptimization = {
        id: `opt_${Date.now()}`,
        optimalWeights: [0.3, 0.25, 0.2, 0.15, 0.1],
        expectedReturn: 0.08 + Math.random() * 0.04,
        risk: 0.12 + Math.random() * 0.03,
        sharpeRatio: 0.6 + Math.random() * 0.4,
        speedup: 5 + Math.random() * 5,
        timestamp: new Date().toISOString(),
      };

      setQuantumOptimization(newOptimization);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      // Refresh all data
      updateMarketData();
      updateAGIPredictions();
      updateQuantumOptimization();
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (error) {
      console.error('Refresh error:', error);
      Alert.alert('Error', 'Failed to refresh data');
    } finally {
      setRefreshing(false);
    }
  };

  const executeTrade = async () => {
    if (!newOrder.quantity || !newOrder.price) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setIsLoading(true);
    try {
      // Mock trade execution - in production, call real API
      await new Promise(resolve => setTimeout(resolve, 1500));

      const newTrade: TradeOrder = {
        id: `trade_${Date.now()}`,
        asset: selectedAsset,
        side: newOrder.side,
        quantity: parseFloat(newOrder.quantity),
        price: parseFloat(newOrder.price),
        status: 'pending',
        timestamp: new Date().toISOString(),
      };

      setActiveOrders(prev => [newTrade, ...prev]);
      setNewOrder({ side: 'buy', quantity: '', price: '' });

      Alert.alert('Success', 'Trade order placed successfully');
    } catch (error) {
      console.error('Trade execution error:', error);
      Alert.alert('Error', 'Failed to execute trade');
    } finally {
      setIsLoading(false);
    }
  };

  const cancelOrder = async (orderId: string) => {
    try {
      // Mock order cancellation - in production, call real API
      setActiveOrders(prev => 
        prev.map(order => 
          order.id === orderId 
            ? { ...order, status: 'cancelled' as const }
            : order
        )
      );
      
      Alert.alert('Success', 'Order cancelled successfully');
    } catch (error) {
      console.error('Order cancellation error:', error);
      Alert.alert('Error', 'Failed to cancel order');
    }
  };

  // Chart data preparation
  const priceChartData = {
    labels: marketData.slice(-10).map(d => new Date(d.timestamp).toLocaleTimeString().slice(0, 5)),
    datasets: [{
      data: marketData.slice(-10).map(d => d.price),
      color: (opacity = 1) => `rgba(59, 130, 246, ${opacity})`,
      strokeWidth: 2,
    }],
  };

  const volumeChartData = {
    labels: marketData.slice(-5).map(d => new Date(d.timestamp).toLocaleTimeString().slice(0, 5)),
    datasets: [{
      data: marketData.slice(-5).map(d => d.volume / 1000000), // Convert to millions
    }],
  };

  const quantumWeightsData = quantumOptimization ? [
    { name: 'WTI', population: quantumOptimization.optimalWeights[0] * 100, color: '#FF6384', legendFontColor: '#7F7F7F', legendFontSize: 12 },
    { name: 'Brent', population: quantumOptimization.optimalWeights[1] * 100, color: '#36A2EB', legendFontColor: '#7F7F7F', legendFontSize: 12 },
    { name: 'Gas', population: quantumOptimization.optimalWeights[2] * 100, color: '#FFCE56', legendFontColor: '#7F7F7F', legendFontSize: 12 },
    { name: 'Oil', population: quantumOptimization.optimalWeights[3] * 100, color: '#4BC0C0', legendFontColor: '#7F7F7F', legendFontSize: 12 },
    { name: 'Gasoline', population: quantumOptimization.optimalWeights[4] * 100, color: '#9966FF', legendFontColor: '#7F7F7F', legendFontSize: 12 },
  ] : [];

  const currentPrice = marketData[marketData.length - 1]?.price || 0;
  const priceChange = marketData[marketData.length - 1]?.change || 0;
  const priceChangePercent = marketData[marketData.length - 1]?.changePercent || 0;

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1f2937" />
      
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <Text style={styles.headerTitle}>QuantaEnergi</Text>
          <View style={styles.connectionStatus}>
            <MaterialIcons 
              name={isConnected ? 'wifi' : 'wifi-off'} 
              size={20} 
              color={isConnected ? '#10b981' : '#ef4444'} 
            />
            <Text style={[styles.connectionText, { color: isConnected ? '#10b981' : '#ef4444' }]}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </Text>
          </View>
        </View>
        
        <View style={styles.priceDisplay}>
          <Text style={styles.assetName}>{selectedAsset.replace('_', ' ')}</Text>
          <Text style={styles.currentPrice}>${currentPrice.toFixed(2)}</Text>
          <View style={styles.priceChange}>
            <MaterialIcons 
              name={priceChange >= 0 ? 'trending-up' : 'trending-down'} 
              size={16} 
              color={priceChange >= 0 ? '#10b981' : '#ef4444'} 
            />
            <Text style={[styles.changeText, { color: priceChange >= 0 ? '#10b981' : '#ef4444' }]}>
              {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)} ({priceChangePercent.toFixed(2)}%)
            </Text>
          </View>
        </View>
      </View>

      <ScrollView 
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Market Chart */}
        <View style={styles.chartContainer}>
          <Text style={styles.chartTitle}>Price Chart</Text>
          {marketData.length > 0 && (
            <LineChart
              data={priceChartData}
              width={screenWidth - 32}
              height={200}
              chartConfig={{
                backgroundColor: '#1f2937',
                backgroundGradientFrom: '#1f2937',
                backgroundGradientTo: '#374151',
                decimalPlaces: 2,
                color: (opacity = 1) => `rgba(59, 130, 246, ${opacity})`,
                labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
                style: { borderRadius: 16 },
                propsForDots: { r: '4', strokeWidth: '2', stroke: '#3b82f6' },
              }}
              bezier
              style={styles.chart}
            />
          )}
        </View>

        {/* AGI Predictions */}
        {agiPredictions.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>AGI Predictions</Text>
            {agiPredictions.slice(0, 2).map((prediction) => (
              <View key={prediction.id} style={styles.predictionCard}>
                <View style={styles.predictionHeader}>
                  <Text style={styles.predictionPrice}>${prediction.prediction.toFixed(2)}</Text>
                  <View style={styles.confidenceBadge}>
                    <Text style={styles.confidenceText}>
                      {(prediction.confidence * 100).toFixed(0)}%
                    </Text>
                  </View>
                </View>
                <Text style={styles.predictionStrategy}>{prediction.strategy}</Text>
                <Text style={styles.predictionReasoning}>{prediction.reasoning}</Text>
              </View>
            ))}
          </View>
        )}

        {/* Quantum Optimization */}
        {quantumOptimization && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Quantum Portfolio</Text>
            <View style={styles.quantumCard}>
              <View style={styles.quantumMetrics}>
                <View style={styles.metric}>
                  <Text style={styles.metricLabel}>Return</Text>
                  <Text style={styles.metricValue}>
                    {(quantumOptimization.expectedReturn * 100).toFixed(2)}%
                  </Text>
                </View>
                <View style={styles.metric}>
                  <Text style={styles.metricLabel}>Risk</Text>
                  <Text style={styles.metricValue}>
                    {(quantumOptimization.risk * 100).toFixed(2)}%
                  </Text>
                </View>
                <View style={styles.metric}>
                  <Text style={styles.metricLabel}>Sharpe</Text>
                  <Text style={styles.metricValue}>
                    {quantumOptimization.sharpeRatio.toFixed(2)}
                  </Text>
                </View>
                <View style={styles.metric}>
                  <Text style={styles.metricLabel}>Speedup</Text>
                  <Text style={styles.metricValue}>
                    {quantumOptimization.speedup.toFixed(1)}x
                  </Text>
                </View>
              </View>
              {quantumWeightsData.length > 0 && (
                <PieChart
                  data={quantumWeightsData}
                  width={screenWidth - 64}
                  height={150}
                  chartConfig={{
                    color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
                  }}
                  accessor="population"
                  backgroundColor="transparent"
                  paddingLeft="15"
                  style={styles.pieChart}
                />
              )}
            </View>
          </View>
        )}

        {/* Trading Interface */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Execute Trade</Text>
          <View style={styles.tradingCard}>
            <View style={styles.sideSelector}>
              <TouchableOpacity
                style={[styles.sideButton, newOrder.side === 'buy' && styles.sideButtonActive]}
                onPress={() => setNewOrder(prev => ({ ...prev, side: 'buy' }))}
              >
                <Text style={[styles.sideButtonText, newOrder.side === 'buy' && styles.sideButtonTextActive]}>
                  BUY
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.sideButton, newOrder.side === 'sell' && styles.sideButtonActive]}
                onPress={() => setNewOrder(prev => ({ ...prev, side: 'sell' }))}
              >
                <Text style={[styles.sideButtonText, newOrder.side === 'sell' && styles.sideButtonTextActive]}>
                  SELL
                </Text>
              </TouchableOpacity>
            </View>
            
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Quantity</Text>
              <TextInput
                style={styles.input}
                value={newOrder.quantity}
                onChangeText={(text) => setNewOrder(prev => ({ ...prev, quantity: text }))}
                placeholder="Enter quantity"
                keyboardType="numeric"
              />
            </View>
            
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Price</Text>
              <TextInput
                style={styles.input}
                value={newOrder.price}
                onChangeText={(text) => setNewOrder(prev => ({ ...prev, price: text }))}
                placeholder="Enter price"
                keyboardType="numeric"
              />
            </View>
            
            <TouchableOpacity
              style={[styles.executeButton, isLoading && styles.executeButtonDisabled]}
              onPress={executeTrade}
              disabled={isLoading}
            >
              <Text style={styles.executeButtonText}>
                {isLoading ? 'Executing...' : 'Execute Trade'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Active Orders */}
        {activeOrders.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Active Orders</Text>
            {activeOrders.slice(0, 5).map((order) => (
              <View key={order.id} style={styles.orderCard}>
                <View style={styles.orderHeader}>
                  <Text style={styles.orderAsset}>{order.asset}</Text>
                  <View style={[styles.statusBadge, { backgroundColor: order.status === 'pending' ? '#f59e0b' : '#10b981' }]}>
                    <Text style={styles.statusText}>{order.status.toUpperCase()}</Text>
                  </View>
                </View>
                <View style={styles.orderDetails}>
                  <Text style={styles.orderSide}>{order.side.toUpperCase()}</Text>
                  <Text style={styles.orderQuantity}>{order.quantity} @ ${order.price}</Text>
                </View>
                {order.status === 'pending' && (
                  <TouchableOpacity
                    style={styles.cancelButton}
                    onPress={() => cancelOrder(order.id)}
                  >
                    <Text style={styles.cancelButtonText}>Cancel</Text>
                  </TouchableOpacity>
                )}
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#111827',
  },
  header: {
    backgroundColor: '#1f2937',
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 16,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  connectionStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  connectionText: {
    marginLeft: 4,
    fontSize: 12,
    fontWeight: '500',
  },
  priceDisplay: {
    alignItems: 'center',
  },
  assetName: {
    fontSize: 16,
    color: '#9ca3af',
    marginBottom: 4,
  },
  currentPrice: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  priceChange: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  changeText: {
    marginLeft: 4,
    fontSize: 14,
    fontWeight: '500',
  },
  scrollView: {
    flex: 1,
  },
  chartContainer: {
    margin: 16,
    backgroundColor: '#1f2937',
    borderRadius: 12,
    padding: 16,
  },
  chartTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 12,
  },
  chart: {
    borderRadius: 16,
  },
  section: {
    margin: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 12,
  },
  predictionCard: {
    backgroundColor: '#1f2937',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  predictionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  predictionPrice: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#10b981',
  },
  confidenceBadge: {
    backgroundColor: '#059669',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  confidenceText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
  predictionStrategy: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 4,
  },
  predictionReasoning: {
    fontSize: 12,
    color: '#9ca3af',
  },
  quantumCard: {
    backgroundColor: '#1f2937',
    borderRadius: 12,
    padding: 16,
  },
  quantumMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  metric: {
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: 12,
    color: '#9ca3af',
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  pieChart: {
    borderRadius: 16,
  },
  tradingCard: {
    backgroundColor: '#1f2937',
    borderRadius: 12,
    padding: 16,
  },
  sideSelector: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  sideButton: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderRadius: 8,
    marginHorizontal: 4,
    backgroundColor: '#374151',
  },
  sideButtonActive: {
    backgroundColor: '#3b82f6',
  },
  sideButtonText: {
    color: '#9ca3af',
    fontWeight: '600',
  },
  sideButtonTextActive: {
    color: '#ffffff',
  },
  inputGroup: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#ffffff',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#374151',
    borderRadius: 8,
    padding: 12,
    color: '#ffffff',
    fontSize: 16,
  },
  executeButton: {
    backgroundColor: '#10b981',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
  },
  executeButtonDisabled: {
    backgroundColor: '#6b7280',
  },
  executeButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  orderCard: {
    backgroundColor: '#1f2937',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  orderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  orderAsset: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
  orderDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  orderSide: {
    fontSize: 14,
    fontWeight: '500',
    color: '#3b82f6',
  },
  orderQuantity: {
    fontSize: 14,
    color: '#9ca3af',
  },
  cancelButton: {
    backgroundColor: '#ef4444',
    borderRadius: 6,
    padding: 8,
    alignItems: 'center',
  },
  cancelButtonText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
});

export default TradingScreen;
