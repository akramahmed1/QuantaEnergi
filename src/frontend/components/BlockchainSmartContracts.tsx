import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import axios from 'axios';

interface SmartContract {
  id: string;
  name: string;
  type: 'energy_trading' | 'carbon_credits' | 'esg_certificates' | 'grid_balancing';
  status: 'active' | 'pending' | 'completed' | 'failed';
  address: string;
  created_at: string;
  value: number;
  gas_used: number;
  block_number: number;
}

interface CarbonCredit {
  id: string;
  project_name: string;
  credit_amount: number;
  verification_status: 'verified' | 'pending' | 'rejected';
  issuer: string;
  buyer: string;
  price_per_credit: number;
  created_at: string;
  expiry_date: string;
}

interface ESGScore {
  environmental: number;
  social: number;
  governance: number;
  overall: number;
  blockchain_verified: boolean;
  last_updated: string;
}

interface TransactionHistory {
  timestamp: string;
  type: 'deploy' | 'execute' | 'transfer' | 'verify';
  contract_address: string;
  gas_used: number;
  status: 'success' | 'failed' | 'pending';
  block_number: number;
}

const BlockchainSmartContracts: React.FC = () => {
  const [smartContracts, setSmartContracts] = useState<SmartContract[]>([]);
  const [carbonCredits, setCarbonCredits] = useState<CarbonCredit[]>([]);
  const [esgScore, setEsgScore] = useState<ESGScore | null>(null);
  const [transactionHistory, setTransactionHistory] = useState<TransactionHistory[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedContractType, setSelectedContractType] = useState('all');
  const [networkStatus, setNetworkStatus] = useState('connected');

  const generateMockSmartContracts = (): SmartContract[] => [
    {
      id: '1',
      name: 'Solar Energy Trading Contract',
      type: 'energy_trading',
      status: 'active',
      address: '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
      created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      value: 15000,
      gas_used: 21000,
      block_number: 18456789,
    },
    {
      id: '2',
      name: 'Carbon Credit Verification',
      type: 'carbon_credits',
      status: 'active',
      address: '0x8ba1f109551bA432bdf5c3c92bEa6eEe3562562D',
      created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      value: 5000,
      gas_used: 18000,
      block_number: 18457890,
    },
    {
      id: '3',
      name: 'ESG Certificate Issuance',
      type: 'esg_certificates',
      status: 'pending',
      address: '0x1234567890123456789012345678901234567890',
      created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      value: 8000,
      gas_used: 25000,
      block_number: 18458901,
    },
    {
      id: '4',
      name: 'Grid Balancing Contract',
      type: 'grid_balancing',
      status: 'completed',
      address: '0xabcdef1234567890abcdef1234567890abcdef12',
      created_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
      value: 12000,
      gas_used: 32000,
      block_number: 18451234,
    },
  ];

  const generateMockCarbonCredits = (): CarbonCredit[] => [
    {
      id: 'cc1',
      project_name: 'Solar Farm Project Alpha',
      credit_amount: 1000,
      verification_status: 'verified',
      issuer: '0xSolarFarmAlpha',
      buyer: '0xEnergyCorp',
      price_per_credit: 25.50,
      created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      expiry_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 'cc2',
      project_name: 'Wind Energy Initiative',
      credit_amount: 750,
      verification_status: 'verified',
      issuer: '0xWindEnergyInitiative',
      buyer: '0xGreenEnergyLtd',
      price_per_credit: 28.75,
      created_at: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(),
      expiry_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 'cc3',
      project_name: 'Forest Conservation Project',
      credit_amount: 500,
      verification_status: 'pending',
      issuer: '0xForestConservation',
      buyer: '0xCarbonNeutralCorp',
      price_per_credit: 22.00,
      created_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
      expiry_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ];

  const generateMockESGScore = (): ESGScore => ({
    environmental: 88 + Math.random() * 12,
    social: 85 + Math.random() * 15,
    governance: 92 + Math.random() * 8,
    overall: 88 + Math.random() * 12,
    blockchain_verified: true,
    last_updated: new Date().toISOString(),
  });

  const generateMockTransactionHistory = (): TransactionHistory[] => [
    {
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      type: 'execute',
      contract_address: '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
      gas_used: 45000,
      status: 'success',
      block_number: 18459012,
    },
    {
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      type: 'deploy',
      contract_address: '0x1234567890123456789012345678901234567890',
      gas_used: 180000,
      status: 'success',
      block_number: 18458901,
    },
    {
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      type: 'transfer',
      contract_address: '0x8ba1f109551bA432bdf5c3c92bEa6eEe3562562D',
      gas_used: 21000,
      status: 'success',
      block_number: 18458890,
    },
    {
      timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
      type: 'verify',
      contract_address: '0xabcdef1234567890abcdef1234567890abcdef12',
      gas_used: 35000,
      status: 'success',
      block_number: 18458879,
    },
  ];

  useEffect(() => {
    // Load mock data initially
    setSmartContracts(generateMockSmartContracts());
    setCarbonCredits(generateMockCarbonCredits());
    setEsgScore(generateMockESGScore());
    setTransactionHistory(generateMockTransactionHistory());
  }, []);

  const handleDeployContract = async () => {
    setLoading(true);
    try {
      // In production, this would call the actual backend API
      // const response = await axios.post('/api/disruptive/blockchain/deploy', {
      //   contract_type: selectedContractType,
      //   name: `New ${selectedContractType} Contract`,
      // });
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Add new contract to the list
      const newContract: SmartContract = {
        id: Date.now().toString(),
        name: `New ${selectedContractType} Contract`,
        type: selectedContractType as any,
        status: 'pending',
        address: `0x${Math.random().toString(16).substr(2, 40)}`,
        created_at: new Date().toISOString(),
        value: Math.random() * 20000 + 5000,
        gas_used: Math.random() * 50000 + 15000,
        block_number: 18459000 + Math.floor(Math.random() * 1000),
      };
      
      setSmartContracts(prev => [newContract, ...prev]);
      toast.success('Smart contract deployed successfully!');
    } catch (error) {
      toast.error('Failed to deploy contract');
      console.error('Deploy error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      case 'completed': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'energy_trading': return '⚡';
      case 'carbon_credits': return '🌱';
      case 'esg_certificates': return '🏆';
      case 'grid_balancing': return '🔌';
      default: return '📄';
    }
  };

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'deploy': return '🚀';
      case 'execute': return '▶️';
      case 'transfer': return '💸';
      case 'verify': return '✅';
      default: return '📝';
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const filteredContracts = selectedContractType === 'all' 
    ? smartContracts 
    : smartContracts.filter(contract => contract.type === selectedContractType);

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Blockchain Smart Contracts</h2>
          <p className="text-gray-600">Secure and transparent energy trading on the blockchain</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            networkStatus === 'connected' ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100'
          }`}>
            {networkStatus === 'connected' ? '🟢 Connected' : '🔴 Disconnected'}
          </div>
          <button
            onClick={handleDeployContract}
            disabled={loading}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Deploying...</span>
              </>
            ) : (
              <>
                <span>🚀</span>
                <span>Deploy Contract</span>
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Contract Type</label>
            <select
              value={selectedContractType}
              onChange={(e) => setSelectedContractType(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="all">All Types</option>
              <option value="energy_trading">Energy Trading</option>
              <option value="carbon_credits">Carbon Credits</option>
              <option value="esg_certificates">ESG Certificates</option>
              <option value="grid_balancing">Grid Balancing</option>
            </select>
          </div>
        </div>
      </motion.div>

      {/* Smart Contracts Overview */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white p-6 rounded-lg shadow-sm border"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Smart Contracts</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contract</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Address</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gas Used</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredContracts.map((contract) => (
                <tr key={contract.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-2xl mr-3">{getTypeIcon(contract.type)}</span>
                      <div>
                        <div className="text-sm font-medium text-gray-900">{contract.name}</div>
                        <div className="text-sm text-gray-500">Block #{contract.block_number}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 capitalize">
                    {contract.type.replace('_', ' ')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(contract.status)}`}>
                      {contract.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">
                    {contract.address.slice(0, 8)}...{contract.address.slice(-6)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${contract.value.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {contract.gas_used.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Carbon Credits and ESG */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Carbon Credits */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white p-6 rounded-lg shadow-sm border"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Carbon Credits</h3>
          <div className="space-y-3">
            {carbonCredits.map((credit) => (
              <div key={credit.id} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{credit.project_name}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    credit.verification_status === 'verified' ? 'text-green-600 bg-green-100' : 
                    credit.verification_status === 'pending' ? 'text-yellow-600 bg-yellow-100' : 
                    'text-red-600 bg-red-100'
                  }`}>
                    {credit.verification_status}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                  <div>Amount: {credit.credit_amount.toLocaleString()}</div>
                  <div>Price: ${credit.price_per_credit}</div>
                  <div>Total: ${(credit.credit_amount * credit.price_per_credit).toLocaleString()}</div>
                  <div>Expires: {new Date(credit.expiry_date).toLocaleDateString()}</div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* ESG Score */}
        {esgScore && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white p-6 rounded-lg shadow-sm border"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">ESG Score</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{esgScore.environmental.toFixed(0)}</div>
                  <div className="text-sm text-gray-600">Environmental</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{esgScore.social.toFixed(0)}</div>
                  <div className="text-sm text-gray-600">Social</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{esgScore.governance.toFixed(0)}</div>
                  <div className="text-sm text-gray-600">Governance</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-indigo-600">{esgScore.overall.toFixed(0)}</div>
                  <div className="text-sm text-gray-600">Overall</div>
                </div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-sm text-green-600">
                  {esgScore.blockchain_verified ? '✅ Blockchain Verified' : '❌ Not Verified'}
                </div>
                <div className="text-xs text-green-500 mt-1">
                  Last updated: {new Date(esgScore.last_updated).toLocaleString()}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Transaction History */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-white p-6 rounded-lg shadow-sm border"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Transaction History</h3>
        <div className="space-y-3">
          {transactionHistory.map((tx, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{getTransactionIcon(tx.type)}</span>
                <div>
                  <div className="font-medium text-gray-900 capitalize">{tx.type}</div>
                  <div className="text-sm text-gray-500">
                    {tx.contract_address.slice(0, 8)}...{tx.contract_address.slice(-6)}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-900">Gas: {tx.gas_used.toLocaleString()}</div>
                <div className="text-xs text-gray-500">Block #{tx.block_number}</div>
                <div className="text-xs text-gray-500">{new Date(tx.timestamp).toLocaleString()}</div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default BlockchainSmartContracts;
