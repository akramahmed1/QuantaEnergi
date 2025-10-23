/**
 * Trade Capture Form - PRD 4.1 UX
 * Basic form skeleton for energy trade entry
 */

import React, { useState } from 'react';
import { useCaptureTrade } from '../hooks/useTradeCapture';

const TradeCapture: React.FC = () => {
  const [formData, setFormData] = useState({
    asset: 'oil',
    volume: '',
    price: '',
    region: 'me'
  });

  const captureTradeMutation = useCaptureTrade();

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const tradeData = {
      asset: formData.asset,
      volume: parseFloat(formData.volume),
      price: parseFloat(formData.price),
      region: formData.region
    };
    captureTradeMutation.mutate(tradeData);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white shadow-lg rounded-lg p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Trade Capture</h1>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Asset Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Asset Type
              </label>
              <select
                value={formData.asset}
                onChange={(e) => handleInputChange('asset', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="oil">Oil</option>
                <option value="gas">Gas</option>
              </select>
            </div>

            {/* Volume and Price */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Volume
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.volume}
                  onChange={(e) => handleInputChange('volume', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter volume"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Price per Unit
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.price}
                  onChange={(e) => handleInputChange('price', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter price"
                />
              </div>
            </div>

            {/* Region Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Trading Region
              </label>
              <select
                value={formData.region}
                onChange={(e) => handleInputChange('region', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="me">Middle East</option>
                <option value="guyana">Guyana</option>
                <option value="us">United States</option>
                <option value="uk">United Kingdom</option>
                <option value="eu">European Union</option>
              </select>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={captureTradeMutation.isPending}
              className="w-full px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {captureTradeMutation.isPending ? 'Capturing...' : 'Capture Trade'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default TradeCapture;