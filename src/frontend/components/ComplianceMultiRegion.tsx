import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import axios from 'axios';

interface ComplianceRule {
  id: string;
  region: string;
  framework: string;
  rule_name: string;
  description: string;
  status: 'compliant' | 'non_compliant' | 'pending' | 'exempt';
  last_audit: string;
  next_audit: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  penalty_amount?: number;
}

interface ComplianceScore {
  region: string;
  overall_score: number;
  environmental_score: number;
  social_score: number;
  governance_score: number;
  last_updated: string;
  trend: 'improving' | 'stable' | 'declining';
}

interface AuditHistory {
  id: string;
  region: string;
  audit_type: string;
  auditor: string;
  date: string;
  score: number;
  findings: string[];
  recommendations: string[];
  status: 'passed' | 'failed' | 'conditional';
}

interface RegulatoryUpdate {
  id: string;
  region: string;
  regulation: string;
  effective_date: string;
  description: string;
  impact: 'low' | 'medium' | 'high' | 'critical';
  compliance_deadline: string;
  status: 'pending' | 'in_progress' | 'completed';
}

const ComplianceMultiRegion: React.FC = () => {
  const [complianceRules, setComplianceRules] = useState<ComplianceRule[]>([]);
  const [complianceScores, setComplianceScores] = useState<ComplianceScore[]>([]);
  const [auditHistory, setAuditHistory] = useState<AuditHistory[]>([]);
  const [regulatoryUpdates, setRegulatoryUpdates] = useState<RegulatoryUpdate[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedRegion, setSelectedRegion] = useState('all');
  const [selectedFramework, setSelectedFramework] = useState('all');

  const generateMockComplianceRules = (): ComplianceRule[] => [
    {
      id: 'rule_001',
      region: 'US',
      framework: 'FERC',
      rule_name: 'Energy Market Manipulation Prevention',
      description: 'Prohibits manipulation of energy markets through false information or artificial transactions',
      status: 'compliant',
      last_audit: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      next_audit: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
      risk_level: 'high',
    },
    {
      id: 'rule_002',
      region: 'EU',
      framework: 'REMIT',
      rule_name: 'Market Abuse Regulation',
      description: 'Prevents insider trading and market manipulation in energy markets',
      status: 'compliant',
      last_audit: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(),
      next_audit: new Date(Date.now() + 75 * 24 * 60 * 60 * 1000).toISOString(),
      risk_level: 'high',
    },
    {
      id: 'rule_003',
      region: 'UK',
      framework: 'UK-ETS',
      rule_name: 'Carbon Emissions Trading',
      description: 'Compliance with UK Emissions Trading Scheme requirements',
      status: 'pending',
      last_audit: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
      next_audit: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      risk_level: 'medium',
    },
    {
      id: 'rule_004',
      region: 'Middle East',
      framework: 'ADNOC',
      rule_name: 'Local Content Requirements',
      description: 'Ensures minimum local content in energy projects',
      status: 'non_compliant',
      last_audit: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
      next_audit: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString(),
      risk_level: 'critical',
      penalty_amount: 50000,
    },
    {
      id: 'rule_005',
      region: 'Guyana',
      framework: 'Petroleum Act',
      rule_name: 'Environmental Impact Assessment',
      description: 'Requires comprehensive environmental impact assessment for petroleum activities',
      status: 'compliant',
      last_audit: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
      next_audit: new Date(Date.now() + 100 * 24 * 60 * 60 * 1000).toISOString(),
      risk_level: 'medium',
    },
  ];

  const generateMockComplianceScores = (): ComplianceScore[] => [
    {
      region: 'US',
      overall_score: 92,
      environmental_score: 88,
      social_score: 95,
      governance_score: 94,
      last_updated: new Date().toISOString(),
      trend: 'improving',
    },
    {
      region: 'EU',
      overall_score: 89,
      environmental_score: 92,
      social_score: 87,
      governance_score: 88,
      last_updated: new Date().toISOString(),
      trend: 'stable',
    },
    {
      region: 'UK',
      overall_score: 85,
      environmental_score: 90,
      social_score: 82,
      governance_score: 83,
      last_updated: new Date().toISOString(),
      trend: 'declining',
    },
    {
      region: 'Middle East',
      overall_score: 78,
      environmental_score: 75,
      social_score: 80,
      governance_score: 79,
      last_updated: new Date().toISOString(),
      trend: 'improving',
    },
    {
      region: 'Guyana',
      overall_score: 82,
      environmental_score: 85,
      social_score: 78,
      governance_score: 83,
      last_updated: new Date().toISOString(),
      trend: 'stable',
    },
  ];

  const generateMockAuditHistory = (): AuditHistory[] => [
    {
      id: 'audit_001',
      region: 'US',
      audit_type: 'FERC Compliance',
      auditor: 'Deloitte & Touche',
      date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      score: 92,
      findings: ['Minor documentation gaps in trade reporting', 'Recommendation for enhanced monitoring systems'],
      recommendations: ['Implement automated trade monitoring', 'Enhance staff training on reporting requirements'],
      status: 'passed',
    },
    {
      id: 'audit_002',
      region: 'EU',
      audit_type: 'REMIT Compliance',
      auditor: 'PwC',
      date: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(),
      score: 89,
      findings: ['Some delays in insider information disclosure', 'Market abuse prevention systems adequate'],
      recommendations: ['Streamline disclosure processes', 'Consider AI-powered monitoring'],
      status: 'passed',
    },
    {
      id: 'audit_003',
      region: 'Middle East',
      audit_type: 'ADNOC Compliance',
      auditor: 'KPMG',
      date: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
      score: 78,
      findings: ['Significant gaps in local content requirements', 'Environmental compliance needs improvement'],
      recommendations: ['Develop local supplier network', 'Implement environmental management system'],
      status: 'failed',
    },
  ];

  const generateMockRegulatoryUpdates = (): RegulatoryUpdate[] => [
    {
      id: 'update_001',
      region: 'US',
      regulation: 'FERC Order 2222',
      effective_date: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(),
      description: 'New requirements for distributed energy resource participation in wholesale markets',
      impact: 'high',
      compliance_deadline: new Date(Date.now() + 120 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'in_progress',
    },
    {
      id: 'update_002',
      region: 'EU',
      regulation: 'EU Taxonomy Regulation',
      effective_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      description: 'Classification system for environmentally sustainable economic activities',
      impact: 'medium',
      compliance_deadline: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'pending',
    },
    {
      id: 'update_003',
      region: 'UK',
      regulation: 'Net Zero Strategy',
      effective_date: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString(),
      description: 'Enhanced requirements for carbon reduction and renewable energy integration',
      impact: 'high',
      compliance_deadline: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'in_progress',
    },
  ];

  useEffect(() => {
    // Load mock data initially
    setComplianceRules(generateMockComplianceRules());
    setComplianceScores(generateMockComplianceScores());
    setAuditHistory(generateMockAuditHistory());
    setRegulatoryUpdates(generateMockRegulatoryUpdates());
  }, []);

  const handleComplianceCheck = async () => {
    setLoading(true);
    try {
      // In production, this would call the actual backend API
      // const response = await axios.post('/api/disruptive/compliance/check', {
      //   region: selectedRegion,
      //   framework: selectedFramework,
      // });
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Update with new mock data
      setComplianceRules(generateMockComplianceRules());
      setComplianceScores(generateMockComplianceScores());
      
      toast.success('Compliance check completed successfully!');
    } catch (error) {
      toast.error('Failed to complete compliance check');
      console.error('Compliance check error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant': return 'text-green-600 bg-green-100';
      case 'non_compliant': return 'text-red-600 bg-red-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      case 'exempt': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getRiskLevelColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return '📈';
      case 'stable': return '➡️';
      case 'declining': return '📉';
      default: return '➡️';
    }
  };

  const getRegionFlag = (region: string) => {
    switch (region) {
      case 'US': return '🇺🇸';
      case 'EU': return '🇪🇺';
      case 'UK': return '🇬🇧';
      case 'Middle East': return '🌍';
      case 'Guyana': return '🇬🇾';
      default: return '🌍';
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const filteredRules = selectedRegion === 'all' && selectedFramework === 'all'
    ? complianceRules
    : complianceRules.filter(rule => 
        (selectedRegion === 'all' || rule.region === selectedRegion) &&
        (selectedFramework === 'all' || rule.framework === selectedFramework)
      );

  const filteredScores = selectedRegion === 'all'
    ? complianceScores
    : complianceScores.filter(score => score.region === selectedRegion);

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Compliance & Multi-Region</h2>
          <p className="text-gray-600">Multi-jurisdictional compliance monitoring and regulatory updates</p>
        </div>
        <button
          onClick={handleComplianceCheck}
          disabled={loading}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center space-x-2"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Checking...</span>
            </>
          ) : (
            <>
              <span>🔍</span>
              <span>Run Compliance Check</span>
            </>
          )}
        </button>
      </motion.div>

      {/* Controls */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white p-4 rounded-lg shadow-sm border"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Region</label>
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 w-full"
            >
              <option value="all">All Regions</option>
              <option value="US">United States</option>
              <option value="EU">European Union</option>
              <option value="UK">United Kingdom</option>
              <option value="Middle East">Middle East</option>
              <option value="Guyana">Guyana</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Framework</label>
            <select
              value={selectedFramework}
              onChange={(e) => setSelectedFramework(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 w-full"
            >
              <option value="all">All Frameworks</option>
              <option value="FERC">FERC (US)</option>
              <option value="REMIT">REMIT (EU)</option>
              <option value="UK-ETS">UK-ETS</option>
              <option value="ADNOC">ADNOC (Middle East)</option>
              <option value="Petroleum Act">Petroleum Act (Guyana)</option>
            </select>
          </div>
          <div className="flex items-end">
            <div className="text-sm text-gray-600">
              <div>Total Rules: {filteredRules.length}</div>
              <div>Compliant: {filteredRules.filter(r => r.status === 'compliant').length}</div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Compliance Scores Overview */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white p-6 rounded-lg shadow-sm border"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Regional Compliance Scores</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={filteredScores}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="region" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="overall_score" fill="#8884d8" name="Overall Score" />
              <Bar dataKey="environmental_score" fill="#82ca9d" name="Environmental" />
              <Bar dataKey="social_score" fill="#ffc658" name="Social" />
              <Bar dataKey="governance_score" fill="#ff8042" name="Governance" />
            </BarChart>
          </ResponsiveContainer>
          
          <div className="space-y-4">
            {filteredScores.map((score) => (
              <div key={score.region} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">{getRegionFlag(score.region)}</span>
                    <span className="font-medium text-gray-900">{score.region}</span>
                  </div>
                  <span className="text-2xl">{getTrendIcon(score.trend)}</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>Overall: <span className="font-medium">{score.overall_score}</span></div>
                  <div>Environmental: <span className="font-medium">{score.environmental_score}</span></div>
                  <div>Social: <span className="font-medium">{score.social_score}</span></div>
                  <div>Governance: <span className="font-medium">{score.governance_score}</span></div>
                </div>
                <div className="text-xs text-gray-500 mt-2">
                  Last updated: {new Date(score.last_updated).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Compliance Rules Table */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white p-6 rounded-lg shadow-sm border"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance Rules</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Region</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Framework</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rule</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Level</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Next Audit</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredRules.map((rule) => (
                <tr key={rule.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-xl mr-2">{getRegionFlag(rule.region)}</span>
                      <span className="text-sm font-medium text-gray-900">{rule.region}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{rule.framework}</td>
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{rule.rule_name}</div>
                      <div className="text-sm text-gray-500">{rule.description}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(rule.status)}`}>
                      {rule.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskLevelColor(rule.risk_level)}`}>
                      {rule.risk_level}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(rule.next_audit).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Audit History and Regulatory Updates */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Audit History */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white p-6 rounded-lg shadow-sm border"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Audits</h3>
          <div className="space-y-3">
            {auditHistory.map((audit) => (
              <div key={audit.id} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-xl">{getRegionFlag(audit.region)}</span>
                    <span className="font-medium text-gray-900">{audit.audit_type}</span>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    audit.status === 'passed' ? 'text-green-600 bg-green-100' : 
                    audit.status === 'failed' ? 'text-red-600 bg-red-100' : 
                    'text-yellow-600 bg-yellow-100'
                  }`}>
                    {audit.status}
                  </span>
                </div>
                <div className="text-sm text-gray-600 mb-2">
                  <div>Auditor: {audit.auditor}</div>
                  <div>Score: {audit.score}/100</div>
                  <div>Date: {new Date(audit.date).toLocaleDateString()}</div>
                </div>
                <div className="text-xs text-gray-500">
                  <div className="font-medium">Key Findings:</div>
                  <ul className="list-disc list-inside mt-1">
                    {audit.findings.slice(0, 2).map((finding, index) => (
                      <li key={index}>{finding}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Regulatory Updates */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white p-6 rounded-lg shadow-sm border"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Regulatory Updates</h3>
          <div className="space-y-3">
            {regulatoryUpdates.map((update) => (
              <div key={update.id} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-xl">{getRegionFlag(update.region)}</span>
                    <span className="font-medium text-gray-900">{update.regulation}</span>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(update.impact)}`}>
                    {update.impact}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{update.description}</p>
                <div className="grid grid-cols-2 gap-2 text-xs text-gray-500">
                  <div>Effective: {new Date(update.effective_date).toLocaleDateString()}</div>
                  <div>Deadline: {new Date(update.compliance_deadline).toLocaleDateString()}</div>
                </div>
                <div className="mt-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    update.status === 'completed' ? 'text-green-600 bg-green-100' : 
                    update.status === 'in_progress' ? 'text-blue-600 bg-blue-100' : 
                    'text-yellow-600 bg-yellow-100'
                  }`}>
                    {update.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ComplianceMultiRegion;
