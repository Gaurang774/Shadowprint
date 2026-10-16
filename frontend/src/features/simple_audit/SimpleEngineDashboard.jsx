import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Shield, Code, MessageSquare, Terminal, Key } from 'lucide-react';

export default function SimpleEngineDashboard({ auditReport, isAuditing, selectedTarget }) {
  const [viewMode, setViewMode] = React.useState('cards'); // 'cards' | 'cli'
  const [copied, setCopied] = React.useState(false);

  const findings = auditReport?.findings || [];
  const status = auditReport?.status || 'IDLE';
  const target = auditReport?.target || selectedTarget;

  // Group findings by Engine
  const s0Findings = findings.filter(f => f.engine === 'S0');
  const s1Findings = findings.filter(f => f.engine === 'S1');
  const s2Findings = findings.filter(f => f.engine === 'S2');
  const s3Findings = findings.filter(f => f.engine === 'S3');

  const getStatusPill = (st) => {
    switch (st) {
      case 'PASSED':
        return <span className="badge badge-pass" style={{ fontSize: '0.85rem', padding: '6px 12px' }}>✓ SECURE (PASSED)</span>;
      case 'FLAGGED':
        return <span className="badge badge-medium" style={{ fontSize: '0.85rem', padding: '6px 12px' }}>⚠ FLAGGED (SUSPICIOUS)</span>;
      case 'FAILED':
        return <span className="badge badge-fail" style={{ fontSize: '0.85rem', padding: '6px 12px' }}>✕ COMPROMISED (FAILED)</span>;
      default:
        return <span className="badge badge-info" style={{ fontSize: '0.85rem', padding: '6px 12px' }}>READY TO AUDIT</span>;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Executive Verdict Banner */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '4px' }}>
              Target Server Audit Result
            </div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', fontFamily: 'var(--font-mono)' }}>
              {target}
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '4px' }}>
              Audited across all 4 independent security layers before agent integration.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '2px' }}>
                Overall Verdict
              </div>
              <div>{getStatusPill(status)}</div>
            </div>

            <div style={{
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '6px',
              padding: '10px 18px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Issues Caught
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: findings.length > 0 ? '#dc2626' : '#15803d' }}>
                {findings.length}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* View Switcher: 4-Engine Cards vs CLI Terminal Response */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
          {viewMode === 'cards' ? 'How the 4 Engines Work & What Each Engine Outputs:' : 'CLI Terminal Response (shadowprint audit):'}
        </h3>

        <div style={{ display: 'flex', gap: '4px', background: '#f1f5f9', padding: '4px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
          <button
            onClick={() => setViewMode('cards')}
            style={{
              padding: '6px 14px',
              fontSize: '0.82rem',
              fontWeight: 600,
              borderRadius: '4px',
              border: 'none',
              background: viewMode === 'cards' ? '#ffffff' : 'transparent',
              color: viewMode === 'cards' ? '#0f172a' : '#64748b',
              boxShadow: viewMode === 'cards' ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Shield size={14} /> 4-Engine Cards
          </button>
          <button
            onClick={() => setViewMode('cli')}
            style={{
              padding: '6px 14px',
              fontSize: '0.82rem',
              fontWeight: 600,
              borderRadius: '4px',
              border: 'none',
              background: viewMode === 'cli' ? '#ffffff' : 'transparent',
              color: viewMode === 'cli' ? '#0f172a' : '#64748b',
              boxShadow: viewMode === 'cli' ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Terminal size={14} /> CLI Response
          </button>
        </div>
      </div>

      {viewMode === 'cli' ? (
        /* Full CLI Terminal View */
        <div style={{
          background: '#0f172a',
          color: '#f8fafc',
          borderRadius: '8px',
          border: '1px solid #334155',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          overflow: 'hidden'
        }}>
          {/* Terminal Titlebar */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: '#1e293b',
            padding: '10px 16px',
            borderBottom: '1px solid #334155'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ef4444' }} />
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#f59e0b' }} />
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#10b981' }} />
              <span style={{ fontSize: '0.8rem', color: '#cbd5e1', fontFamily: 'var(--font-mono)', marginLeft: '8px' }}>
                shadowprint audit fixtures/{target}
              </span>
            </div>

            <button
              onClick={() => {
                navigator.clipboard.writeText(`shadowprint audit fixtures/${target}`);
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
              }}
              style={{
                fontSize: '0.75rem',
                padding: '4px 10px',
                background: '#334155',
                color: '#f8fafc',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              {copied ? '✓ Copied' : 'Copy CLI Command'}
            </button>
          </div>

          {/* Terminal Body */}
          <pre style={{
            margin: 0,
            padding: '16px 20px',
            fontFamily: 'Consolas, Monaco, "Courier New", monospace',
            fontSize: '0.82rem',
            lineHeight: '1.45',
            color: '#e2e8f0',
            overflowX: 'auto',
            whiteSpace: 'pre',
            maxHeight: '520px'
          }}>
            {auditReport?.cli_output || (
              `$ shadowprint audit fixtures/${target}\n\n[Evaluating server across Engines S0-S3...]\nStatus: ${status}\nIssues Caught: ${findings.length}\n`
            )}
          </pre>
        </div>
      ) : (
        /* The 4 Engines: Direct Input -> Process -> Output Cards */
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          {/* Engine S0 Card */}
          <div className="glass-panel" style={{ padding: '20px', borderTop: s0Findings.length > 0 ? '3px solid #dc2626' : '3px solid #15803d' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Code size={16} color="#0f172a" />
                <strong style={{ fontSize: '0.9rem', color: '#0f172a' }}>Engine S0</strong>
              </div>
              <span className={`badge ${s0Findings.length > 0 ? 'badge-fail' : 'badge-pass'}`}>
                {s0Findings.length > 0 ? 'FLAGGED' : 'CLEAN'}
              </span>
            </div>

            <div style={{ fontWeight: 700, fontSize: '0.92rem', color: '#0f172a', marginBottom: '6px' }}>
              Static Code Scanner
            </div>

            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '12px', lineHeight: 1.4 }}>
              <strong>Input:</strong> Source code files.<br />
              <strong>Checks:</strong> Bandit rules, hardcoded API secrets, unsafe shell execution.
            </div>

            <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '10px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                Engine Output:
              </div>
              {s0Findings.length === 0 ? (
                <div style={{ fontSize: '0.8rem', color: '#15803d', fontWeight: 600 }}>✓ Zero code vulnerabilities</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {s0Findings.map((f, i) => (
                    <div key={i} style={{ fontSize: '0.76rem', color: '#b91c1c', background: '#fef2f2', padding: '4px 6px', borderRadius: '4px' }}>
                      • {f.category}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Engine S1 Card */}
          <div className="glass-panel" style={{ padding: '20px', borderTop: s1Findings.length > 0 ? '3px solid #dc2626' : '3px solid #15803d' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <MessageSquare size={16} color="#0f172a" />
                <strong style={{ fontSize: '0.9rem', color: '#0f172a' }}>Engine S1</strong>
              </div>
              <span className={`badge ${s1Findings.length > 0 ? 'badge-fail' : 'badge-pass'}`}>
                {s1Findings.length > 0 ? 'FLAGGED' : 'CLEAN'}
              </span>
            </div>

            <div style={{ fontWeight: 700, fontSize: '0.92rem', color: '#0f172a', marginBottom: '6px' }}>
              Prompt & Steganography
            </div>

            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '12px', lineHeight: 1.4 }}>
              <strong>Input:</strong> Tool descriptions & schemas.<br />
              <strong>Checks:</strong> Plane 14 Unicode tags, zero-width characters, offline Qwen3 AI judge.
            </div>

            <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '10px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                Engine Output:
              </div>
              {s1Findings.length === 0 ? (
                <div style={{ fontSize: '0.8rem', color: '#15803d', fontWeight: 600 }}>✓ Safe tool descriptions</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {s1Findings.map((f, i) => (
                    <div key={i} style={{ fontSize: '0.76rem', color: '#b91c1c', background: '#fef2f2', padding: '4px 6px', borderRadius: '4px' }}>
                      • {f.category}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Engine S2 Card */}
          <div className="glass-panel" style={{ padding: '20px', borderTop: s2Findings.length > 0 ? '3px solid #dc2626' : '3px solid #15803d' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Terminal size={16} color="#0f172a" />
                <strong style={{ fontSize: '0.9rem', color: '#0f172a' }}>Engine S2</strong>
              </div>
              <span className={`badge ${s2Findings.length > 0 ? 'badge-fail' : 'badge-pass'}`}>
                {s2Findings.length > 0 ? 'FLAGGED' : 'CLEAN'}
              </span>
            </div>

            <div style={{ fontWeight: 700, fontSize: '0.92rem', color: '#0f172a', marginBottom: '6px' }}>
              Dynamic Sandbox Prober
            </div>

            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '12px', lineHeight: 1.4 }}>
              <strong>Input:</strong> Test inputs to live tools.<br />
              <strong>Checks:</strong> Linux strace syscalls (openat, connect), decoy canary access.
            </div>

            <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '10px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                Engine Output:
              </div>
              {s2Findings.length === 0 ? (
                <div style={{ fontSize: '0.8rem', color: '#15803d', fontWeight: 600 }}>✓ Zero unauthorized syscalls</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {s2Findings.map((f, i) => (
                    <div key={i} style={{ fontSize: '0.76rem', color: '#b91c1c', background: '#fef2f2', padding: '4px 6px', borderRadius: '4px' }}>
                      • {f.category}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Engine S3 Card */}
          <div className="glass-panel" style={{ padding: '20px', borderTop: s3Findings.length > 0 ? '3px solid #dc2626' : '3px solid #15803d' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Key size={16} color="#0f172a" />
                <strong style={{ fontSize: '0.9rem', color: '#0f172a' }}>Engine S3</strong>
              </div>
              <span className={`badge ${s3Findings.length > 0 ? 'badge-fail' : 'badge-pass'}`}>
                {s3Findings.length > 0 ? 'MUTATED' : 'FROZEN'}
              </span>
            </div>

            <div style={{ fontWeight: 700, fontSize: '0.92rem', color: '#0f172a', marginBottom: '6px' }}>
              Cryptographic Integrity
            </div>

            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '12px', lineHeight: 1.4 }}>
              <strong>Input:</strong> 3-Layer SHA-256 vs SQLite.<br />
              <strong>Checks:</strong> Post-approval schema drift, tool tampering, mid-session rug-pulls.
            </div>

            <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '10px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                Engine Output:
              </div>
              {s3Findings.length === 0 ? (
                <div style={{ fontSize: '0.8rem', color: '#15803d', fontWeight: 600 }}>✓ Hash identical to approved pin</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {s3Findings.map((f, i) => (
                    <div key={i} style={{ fontSize: '0.76rem', color: '#b91c1c', background: '#fef2f2', padding: '4px 6px', borderRadius: '4px' }}>
                      • {f.category}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Detailed Caught Evidence Log */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', marginBottom: '16px' }}>
          Detailed Evidence Caught by Engines ({findings.length})
        </h3>

        {findings.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '36px', color: '#15803d' }}>
            <CheckCircle2 size={36} color="#15803d" style={{ marginBottom: '8px' }} />
            <div style={{ fontWeight: 700, fontSize: '1rem', color: '#0f172a' }}>Server Verified 100% Clean</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              All 4 engines verified that this MCP server contains no malware, prompt injections, or unauthorized syscalls.
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {findings.map((f, idx) => (
              <div key={idx} className="glass-card" style={{ borderColor: '#fca5a5', background: '#ffffff' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span className="badge badge-info">{f.engine}</span>
                    <strong style={{ color: '#991b1b', fontSize: '0.92rem' }}>{f.category}</strong>
                    {f.tool && <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>• Tool: {f.tool}</span>}
                  </div>
                  <span className="badge badge-critical">{f.severity}</span>
                </div>

                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  <strong>Claim:</strong> {f.claim || 'Server claimed benign capability.'}
                </div>

                <pre className="code-box" style={{ background: '#fef2f2', color: '#b91c1c', whiteSpace: 'pre-wrap', marginBottom: '8px' }}>
                  {f.evidence}
                </pre>

                {f.remediation && (
                  <div style={{ fontSize: '0.78rem', color: '#15803d', fontWeight: 600 }}>
                    Fix: {f.remediation}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )}
</div>
  );
}
