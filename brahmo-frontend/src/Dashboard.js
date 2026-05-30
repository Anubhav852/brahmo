import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Dashboard({ userId }) {
  const [data, setData] = useState(null);
  const [currentNode, setCurrentNode] = useState("N-03"); // Your entry node
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // This calls your FastAPI backend
        const response = await axios.get(`http://127.0.0.1:8000/dashboard/${userId}/${currentNode}`);
        setData(response.data);
      } catch (err) {
        setError("Could not connect to the Brahmo Backend. Is it running?");
        console.error(err);
      }
    };
    fetchData();
  }, [userId, currentNode]);

  if (error) return <div style={{color: 'red'}}>{error}</div>;
  if (!data) return <div>Loading Brahmo data...</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h1>Brahmo Dashboard</h1>
      <h3>Current Node: {currentNode}</h3>

      {data.status === 'granted' ? (
        <div>
          <h4>Content:</h4>
          {data.content.map((item, index) => (
            <div key={index} style={{ border: '1px solid #ccc', margin: '10px', padding: '10px' }}>
              <strong>{item.title}</strong>
              <p>{item.body}</p>
            </div>
          ))}
          
          <h4>Navigate to sub-nodes:</h4>
          {data.authorized_nodes.map(nodeId => (
            <button key={nodeId} onClick={() => setCurrentNode(nodeId)} style={{ margin: '5px' }}>
              Go to {nodeId}
            </button>
          ))}
        </div>
      ) : (
        <p>Access Denied: {data.message}</p>
      )}
    </div>
  );
}

export default Dashboard;