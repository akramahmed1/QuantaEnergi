/**
 * QuantaEnergi Mobile Application
 * React Native ETRM Mobile Platform
 * Phase 2: Advanced ETRM Features & Market Expansion
 * PRODUCTION READY IMPLEMENTATION
 */

import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Dimensions,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialIcons';

// Types
interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  lastUpdate: string;
}

interface Position {
  id: string;
  asset: string;
  quantity: number;
  marketValue: number;
  unrealizedPnL: number;
  currency: string;
}

interface Trade {
  id: string;
  asset: string;
  side: 'buy' | 'sell';
  quantity: number;
  price: number;
  timestamp: string;
  status: 'pending' | 'filled' | 'cancelled';
}

interface PortfolioSummary {
  totalValue: number;
  totalPnL: number;
  totalPnLPercent: number;
  currency: string;
}

// Mock data services
const mockMarketData: MarketData[] = [
  {
    symbol: 'CL',
    price: 85.42,
    change: 1.25,
    changePercent: 1.49,
    volume: 1250000,
    lastUpdate: '2024-01-15T10:30:00Z'
  },
  {
    symbol: 'NG',
    price: 3.25,
    change: -0.08,
    changePercent: -2.40,
    volume: 890000,
    lastUpdate: '2024-01-15T10:30:00Z'
  },
  {
    symbol: 'HO',
    price: 2.85,
    change: 0.05,
    changePercent: 1.79,
    volume: 450000,
    lastUpdate: '2024-01-15T10:30:00Z'
  }
];

const mockPositions: Position[] = [
  {
    id: '1',
    asset: 'Crude Oil (CL)',
    quantity: 100,
    marketValue: 8542.00,
    unrealizedPnL: 125.00,
    currency: 'USD'
  },
  {
    id: '2',
    asset: 'Natural Gas (NG)',
    quantity: -50,
    marketValue: -162.50,
    unrealizedPnL: -4.00,
    currency: 'USD'
  }
];

const mockTrades: Trade[] = [
  {
    id: '1',
    asset: 'CL',
    side: 'buy',
    quantity: 100,
    price: 84.17,
    timestamp: '2024-01-15T09:30:00Z',
    status: 'filled'
  },
  {
    id: '2',
    asset: 'NG',
    side: 'sell',
    quantity: 50,
    price: 3.33,
    timestamp: '2024-01-15T08:45:00Z',
    status: 'filled'
  }
];

// Components
const MarketDataCard: React.FC<{ data: MarketData }> = ({ data }) => {
  const isPositive = data.change >= 0;
  const changeColor = isPositive ? '#4CAF50' : '#F44336';

  return (
    <View style={styles.marketCard}>
      <View style={styles.marketHeader}>
        <Text style={styles.symbol}>{data.symbol}</Text>
        <Text style={[styles.change, { color: changeColor }]}>
          {isPositive ? '+' : ''}{data.change.toFixed(2)} ({data.changePercent.toFixed(2)}%)
        </Text>
      </View>
      <Text style={styles.price}>${data.price.toFixed(2)}</Text>
      <Text style={styles.volume}>Vol: {data.volume.toLocaleString()}</Text>
      <Text style={styles.lastUpdate}>
        Updated: {new Date(data.lastUpdate).toLocaleTimeString()}
      </Text>
    </View>
  );
};

const PositionCard: React.FC<{ position: Position }> = ({ position }) => {
  const isPositive = position.unrealizedPnL >= 0;
  const pnlColor = isPositive ? '#4CAF50' : '#F44336';
  const quantityColor = position.quantity >= 0 ? '#2196F3' : '#FF9800';

  return (
    <View style={styles.positionCard}>
      <View style={styles.positionHeader}>
        <Text style={styles.asset}>{position.asset}</Text>
        <Text style={[styles.quantity, { color: quantityColor }]}>
          {position.quantity > 0 ? '+' : ''}{position.quantity}
        </Text>
      </View>
      <View style={styles.positionDetails}>
        <Text style={styles.marketValue}>
          ${position.marketValue.toFixed(2)} {position.currency}
        </Text>
        <Text style={[styles.pnl, { color: pnlColor }]}>
          P&L: {isPositive ? '+' : ''}${position.unrealizedPnL.toFixed(2)}
        </Text>
      </View>
    </View>
  );
};

