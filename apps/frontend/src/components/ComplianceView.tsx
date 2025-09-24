import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';

interface ShariaCompliance {
  trade_id: string;
  overall_status: string;
  compliance_checks: Record<string, any>;
  recommendations: string[];
  compliance_score: number;
  checked_at: string;
}

interface ComplianceReport {
  report_id: string;
  report_type: string;
  report_name: string;
  generated_at: string;
  report_period: {
    start_date: string;
    end_date: string;
  };
  data_summary: {
    total_records: number;
    total_value: number;
    threshold_exceeded: boolean;
  };
  compliance_status: {
    status: string;
    exceeds_threshold: boolean;
  };
  anonymized: boolean;
}

interface SubscriptionPlan {
  name: string;
  price: number;
  currency: string;
  interval: string;
  features: string[];
  limits: {
    trades_per_month: number;
    api_calls_per_day: number;
    storage_gb: number;
  };
}

const ComplianceView: React.FC = () => {
  const [selectedReportType, setSelectedReportType] = useState('cftc');
  const [shariaTradeData, setShariaTradeData] = useState({
    id: '',
    commodity: 'electricity',
    price: 0,
    quantity: 0,
    trade_type: 'spot',
    delivery_date: '',
    delivery_location: ''
  });

  // Fetch subscription plans
  const { data: plans, isLoading: plansLoading } = useQuery({
    queryKey: ['billing-plans'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/v1/billing/plans', {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    }
  });

  // Sharia compliance check mutation
  const shariaComplianceMutation = useMutation({
    mutationFn: async (tradeData: any) => {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:8000/api/v1/sharia/check', tradeData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data as ShariaCompliance;
    }
  });

  // Compliance report generation mutation
  const reportGenerationMutation = useMutation({
    mutationFn: async (reportData: any) => {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:8000/api/v1/reports/generate', reportData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data as ComplianceReport;
    }
  });

  const handleShariaCheck = () => {
    if (shariaTradeData.id && shariaTradeData.commodity && shariaTradeData.price > 0) {
      shariaComplianceMutation.mutate(shariaTradeData);
    }
  };

  const handleGenerateReport = () => {
    const reportData = {
      report_type: selectedReportType,
      start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      end_date: new Date().toISOString(),
      data: [], // Mock data - in real app, this would come from actual trades
      anonymize: true
    };
    reportGenerationMutation.mutate(reportData);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant': return 'text-green-600 bg-green-100';
      case 'non_compliant': return 'text-red-600 bg-red-100';
      case 'requires_review': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Compliance & Billing</h1>
          <p className="text-gray-600">Sharia compliance, regulatory reporting, and subscription management</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Sharia Compliance */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Sharia Compliance Check</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Trade ID</label>
                <input
                  type="text"
                  value={shariaTradeData.id}
                  onChange={(e) => setShariaTradeData({...shariaTradeData, id: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Enter trade ID"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Commodity</label>
                  <select
                    value={shariaTradeData.commodity}
                    onChange={(e) => setShariaTradeData({...shariaTradeData, commodity: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="electricity">Electricity</option>
                    <option value="solar_energy">Solar Energy</option>
                    <option value="wind_energy">Wind Energy</option>
                    <option value="natural_gas">Natural Gas</option>
                    <option value="crude_oil">Crude Oil</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Price</label>
                  <input
                    type="number"
                    value={shariaTradeData.price}
                    onChange={(e) => setShariaTradeData({...shariaTradeData, price: Number(e.target.value)})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="0.00"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                  <input
                    type="number"
                    value={shariaTradeData.quantity}
                    onChange={(e) => setShariaTradeData({...shariaTradeData, quantity: Number(e.target.value)})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="0"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Trade Type</label>
                  <select
                    value={shariaTradeData.trade_type}
                    onChange={(e) => setShariaTradeData({...shariaTradeData, trade_type: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="spot">Spot</option>
                    <option value="forward">Forward</option>
                    <option value="futures">Futures</option>
                  </select>
                </div>
              </div>
              
              <button
                onClick={handleShariaCheck}
                disabled={shariaComplianceMutation.isPending}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                {shariaComplianceMutation.isPending ? 'Checking...' : 'Check Sharia Compliance'}
              </button>
            </div>

            {/* Sharia Compliance Results */}
            {shariaComplianceMutation.data && (
              <div className="mt-6 p-4 bg-gray-50 rounded-md">
                <h3 className="font-semibold mb-2">Compliance Results</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Overall Status:</span>
                    <span className={`px-2 py-1 rounded text-sm ${getStatusColor(shariaComplianceMutation.data.overall_status)}`}>
                      {shariaComplianceMutation.data.overall_status.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Compliance Score:</span>
                    <span className="font-semibold">{shariaComplianceMutation.data.compliance_score.toFixed(1)}%</span>
                  </div>
                  <div>
                    <span className="font-medium">Recommendations:</span>
                    <ul className="mt-1 space-y-1">
                      {shariaComplianceMutation.data.recommendations.map((rec, index) => (
                        <li key={index} className="text-sm text-gray-600">{rec}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Compliance Reporting */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Regulatory Reporting</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Report Type</label>
                <select
                  value={selectedReportType}
                  onChange={(e) => setSelectedReportType(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="cftc">CFTC Large Trader Report</option>
                  <option value="emir">EMIR Trade Repository Report</option>
                  <option value="gdpr">GDPR Data Processing Report</option>
                  <option value="guyana">Guyana Energy Sector Report</option>
                </select>
              </div>
              
              <div className="text-sm text-gray-600">
                <p><strong>CFTC:</strong> Daily reporting for large traders</p>
                <p><strong>EMIR:</strong> European trade repository reporting</p>
                <p><strong>GDPR:</strong> Data protection compliance</p>
                <p><strong>Guyana:</strong> Energy sector regulatory reporting</p>
              </div>
              
              <button
                onClick={handleGenerateReport}
                disabled={reportGenerationMutation.isPending}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {reportGenerationMutation.isPending ? 'Generating...' : 'Generate Report'}
              </button>
            </div>

            {/* Report Results */}
            {reportGenerationMutation.data && (
              <div className="mt-6 p-4 bg-gray-50 rounded-md">
                <h3 className="font-semibold mb-2">Report Generated</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Report ID:</span>
                    <span className="font-mono">{reportGenerationMutation.data.report_id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Records:</span>
                    <span>{reportGenerationMutation.data.data_summary.total_records}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Value:</span>
                    <span>${reportGenerationMutation.data.data_summary.total_value.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Status:</span>
                    <span className={`px-2 py-1 rounded text-xs ${getStatusColor(reportGenerationMutation.data.compliance_status.status)}`}>
                      {reportGenerationMutation.data.compliance_status.status.toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Subscription Plans */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Subscription Plans</h2>
          
          {plansLoading ? (
            <div className="animate-pulse">Loading plans...</div>
          ) : plans?.plans ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {Object.entries(plans.plans).map(([tier, plan]) => (
                <div key={tier} className="border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-2">{plan.name}</h3>
                  <div className="text-3xl font-bold text-indigo-600 mb-4">
                    ${plan.price}
                    <span className="text-sm font-normal text-gray-500">/{plan.interval}</span>
                  </div>
                  
                  <ul className="space-y-2 mb-6">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-center text-sm text-gray-600">
                        <span className="text-green-500 mr-2">✓</span>
                        {feature}
                      </li>
                    ))}
                  </ul>
                  
                  <div className="text-xs text-gray-500 mb-4">
                    <p>Trades: {plan.limits.trades_per_month === -1 ? 'Unlimited' : plan.limits.trades_per_month}/month</p>
                    <p>API Calls: {plan.limits.api_calls_per_day === -1 ? 'Unlimited' : plan.limits.api_calls_per_day}/day</p>
                    <p>Storage: {plan.limits.storage_gb}GB</p>
                  </div>
                  
                  <button className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700">
                    Choose Plan
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-500">No plans available</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ComplianceView;
