import React, { useState, useEffect } from 'react';
import { GitCompare, ShieldCheck, CheckCircle2, AlertTriangle } from 'lucide-react';
import HashCards from './HashCards';
import { api } from '../../services/api';

export default function BaselineDiffViewer({ fixtures }) {
  const [pins, setPins] = useState([]);
  const [selectedServer, setSelectedServer] = useState('rugpull_suite');
  const [diffResult, setDiffResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [approveStatus, setApproveStatus] = useState('');

  const fetchPins = async () => {
    try {
      const data = await api.getPins();
      setPins(data);
    } catch (e) {
      console.error("Could not fetch pins", e);
    }
  };

  useEffect(() => {
    fetchPins();
    handleRunDiff(selectedServer);
  }, []);

  const handleRunDiff = async (srv) => {
    if (!srv) return;
    setLoading(true);
    setDiffResult(null);
    try {
      const data = await api.getDiff(srv);
      setDiffResult(data);
    } catch (e) {
      setDiffResult({ error: e.message || 'Failed to compute diff' });
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!selectedServer) return;
    setApproveStatus('Saving cryptographic baseline to SQLite...');
    try {
      const data = await api.approveBaseline(selectedServer);
      setApproveStatus(`Approved & Pinned! Definition SHA-256: ${data.definition_hash.substring(0, 16)}...`);
      fetchPins();
      handleRunDiff(selectedServer);
    } catch (e) {
      setApproveStatus(`Approval failed: ${e.message}`);
    }
  };

  const selectedPin = pins.find(p => p.server_name === selectedServer);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Clean White Header */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span className="badge badge-info">ENGINE S3</span>
              <span className="badge badge-pass">CRYPTOGRAPHIC BASELINE</span>
            </div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#0f172a' }}>
              Cryptographic Pin-and-Diff Visualizer
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Freezes canonical tool definitions in SQLite and detects mid-session schema drift and rug-pulls.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <select
              value={selectedServer}
              onChange={(e) => {
                setSelectedServer(e.target.value);
                handleRunDiff(e.target.value);
              }}
              style={{
                padding: '8px 14px',
                fontSize: '0.875rem',
                minWidth: '220px',
              }}
            >
              <optgroup label="Benchmark Fixtures">
                {fixtures.map(f => (
                  <option key={f.name} value={f.name}>
                    {f.name} {pins.some(p => p.server_name === f.name) ? '★ (Pinned)' : '(Unpinned)'}
                  </option>
                ))}
              </optgroup>
            </select>

            <button
              className="btn btn-primary"
              onClick={() => handleRunDiff(selectedServer)}
              disabled={loading}
            >
              <GitCompare size={15} />
              <span>{loading ? 'Diffing...' : 'Compare Live Diff'}</span>
            </button>

            <button
              className="btn btn-outline"
              onClick={handleApprove}
            >
              <ShieldCheck size={15} color="#15803d" />
              <span>Approve Pin</span>
            </button>
          </div>
        </div>

        {approveStatus && (
          <div style={{ marginTop: '12px', fontSize: '0.82rem', color: '#15803d', fontWeight: 600 }}>
            ✓ {approveStatus}
          </div>
        )}
      </div>

      {/* 3-Layer Fingerprints */}
      <HashCards selectedPin={selectedPin} />

      {/* Side-by-Side Visual Diff Studio */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a' }}>
              Visual Diff & Character Unmasking Studio
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Compares canonical baseline against live stdio snapshot, escaping zero-width characters and Plane 14 tags.
            </p>
          </div>

          {diffResult && !diffResult.error && (
            <span className={`badge ${diffResult.has_drift ? 'badge-fail' : 'badge-pass'}`} style={{ fontSize: '0.8rem', padding: '4px 10px' }}>
              {diffResult.has_drift ? 'MUTATED (RUG-PULL)' : 'IDENTICAL BASELINE'}
            </span>
          )}
        </div>

        {!diffResult ? (
          <div style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
            <GitCompare size={36} style={{ marginBottom: '8px' }} />
            <div>Select a server and run diff to inspect cryptographic divergence.</div>
          </div>
        ) : diffResult.error ? (
          <div className="glass-card" style={{ borderColor: '#fca5a5', background: '#fef2f2', color: '#991b1b' }}>
            <AlertTriangle size={16} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
            {diffResult.error}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Side-by-Side Comparison Columns */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              {/* Pinned Baseline Column */}
              <div className="glass-card" style={{ borderColor: '#bbf7d0', background: '#f0fdf4' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <CheckCircle2 size={16} color="#15803d" />
                    <strong style={{ fontSize: '0.9rem', color: '#166534' }}>Approved SQLite Baseline</strong>
                  </div>
                  <span className="badge badge-pass">{diffResult.tool_count_pinned} Tools</span>
                </div>
                <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: '#475569', marginBottom: '6px' }}>
                  Definition SHA-256: <code>{diffResult.pinned_definition_hash?.substring(0, 24)}...</code>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#334155' }}>
                  Canonical tool schema authorized by security auditor. Zero hidden powers or unexpected instructions.
                </div>
              </div>

              {/* Live Server Column */}
              <div className="glass-card" style={{
                borderColor: diffResult.has_drift ? '#fecaca' : '#bbf7d0',
                background: diffResult.has_drift ? '#fef2f2' : '#f0fdf4'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    {diffResult.has_drift ? <AlertTriangle size={16} color="#dc2626" /> : <CheckCircle2 size={16} color="#15803d" />}
                    <strong style={{ fontSize: '0.9rem', color: diffResult.has_drift ? '#991b1b' : '#166534' }}>
                      Live Observed Stdio Server
                    </strong>
                  </div>
                  <span className={`badge ${diffResult.has_drift ? 'badge-fail' : 'badge-pass'}`}>
                    {diffResult.tool_count_live} Tools
                  </span>
                </div>
                <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: '#475569', marginBottom: '6px' }}>
                  Definition SHA-256: <code>{diffResult.live_definition_hash?.substring(0, 24)}...</code>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#334155' }}>
                  {diffResult.has_drift
                    ? 'WARNING: Live tool definition deviates from approved baseline! Possible malicious rug-pull.'
                    : 'Verified identical to baseline state. Tool schema is secure and unmodified.'}
                </div>
              </div>
            </div>

            {/* Diff Structural Findings */}
            {diffResult.findings && diffResult.findings.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '10px' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#dc2626' }}>
                  Detected Cryptographic Discrepancies ({diffResult.findings.length}):
                </div>
                {diffResult.findings.map((f, i) => (
                  <div key={i} className="glass-card" style={{ borderColor: '#fca5a5', background: '#fef2f2' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <strong style={{ color: '#991b1b', fontSize: '0.9rem' }}>{f.category}</strong>
                      <span className="badge badge-critical">{f.severity}</span>
                    </div>
                    <pre className="code-box" style={{ background: '#ffffff', color: '#b91c1c' }}>
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
