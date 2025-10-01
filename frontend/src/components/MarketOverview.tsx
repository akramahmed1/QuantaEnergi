import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    tension: number;
  }>;
}

interface MarketData {
  prices: Array<{
    timestamp: string;
    price: number;
    volume: number;
  }>;
  signals: Array<{
    type: string;
    strength: number;
    timestamp: string;
  }>;
}

interface WeatherData {
  temp: number;
  humidity: number;
  description: string;
  wind_speed: number;
}

interface WeatherForecastData {
  forecasts: Array<{
    date: string;
    temp: number;
    description: string;
  }>;
}

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    tension: number;
  }[];
}

interface MarketOverviewProps {
  data?: MarketData;
  loading: boolean;
  weatherData?: WeatherData | null;
  weatherForecast?: WeatherForecastData | null;
}

const MarketOverview: React.FC<MarketOverviewProps> = ({
  data,
  loading,
  weatherData,
  weatherForecast
}) => {
  const [chartData, setChartData] = useState<ChartData>({
    labels: [],
    datasets: []
  });

  useEffect(() => {
    if (data?.prices) {
      const labels = data.prices.map(price => 
        new Date(price.timestamp).toLocaleTimeString()
      );
      const prices = data.prices.map(price => price.price);

      const newChartData: ChartData = {
        labels,
        datasets: [
          {
            label: 'Energy Price',
            data: prices,
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.1,
          },
        ],
      };
      setChartData(newChartData);
    }
  }, [data]);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Real-time Energy Prices',
      },
    },
    scales: {
      y: {
        beginAtZero: false,
      },
    },
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Market Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Market Overview
        </h2>
        {chartData.labels.length > 0 ? (
          <Line data={chartData} options={options} />
        ) : (
          <div className="h-64 flex items-center justify-center text-gray-500">
            No market data available
          </div>
        )}
      </div>

      {/* Weather Information */}
      {(weatherData || weatherForecast) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {weatherData && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Current Weather
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Temperature:</span>
                  <span className="font-medium">{weatherData.temp}°C</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Humidity:</span>
                  <span className="font-medium">{weatherData.humidity}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Description:</span>
                  <span className="font-medium capitalize">{weatherData.description}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Wind Speed:</span>
                  <span className="font-medium">{weatherData.wind_speed} m/s</span>
                </div>
              </div>
            </div>
          )}

          {weatherForecast && weatherForecast.forecasts.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Weather Forecast
              </h3>
              <div className="space-y-2">
                {weatherForecast.forecasts.slice(0, 5).map((forecast, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-gray-600">{forecast.date}</span>
                    <div className="flex items-center space-x-2">
                      <span className="font-medium">{forecast.temp}°C</span>
                      <span className="text-sm text-gray-500 capitalize">
                        {forecast.description}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MarketOverview;
