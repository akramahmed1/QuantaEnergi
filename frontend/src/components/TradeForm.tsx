import React, { useState } from 'react';
import { createTrade } from '../services/api';

interface Trade {
  asset: string;
  quantity: number;
  price: number;
}

const TradeForm: React.FC = () => {
  const [trade, setTrade] = useState<Trade>({
    asset: '',
    quantity: 0,
    price: 0
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setTrade(prev => ({
      ...prev,
      [name]: name === 'asset' ? value : parseFloat(value) || 0
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createTrade(trade);
      alert('Trade created');
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
        <h1 className="text-2xl font-bold text-gray-800 mb-6 text-center">
          Trade Capture
        </h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="asset" className="block text-sm font-medium text-gray-700 mb-1">
              Asset
            </label>
            <input
              type="text"
              id="asset"
              name="asset"
              value={trade.asset}
              onChange={handleInputChange}
              className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter asset name (e.g., Crude Oil)"
              required
            />
          </div>

          <div>
            <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
              Quantity
            </label>
            <input
              type="number"
              id="quantity"
              name="quantity"
              value={trade.quantity}
              onChange={handleInputChange}
              className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter quantity"
              min="0"
              step="0.01"
              required
            />
          </div>

          <div>
            <label htmlFor="price" className="block text-sm font-medium text-gray-700 mb-1">
              Price
            </label>
            <input
              type="number"
              id="price"
              name="price"
              value={trade.price}
              onChange={handleInputChange}
              className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter price per unit"
              min="0"
              step="0.01"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-200 font-medium"
          >
            Capture Trade
          </button>
        </form>

        <div className="mt-6 p-4 bg-gray-50 rounded-md">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Trade Preview:</h3>
          <div className="text-sm text-gray-600">
            <p><strong>Asset:</strong> {trade.asset || 'Not specified'}</p>
            <p><strong>Quantity:</strong> {trade.quantity}</p>
            <p><strong>Price:</strong> ${trade.price.toFixed(2)}</p>
            <p><strong>Total Value:</strong> ${(trade.quantity * trade.price).toFixed(2)}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradeForm;
