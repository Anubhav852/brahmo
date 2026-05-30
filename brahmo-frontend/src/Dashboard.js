import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Dashboard({ userId }) {
  const [data, setData] = useState(null);
  const [currentNode, setCurrentNode] = useState("N-03");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`http://127.0.0.1:8000/dashboard/${userId}/${currentNode}`);
        setData(response.data);
      } catch (err) {
        console.error("Error fetching Brahmo data:", err);
      }
      setLoading(false);
    };
    fetchData();
  }, [userId, currentNode]);

  if (loading) return <div>Pipeline running...</div>;
  if (!data || data.status !== 'granted') return <div>Access Denied for {userId}</div>;

  return (
    <div style={{ border: '2px solid #333', padding: '15px', margin: '10px', width: '45%' }}>
      <h2>User: {userId}</h2>
      
      {/* 1. FILTER FUNNEL (Shows all 5 stages of the pipeline) */}
      <div style={{ background: '#f4f4f4', padding: '10px', marginBottom: '10px' }}>
        <h4>Filter Funnel: Pipeline Progress</h4>
        {data.funnel_stats ? (
          <ul>
            <li>Initial BFS Traversal: {data.funnel_stats.initial} nodes</li>
            <li>After Dept Filter: {data.funnel_stats.after_dept} nodes</li>
            <li>After Temporal Check: {data.funnel_stats.after_temporal} nodes</li>
            <li>After Compliance Check: {data.funnel_stats.after_compliance} nodes</li>
            <li>Final Candidate Set: {data.funnel_stats.final} nodes</li>
          </ul>
        ) : <p>Funnel stats unavailable.</p>}
      </div>

      {/* 2. DAG VISUALIZATION */}
      <h4>Knowledge Path (DAG):</h4>
      <div style={{ fontSize: '0.8em', color: '#666', background: '#eee', padding: '5px' }}>
        {data.authorized_nodes.join(" → ")}
      </div>

      <hr />

      {/* 3. CONTENT VIEW */}
      <h4>Authorized Clinical Content:</h4>
      {data.content.length > 0 ? (
        data.content.map((item, idx) => (
          <div key={idx} style={{ marginBottom: '8px', borderBottom: '1px solid #ddd' }}>
            <strong>{item.title}</strong>
          </div>
        ))
      ) : <p>No content authorized for this user.</p>}
    </div>
  );
}

export default Dashboard;