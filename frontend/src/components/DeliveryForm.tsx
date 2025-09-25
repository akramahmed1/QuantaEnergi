import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

interface DeliveryFormData {
  commodity: string;
  quantity: number;
  unit: string;
  origin: string;
  destination: string;
  delivery_date: string;
  special_instructions: string[];
  contact_info: {
    name: string;
    email: string;
    phone: string;
  };
}

const DeliveryForm: React.FC = () => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<DeliveryFormData>({
    commodity: '',
    quantity: 0,
    unit: 'barrels',
    origin: '',
    destination: '',
    delivery_date: '',
    special_instructions: [],
    contact_info: {
      name: '',
      email: '',
      phone: ''
    }
  });

  const [instructionInput, setInstructionInput] = useState('');

  const scheduleDeliveryMutation = useMutation({
    mutationFn: async (data: DeliveryFormData) => {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:8000/api/v1/delivery/schedule', data, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliveries'] });
      alert('Delivery scheduled successfully!');
      resetForm();
    },
    onError: (error: any) => {
      console.error('Failed to schedule delivery:', error);
      alert('Failed to schedule delivery. Please try again.');
    }
  });

  const resetForm = () => {
    setFormData({
      commodity: '',
      quantity: 0,
      unit: 'barrels',
      origin: '',
      destination: '',
      delivery_date: '',
      special_instructions: [],
      contact_info: {
        name: '',
        email: '',
        phone: ''
      }
    });
    setInstructionInput('');
  };

  const handleInputChange = (field: string, value: any) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...(prev[parent as keyof DeliveryFormData] as any),
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const addInstruction = () => {
    if (instructionInput.trim()) {
      setFormData(prev => ({
        ...prev,
        special_instructions: [...prev.special_instructions, instructionInput.trim()]
      }));
      setInstructionInput('');
    }
  };

  const removeInstruction = (index: number) => {
    setFormData(prev => ({
      ...prev,
      special_instructions: prev.special_instructions.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    scheduleDeliveryMutation.mutate(formData);
  };

  const commodities = [
    'crude_oil',
    'natural_gas',
    'lng',
    'lpg',
    'refined_products',
    'coal',
    'electricity',
    'renewables'
  ];

  const units = ['barrels', 'mmbtu', 'tons', 'mwh', 'gallons'];

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white shadow-xl rounded-lg overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4">
          <h2 className="text-2xl font-bold text-white">Schedule Physical Delivery</h2>
          <p className="text-blue-100 mt-1">Plan and schedule commodity deliveries with real-time tracking</p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Commodity Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Commodity Type *
              </label>
              <select
                value={formData.commodity}
                onChange={(e) => handleInputChange('commodity', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="">Select commodity</option>
                {commodities.map(commodity => (
                  <option key={commodity} value={commodity}>
                    {commodity.replace('_', ' ').toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quantity *
                </label>
                <input
                  type="number"
                  value={formData.quantity}
                  onChange={(e) => handleInputChange('quantity', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                  min="0"
                  step="0.01"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Unit
                </label>
                <select
                  value={formData.unit}
                  onChange={(e) => handleInputChange('unit', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {units.map(unit => (
                    <option key={unit} value={unit}>{unit.toUpperCase()}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Origin and Destination */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Origin Location *
              </label>
              <input
                type="text"
                value={formData.origin}
                onChange={(e) => handleInputChange('origin', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Saudi Arabia Oil Terminal"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Destination Location *
              </label>
              <input
                type="text"
                value={formData.destination}
                onChange={(e) => handleInputChange('destination', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Rotterdam Port"
                required
              />
            </div>
          </div>

          {/* Delivery Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Scheduled Delivery Date *
            </label>
            <input
              type="datetime-local"
              value={formData.delivery_date}
              onChange={(e) => handleInputChange('delivery_date', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Special Instructions */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Special Instructions
            </label>
            <div className="space-y-2">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={instructionInput}
                  onChange={(e) => setInstructionInput(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Add special instruction..."
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addInstruction())}
                />
                <button
                  type="button"
                  onClick={addInstruction}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Add
                </button>
              </div>
              {formData.special_instructions.length > 0 && (
                <div className="space-y-1">
                  {formData.special_instructions.map((instruction, index) => (
                    <div key={index} className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded-md">
                      <span className="text-sm text-gray-700">{instruction}</span>
                      <button
                        type="button"
                        onClick={() => removeInstruction(index)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Contact Information */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Contact Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contact Name
                </label>
                <input
                  type="text"
                  value={formData.contact_info.name}
                  onChange={(e) => handleInputChange('contact_info.name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Full name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.contact_info.email}
                  onChange={(e) => handleInputChange('contact_info.email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="email@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone
                </label>
                <input
                  type="tel"
                  value={formData.contact_info.phone}
                  onChange={(e) => handleInputChange('contact_info.phone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="+1 (555) 123-4567"
                />
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={resetForm}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Reset
            </button>
            <button
              type="submit"
              disabled={scheduleDeliveryMutation.isPending}
              className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-md hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {scheduleDeliveryMutation.isPending ? 'Scheduling...' : 'Schedule Delivery'}
            </button>
          </div>
        </form>
      </div>

      {/* Delivery Information */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-3">Delivery Information</h3>
        <div className="text-sm text-blue-800 space-y-2">
          <p>• <strong>Real-time Tracking:</strong> Your delivery will be tracked in real-time using MQTT sensors</p>
          <p>• <strong>Automatic Route Planning:</strong> Optimal routes are calculated based on commodity type and locations</p>
          <p>• <strong>Status Updates:</strong> Receive notifications at each stage of the delivery process</p>
          <p>• <strong>Compliance Monitoring:</strong> Temperature, pressure, and safety parameters are continuously monitored</p>
        </div>
      </div>
    </div>
  );
};

export default DeliveryForm;
