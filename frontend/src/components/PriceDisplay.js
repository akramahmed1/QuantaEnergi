import React, { useEffect, useState } from 'react';
import axios from 'axios';
const PriceDisplay = () => {
  const [priceData, setPriceData] = useState(null);
  useEffect(() => {
    axios.get('http://localhost:8000/api/prices').then(response => {
      setPriceData({ ...response.data, explanation: "Predicted value" });
    }).catch(error => console.error(error));
  }, []);
  return priceData ? (
    <div aria-live="polite" aria-label="Price Data Display">
      <p>Quantum-Safe Certified</p>
      <p>Source: {priceData.source}, Data: {priceData.data}</p>
      <p>Explanation: {priceData.explanation}</p>
      <p>Tooltip: Click for details</p>
    </div>
  ) : <div aria-live="polite" aria-label="Loading Price Data">Loading...</div>;
};
export default PriceDisplay;
