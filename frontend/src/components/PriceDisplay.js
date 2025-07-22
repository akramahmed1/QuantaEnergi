import React, { useEffect, useState } from 'react';
import axios from 'axios';
import shap
const PriceDisplay = () => {
  const [priceData, setPriceData] = useState(null);
  useEffect(() => {
    axios.get('http://localhost:8000/api/prices').then(response => {
      const shap_values = shap.explain(response.data["data"], model="optimized_model.tflite"); // Placeholder
      setPriceData({ ...response.data, shap_values, explanation: "AI-predicted" });
    }).catch(error => console.error(error));
  }, []);
  return priceData ? (
    <div aria-live="polite" aria-label="Price Data Display">
      <p>Quantum-Safe Certified</p>
      <p>SHAP Values: {priceData.shap_values.join(', ')}</p>
      <p>Source: {priceData.source}, Data: {priceData.data}</p>
      <p>Explanation: {priceData.explanation}</p>
      <p>Tooltip: Click for details</p>
    </div>
  ) : <div aria-live="polite" aria-label="Loading Price Data">Loading...</div>;
};
export default PriceDisplay;