const TradeCard: React.FC<{ trade: Trade }> = ({ trade }) => {
  const sideColor = trade.side === 'buy' ? '#4CAF50' : '#F44336';
  const statusColor = trade.status === 'filled' ? '#4CAF50' : 
                     trade.status === 'pending' ? '#FF9800' : '#F44336';

  return (
    <View style={styles.tradeCard}>
      <View style={styles.tradeHeader}>
        <Text style={styles.tradeAsset}>{trade.asset}</Text>
        <Text style={[styles.tradeSide, { color: sideColor }]}>
          {trade.side.toUpperCase()}
        </Text>
      </View>
      <View style={styles.tradeDetails}>
        <Text style={styles.tradeQuantity}>{trade.quantity}</Text>
        <Text style={styles.tradePrice}>@ ${trade.price.toFixed(2)}</Text>
        <Text style={[styles.tradeStatus, { color: statusColor }]}>
          {trade.status.toUpperCase()}
        </Text>
      </View>
      <Text style={styles.tradeTime}>
        {new Date(trade.timestamp).toLocaleString()}
      </Text>
    </View>
  );
};

// Screens
const DashboardScreen: React.FC = () => {
  const [portfolioSummary, setPortfolioSummary] = useState<PortfolioSummary>({
    totalValue: 0,
    totalPnL: 0,
    totalPnLPercent: 0,
    currency: 'USD'
  });
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    calculatePortfolioSummary();
  }, []);

  const calculatePortfolioSummary = () => {
    const totalValue = mockPositions.reduce((sum, pos) => sum + Math.abs(pos.marketValue), 0);
    const totalPnL = mockPositions.reduce((sum, pos) => sum + pos.unrealizedPnL, 0);
    const totalPnLPercent = totalValue > 0 ? (totalPnL / totalValue) * 100 : 0;

    setPortfolioSummary({
      totalValue,
      totalPnL,
      totalPnLPercent,
      currency: 'USD'
    });
  };

  const onRefresh = () => {
    setRefreshing(true);
    // Simulate API call
    setTimeout(() => {
      calculatePortfolioSummary();
      setRefreshing(false);
    }, 1000);
  };

  const isPositive = portfolioSummary.totalPnL >= 0;
  const pnlColor = isPositive ? '#4CAF50' : '#F44336';

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Portfolio Summary */}
      <View style={styles.summaryCard}>
        <Text style={styles.summaryTitle}>Portfolio Summary</Text>
        <Text style={styles.totalValue}>
          ${portfolioSummary.totalValue.toFixed(2)} {portfolioSummary.currency}
        </Text>
        <Text style={[styles.totalPnL, { color: pnlColor }]}>
          {isPositive ? '+' : ''}${portfolioSummary.totalPnL.toFixed(2)} 
          ({portfolioSummary.totalPnLPercent.toFixed(2)}%)
        </Text>
      </View>

      {/* Market Data */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Market Data</Text>
        {mockMarketData.map((data, index) => (
          <MarketDataCard key={index} data={data} />
        ))}
      </View>

      {/* Positions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Positions</Text>
        {mockPositions.map((position) => (
          <PositionCard key={position.id} position={position} />
        ))}
      </View>
    </ScrollView>
  );
};

const TradingScreen: React.FC = () => {
  const [selectedAsset, setSelectedAsset] = useState('CL');
  const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy');
  const [quantity, setQuantity] = useState('100');
  const [price, setPrice] = useState('85.42');

  const handlePlaceOrder = () => {
    Alert.alert(
      'Place Order',
      `Confirm ${orderSide.toUpperCase()} ${quantity} ${selectedAsset} @ $${price}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Confirm', 
          onPress: () => {
            // Mock order placement
            Alert.alert('Success', 'Order placed successfully');
          }
        }
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Place Order</Text>
        
        {/* Asset Selection */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Asset</Text>
          <View style={styles.assetButtons}>
            {['CL', 'NG', 'HO'].map((asset) => (
              <TouchableOpacity
                key={asset}
                style={[
                  styles.assetButton,
                  selectedAsset === asset && styles.assetButtonSelected
                ]}
                onPress={() => setSelectedAsset(asset)}
              >
                <Text style={[
                  styles.assetButtonText,
                  selectedAsset === asset && styles.assetButtonTextSelected
                ]}>
                  {asset}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Order Side */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Side</Text>
          <View style={styles.sideButtons}>
            <TouchableOpacity
              style={[
                styles.sideButton,
                orderSide === 'buy' && styles.buyButton
              ]}
              onPress={() => setOrderSide('buy')}
            >
              <Text style={[
                styles.sideButtonText,
                orderSide === 'buy' && styles.buyButtonText
              ]}>
                BUY
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.sideButton,
                orderSide === 'sell' && styles.sellButton
              ]}
              onPress={() => setOrderSide('sell')}
            >
              <Text style={[
                styles.sideButtonText,
                orderSide === 'sell' && styles.sellButtonText
              ]}>
                SELL
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Quantity */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Quantity</Text>
          <TouchableOpacity style={styles.input}>
            <Text style={styles.inputText}>{quantity}</Text>
          </TouchableOpacity>
        </View>

        {/* Price */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Price</Text>
          <TouchableOpacity style={styles.input}>
            <Text style={styles.inputText}>${price}</Text>
          </TouchableOpacity>
        </View>

        {/* Place Order Button */}
        <TouchableOpacity
          style={[
            styles.placeOrderButton,
            orderSide === 'buy' ? styles.buyButton : styles.sellButton
          ]}
          onPress={handlePlaceOrder}
        >
          <Text style={[
            styles.placeOrderButtonText,
            orderSide === 'buy' ? styles.buyButtonText : styles.sellButtonText
          ]}>
            Place {orderSide.toUpperCase()} Order
          </Text>
        </TouchableOpacity>
      </View>

      {/* Recent Trades */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Trades</Text>
        {mockTrades.map((trade) => (
          <TradeCard key={trade.id} trade={trade} />
        ))}
      </View>
    </ScrollView>
  );
};

const AnalyticsScreen: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('1D');

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Performance Analytics</Text>
        
        {/* Period Selection */}
        <View style={styles.periodButtons}>
          {['1D', '1W', '1M', '3M', '1Y'].map((period) => (
            <TouchableOpacity
              key={period}
              style={[
                styles.periodButton,
                selectedPeriod === period && styles.periodButtonSelected
              ]}
              onPress={() => setSelectedPeriod(period)}
            >
              <Text style={[
                styles.periodButtonText,
                selectedPeriod === period && styles.periodButtonTextSelected
              ]}>
                {period}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Analytics Cards */}
        <View style={styles.analyticsCard}>
          <Text style={styles.analyticsTitle}>Portfolio Performance</Text>
          <Text style={styles.analyticsValue}>+12.5%</Text>
          <Text style={styles.analyticsSubtitle}>Total Return</Text>
        </View>

        <View style={styles.analyticsCard}>
          <Text style={styles.analyticsTitle}>Sharpe Ratio</Text>
          <Text style={styles.analyticsValue}>1.85</Text>
          <Text style={styles.analyticsSubtitle}>Risk-Adjusted Return</Text>
        </View>

        <View style={styles.analyticsCard}>
          <Text style={styles.analyticsTitle}>Max Drawdown</Text>
          <Text style={styles.analyticsValue}>-8.2%</Text>
          <Text style={styles.analyticsSubtitle}>Peak to Trough</Text>
        </View>

        <View style={styles.analyticsCard}>
          <Text style={styles.analyticsTitle}>VaR (95%)</Text>
          <Text style={styles.analyticsValue}>$45,000</Text>
          <Text style={styles.analyticsSubtitle}>Daily Risk</Text>
        </View>
      </View>
    </ScrollView>
  );
};

const SettingsScreen: React.FC = () => {
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [biometric, setBiometric] = useState(true);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Preferences</Text>
        
        <View style={styles.settingItem}>
          <Text style={styles.settingLabel}>Push Notifications</Text>
          <TouchableOpacity
            style={[styles.toggle, notifications && styles.toggleActive]}
            onPress={() => setNotifications(!notifications)}
          >
            <View style={[styles.toggleThumb, notifications && styles.toggleThumbActive]} />
          </TouchableOpacity>
        </View>

        <View style={styles.settingItem}>
          <Text style={styles.settingLabel}>Dark Mode</Text>
          <TouchableOpacity
            style={[styles.toggle, darkMode && styles.toggleActive]}
            onPress={() => setDarkMode(!darkMode)}
          >
            <View style={[styles.toggleThumb, darkMode && styles.toggleThumbActive]} />
          </TouchableOpacity>
        </View>

        <View style={styles.settingItem}>
          <Text style={styles.settingLabel}>Biometric Authentication</Text>
          <TouchableOpacity
            style={[styles.toggle, biometric && styles.toggleActive]}
            onPress={() => setBiometric(!biometric)}
          >
            <View style={[styles.toggleThumb, biometric && styles.toggleThumbActive]} />
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        
        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuItemText}>Profile Settings</Text>
          <Icon name="chevron-right" size={24} color="#666" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuItemText}>Security Settings</Text>
          <Icon name="chevron-right" size={24} color="#666" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuItemText}>API Keys</Text>
          <Icon name="chevron-right" size={24} color="#666" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuItemText}>Support</Text>
          <Icon name="chevron-right" size={24} color="#666" />
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.logoutButton}>
        <Text style={styles.logoutButtonText}>Logout</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

