import React from 'react';
import Dashboard from './Dashboard';
import './App.css';

function App() {
  return (
    <div className="App" style={{ padding: '20px' }}>
      <h1>Brahmo Pipeline: Comparison View</h1>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '20px' }}>
        {/* These two components will now show your real data */}
        <Dashboard userId="U-PRIYA" />
        <Dashboard userId="U-VIKRAM" />
      </div>
    </div>
  );
}

export default App;