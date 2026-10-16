import React, { useState, useEffect } from 'react';
import { Database, GitCompare, CheckCircle2, AlertTriangle, ShieldCheck, RefreshCw } from 'lucide-react';

export default function BaselineDiffViewer({ fixtures }) {
  const [pins, setPins] = useState([]);
  const [selectedServer, setSelectedServer] = useState('');
  const [diffResult, setDiffResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [approveStatus, setApproveStatus] = useState('');

  const fetchPins = async () => {
    try {
      const res = await fetch('/api/pins');
      if (res.ok) {
        const data = await res.json();
        setPins(data);
        if (data.length > 0 && !selectedServer) {
          setSelectedServer(data[0].server_name);
        }
      }
    } catch (e) {
      console.error("Could not fetch pins", e);
    }
  };

  useEffect(() => {
    fetchPins();
  }, []);

  const handleRunDiff = async (srv) => {
    if (!srv) return;
    setLoading(true);
    setDiffResult(null);
    try {
      const res = await fetch(`/api/diff/${srv}`);
      if (res.ok) {
        const data = await res.json();
        setDiffResult(data);
      } else {
        const err = await res.json();
        setDiffResult({ error: err.detail || 'Could not compute diff' });
      }
    } catch (e) {
      setDiffResult({ error: 'Failed to connect to diff service' });
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!selectedServer) return;
    setApproveStatus('Pinning baseline in SQLite...');
    try {
      const res = await fetch('/api/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: selectedServer })
      });
      if (res.ok) {
        const data = await res.json();
        setApproveStatus(`Approved! Definition hash: ${data.definition_hash.substring(0, 16)}...`);
        fetchPins();
      } else {
        setApproveStatus('Approval failed.');
      }
    } catch (e) {
      setApproveStatus('Network error approving baseline.');
    }
  };

  const selectedPin = pins.find(p => p.server_name === selectedServer);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Controls */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.4rem', fontWeight: 700 }}>
              Engine S3: Cryptographic Baseline Pin & Diff
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Stores canonical SHA-256 fingerprints in SQLite (<code style={{ color: '#38bdf8' }}>shadowprint.db</code>) and detects mid-session schema drift with character escaping.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <select
              value={selectedServer}
              onChange={(e) => {
                setSelectedServer(e.target.value);
                setDiffResult(null);
              }}
              style={{
                background: '#0d1322',
                color: '#ffffff',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '10px 16px',
                fontSize: '0.875rem',
                minWidth: '220px',
                fontFamily: 'var(--font-mono)'
              }}
            >
              {pins.map(p => (
                <option key={p.server_name} value={p.server_name}>
                  {p.server_name} (Pinned)
                </option>
              ))}
              {fixtures.filter(f => !pins.some(p => p.server_name === f.name)).map(f => (
                <option key={f.name} value={f.name}>
                  {f.name} (Unpinned)
                </option>
              ))}
            </select>

            <button
              className="btn btn-primary"
              onClick={() => handleRunDiff(selectedServer)}
              disabled={loading}
            >
              <GitCompare size={16} />
              <span>{loading ? 'Comparing...' : 'Compare Live Diff'}</span>
            </button>

            <button
              className="btn btn-outline"
              onClick={handleApprove}
              title="Pin baseline to SQLite"
            >
              <ShieldCheck size={16} color="#10b981" />
              <span>Approve Baseline</span>
            </button>
          </div>
        </div>

        {approveStatus && (
          <div style={{ marginTop: '12px', fontSize: '0.82rem', color: '#34d399', fontFamily: 'var(--font-mono)' }}>
            ✓ {approveStatus}
          </div>
        )}
      </div>

      {/* 3-Layer SHA-256 Hashes Cards */}
      <div className="grid-3">
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>LAYER 1 FINGERPRINT</span>
            <span className="badge badge-info">DEFINITION</span>
          </div>
          <div style={{ fontSize: '1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '6px' }}>
            Tool Schema SHA-256
          </div>
          <pre className="code-box" style={{ fontSize: '0.72rem', color: '#38bdf8' }}>
            {selectedPin?.definition_hash || 'Unpinned / Pending'}
          </pre>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
            Hashes inputSchema, tool names, and parameter definitions.
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>LAYER 2 FINGERPRINT</span>
            <span className="badge badge-pass">ARTIFACT</span>
          </div>
          <div style={{ fontSize: '1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '6px' }}>
            Source File SHA-256
          </div>
          <pre className="code-box" style={{ fontSize: '0.72rem', color: '#34d399' }}>
            {selectedPin?.artifact_hash || 'Unpinned / Pending'}
          </pre>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
            Source tree fingerprint ensuring uncorrupted file integrity.
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>LAYER 3 FINGERPRINT</span>
            <span className="badge badge-high">BEHAVIOR</span>
          </div>
          <div style={{ fontSize: '1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '6px' }}>
            Observed Syscall Hash
          </div>
          <pre className="code-box" style={{ fontSize: '0.72rem', color: '#fbbf24' }}>
            {selectedPin?.behavior_hash || 'Unpinned / Pending'}
          </pre>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
            Runtime profile of observed file accesses and network sinks.
          </div>
        </div>
      </div>

      {/* Side-by-Side Diff Inspector */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.15rem', fontWeight: 700, marginBottom: '16px' }}>
          Baseline Drift Comparison Analysis
        </h3>

        {!diffResult ? (
          <div style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
            <GitCompare size={36} style={{ marginBottom: '8px' }} />
            <div style={{ fontSize: '0.95rem' }}>Select a pinned server above and click "Compare Live Diff" to inspect schema drift.</div>
          </div>
        ) : diffResult.error ? (
          <div className="glass-card" style={{ borderColor: 'rgba(239, 68, 68, 0.4)', padding: '16px', color: '#fca5a5' }}>
            <AlertTriangle size={18} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
            {diffResult.error}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px 18px',
              borderRadius: 'var(--radius-sm)',
              background: diffResult.has_drift ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
              border: `1px solid ${diffResult.has_drift ? 'rgba(239, 68, 68, 0.4)' : 'rgba(16, 185, 129, 0.4)'}`,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                {diffResult.has_drift ? (
                  <AlertTriangle size={20} color="#ef4444" />
                ) : (
                  <CheckCircle2 size={20} color="#10b981" />
                )}
                <div>
                  <strong style={{ color: diffResult.has_drift ? '#f87171' : '#34d399' }}>
                    {diffResult.has_drift ? 'SCHEMA DRIFT DETECTED (RUG-PULL)' : 'CRYPTO BASELINE IDENTICAL (NO DRIFT)'}
                  </strong>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                    Pinned: {diffResult.tool_count_pinned} tools • Live: {diffResult.tool_count_live} tools
                  </div>
                </div>
              </div>

              <span className={`badge ${diffResult.has_drift ? 'badge-fail' : 'badge-pass'}`}>
                {diffResult.has_drift ? 'MUTATED' : 'FROZEN'}
              </span>
            </div>

            {/* Diff Findings */}
            {diffResult.findings && diffResult.findings.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {diffResult.findings.map((f, i) => (
                  <div key={i} className="glass-card" style={{ borderColor: 'rgba(239, 68, 68, 0.3)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <strong style={{ color: '#f87171', fontSize: '0.9rem' }}>{f.category}</strong>
                      <span className="badge badge-critical">{f.severity}</span>
                    </div>
                    <pre className="code-box" style={{ whiteSpace: 'pre-wrap', color: '#fca5a5' }}>
                      {f.evidence}
                    </pre>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