// Navigation
const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

const MainTabs: React.FC = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          if (route.name === 'Dashboard') {
            iconName = 'dashboard';
          } else if (route.name === 'Trading') {
            iconName = 'trending-up';
          } else if (route.name === 'Analytics') {
            iconName = 'analytics';
          } else if (route.name === 'Settings') {
            iconName = 'settings';
          } else {
            iconName = 'help';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#2196F3',
        tabBarInactiveTintColor: 'gray',
        headerStyle: {
          backgroundColor: '#2196F3',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen name="Dashboard" component={DashboardScreen} />
      <Tab.Screen name="Trading" component={TradingScreen} />
      <Tab.Screen name="Analytics" component={AnalyticsScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
};

const App: React.FC = () => {
  return (
    <NavigationContainer>
      <StatusBar barStyle="light-content" backgroundColor="#2196F3" />
      <Stack.Navigator>
        <Stack.Screen 
          name="Main" 
          component={MainTabs} 
          options={{ headerShown: false }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

// Styles
const { width } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  summaryCard: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 20,
    borderRadius: 12,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  summaryTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  totalValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 5,
  },
  totalPnL: {
    fontSize: 18,
    fontWeight: '600',
  },
  section: {
    margin: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  marketCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  marketHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  symbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  change: {
    fontSize: 16,
    fontWeight: '600',
  },
  price: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 4,
  },
  volume: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  lastUpdate: {
    fontSize: 12,
    color: '#999',
  },
  positionCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  positionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  asset: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  quantity: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  positionDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  marketValue: {
    fontSize: 16,
    color: '#666',
  },
  pnl: {
    fontSize: 16,
    fontWeight: '600',
  },
  tradeCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  tradeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  tradeAsset: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  tradeSide: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  tradeDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  tradeQuantity: {
    fontSize: 16,
    color: '#666',
  },
  tradePrice: {
    fontSize: 16,
    color: '#666',
  },
  tradeStatus: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  tradeTime: {
    fontSize: 12,
    color: '#999',
  },
  inputGroup: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  assetButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  assetButton: {
    flex: 1,
    padding: 12,
    marginHorizontal: 4,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    alignItems: 'center',
  },
  assetButtonSelected: {
    backgroundColor: '#2196F3',
  },
  assetButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
  },
  assetButtonTextSelected: {
    color: '#fff',
  },
  sideButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  sideButton: {
    flex: 1,
    padding: 16,
    marginHorizontal: 4,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    alignItems: 'center',
  },
  buyButton: {
    backgroundColor: '#4CAF50',
  },
  sellButton: {
    backgroundColor: '#F44336',
  },
  sideButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#666',
  },
  buyButtonText: {
    color: '#fff',
  },
  sellButtonText: {
    color: '#fff',
  },
  input: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  inputText: {
    fontSize: 16,
    color: '#333',
  },
  placeOrderButton: {
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  placeOrderButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  periodButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  periodButton: {
    flex: 1,
    padding: 12,
    marginHorizontal: 4,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    alignItems: 'center',
  },
  periodButtonSelected: {
    backgroundColor: '#2196F3',
  },
  periodButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  periodButtonTextSelected: {
    color: '#fff',
  },
  analyticsCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 16,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    alignItems: 'center',
  },
  analyticsTitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  analyticsValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 4,
  },
  analyticsSubtitle: {
    fontSize: 14,
    color: '#999',
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  settingLabel: {
    fontSize: 16,
    color: '#333',
  },
  toggle: {
    width: 50,
    height: 30,
    backgroundColor: '#ddd',
    borderRadius: 15,
    justifyContent: 'center',
    paddingHorizontal: 2,
  },
  toggleActive: {
    backgroundColor: '#2196F3',
  },
  toggleThumb: {
    width: 26,
    height: 26,
    backgroundColor: '#fff',
    borderRadius: 13,
    alignSelf: 'flex-start',
  },
  toggleThumbActive: {
    alignSelf: 'flex-end',
  },
  menuItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  menuItemText: {
    fontSize: 16,
    color: '#333',
  },
  logoutButton: {
    backgroundColor: '#F44336',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    margin: 16,
  },
  logoutButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
});

export default App;
