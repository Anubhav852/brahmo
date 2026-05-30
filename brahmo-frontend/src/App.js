import React, { useState } from 'react';
import './App.css';

const USERS = [
  { id: 'U-PRIYA',  label: 'Nurse Priya — VIEWER, L10, Ortho' },
  { id: 'U-VIKRAM', label: 'Dr. Vikram — HOD, L4, Ortho' },
  { id: 'U-ANANYA', label: 'Dr. Ananya — EDITOR, L8, Medicine' },
  { id: 'U-SHARMA', label: 'Dr. Sharma — HOD, L4, Medicine' },
  { id: 'U-RAVI',   label: 'Pharmacist Ravi — VIEWER, L12, Pharmacy' },
  { id: 'U-SUNITA', label: 'Dr. Sunita — QUALITY, L6' },
  { id: 'U-SURESH', label: 'Admin Suresh — ADMIN, L1' },
];

const FUNNEL_STAGES = [
  { key: 'total_nodes',  label: '🗄 Total nodes in graph' },
  { key: 'after_bfs',    label: '🌲 After BFS Traversal' },
  { key: 'after_zone2',  label: '💉 After Zone 2 Injection' },
  { key: 'after_check1', label: 'Check 1 — Isolation' },
  { key: 'after_check2', label: 'Check 2 — Compliance' },
  { key: 'after_check3', label: 'Check 3 — Permission' },
  { key: 'after_check4', label: 'Check 4 — Temporal' },
  { key: 'after_check5', label: 'Check 5 — Derivability' },
];

const TYPE_COLORS = {
  CONSTRAINT:   { bg: '#fee2e2', color: '#dc2626' },
  DECISION:     { bg: '#dbeafe', color: '#2563eb' },
  ANTI_PATTERN: { bg: '#fef9c3', color: '#ca8a04' },
  FACT:         { bg: '#f1f5f9', color: '#64748b' },
};

const HINT_COLORS = {
  FULL:             { bg: '#dcfce7', color: '#16a34a' },
  COMPRESSED:       { bg: '#fef9c3', color: '#ca8a04' },
  CONSTRAINT_ONLY:  { bg: '#fee2e2', color: '#dc2626' },
};

const TIMING_LABELS = {
  permission_compile: 'Permission compile',
  bfs:                'BFS traversal',
  zone2_inject:       'Zone 2 inject',
  check1_isolation:   'Check 1 isolation',
  check2_compliance:  'Check 2 compliance',
  check3_permission:  'Check 3 permission',
  check4_temporal:    'Check 4 temporal',
  check5_derivability:'Check 5 derivability',
};

function Badge({ text, bg, color }) {
  return (
    <span style={{
      background: bg, color, fontSize: '11px', fontWeight: '600',
      padding: '2px 8px', borderRadius: '12px', whiteSpace: 'nowrap'
    }}>{text}</span>
  );
}

