import React, { useState } from 'react';
import { PlusIcon, MinusIcon } from '@heroicons/react/24/outline';

interface TradeFormData {
  asset: string;
  quantity: number;
  price: number;
  tradeType: 'buy' | 'sell';
  orderType: 'market' | 'limit';
}

const TradingForm: React.FC = () => {
  const [formData, setFormData] = useState<TradeFormData>({
    asset: 'BRENT',
    quantity: 1000,
    price: 85.50,
    tradeType: 'buy',
    orderType: 'market'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const assets = [
    { value: 'BRENT', label: 'Brent Crude Oil', price: 85.50 },
    { value: 'WTI', label: 'WTI Crude Oil', price: 83.25 },
    { value: 'NG', label: 'Natural Gas', price: 3.45 },
    { value: 'COAL', label: 'Coal', price: 125.00 },
    { value: 'ELECTRICITY', label: 'Electricity', price: 0.08 }
  ];

  const handleAssetChange = (assetValue: string) => {
    const asset = assets.find(a => a.value === assetValue);
    setFormData({
      ...formData,
      asset: assetValue,
      price: asset?.price || formData.price
    });
  };

  const handleQuantityChange = (delta: number) => {
    const newQuantity = Math.max(100, formData.quantity + delta);
    setFormData({ ...formData, quantity: newQuantity });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/trades`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          asset: formData.asset,
          quantity: formData.quantity,
          price: formData.price
        })
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: 'Failed to create trade' });
    } finally {
      setLoading(false);
    }
  };

  const totalValue = formData.quantity * formData.price;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Create New Trade</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Asset Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Asset
            </label>
            <select
              value={formData.asset}
              onChange={(e) => handleAssetChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              {assets.map((asset) => (
                <option key={asset.value} value={asset.value}>
                  {asset.label} (${asset.price})
                </option>
              ))}
            </select>
          </div>

          {/* Trade Type */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Trade Type
              </label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="buy"
                    checked={formData.tradeType === 'buy'}
                    onChange={(e) => setFormData({ ...formData, tradeType: e.target.value as 'buy' | 'sell' })}
                    className="mr-2"
                  />
                  <span className={`px-3 py-1 rounded text-sm font-medium ${formData.tradeType === 'buy' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    Buy
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="sell"
                    checked={formData.tradeType === 'sell'}
                    onChange={(e) => setFormData({ ...formData, tradeType: e.target.value as 'buy' | 'sell' })}
                    className="mr-2"
                  />
                  <span className={`px-3 py-1 rounded text-sm font-medium ${formData.tradeType === 'sell' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}`}>
                    Sell
                  </span>
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Order Type
              </label>
              <select
                value={formData.orderType}
                onChange={(e) => setFormData({ ...formData, orderType: e.target.value as 'market' | 'limit' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="market">Market Order</option>
                <option value="limit">Limit Order</option>
              </select>
            </div>
          </div>

          {/* Quantity */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quantity
            </label>
            <div className="flex items-center space-x-2">
              <button
                type="button"
                onClick={() => handleQuantityChange(-100)}
                className="p-2 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                <MinusIcon className="h-4 w-4" />
              </button>
              <input
                type="number"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) || 0 })}
                min="100"
                step="100"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                type="button"
                onClick={() => handleQuantityChange(100)}
                className="p-2 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                <PlusIcon className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Price */}
          {formData.orderType === 'limit' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Limit Price ($)
              </label>
              <input
                type="number"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) || 0 })}
                step="0.01"
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          )}

          {/* Market Price Display */}
          {formData.orderType === 'market' && (
            <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
              <p className="text-sm text-blue-800">
                Market Price: <span className="font-semibold">${formData.price}</span>
              </p>
            </div>
          )}

          {/* Trade Summary */}
          <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
            <h3 className="text-sm font-medium text-gray-900 mb-2">Trade Summary</h3>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Asset:</span>
                <span className="font-medium">{assets.find(a => a.value === formData.asset)?.label}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Type:</span>
                <span className="font-medium capitalize">{formData.tradeType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Quantity:</span>
                <span className="font-medium">{formData.quantity.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Price:</span>
                <span className="font-medium">${formData.price.toFixed(2)}</span>
              </div>
              <div className="flex justify-between border-t border-gray-300 pt-1">
                <span className="text-gray-600">Total Value:</span>
                <span className="font-semibold">${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating Trade...' : 'Create Trade'}
          </button>
        </form>

        {/* Result Display */}
        {result && (
          <div className="mt-6">
            {result.error ? (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
                {result.error}
              </div>
            ) : (
              <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-md">
                <h3 className="font-semibold">Trade Created Successfully!</h3>
                <p className="text-sm mt-1">Trade ID: {result.trade_id}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TradingForm;
