import React from 'react';

function App() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>QuantaEnergi ETRM/CTRM Platform</h1>
      <p>Welcome to the Energy Trading and Risk Management System</p>
      <div style={{ marginTop: '20px', padding: '20px', border: '1px solid #ccc', borderRadius: '5px' }}>
        <h2>Login Form</h2>
        <form>
          <div style={{ marginBottom: '10px' }}>
            <label>Username:</label><br/>
            <input type="text" placeholder="Enter username" style={{ padding: '5px', width: '200px' }} />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label>Password:</label><br/>
            <input type="password" placeholder="Enter password" style={{ padding: '5px', width: '200px' }} />
          </div>
          <button type="submit" style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '3px' }}>
            Login
          </button>
        </form>
      </div>
      <div style={{ marginTop: '20px' }}>
        <h3>Available Features:</h3>
        <ul>
          <li>✅ Trading Dashboard</li>
          <li>✅ Risk Management</li>
          <li>✅ ESG Analytics</li>
          <li>✅ Portfolio Optimization</li>
          <li>✅ Compliance Monitoring</li>
        </ul>
      </div>
    </div>
  );
}

export default App;
