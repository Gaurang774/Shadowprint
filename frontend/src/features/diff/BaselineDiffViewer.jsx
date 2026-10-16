import React, { useState, useEffect } from 'react';
import { GitCompare, ShieldCheck, CheckCircle2, AlertTriangle, Sparkles, RefreshCw, Layers, ArrowRight } from 'lucide-react';
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
      setDiffResult({ error: e.message || 'Failed to compute cryptographic diff' });
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!selectedServer) return;
    setApproveStatus('Computing 3-layer SHA-256 hashes and saving to SQLite...');
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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Clean Header */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span className="badge badge-info">ENGINE S3</span>
              <span className="badge badge-pass">CRYPTOGRAPHIC BASELINE</span>
            </div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>
              Cryptographic Pin-and-Diff Visualizer
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Freezes canonical tool definitions in SQLite and detects mid-session schema drift and rug-pulls.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <select
              value={selectedServer}
              onChange={(e) => {
                setSelectedServer(e.target.value);
                handleRunDiff(e.target.value);
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
              <GitCompare size={16} />
              <span>{loading ? 'Diffing...' : 'Compare Live Diff'}</span>
            </button>

            <button
              className="btn btn-outline"
              onClick={handleApprove}
              title="Pin baseline to SQLite"
            >
              <ShieldCheck size={16} color="#10b981" />
              <span>Approve Pin</span>
            </button>
          </div>
        </div>

        {approveStatus && (
          <div style={{ marginTop: '14px', fontSize: '0.82rem', color: '#34d399', fontFamily: 'var(--font-mono)' }}>
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
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', fontWeight: 700 }}>
              Visual Diff & Character Unmasking Studio
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Compares canonical baseline against live stdio snapshot, escaping zero-width characters and Plane 14 tags.
            </p>
          </div>

          {diffResult && !diffResult.error && (
            <span className={`badge ${diffResult.has_drift ? 'badge-fail' : 'badge-pass'}`} style={{ fontSize: '0.82rem', padding: '6px 14px' }}>
              {diffResult.has_drift ? 'MUTATED (RUG-PULL)' : 'IDENTICAL BASELINE'}
            </span>
          )}
        </div>

        {!diffResult ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            <GitCompare size={40} style={{ marginBottom: '10px' }} />
            <div>Select a server and run diff to inspect cryptographic divergence.</div>
          </div>
        ) : diffResult.error ? (
          <div className="glass-card" style={{ borderColor: 'rgba(239, 68, 68, 0.4)', color: '#fca5a5' }}>
            <AlertTriangle size={18} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
            {diffResult.error}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Side-by-Side Comparison Columns */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              {/* Pinned Baseline Column */}
              <div className="glass-card" style={{ borderColor: 'rgba(16, 185, 129, 0.3)', background: 'rgba(16, 185, 129, 0.04)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={16} color="#10b981" />
                    <strong style={{ fontSize: '0.9rem', color: '#34d399' }}>Approved SQLite Baseline</strong>
                  </div>
                  <span className="badge badge-pass">{diffResult.tool_count_pinned} Tools</span>
                </div>
                <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginBottom: '8px' }}>
                  Definition SHA-256: <code style={{ color: '#38bdf8' }}>{diffResult.pinned_definition_hash?.substring(0, 24)}...</code>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                  Canonical tool schema authorized by security auditor. Zero hidden powers or unexpected instructions.
                </div>
              </div>

              {/* Live Server Column */}
              <div className="glass-card" style={{
                borderColor: diffResult.has_drift ? 'rgba(239, 68, 68, 0.5)' : 'rgba(16, 185, 129, 0.3)',
                background: diffResult.has_drift ? 'rgba(239, 68, 68, 0.08)' : 'rgba(16, 185, 129, 0.04)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {diffResult.has_drift ? <AlertTriangle size={16} color="#ef4444" /> : <CheckCircle2 size={16} color="#10b981" />}
                    <strong style={{ fontSize: '0.9rem', color: diffResult.has_drift ? '#f87171' : '#34d399' }}>
                      Live Observed Stdio Server
                    </strong>
                  </div>
                  <span className={`badge ${diffResult.has_drift ? 'badge-fail' : 'badge-pass'}`}>
                    {diffResult.tool_count_live} Tools
                  </span>
                </div>
                <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginBottom: '8px' }}>
                  Definition SHA-256: <code style={{ color: diffResult.has_drift ? '#f87171' : '#38bdf8' }}>{diffResult.live_definition_hash?.substring(0, 24)}...</code>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                  {diffResult.has_drift
                    ? 'WARNING: Live tool definition deviates from approved baseline! Possible malicious rug-pull.'
                    : 'Verified identical to baseline state. Tool schema is secure and unmodified.'}
                </div>
              </div>
            </div>

            {/* Diff Structural Findings */}
            {diffResult.findings && diffResult.findings.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '10px' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f87171' }}>
                  Detected Cryptographic Discrepancies ({diffResult.findings.length}):
                </div>
                {diffResult.findings.map((f, i) => (
                  <div key={i} className="glass-card" style={{ borderColor: 'rgba(239, 68, 68, 0.4)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
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
