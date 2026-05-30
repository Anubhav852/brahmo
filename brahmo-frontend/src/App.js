import React from 'react';
import Dashboard from './Dashboard';
import './App.css'; // Keep the styling

function App() {
  return (
    <div className="App">
      {/* This renders your custom Brahmo Dashboard */}
      <Dashboard userId="U-PRIYA" />
    </div>
  );
}

export default App;