import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ComposedChart,
  AreaChart,
  Area
} from 'recharts';
import { 
  Shield, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  FileText,
  Globe,
  Building,
  Scale,
  Gavel,
  BookOpen,
  Target,
  Activity,
  BarChart3,
  PieChart,
  Settings,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react';

interface ComplianceDashboardProps {
  userId?: string;
}

const ComplianceDashboard: React.FC<ComplianceDashboardProps> = ({ userId = 'user123' }) => {
  const [selectedFramework, setSelectedFramework] = useState('remit');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sample compliance frameworks
  const frameworks = [
    { 
      id: 'remit', 
      name: 'REMIT', 
      description: 'EU Energy Market Integrity',
      region: 'European Union',
      status: 'Compliant',
      score: 95,
      violations: 0,
      color: '#8884d8'
    },
    { 
      id: 'ferc', 
      name: 'FERC', 
      description: 'US Federal Energy Regulatory',
      region: 'United States',
      status: 'Compliant',
      score: 92,
      violations: 0,
      color: '#82ca9d'
    },
    { 
      id: 'cftc', 
      name: 'CFTC', 
      description: 'US Commodity Futures Trading',
      region: 'United States',
      status: 'Warning',
      score: 85,
      violations: 2,
      color: '#ffc658'
    },
    { 
      id: 'emir', 
      name: 'EMIR', 
      description: 'EU Market Infrastructure',
      region: 'European Union',
      status: 'Compliant',
      score: 88,
      violations: 0,
      color: '#00c49f'
    },
    { 
      id: 'islamic_finance', 
      name: 'Islamic Finance', 
      description: 'AAOIFI Standards',
      region: 'Global',
      status: 'Compliant',
      score: 98,
      violations: 0,
      color: '#ff7300'
    }
  ];

  const complianceHistory = [
    { date: '2024-01-01', remit: 90, ferc: 88, cftc: 82, emir: 85, islamic: 95 },
    { date: '2024-01-15', remit: 92, ferc: 90, cftc: 84, emir: 87, islamic: 96 },
    { date: '2024-02-01', remit: 94, ferc: 91, cftc: 83, emir: 88, islamic: 97 },
    { date: '2024-02-15', remit: 95, ferc: 92, cftc: 85, emir: 88, islamic: 98 },
    { date: '2024-03-01', remit: 95, ferc: 92, cftc: 85, emir: 88, islamic: 98 }
  ];

  const violationData = [
    { framework: 'REMIT', critical: 0, high: 0, medium: 0, low: 0 },
    { framework: 'FERC', critical: 0, high: 0, medium: 1, low: 1 },
    { framework: 'CFTC', critical: 0, high: 1, medium: 1, low: 0 },
    { framework: 'EMIR', critical: 0, high: 0, medium: 0, low: 0 },
    { framework: 'Islamic Finance', critical: 0, high: 0, medium: 0, low: 0 }
  ];

  const ruleCompliance = [
    { rule: 'Inside Information Disclosure', remit: 100, ferc: 95, cftc: 90, emir: 98, islamic: 100 },
    { rule: 'Market Manipulation Prevention', remit: 95, ferc: 92, cftc: 85, emir: 90, islamic: 98 },
    { rule: 'Position Reporting', remit: 90, ferc: 88, cftc: 82, emir: 85, islamic: 95 },
    { rule: 'Record Keeping', remit: 98, ferc: 95, cftc: 88, emir: 92, islamic: 100 },
    { rule: 'Anti-Manipulation', remit: 92, ferc: 90, cftc: 85, emir: 88, islamic: 95 }
  ];

  const auditTimeline = [
    { date: '2024-01-15', event: 'REMIT Report Submitted', status: 'Completed', framework: 'REMIT' },
    { date: '2024-01-20', event: 'FERC Audit', status: 'Completed', framework: 'FERC' },
    { date: '2024-01-25', event: 'CFTC Review', status: 'In Progress', framework: 'CFTC' },
    { date: '2024-02-01', event: 'Islamic Finance Assessment', status: 'Scheduled', framework: 'Islamic Finance' },
    { date: '2024-02-15', event: 'EMIR Compliance Check', status: 'Scheduled', framework: 'EMIR' }
  ];

  const riskMetrics = [
    { metric: 'Overall Compliance Score', value: 92, change: 2.1, status: 'good' },
    { metric: 'Active Violations', value: 2, change: -1, status: 'warning' },
    { metric: 'Critical Issues', value: 0, change: 0, status: 'good' },
    { metric: 'Audit Readiness', value: 95, change: 3.2, status: 'excellent' }
  ];

  const selectedFrameworkData = frameworks.find(f => f.id === selectedFramework);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Compliant': return 'text-green-600 bg-green-100';
      case 'Warning': return 'text-yellow-600 bg-yellow-100';
      case 'Non-Compliant': return 'text-red-600 bg-red-100';
      case 'In Progress': return 'text-blue-600 bg-blue-100';
      case 'Scheduled': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Completed': return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'In Progress': return <Clock className="h-5 w-5 text-blue-500" />;
      case 'Scheduled': return <Clock className="h-5 w-5 text-gray-500" />;
      default: return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-blue-600" />
              <h1 className="ml-3 text-2xl font-bold text-gray-900">Compliance Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Multi-Regional Regulatory Compliance
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Framework Selector */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-4 py-4">
            {frameworks.map((framework) => (
              <button
                key={framework.id}
                onClick={() => setSelectedFramework(framework.id)}
                className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedFramework === framework.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Scale className="h-4 w-4 mr-2" />
                {framework.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {riskMetrics.map((metric, index) => (
              <div key={index} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{metric.metric}</p>
                    <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                  </div>
                  <div className={`flex items-center ${
                    metric.status === 'excellent' ? 'text-green-600' :
                    metric.status === 'good' ? 'text-blue-600' :
                    metric.status === 'warning' ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {metric.change > 0 ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
                    <span className="ml-1 text-sm">{Math.abs(metric.change)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Framework Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Framework Status Overview</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
              {frameworks.map((framework, index) => (
                <div key={index} className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">{framework.score}%</div>
                  <div className="text-sm text-gray-600">{framework.name}</div>
                  <div className="mt-2">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(framework.status)}`}>
                      {framework.status}
                    </span>
                  </div>
                  <div className="mt-2 text-xs text-gray-500">
                    {framework.violations} violations
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Compliance History */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance Score History</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={complianceHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="remit" stroke="#8884d8" strokeWidth={2} name="REMIT" />
                <Line type="monotone" dataKey="ferc" stroke="#82ca9d" strokeWidth={2} name="FERC" />
                <Line type="monotone" dataKey="cftc" stroke="#ffc658" strokeWidth={2} name="CFTC" />
                <Line type="monotone" dataKey="emir" stroke="#00c49f" strokeWidth={2} name="EMIR" />
                <Line type="monotone" dataKey="islamic" stroke="#ff7300" strokeWidth={2} name="Islamic Finance" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Violation Analysis */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Violation Analysis by Severity</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={violationData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="framework" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="critical" stackId="a" fill="#dc2626" name="Critical" />
                <Bar dataKey="high" stackId="a" fill="#ea580c" name="High" />
                <Bar dataKey="medium" stackId="a" fill="#d97706" name="Medium" />
                <Bar dataKey="low" stackId="a" fill="#65a30d" name="Low" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Rule Compliance Radar */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Rule Compliance Radar</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={ruleCompliance}>
                <PolarGrid />
                <PolarAngleAxis dataKey="rule" />
                <PolarRadiusAxis angle={30} domain={[0, 100]} />
                <Radar name="REMIT" dataKey="remit" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                <Radar name="FERC" dataKey="ferc" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} />
                <Radar name="CFTC" dataKey="cftc" stroke="#ffc658" fill="#ffc658" fillOpacity={0.6} />
                <Radar name="EMIR" dataKey="emir" stroke="#00c49f" fill="#00c49f" fillOpacity={0.6} />
                <Radar name="Islamic Finance" dataKey="islamic" stroke="#ff7300" fill="#ff7300" fillOpacity={0.6} />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Audit Timeline */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Audit Timeline</h3>
            <div className="space-y-4">
              {auditTimeline.map((audit, index) => (
                <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      {getStatusIcon(audit.status)}
                    </div>
                    <div className="ml-4">
                      <p className="font-medium">{audit.event}</p>
                      <p className="text-sm text-gray-600">{audit.date}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-600">{audit.framework}</span>
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(audit.status)}`}>
                      {audit.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Compliance Recommendations */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance Recommendations</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { 
                  title: 'Address CFTC Violations', 
                  description: 'Resolve 2 medium-severity violations in CFTC framework',
                  priority: 'High',
                  framework: 'CFTC',
                  icon: AlertTriangle
                },
                { 
                  title: 'Enhance Record Keeping', 
                  description: 'Improve documentation for better audit readiness',
                  priority: 'Medium',
                  framework: 'All',
                  icon: FileText
                },
                { 
                  title: 'Update REMIT Reporting', 
                  description: 'Ensure timely submission of position reports',
                  priority: 'High',
                  framework: 'REMIT',
                  icon: Globe
                },
                { 
                  title: 'Strengthen Anti-Manipulation', 
                  description: 'Implement enhanced monitoring systems',
                  priority: 'Critical',
                  framework: 'FERC',
                  icon: Shield
                },
                { 
                  title: 'Islamic Finance Compliance', 
                  description: 'Maintain Sharia compliance for all transactions',
                  priority: 'High',
                  framework: 'Islamic Finance',
                  icon: BookOpen
                },
                { 
                  title: 'Automated Monitoring', 
                  description: 'Implement real-time compliance monitoring',
                  priority: 'Medium',
                  framework: 'All',
                  icon: Activity
                }
              ].map((recommendation, index) => {
                const Icon = recommendation.icon;
                return (
                  <div key={index} className="p-4 border rounded-lg">
                    <div className="flex items-start">
                      <Icon className="h-6 w-6 text-blue-600 mt-1 mr-3" />
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{recommendation.title}</h4>
                        <p className="text-sm text-gray-600 mt-1">{recommendation.description}</p>
                        <div className="mt-2 flex items-center justify-between">
                          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                            recommendation.priority === 'Critical' 
                              ? 'bg-red-100 text-red-800'
                              : recommendation.priority === 'High'
                              ? 'bg-orange-100 text-orange-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {recommendation.priority}
                          </span>
                          <span className="text-xs text-gray-500">{recommendation.framework}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Regulatory Framework Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Regulatory Framework Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {frameworks.map((framework, index) => (
                <div key={index} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium text-gray-900">{framework.name}</h4>
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(framework.status)}`}>
                      {framework.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-4">{framework.description}</p>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Region</span>
                      <span className="text-sm font-medium">{framework.region}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Score</span>
                      <span className="text-sm font-medium">{framework.score}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Violations</span>
                      <span className="text-sm font-medium">{framework.violations}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComplianceDashboard;
