import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

interface ComplianceData {
  report_id: string;
  report_type: string;
  template_name: string;
  generated_at: string;
  status: string;
  sections_count: number;
  total_pages: number;
}

interface ReportTemplate {
  name: string;
  description: string;
  sections: Array<{
    id: string;
    title: string;
    fields: string[];
  }>;
}

const ComplianceView: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedReportType, setSelectedReportType] = useState('ferc');
  const [reportData, setReportData] = useState<any>({});
  const [customTemplate, setCustomTemplate] = useState<any>({});

  // Fetch available report templates
  const { data: templates, isLoading: templatesLoading } = useQuery({
    queryKey: ['report-templates'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/v1/reports/templates', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      return response.data;
    }
  });

  // Fetch generated reports
  const { data: reports, isLoading: reportsLoading } = useQuery({
    queryKey: ['generated-reports'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/v1/reports', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      return response.data;
    }
  });

  // Build report mutation
  const buildReportMutation = useMutation({
    mutationFn: async ({ reportType, data, templateConfig }: { reportType: string; data: any; templateConfig?: any }) => {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:8000/api/v1/reports/build', {
        report_type: reportType,
        data: data,
        template_config: templateConfig
      }, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['generated-reports'] });
      alert('Report built successfully!');
    },
    onError: (error: any) => {
      console.error('Failed to build report:', error);
      alert('Failed to build report. Please try again.');
    }
  });

  // Export report mutation
  const exportReportMutation = useMutation({
    mutationFn: async ({ reportId, format }: { reportId: string; format: string }) => {
      const token = localStorage.getItem('token');
      const response = await axios.post(`http://localhost:8000/api/v1/reports/${reportId}/export`, {
        export_format: format
      }, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    },
    onSuccess: (data, variables) => {
      // Download the exported file
      const blob = new Blob([atob(data.export_data.content)], { type: data.export_data.content_type });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = data.export_data.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    },
    onError: (error: any) => {
      console.error('Failed to export report:', error);
      alert('Failed to export report. Please try again.');
    }
  });

  const generateComplianceData = () => {
    // Generate mock compliance data based on selected report type
    const mockData = {
      ferc: {
        total_trades: 150,
        total_volume: 2500000,
        total_value: 125000000,
        compliance_status: 'compliant',
        trades: [
          { trade_id: 'TRD001', commodity: 'crude_oil', quantity: 10000, price: 75.50, counterparty: 'Shell Trading', delivery_date: '2024-02-15', status: 'completed' },
          { trade_id: 'TRD002', commodity: 'natural_gas', quantity: 50000, price: 3.25, counterparty: 'BP Energy', delivery_date: '2024-02-20', status: 'pending' },
          { trade_id: 'TRD003', commodity: 'lng', quantity: 25000, price: 8.75, counterparty: 'ExxonMobil', delivery_date: '2024-02-25', status: 'completed' }
        ],
        var_95: 2500000,
        var_99: 3500000,
        expected_shortfall: 4200000,
        stress_test_results: 'passed',
        ferc_compliance: 'compliant',
        reporting_accuracy: 99.8,
        audit_trail: 'complete'
      },
      remit: {
        participant_id: 'MP001',
        name: 'QuantaEnergi Trading',
        registration_status: 'active',
        contact_info: {
          email: 'compliance@quantaenergi.com',
          phone: '+1-555-0123'
        },
        transactions: [
          { transaction_id: 'TXN001', market: 'NYMEX', product: 'Crude Oil Futures', quantity: 1000, price: 76.25, timestamp: '2024-02-01T10:30:00Z' },
          { transaction_id: 'TXN002', market: 'ICE', product: 'Natural Gas Futures', quantity: 5000, price: 3.30, timestamp: '2024-02-01T14:15:00Z' }
        ],
        facility_id: 'FAC001',
        generation_capacity: 1000000,
        outage_info: 'none',
        forecast_data: 'updated',
        information_type: 'market_data',
        disclosure_time: '2024-02-01T09:00:00Z',
        recipients: ['market_operators'],
        market_impact: 'minimal'
      },
      trade_summary: {
        total_trades: 150,
        total_volume: 2500000,
        total_value: 125000000,
        average_price: 50.00,
        top_commodities: ['crude_oil', 'natural_gas', 'lng'],
        pnl_summary: {
          realized_pnl: 2500000,
          unrealized_pnl: 750000,
          total_pnl: 3250000
        },
        risk_metrics: {
          var_95: 2500000,
          var_99: 3500000,
          max_drawdown: 500000
        },
        compliance_score: 98.5,
        efficiency_metrics: {
          trade_execution_time: 2.5,
          settlement_time: 1.2,
          error_rate: 0.1
        },
        price_trends: {
          trend_direction: 'upward',
          volatility: 15.2,
          momentum: 'positive'
        },
        volume_analysis: {
          daily_average: 8500,
          peak_volume: 15000,
          volume_trend: 'stable'
        },
        market_share: 12.5,
        competitive_position: 'strong'
      }
    };

    return mockData[selectedReportType as keyof typeof mockData] || {};
  };

  const handleBuildReport = () => {
    const data = generateComplianceData();
    buildReportMutation.mutate({
      reportType: selectedReportType,
      data: data,
      templateConfig: customTemplate
    });
  };

  const handleExportPDF = (reportId: string) => {
    exportReportMutation.mutate({
      reportId: reportId,
      format: 'pdf'
    });
  };

  const handleExportExcel = (reportId: string) => {
    exportReportMutation.mutate({
      reportId: reportId,
      format: 'excel'
    });
  };

  const generatePDFReport = () => {
    const data = generateComplianceData();
    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(20);
    doc.text(`${templates?.templates[selectedReportType]?.name || 'Compliance Report'}`, 20, 30);
    
    // Add generation date
    doc.setFontSize(12);
    doc.text(`Generated: ${new Date().toLocaleDateString()}`, 20, 45);
    
    let yPosition = 60;
    
    // Add sections
    if (templates?.templates[selectedReportType]?.sections) {
      templates.templates[selectedReportType].sections.forEach((section: any) => {
        // Section title
        doc.setFontSize(14);
        doc.setFont(undefined, 'bold');
        doc.text(section.title, 20, yPosition);
        yPosition += 15;
        
        // Section data
        doc.setFontSize(10);
        doc.setFont(undefined, 'normal');
        
        const sectionData = data[section.id] || {};
        
        if (Array.isArray(sectionData)) {
          // Handle array data (like trades)
          const tableData = sectionData.map((item: any) => 
            section.fields.map((field: string) => item[field] || 'N/A')
          );
          
          doc.autoTable({
            head: [section.fields],
            body: tableData,
            startY: yPosition,
            styles: { fontSize: 8 }
          });
          
          yPosition = (doc as any).lastAutoTable.finalY + 20;
        } else if (typeof sectionData === 'object') {
          // Handle object data
          Object.entries(sectionData).forEach(([key, value]) => {
            doc.text(`${key}: ${value}`, 20, yPosition);
            yPosition += 10;
          });
          yPosition += 10;
        } else {
          // Handle simple values
          section.fields.forEach((field: string) => {
            const value = data[field] || 'N/A';
            doc.text(`${field}: ${value}`, 20, yPosition);
            yPosition += 10;
          });
          yPosition += 10;
        }
        
        // Add new page if needed
        if (yPosition > 250) {
          doc.addPage();
          yPosition = 20;
        }
      });
    }
    
    // Save the PDF
    doc.save(`compliance_report_${selectedReportType}_${new Date().toISOString().split('T')[0]}.pdf`);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (templatesLoading || reportsLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading compliance reports...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="bg-white shadow-xl rounded-lg overflow-hidden mb-8">
        <div className="bg-gradient-to-r from-green-600 to-blue-600 px-6 py-4">
          <h1 className="text-3xl font-bold text-white">Compliance Reporting</h1>
          <p className="text-green-100 mt-2">Generate and manage regulatory compliance reports (FERC/REMIT)</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Report Builder */}
        <div className="bg-white shadow-lg rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Build New Report</h2>
          
          {/* Report Type Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Report Type
            </label>
            <div className="grid grid-cols-1 gap-3">
              {templates?.templates && Object.entries(templates.templates).map(([key, template]: [string, any]) => (
                <label key={key} className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="radio"
                    name="reportType"
                    value={key}
                    checked={selectedReportType === key}
                    onChange={(e) => setSelectedReportType(e.target.value)}
                    className="mr-3"
                  />
                  <div>
                    <div className="font-medium text-gray-900">{template.name}</div>
                    <div className="text-sm text-gray-500">{template.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Report Preview */}
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-3">Report Preview</h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">
                <p><strong>Template:</strong> {templates?.templates[selectedReportType]?.name}</p>
                <p><strong>Sections:</strong> {templates?.templates[selectedReportType]?.sections?.length || 0}</p>
                <p><strong>Description:</strong> {templates?.templates[selectedReportType]?.description}</p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button
              onClick={handleBuildReport}
              disabled={buildReportMutation.isPending}
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {buildReportMutation.isPending ? 'Building...' : 'Build Report'}
            </button>
            
            <button
              onClick={generatePDFReport}
              className="flex-1 bg-gradient-to-r from-red-600 to-pink-600 text-white px-6 py-3 rounded-lg font-medium hover:from-red-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              Export PDF (Client)
            </button>
          </div>
        </div>

        {/* Generated Reports */}
        <div className="bg-white shadow-lg rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Generated Reports</h2>
          
          {reports?.reports?.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-500 mb-4">No reports generated yet</div>
              <p className="text-sm text-gray-400">Build your first report using the form on the left</p>
            </div>
          ) : (
            <div className="space-y-4">
              {reports?.reports?.slice(0, 10).map((report: ComplianceData) => (
                <div key={report.report_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-medium text-gray-900">{report.template_name}</h3>
                      <p className="text-sm text-gray-500">ID: {report.report_id.slice(0, 8)}...</p>
                    </div>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      report.status === 'completed' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {report.status}
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-600 mb-3">
                    <p>Generated: {formatDate(report.generated_at)}</p>
                    <p>Sections: {report.sections_count} • Pages: {report.total_pages}</p>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleExportPDF(report.report_id)}
                      disabled={exportReportMutation.isPending}
                      className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                    >
                      PDF
                    </button>
                    <button
                      onClick={() => handleExportExcel(report.report_id)}
                      disabled={exportReportMutation.isPending}
                      className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                    >
                      Excel
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Report Information */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-3">Report Information</h3>
        <div className="text-sm text-blue-800 space-y-2">
          <p>• <strong>FERC Reports:</strong> Federal Energy Regulatory Commission compliance reporting for energy trading activities</p>
          <p>• <strong>REMIT Reports:</strong> Regulation on Energy Market Integrity and Transparency reporting for European markets</p>
          <p>• <strong>Custom Templates:</strong> Create custom report templates for specific compliance requirements</p>
          <p>• <strong>Multiple Formats:</strong> Export reports in PDF, Excel, CSV, JSON, and HTML formats</p>
          <p>• <strong>Automated Generation:</strong> Schedule automated report generation with Celery tasks</p>
        </div>
      </div>
    </div>
  );
};

export default ComplianceView;
