import React, { useState, useEffect } from 'react';
import {
  generateComplianceReport,
  generateBulkComplianceReports,
  anonymizeComplianceData,
  getComplianceRegions,
  getComplianceStatus,
  getComplianceDashboard,
  validateComplianceRequirements,
  getComplianceHistory,
  ComplianceReport,
  formatDate
} from '../services/tradingApi';

interface RegulatoryComplianceDashboardProps {
  userId?: string;
}

const RegulatoryComplianceDashboard: React.FC<RegulatoryComplianceDashboardProps> = ({ userId = 'user123' }) => {
  // State management
  const [complianceRegions, setComplianceRegions] = useState<string[]>([]);
  const [complianceStatus, setComplianceStatus] = useState<Record<string, { compliant: boolean; score: number }>>({});
  const [complianceHistory, setComplianceHistory] = useState<ComplianceReport[]>([]);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'reports' | 'validation' | 'history'>('overview');

  // Report generation state
  const [reportGeneration, setReportGeneration] = useState({
    selectedRegion: 'US',
    regulationType: 'CFTC',
    selectedRegions: ['US', 'EU', 'UK', 'Middle East']
  });

  // Compliance validation state
  const [validationParams, setValidationParams] = useState({
    region: 'US',
    regulationType: 'CFTC'
  });

  // Data anonymization state
  const [anonymizationData, setAnonymizationData] = useState({
    data: {
      counterparty_name: 'ABC Trading Corp',
      trade_amount: 1000000,
      trade_date: '2024-01-15',
      commodity: 'crude_oil',
      location: 'Houston, TX'
    }
  });

  // Load initial data
  useEffect(() => {
    loadComplianceData();
  }, []);

  const loadComplianceData = async () => {
    try {
      setLoading(true);
      
      // Load compliance regions
      const regionsResult = await getComplianceRegions();
      if (regionsResult.success) {
        setComplianceRegions(regionsResult.data);
      }

      // Load compliance status
      const statusResult = await getComplianceStatus();
      if (statusResult.success) {
        setComplianceStatus(statusResult.data);
      }

      // Load compliance dashboard
      const dashboardResult = await getComplianceDashboard();
      if (dashboardResult.success) {
        setDashboardData(dashboardResult.data);
      }

      // Load compliance history
      const historyResult = await getComplianceHistory();
      if (historyResult.success) {
        setComplianceHistory(historyResult.data);
      }
    } catch (err) {
      setError('Failed to load compliance data');
      console.error('Error loading compliance data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateComplianceReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await generateComplianceReport(
        reportGeneration.selectedRegion,
        reportGeneration.regulationType
      );
      
      if (result.success) {
        alert('Compliance report generated successfully!');
        await loadComplianceData(); // Refresh data
      }
    } catch (err) {
      setError('Failed to generate compliance report');
      console.error('Error generating compliance report:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateBulkReports = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await generateBulkComplianceReports(reportGeneration.selectedRegions);
      
      if (result.success) {
        alert(`Bulk compliance reports generated for ${reportGeneration.selectedRegions.length} regions!`);
        await loadComplianceData(); // Refresh data
      }
    } catch (err) {
      setError('Failed to generate bulk compliance reports');
      console.error('Error generating bulk compliance reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnonymizeData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await anonymizeComplianceData(anonymizationData.data);
      
      if (result.success) {
        alert('Data anonymized successfully! Check the anonymized data below.');
        console.log('Anonymized data:', result.data);
      }
    } catch (err) {
      setError('Failed to anonymize data');
      console.error('Error anonymizing data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleValidateCompliance = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await validateComplianceRequirements(
        validationParams.region,
        validationParams.regulationType
      );
      
      if (result.success) {
        const message = result.data.compliant 
          ? `Compliant! Score: ${(result.data.score * 100).toFixed(1)}%`
          : `Non-compliant! Score: ${(result.data.score * 100).toFixed(1)}%`;
        alert(message);
      }
    } catch (err) {
      setError('Failed to validate compliance requirements');
      console.error('Error validating compliance requirements:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRegionIcon = (region: string) => {
    const icons: Record<string, string> = {
      'US': '🇺🇸',
      'EU': '🇪🇺',
      'UK': '🇬🇧',
      'Middle East': '🌍',
      'Guyana': '🇬🇾',
      'Asia': '🌏',
      'Africa': '🌍',
      'Australia': '🇦🇺'
    };
    return icons[region] || '🌍';
  };

  const getRegulationIcon = (regulation: string) => {
    const icons: Record<string, string> = {
      'CFTC': '📊',
      'EMIR': '🏛️',
      'ACER': '⚡',
      'GDPR': '🔒',
      'FERC': '⚡',
      'NERC': '🔌',
      'Dodd-Frank': '🏦',
      'MiFID II': '📈',
      'REMIT': '⚡',
      'MAR': '📊'
    };
    return icons[regulation] || '📋';
  };

  const getComplianceStatusColor = (compliant: boolean) => {
    return compliant ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  };

  const getComplianceScoreColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-100 text-green-800';
    if (score >= 0.6) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getRegulationDescription = (regulation: string) => {
    const descriptions: Record<string, string> = {
      'CFTC': 'Commodity Futures Trading Commission - US derivatives regulation',
      'EMIR': 'European Market Infrastructure Regulation - EU derivatives regulation',
      'ACER': 'Agency for the Cooperation of Energy Regulators - EU energy regulation',
      'GDPR': 'General Data Protection Regulation - EU data privacy',
      'FERC': 'Federal Energy Regulatory Commission - US energy regulation',
      'NERC': 'North American Electric Reliability Corporation - US grid reliability',
      'Dodd-Frank': 'Dodd-Frank Wall Street Reform - US financial regulation',
      'MiFID II': 'Markets in Financial Instruments Directive - EU financial markets',
      'REMIT': 'Regulation on Energy Market Integrity and Transparency - EU energy',
      'MAR': 'Market Abuse Regulation - EU market abuse prevention'
    };
    return descriptions[regulation] || 'Regulatory compliance requirements';
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Regulatory Compliance Dashboard</h1>
        <p className="text-gray-600">Comprehensive regulatory compliance management across all regions</p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Compliance Overview', icon: '📊' },
            { id: 'reports', label: 'Report Generation', icon: '📋' },
            { id: 'validation', label: 'Compliance Validation', icon: '✅' },
            { id: 'history', label: 'Compliance History', icon: '📈' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Compliance Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Compliance Dashboard Summary */}
          {dashboardData && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Global Compliance Overview</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">{dashboardData.total_regions}</div>
                  <div className="text-sm text-gray-600">Regions Monitored</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {Object.values(complianceStatus).filter(s => s.compliant).length}
                  </div>
                  <div className="text-sm text-gray-600">Compliant Regions</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-orange-600">
                    {Object.values(complianceStatus).filter(s => !s.compliant).length}
                  </div>
                  <div className="text-sm text-gray-600">Non-Compliant Regions</div>
                </div>
              </div>
            </div>
          )}

          {/* Regional Compliance Status */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold">Regional Compliance Status</h3>
            </div>
            <div className="p-6">
              {loading ? (
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="mt-2 text-gray-600">Loading compliance status...</p>
                </div>
              ) : complianceRegions.length === 0 ? (
                <div className="text-center text-gray-500">
                  <p>No compliance regions found.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {complianceRegions.map((region) => {
                    const status = complianceStatus[region] || { compliant: false, score: 0 };
                    return (
                      <div key={region} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center">
                            <span className="text-2xl mr-3">{getRegionIcon(region)}</span>
                            <h4 className="font-medium">{region}</h4>
                          </div>
                          <span className={`px-2 py-1 text-xs rounded-full ${getComplianceStatusColor(status.compliant)}`}>
                            {status.compliant ? 'Compliant' : 'Non-Compliant'}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600">
                          <div className="mb-2">Compliance Score: 
                            <span className={`ml-2 px-2 py-1 text-xs rounded-full ${getComplianceScoreColor(status.score)}`}>
                              {(status.score * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div>Last Updated: {new Date().toLocaleDateString()}</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={() => setActiveTab('reports')}
                className="p-4 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">📋</div>
                  <div className="font-medium text-blue-900">Generate Reports</div>
                  <div className="text-sm text-blue-600">Create compliance reports</div>
                </div>
              </button>

              <button
                onClick={() => setActiveTab('validation')}
                className="p-4 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors"
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">✅</div>
                  <div className="font-medium text-green-900">Validate Compliance</div>
                  <div className="text-sm text-green-600">Check compliance status</div>
                </div>
              </button>

              <button
                onClick={() => setActiveTab('history')}
                className="p-4 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors"
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">📈</div>
                  <div className="font-medium text-purple-900">View History</div>
                  <div className="text-sm text-purple-600">Track compliance changes</div>
                </div>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Report Generation Tab */}
      {activeTab === 'reports' && (
        <div className="space-y-6">
          {/* Single Region Report */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Generate Single Region Compliance Report</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Region</label>
                <select
                  value={reportGeneration.selectedRegion}
                  onChange={(e) => setReportGeneration(prev => ({ ...prev, selectedRegion: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {complianceRegions.map((region) => (
                    <option key={region} value={region}>{region}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Regulation Type</label>
                <select
                  value={reportGeneration.regulationType}
                  onChange={(e) => setReportGeneration(prev => ({ ...prev, regulationType: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="CFTC">CFTC (US Derivatives)</option>
                  <option value="EMIR">EMIR (EU Derivatives)</option>
                  <option value="ACER">ACER (EU Energy)</option>
                  <option value="GDPR">GDPR (EU Data Privacy)</option>
                  <option value="FERC">FERC (US Energy)</option>
                  <option value="NERC">NERC (US Grid Reliability)</option>
                  <option value="Dodd-Frank">Dodd-Frank (US Financial)</option>
                  <option value="MiFID II">MiFID II (EU Financial Markets)</option>
                  <option value="REMIT">REMIT (EU Energy Markets)</option>
                  <option value="MAR">MAR (EU Market Abuse)</option>
                </select>
              </div>
            </div>

            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium mb-2">Regulation Description</h4>
              <p className="text-sm text-gray-600">
                {getRegulationDescription(reportGeneration.regulationType)}
              </p>
            </div>

            <div className="mt-6">
              <button
                onClick={handleGenerateComplianceReport}
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Generating Report...' : 'Generate Compliance Report'}
              </button>
            </div>
          </div>

          {/* Bulk Report Generation */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Generate Bulk Compliance Reports</h2>
            <p className="text-gray-600 mb-4">
              Generate compliance reports for multiple regions simultaneously.
            </p>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Select Regions</label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {complianceRegions.map((region) => (
                  <label key={region} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={reportGeneration.selectedRegions.includes(region)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setReportGeneration(prev => ({
                            ...prev,
                            selectedRegions: [...prev.selectedRegions, region]
                          }));
                        } else {
                          setReportGeneration(prev => ({
                            ...prev,
                            selectedRegions: prev.selectedRegions.filter(r => r !== region)
                          }));
                        }
                      }}
                      className="mr-2"
                    />
                    <span className="text-sm">{region}</span>
                  </label>
                ))}
              </div>
            </div>

            <button
              onClick={handleGenerateBulkReports}
              disabled={loading || reportGeneration.selectedRegions.length === 0}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
            >
              {loading ? 'Generating Reports...' : `Generate Reports for ${reportGeneration.selectedRegions.length} Regions`}
            </button>
          </div>

          {/* Data Anonymization */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Data Anonymization Tool</h2>
            <p className="text-gray-600 mb-4">
              Anonymize sensitive compliance data for reporting and analysis purposes.
            </p>
            
            <div className="mb-4">
              <h4 className="font-medium mb-2">Sample Data for Anonymization</h4>
              <div className="bg-gray-50 p-4 rounded-lg">
                <pre className="text-sm text-gray-700 overflow-auto">
                  {JSON.stringify(anonymizationData.data, null, 2)}
                </pre>
              </div>
            </div>

            <button
              onClick={handleAnonymizeData}
              disabled={loading}
              className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
            >
              {loading ? 'Anonymizing...' : 'Anonymize Data'}
            </button>
          </div>
        </div>
      )}

      {/* Compliance Validation Tab */}
      {activeTab === 'validation' && (
        <div className="space-y-6">
          {/* Compliance Validation */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Validate Compliance Requirements</h2>
            <p className="text-gray-600 mb-4">
              Check if your current operations meet the compliance requirements for specific regions and regulations.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Region</label>
                <select
                  value={validationParams.region}
                  onChange={(e) => setValidationParams(prev => ({ ...prev, region: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {complianceRegions.map((region) => (
                    <option key={region} value={region}>{region}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Regulation Type</label>
                <select
                  value={validationParams.regulationType}
                  onChange={(e) => setValidationParams(prev => ({ ...prev, regulationType: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="CFTC">CFTC (US Derivatives)</option>
                  <option value="EMIR">EMIR (EU Derivatives)</option>
                  <option value="ACER">ACER (EU Energy)</option>
                  <option value="GDPR">GDPR (EU Data Privacy)</option>
                  <option value="FERC">FERC (US Energy)</option>
                  <option value="NERC">NERC (US Grid Reliability)</option>
                  <option value="Dodd-Frank">Dodd-Frank (US Financial)</option>
                  <option value="MiFID II">MiFID II (EU Financial Markets)</option>
                  <option value="REMIT">REMIT (EU Energy Markets)</option>
                  <option value="MAR">MAR (EU Market Abuse)</option>
                </select>
              </div>
            </div>

            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">Regulation Information</h4>
              <p className="text-sm text-blue-800">
                {getRegulationDescription(validationParams.regulationType)}
              </p>
            </div>

            <div className="mt-6">
              <button
                onClick={handleValidateCompliance}
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Validating...' : 'Validate Compliance'}
              </button>
            </div>
          </div>

          {/* Compliance Guidelines */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Compliance Guidelines</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-green-700 mb-2">✅ Key Compliance Areas</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Trade reporting and transparency</li>
                  <li>• Risk management and capital requirements</li>
                  <li>• Market abuse prevention</li>
                  <li>• Data privacy and protection</li>
                  <li>• Energy market integrity</li>
                  <li>• Financial market stability</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-red-700 mb-2">⚠️ Common Compliance Issues</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Late or incomplete trade reporting</li>
                  <li>• Insufficient risk controls</li>
                  <li>• Market manipulation practices</li>
                  <li>• Data privacy violations</li>
                  <li>• Inadequate record keeping</li>
                  <li>• Non-compliance with energy regulations</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Compliance History Tab */}
      {activeTab === 'history' && (
        <div className="space-y-6">
          {/* Compliance History Table */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold">Compliance History</h2>
            </div>
            <div className="overflow-x-auto">
              {loading ? (
                <div className="p-6 text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="mt-2 text-gray-600">Loading compliance history...</p>
                </div>
              ) : complianceHistory.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  <p>No compliance history found. Generate compliance reports to build history.</p>
                </div>
              ) : (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Region</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Regulation</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Level</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Check</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {complianceHistory.map((report, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <span className="text-2xl mr-3">{getRegionIcon(report.region)}</span>
                            <div className="text-sm font-medium text-gray-900">{report.region}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <span className="text-xl mr-2">{getRegulationIcon(report.regulation_type)}</span>
                            <div className="text-sm text-gray-900">{report.regulation_type}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getComplianceStatusColor(report.compliance_status)}`}>
                            {report.compliance_status ? 'Compliant' : 'Non-Compliant'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            report.risk_level === 'low' ? 'bg-green-100 text-green-800' :
                            report.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {report.risk_level}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(report.last_check)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          {/* Compliance Trends */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Compliance Trends</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {complianceHistory.filter(r => r.compliance_status).length}
                </div>
                <div className="text-sm text-gray-600">Compliant Reports</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {complianceHistory.filter(r => !r.compliance_status).length}
                </div>
                <div className="text-sm text-gray-600">Non-Compliant Reports</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {complianceHistory.length > 0 ? 
                    Math.round((complianceHistory.filter(r => r.compliance_status).length / complianceHistory.length) * 100) : 0
                  }%
                </div>
                <div className="text-sm text-gray-600">Overall Compliance Rate</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Summary Statistics */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <span className="text-2xl">🌍</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Regions Monitored</p>
              <p className="text-2xl font-semibold text-gray-900">{complianceRegions.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <span className="text-2xl">✅</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Compliant Regions</p>
              <p className="text-2xl font-semibold text-gray-900">
                {Object.values(complianceStatus).filter(s => s.compliant).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <span className="text-2xl">⚠️</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Non-Compliant</p>
              <p className="text-2xl font-semibold text-gray-900">
                {Object.values(complianceStatus).filter(s => !s.compliant).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <span className="text-2xl">📋</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Reports Generated</p>
              <p className="text-2xl font-semibold text-gray-900">{complianceHistory.length}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegulatoryComplianceDashboard;
