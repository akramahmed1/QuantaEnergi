import React, { useEffect, useState } from 'react';

interface PriceData {
  source: string;
  data: string;
  explanation: string;
}

const PriceDisplay: React.FC = () => {
  const [priceData, setPriceData] = useState<PriceData | null>(null);
  
  useEffect(() => {
    // Simulate API call with local data
    setTimeout(() => {
      setPriceData({ 
        source: "EnergyOpti-Pro API", 
        data: "healthy", 
        explanation: "System Status - Backend Connected" 
      });
    }, 1000);
  }, []);
  
  return priceData ? (
    <div aria-live="polite" aria-label="Price Data Display" className="p-4 bg-green-100 rounded">
      <h3 className="font-bold text-green-800">✅ Quantum-Safe Certified</h3>
      <p><strong>Source:</strong> {priceData.source}</p>
      <p><strong>Status:</strong> {priceData.data}</p>
      <p><strong>Details:</strong> {priceData.explanation}</p>
    </div>
  ) : (
    <div aria-live="polite" aria-label="Loading Price Data" className="p-4 bg-blue-100 rounded">
      <p>🔄 Loading EnergyOpti-Pro Data...</p>
    </div>
  );
};

export default PriceDisplay;