function FunnelBar({ label, count, max, isFinal }) {
  const pct = max > 0 ? Math.round((count / max) * 100) : 0;
  return (
    <div style={{ marginBottom: '10px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '3px' }}>
        <span style={{ color: isFinal ? '#16a34a' : '#374151', fontWeight: isFinal ? '700' : '400' }}>{label}</span>
        <strong style={{ color: isFinal ? '#16a34a' : '#1e293b' }}>{count} nodes</strong>
      </div>
      <div style={{ background: '#e2e8f0', borderRadius: '4px', height: '14px' }}>
        <div style={{
          width: `${pct}%`,
          background: isFinal ? '#16a34a' : '#2563eb',
          height: '14px', borderRadius: '4px',
          transition: 'width 0.6s ease'
        }} />
      </div>
    </div>
  );
}

export default function App() {
  const [userId, setUserId]         = useState('U-PRIYA');
  const [includeZone2, setIncludeZone2] = useState(true);
  const [result, setResult]         = useState(null);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState(null);
  const [expanded, setExpanded]     = useState({});

  const runPipeline = async (uid) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setExpanded({});
    try {
      const resp = await fetch(`http://localhost:8000/pipeline/${uid}?zone2=${includeZone2}`);
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

  const toggleExpand = (id) => setExpanded(prev => ({ ...prev, [id]: !prev[id] }));

  const maxNodes = result?.funnel?.total_nodes || 50;
  const timings  = result?.pipeline_timing || {};

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto', padding: '32px 24px', fontFamily: 'system-ui, sans-serif', color: '#1e293b' }}>

      {/* Header */}
      <h1 style={{ fontSize: '22px', fontWeight: '700', margin: '0 0 4px' }}>BRAHMO Rules Engine</h1>
      <p style={{ color: '#64748b', margin: '0 0 28px', fontSize: '14px' }}>
        BFS Traversal + 5-Check Filter Pipeline — <strong>ZERO LLM</strong>
      </p>

      {/* Controls */}
      <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '12px' }}>
        <select
          value={userId}
          onChange={handleUserChange}
          style={{ padding: '10px 12px', fontSize: '14px', borderRadius: '8px', border: '1px solid #cbd5e1', flex: 1 }}
        >
          {USERS.map(u => <option key={u.id} value={u.id}>{u.label}</option>)}
        </select>
        <button
          onClick={() => runPipeline(userId)}
          disabled={loading}
          style={{
            padding: '10px 28px', fontSize: '14px', fontWeight: '600',
            background: loading ? '#94a3b8' : '#2563eb',
            color: 'white', border: 'none', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Running...' : '▶ Run Pipeline'}
        </button>
      </div>

      {/* Zone 2 Toggle */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '28px',
        padding: '10px 14px',
        background: includeZone2 ? '#f0fdf4' : '#fef2f2',
        border: `1px solid ${includeZone2 ? '#86efac' : '#fca5a5'}`,
        borderRadius: '8px'
      }}>
        <input
          type="checkbox" id="zone2toggle"
          checked={includeZone2}
          onChange={(e) => setIncludeZone2(e.target.checked)}
          style={{ width: '16px', height: '16px', cursor: 'pointer' }}
        />
        <label htmlFor="zone2toggle" style={{ cursor: 'pointer', fontSize: '13px', fontWeight: '500', flex: 1 }}>
          Zone 2 — global drug safety constraints &amp; hospital-wide policies
        </label>
        <strong style={{ fontSize: '12px', color: includeZone2 ? '#16a34a' : '#dc2626' }}>
          {includeZone2 ? 'ON' : 'OFF'}
        </strong>
      </div>

      {error && (
        <div style={{ background: '#fee2e2', color: '#dc2626', padding: '12px 16px', borderRadius: '8px', marginBottom: '20px' }}>
          ❌ Error: {error}
        </div>
      )}

      {result && (
        <>
          {/* Session Banner */}
          <div style={{
            background: '#f8fafc', border: '1px solid #e2e8f0',
            borderRadius: '10px', padding: '16px 20px', marginBottom: '20px',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center'
          }}>
            <div>
              <div style={{ fontWeight: '700', fontSize: '16px' }}>{result.user_name}</div>
              <div style={{ fontSize: '13px', color: '#64748b', marginTop: '2px' }}>
                {result.role} · Ceiling L{result.ceiling_level} · Entry: <code style={{ fontSize: '12px' }}>{result.entry_point}</code>
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '22px', fontWeight: '700', color: '#2563eb' }}>
                {result.funnel?.after_check5}
              </div>
              <div style={{ fontSize: '12px', color: '#64748b' }}>candidate nodes</div>
            </div>
          </div>

          {!includeZone2 && (
            <div style={{
              background: '#fef2f2', border: '1px solid #fca5a5',
              padding: '10px 14px', borderRadius: '8px', marginBottom: '16px',
              fontSize: '13px', color: '#dc2626'
            }}>
              ⚠️ Zone 2 is OFF — global drug safety constraints excluded from this session.
            </div>
          )}

          {/* Filter Funnel */}
          <div style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '20px', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '15px', fontWeight: '600', margin: '0 0 16px' }}>Filter Funnel</h2>
            {FUNNEL_STAGES.map((stage, i) => (
              <FunnelBar
                key={stage.key}
                label={stage.label}
                count={result.funnel?.[stage.key] ?? 0}
                max={maxNodes}
                isFinal={i === FUNNEL_STAGES.length - 1}
              />
            ))}
          </div>

          {/* Pipeline Timing */}
          <div style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '20px', marginBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h2 style={{ fontSize: '15px', fontWeight: '600', margin: 0 }}>Pipeline Timing</h2>
              <span style={{
                background: timings.total_ms < 500 ? '#dcfce7' : '#fee2e2',
                color: timings.total_ms < 500 ? '#16a34a' : '#dc2626',
                fontSize: '13px', fontWeight: '700', padding: '3px 10px', borderRadius: '12px'
              }}>
                ⏱ {timings.total_ms}ms total
              </span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '8px' }}>
              {Object.entries(timings)
                .filter(([k]) => k !== 'total_ms')
                .map(([k, v]) => {
                  const label = TIMING_LABELS[k.replace(/_ms$/, '')] || k.replace(/_ms$/, '').replace(/_/g, ' ');
                  return (
                    <div key={k} style={{ background: '#f8fafc', padding: '10px 12px', borderRadius: '8px' }}>
                      <div style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '2px' }}>{label}</div>
                      <div style={{ fontSize: '15px', fontWeight: '600', color: '#1e293b' }}>{v}ms</div>
                    </div>
                  );
                })}
            </div>
          </div>

          {/* Candidate Set */}
          <div style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '20px' }}>
            <h2 style={{ fontSize: '15px', fontWeight: '600', margin: '0 0 16px' }}>
              Candidate Set — {result.candidate_set?.length} nodes
            </h2>
            {result.candidate_set?.map(node => {
              const typeStyle = TYPE_COLORS[node.type] || TYPE_COLORS.FACT;
              const hintStyle = HINT_COLORS[node.compression_hint] || HINT_COLORS.FULL;
              const isOpen = expanded[node.id];
              return (
                <div key={node.id} style={{ borderBottom: '1px solid #f1f5f9', padding: '12px 0' }}>
                  <div
                    style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', cursor: 'pointer' }}
                    onClick={() => toggleExpand(node.id)}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                        <span style={{ fontWeight: '600', fontSize: '14px' }}>{node.title}</span>
                        <Badge text={node.type} bg={typeStyle.bg} color={typeStyle.color} />
                        <Badge text={node.compression_hint} bg={hintStyle.bg} color={hintStyle.color} />
                        {node.zone === 2 && <Badge text="GLOBAL" bg="#ede9fe" color="#7c3aed" />}
                      </div>
                      <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>
                        importance: <strong style={{ color: '#64748b' }}>{node.importance}</strong>
                        &nbsp;·&nbsp; dist from entry: <strong style={{ color: '#64748b' }}>{node.distance_from_entry}</strong>
                        &nbsp;·&nbsp; dept: <strong style={{ color: '#64748b' }}>{node.department || 'global'}</strong>
                      </div>
                    </div>
                    <span style={{ fontSize: '18px', color: '#94a3b8', marginTop: '2px' }}>{isOpen ? '▲' : '▼'}</span>
                  </div>
                  {isOpen && (
                    <div style={{
                      marginTop: '10px', padding: '12px', background: '#f8fafc',
                      borderRadius: '8px', fontSize: '13px', color: '#374151', lineHeight: '1.6'
                    }}>
                      {node.content}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}