import React, { useState, useEffect } from 'react';
import './App.css';

const USERS = [
  { id: 'U-PRIYA',  label: 'Nurse Priya — VIEWER, L10, Ortho' },
  { id: 'U-VIKRAM', label: 'Dr. Vikram (HOD) — HOD, L4, Ortho' },
  { id: 'U-ANANYA', label: 'Dr. Ananya — EDITOR, L8, Medicine' },
  { id: 'U-SHARMA', label: 'Dr. Sharma (HOD) — HOD, L4, Medicine' },
  { id: 'U-RAVI',   label: 'Pharmacist Ravi — VIEWER, L12, Pharmacy' },
  { id: 'U-SUNITA', label: 'Dr. Sunita (QA) — QUALITY, L6' },
  { id: 'U-SURESH', label: 'Admin Suresh — ADMIN, L1' },
];

const FUNNEL_STAGES = [
  { key: 'after_bfs',    label: 'After BFS Traversal' },
  { key: 'after_zone2',  label: 'After Zone 2 Injection' },
  { key: 'after_check1', label: 'Check 1: Isolation' },
  { key: 'after_check2', label: 'Check 2: Compliance' },
  { key: 'after_check3', label: 'Check 3: Permission' },
  { key: 'after_check4', label: 'Check 4: Temporal' },
  { key: 'after_check5', label: 'Check 5: Derivability' },
];

function FunnelBar({ label, count, max }) {
  const pct = max > 0 ? (count / max) * 100 : 0;
  return (
    <div style={{ marginBottom: '8px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '2px' }}>
        <span>{label}</span>
        <strong>{count} nodes</strong>
      </div>
      <div style={{ background: '#e0e0e0', borderRadius: '4px', height: '18px' }}>
        <div style={{
          width: `${pct}%`, background: '#2563eb',
          height: '18px', borderRadius: '4px',
          transition: 'width 0.5s ease'
        }} />
      </div>
    </div>
  );
}

export default function App() {
  const [userId, setUserId] = useState('U-PRIYA');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runPipeline = async (uid) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const resp = await fetch(`http://localhost:8000/pipeline/${uid}`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      setResult(data);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  };

  const handleUserChange = (e) => {
    setUserId(e.target.value);
    setResult(null);
  };

  const maxNodes = result?.funnel?.after_zone2 || 50;

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '30px', fontFamily: 'sans-serif' }}>
      <h1 style={{ color: '#1e293b' }}>BRAHMO Rules Engine</h1>
      <p style={{ color: '#64748b' }}>BFS Traversal + 5-Check Filter Pipeline — ZERO LLM</p>

      {/* User Selector */}
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center', margin: '24px 0' }}>
        <select
          value={userId}
          onChange={handleUserChange}
          style={{ padding: '10px', fontSize: '15px', borderRadius: '6px', border: '1px solid #cbd5e1', flex: 1 }}
        >
          {USERS.map(u => (
            <option key={u.id} value={u.id}>{u.label}</option>
          ))}
        </select>
        <button
          onClick={() => runPipeline(userId)}
          disabled={loading}
          style={{
            padding: '10px 24px', fontSize: '15px', background: '#2563eb',
            color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer'
          }}
        >
          {loading ? 'Running...' : 'Run Pipeline'}
        </button>
      </div>

      {error && (
        <div style={{ background: '#fee2e2', color: '#dc2626', padding: '12px', borderRadius: '6px' }}>
          Error: {error}
        </div>
      )}

      {result && (
        <>
          {/* Pipeline Info */}
          <div style={{ background: '#f1f5f9', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
            <strong>{result.user_name}</strong> — {result.role}, Ceiling L{result.ceiling_level}
            <span style={{ float: 'right', color: '#16a34a' }}>
              ⏱ {result.pipeline_timing?.total_ms}ms total
            </span>
            <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
              Entry point: {result.entry_point}
            </div>
          </div>

          {/* Filter Funnel */}
          <div style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '20px', marginBottom: '20px' }}>
            <h3 style={{ margin: '0 0 16px' }}>Filter Funnel</h3>
            {FUNNEL_STAGES.map(stage => (
              <FunnelBar
                key={stage.key}
                label={stage.label}
                count={result.funnel?.[stage.key] ?? 0}
                max={maxNodes}
              />
            ))}
            <div style={{ marginTop: '12px', fontSize: '14px', color: '#16a34a', fontWeight: 'bold' }}>
              ✅ Final candidate set: {result.funnel?.after_check5} nodes
            </div>
          </div>

          {/* Timing Breakdown */}
          <div style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '20px', marginBottom: '20px' }}>
            <h3 style={{ margin: '0 0 12px' }}>Pipeline Timing</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
              {Object.entries(result.pipeline_timing || {}).filter(([k]) => k !== 'total_ms').map(([k, v]) => (
                <div key={k} style={{ background: '#f8fafc', padding: '8px', borderRadius: '6px', fontSize: '12px' }}>
                  <div style={{ color: '#64748b' }}>{k.replace(/_ms$/, '').replace(/_/g, ' ')}</div>
                  <strong>{v}ms</strong>
                </div>
              ))}
            </div>
          </div>

          {/* Candidate Set */}
          <div style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '20px' }}>
            <h3 style={{ margin: '0 0 12px' }}>
              Candidate Set ({result.candidate_set?.length} nodes)
            </h3>
            {result.candidate_set?.map(node => (
              <div key={node.id} style={{
                borderBottom: '1px solid #f1f5f9', padding: '12px 0',
                display: 'grid', gridTemplateColumns: '1fr auto'
              }}>
                <div>
                  <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{node.title}</div>
                  <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>
                    {node.type} · importance: {node.importance} · dist: {node.distance_from_entry}
                  </div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>{node.content?.slice(0, 100)}...</div>
                </div>
                <div style={{ textAlign: 'right', fontSize: '12px', paddingLeft: '12px' }}>
                  <span style={{
                    background: node.compression_hint === 'FULL' ? '#dcfce7' : node.compression_hint === 'COMPRESSED' ? '#fef9c3' : '#fee2e2',
                    padding: '2px 8px', borderRadius: '12px', whiteSpace: 'nowrap'
                  }}>
                    {node.compression_hint}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}