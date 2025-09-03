import React, { useState } from 'react';
import TradeLifecycleManager from './TradeLifecycleManager';
import RiskAnalyticsDashboard from './RiskAnalyticsDashboard';
import AlgorithmicTradingDashboard from './AlgorithmicTradingDashboard';
import CreditManagementDashboard from './CreditManagementDashboard';
import RegulatoryComplianceDashboard from './RegulatoryComplianceDashboard';
import PerformanceMonitoringDashboard from './PerformanceMonitoringDashboard';

interface MainDashboardProps {
  userId?: string;
}

const MainDashboard: React.FC<MainDashboardProps> = ({ userId = 'user123' }) => {
  const [activeFeature, setActiveFeature] = useState<string>('overview');

  const features = [
    {
      id: 'overview',
      name: 'Platform Overview',
      icon: '🏠',
      description: 'High-level platform metrics and quick actions',
      color: 'bg-blue-500'
    },
    {
      id: 'trade-lifecycle',
      name: 'Trade Lifecycle',
      icon: '📊',
      description: 'Complete ETRM/CTRM trade lifecycle management',
      color: 'bg-green-500'
    },
    {
      id: 'risk-analytics',
      name: 'Risk Analytics',
      icon: '⚠️',
      description: 'Comprehensive risk management and analytics',
      color: 'bg-red-500'
    },
    {
      id: 'algo-trading',
      name: 'Algorithmic Trading',
      icon: '🤖',
      description: 'Advanced algorithmic trading with Islamic compliance',
      color: 'bg-purple-500'
    },
    {
      id: 'credit-management',
      name: 'Credit Management',
      icon: '🏦',
      description: 'Credit risk management and counterparty exposure',
      color: 'bg-orange-500'
    },
    {
      id: 'compliance',
      name: 'Regulatory Compliance',
      icon: '☪️',
      description: 'Multi-regional regulatory compliance management',
      color: 'bg-indigo-500'
    },
    {
      id: 'performance',
      name: 'Performance Monitoring',
      icon: '⚡',
      description: 'Real-time performance monitoring and optimization',
      color: 'bg-yellow-500'
    }
  ];

  const renderFeatureContent = () => {
    switch (activeFeature) {
      case 'trade-lifecycle':
        return <TradeLifecycleManager userId={userId} />;
      case 'risk-analytics':
        return <RiskAnalyticsDashboard userId={userId} />;
      case 'algo-trading':
        return <AlgorithmicTradingDashboard userId={userId} />;
      case 'credit-management':
        return <CreditManagementDashboard userId={userId} />;
      case 'compliance':
        return <RegulatoryComplianceDashboard userId={userId} />;
      case 'performance':
        return <PerformanceMonitoringDashboard userId={userId} />;
      default:
        return (
          <div className="max-w-7xl mx-auto p-6">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">QuantaEnergi Platform Dashboard</h1>
              <p className="text-gray-600">Next-generation ETRM/CTRM platform with comprehensive trading, risk management, and compliance features</p>
            </div>

            {/* Platform Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <span className="text-3xl">📊</span>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold text-gray-900">Trading Volume</h3>
                    <p className="text-2xl font-bold text-blue-600">$2.4B</p>
                    <p className="text-sm text-gray-600">+12% from last month</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-3 bg-green-100 rounded-lg">
                    <span className="text-3xl">✅</span>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold text-gray-900">Active Trades</h3>
                    <p className="text-2xl font-bold text-green-600">1,247</p>
                    <p className="text-sm text-gray-600">+8% from last week</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-3 bg-purple-100 rounded-lg">
                    <span className="text-3xl">☪️</span>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold text-gray-900">Compliance Score</h3>
                    <p className="text-2xl font-bold text-purple-600">98.5%</p>
                    <p className="text-sm text-gray-600">Across all regions</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Feature Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {features.slice(1).map((feature) => (
                <div
                  key={feature.id}
                  onClick={() => setActiveFeature(feature.id)}
                  className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-transparent hover:border-blue-500"
                >
                  <div className="flex items-center mb-4">
                    <span className="text-3xl mr-3">{feature.icon}</span>
                    <h3 className="text-lg font-semibold text-gray-900">{feature.name}</h3>
                  </div>
                  <p className="text-gray-600 mb-4">{feature.description}</p>
                  <div className="flex items-center text-blue-600 font-medium">
                    <span>Access Feature</span>
                    <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              ))}
            </div>

            {/* Recent Activity */}
            <div className="mt-8 bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold">Recent Platform Activity</h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center space-x-4">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">New trade captured - Crude Oil Forward</p>
                      <p className="text-xs text-gray-500">2 minutes ago</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">Risk analytics report generated</p>
                      <p className="text-xs text-gray-500">15 minutes ago</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">Algorithmic trading strategy executed</p>
                      <p className="text-xs text-gray-500">1 hour ago</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">Credit limit updated for CP001</p>
                      <p className="text-xs text-gray-500">2 hours ago</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <span className="text-2xl mr-3">⚡</span>
                <h1 className="text-xl font-bold text-gray-900">QuantaEnergi</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">Welcome,</span>
                <span className="text-sm font-medium text-gray-900">{userId}</span>
              </div>
              <button className="p-2 text-gray-400 hover:text-gray-500">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Feature Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8 overflow-x-auto">
            {features.map((feature) => (
              <button
                key={feature.id}
                onClick={() => setActiveFeature(feature.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                  activeFeature === feature.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{feature.icon}</span>
                {feature.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Feature Content */}
      <main className="flex-1">
        {renderFeatureContent()}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span className="text-2xl">⚡</span>
              <span className="text-sm text-gray-500">QuantaEnergi Platform v2.0</span>
            </div>
            <div className="text-sm text-gray-500">
              © 2024 QuantaEnergi. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default MainDashboard;
