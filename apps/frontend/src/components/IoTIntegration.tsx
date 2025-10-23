import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, BarChart, Bar, Cell } from 'recharts';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import axios from 'axios';

interface IoTDevice {
  id: string;
  name: string;
  type: 'sensor' | 'actuator' | 'gateway' | 'controller';
  location: string;
  status: 'online' | 'offline' | 'maintenance' | 'error';
  last_seen: string;
  battery_level: number;
  signal_strength: number;
  data_rate: number;
}

interface SensorData {
  timestamp: string;
  temperature: number;
  humidity: number;
  pressure: number;
  energy_consumption: number;
  grid_frequency: number;
  voltage: number;
  current: number;
}

interface WeatherData {
  timestamp: string;
  temperature: number;
  humidity: number;
  wind_speed: number;
  wind_direction: number;
  solar_radiation: number;
  precipitation: number;
  visibility: number;
}

interface GridStatus {
  frequency: number;
  voltage: number;
  load: number;
  stability: 'stable' | 'warning' | 'critical';
  last_updated: string;
}

interface Alert {
  id: string;
  type: 'warning' | 'error' | 'info' | 'critical';
  message: string;
  device_id: string;
  timestamp: string;
  acknowledged: boolean;
}

const IoTIntegration: React.FC = () => {
  const [iotDevices, setIotDevices] = useState<IoTDevice[]>([]);
  const [sensorData, setSensorData] = useState<SensorData[]>([]);
  const [weatherData, setWeatherData] = useState<WeatherData[]>([]);
  const [gridStatus, setGridStatus] = useState<GridStatus | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDeviceType, setSelectedDeviceType] = useState('all');
  const [autoRefresh, setAutoRefresh] = useState(true);

  const generateMockIoTDevices = (): IoTDevice[] => [
    {
      id: 'sensor_001',
      name: 'Temperature Sensor Alpha',
      type: 'sensor',
      location: 'Solar Panel Array A',
      status: 'online',
      last_seen: new Date().toISOString(),
      battery_level: 85,
      signal_strength: 92,
      data_rate: 1.2,
    },
    {
      id: 'actuator_001',
      name: 'Grid Controller Beta',
      type: 'actuator',
      location: 'Main Substation',
      status: 'online',
      last_seen: new Date().toISOString(),
      battery_level: 100,
      signal_strength: 98,
      data_rate: 5.8,
    },
    {
      id: 'gateway_001',
      name: 'Data Gateway Central',
      type: 'gateway',
      location: 'Control Room',
      status: 'online',
      last_seen: new Date().toISOString(),
      battery_level: 100,
      signal_strength: 100,
      data_rate: 25.4,
    },
    {
      id: 'sensor_002',
      name: 'Humidity Monitor Gamma',
      type: 'sensor',
      location: 'Wind Farm B',
      status: 'maintenance',
      last_seen: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      battery_level: 45,
      signal_strength: 78,
      data_rate: 0.8,
    },
    {
      id: 'controller_001',
      name: 'Load Balancer Delta',
      type: 'controller',
      location: 'Distribution Center',
      status: 'error',
      last_seen: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      battery_level: 100,
      signal_strength: 0,
      data_rate: 0,
    },
  ];

  const generateMockSensorData = (): SensorData[] => {
    const data: SensorData[] = [];
    const now = new Date();
    
    for (let i = 23; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000);
      data.push({
        timestamp: timestamp.toISOString(),
        temperature: 20 + Math.sin(i * 0.3) * 5 + (Math.random() - 0.5) * 2,
        humidity: 60 + Math.sin(i * 0.2) * 15 + (Math.random() - 0.5) * 5,
        pressure: 1013 + Math.sin(i * 0.1) * 10 + (Math.random() - 0.5) * 3,
        energy_consumption: 1000 + Math.sin(i * 0.4) * 200 + (Math.random() - 0.5) * 100,
        grid_frequency: 50 + (Math.random() - 0.5) * 0.2,
        voltage: 230 + (Math.random() - 0.5) * 10,
        current: 4.3 + (Math.random() - 0.5) * 0.5,
      });
    }
    
    return data;
  };

  const generateMockWeatherData = (): WeatherData[] => {
    const data: WeatherData[] = [];
    const now = new Date();
    
    for (let i = 23; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000);
      data.push({
        timestamp: timestamp.toISOString(),
        temperature: 22 + Math.sin(i * 0.3) * 8 + (Math.random() - 0.5) * 3,
        humidity: 65 + Math.sin(i * 0.2) * 20 + (Math.random() - 0.5) * 8,
        wind_speed: 5 + Math.sin(i * 0.4) * 8 + (Math.random() - 0.5) * 3,
        wind_direction: (Math.random() * 360),
        solar_radiation: Math.max(0, 800 + Math.sin(i * 0.3) * 600 + (Math.random() - 0.5) * 100),
        precipitation: Math.max(0, Math.random() * 5),
        visibility: 10 + (Math.random() - 0.5) * 2,
      });
    }
    
    return data;
  };

  const generateMockGridStatus = (): GridStatus => ({
    frequency: 50 + (Math.random() - 0.5) * 0.1,
    voltage: 230 + (Math.random() - 0.5) * 5,
    load: 75 + Math.random() * 20,
    stability: Math.random() > 0.8 ? 'warning' : Math.random() > 0.95 ? 'critical' : 'stable',
    last_updated: new Date().toISOString(),
  });

  const generateMockAlerts = (): Alert[] => [
    {
      id: 'alert_001',
      type: 'warning',
      message: 'High temperature detected in Solar Panel Array A',
      device_id: 'sensor_001',
      timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      acknowledged: false,
    },
    {
      id: 'alert_002',
      type: 'error',
      message: 'Load Balancer Delta connection lost',
      device_id: 'controller_001',
      timestamp: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
      acknowledged: false,
    },
    {
      id: 'alert_003',
      type: 'info',
      message: 'Maintenance scheduled for Humidity Monitor Gamma',
      device_id: 'sensor_002',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      acknowledged: true,
    },
  ];

  useEffect(() => {
    // Load mock data initially
    setIotDevices(generateMockIoTDevices());
    setSensorData(generateMockSensorData());
    setWeatherData(generateMockWeatherData());
    setGridStatus(generateMockGridStatus());
    setAlerts(generateMockAlerts());

    // Set up auto-refresh
    if (autoRefresh) {
      const interval = setInterval(() => {
        setSensorData(generateMockSensorData());
        setWeatherData(generateMockWeatherData());
        setGridStatus(generateMockGridStatus());
      }, 30000); // Refresh every 30 seconds

      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const handleRefreshData = async () => {
    setLoading(true);
    try {
      // In production, this would call the actual backend API
      // const response = await axios.get('/api/disruptive/iot/refresh');
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update with new mock data
      setSensorData(generateMockSensorData());
      setWeatherData(generateMockWeatherData());
      setGridStatus(generateMockGridStatus());
      setAlerts(generateMockAlerts());
      
      toast.success('IoT data refreshed successfully!');
    } catch (error) {
      toast.error('Failed to refresh IoT data');
      console.error('Refresh error:', error);
    } finally {
      setLoading(false);
    }
  };

  const acknowledgeAlert = (alertId: string) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, acknowledged: true } : alert
    ));
    toast.success('Alert acknowledged');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-600 bg-green-100';
      case 'offline': return 'text-gray-600 bg-gray-100';
      case 'maintenance': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStabilityColor = (stability: string) => {
    switch (stability) {
      case 'stable': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getAlertTypeColor = (type: string) => {
    switch (type) {
      case 'info': return 'text-blue-600 bg-blue-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      case 'critical': return 'text-red-800 bg-red-200';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getDeviceTypeIcon = (type: string) => {
    switch (type) {
      case 'sensor': return '📡';
      case 'actuator': return '⚙️';
      case 'gateway': return '🌐';
      case 'controller': return '🎛️';
      default: return '📱';
    }
  };

  const filteredDevices = selectedDeviceType === 'all' 
    ? iotDevices 
    : iotDevices.filter(device => device.type === selectedDeviceType);

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h2 className="text-2xl font-bold text-gray-900">IoT Integration Hub</h2>
          <p className="text-gray-600">Real-time monitoring and control of energy infrastructure</p>
        </div>
        <div className="flex items-center space-x-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-600">Auto-refresh</span>
          </label>
          <button
            onClick={handleRefreshData}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Refreshing...</span>
              </>
            ) : (
              <>
                <span>🔄</span>
                <span>Refresh Data</span>
              </>
            )}
          </button>
        </div>
      </motion.div>

      {/* Controls */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white p-4 rounded-lg shadow-sm border"
      >
        <div className="flex space-x-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Device Type</label>
            <select
              value={selectedDeviceType}
              onChange={(e) => setSelectedDeviceType(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Types</option>
              <option value="sensor">Sensors</option>
              <option value="actuator">Actuators</option>
              <option value="gateway">Gateways</option>
              <option value="controller">Controllers</option>
            </select>
          </div>
        </div>
      </motion.div>

      {/* IoT Devices Overview */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white p-6 rounded-lg shadow-sm border"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">IoT Devices Status</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Device</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Battery</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Signal</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data Rate</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredDevices.map((device) => (
                <tr key={device.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-2xl mr-3">{getDeviceTypeIcon(device.type)}</span>
                      <div>
                        <div className="text-sm font-medium text-gray-900">{device.name}</div>
                        <div className="text-sm text-gray-500">ID: {device.id}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 capitalize">
                    {device.type}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {device.location}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(device.status)}`}>
                      {device.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${device.battery_level}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-900">{device.battery_level}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${device.signal_strength}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-900">{device.signal_strength}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {device.data_rate.toFixed(1)} Mbps
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Real-time Data Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sensor Data */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white p-6 rounded-lg shadow-sm border"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sensor Data (24h)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={sensorData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" tickFormatter={(value) => new Date(value).getHours() + 'h'} />
              <YAxis />
              <Tooltip labelFormatter={(value) => new Date(value).toLocaleString()} />
              <Legend />
              <Line type="monotone" dataKey="temperature" stroke="#8884d8" name="Temperature (°C)" />
              <Line type="monotone" dataKey="humidity" stroke="#82ca9d" name="Humidity (%)" />
              <Line type="monotone" dataKey="energy_consumption" stroke="#ffc658" name="Energy (kWh)" />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Weather Data */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white p-6 rounded-lg shadow-sm border"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Weather Conditions (24h)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={weatherData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" tickFormatter={(value) => new Date(value).getHours() + 'h'} />
              <YAxis />
              <Tooltip labelFormatter={(value) => new Date(value).toLocaleString()} />
              <Legend />
              <Area type="monotone" dataKey="temperature" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} name="Temperature (°C)" />
              <Area type="monotone" dataKey="wind_speed" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} name="Wind Speed (m/s)" />
              <Area type="monotone" dataKey="solar_radiation" stroke="#ffc658" fill="#ffc658" fillOpacity={0.6} name="Solar Radiation (W/m²)" />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Grid Status and Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Grid Status */}
        {gridStatus && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white p-6 rounded-lg shadow-sm border"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Grid Status</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{gridStatus.frequency.toFixed(2)} Hz</div>
                  <div className="text-sm text-gray-600">Frequency</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{gridStatus.voltage.toFixed(0)} V</div>
                  <div className="text-sm text-gray-600">Voltage</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{gridStatus.load.toFixed(1)}%</div>
                  <div className="text-sm text-gray-600">Load</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStabilityColor(gridStatus.stability)}`}>
                    {gridStatus.stability}
                  </span>
                  <div className="text-sm text-gray-600 mt-1">Stability</div>
                </div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-xs text-blue-600">
                  Last updated: {new Date(gridStatus.last_updated).toLocaleString()}
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Alerts */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white p-6 rounded-lg shadow-sm border"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Alerts</h3>
          <div className="space-y-3">
            {alerts.filter(alert => !alert.acknowledged).map((alert) => (
              <div key={alert.id} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getAlertTypeColor(alert.type)}`}>
                    {alert.type}
                  </span>
                  <button
                    onClick={() => acknowledgeAlert(alert.id)}
                    className="text-xs text-blue-600 hover:text-blue-800"
                  >
                    Acknowledge
                  </button>
                </div>
                <p className="text-sm text-gray-900 mb-2">{alert.message}</p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Device: {alert.device_id}</span>
                  <span>{new Date(alert.timestamp).toLocaleString()}</span>
                </div>
              </div>
            ))}
            {alerts.filter(alert => !alert.acknowledged).length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">✅</div>
                <div>No active alerts</div>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default IoTIntegration;
