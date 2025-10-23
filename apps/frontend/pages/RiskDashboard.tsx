import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie } from 'recharts';

const RiskDashboard: React.FC = () => {
  const [data, setData] = useState([
    { name: 'Asset 1', value: 60 },
    { name: 'Asset 2', value: 40 }
  ]);

  // Mock data for VaR over time
  const varData = [
    { name: 'Day 1', var: 0.05 },
    { name: 'Day 2', var: 0.04 },
    { name: 'Day 3', var: 0.06 },
    { name: 'Day 4', var: 0.03 },
    { name: 'Day 5', var: 0.07 },
    { name: 'Day 6', var: 0.05 },
    { name: 'Day 7', var: 0.04 }
  ];

  useEffect(() => {
    fetch('/optimize/portfolio', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ returns: [0.1, 0.2], risks: [0.05, 0.1] })
    }).then(r => r.json()).then(setData);
  }, []);

  // TODO: Fetch real data from /risk/var endpoint
  const fetchRiskData = async () => {
    try {
      // const response = await fetch('http://localhost:8000/risk/var');
      // const data = await response.json();
      console.log('Fetching risk data...');
    } catch (error) {
      console.error('Error fetching risk data:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">
          Risk Dashboard
        </h1>
        
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            Value at Risk (VaR) Trend
          </h2>
          
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={varData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip 
                formatter={(value: number) => [`${(value * 100).toFixed(2)}%`, 'VaR']}
                labelFormatter={(label) => `Day: ${label}`}
              />
              <Line 
                type="monotone" 
                dataKey="var" 
                stroke="#ef4444" 
                strokeWidth={2}
                dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 mt-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            Portfolio Optimization
          </h2>
          
          <PieChart width={400} height={300}>
            <Pie data={data} dataKey="value" />
          </PieChart>
          
          <div className="mt-4 text-sm text-gray-600">
            <p>Risk metrics are updated in real-time. Higher VaR values indicate greater potential losses.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskDashboard;