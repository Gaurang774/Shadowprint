import React, { useState } from 'react';
import { Play, CheckCircle2, AlertTriangle, XCircle, Search, ShieldAlert, FileText, ChevronRight, Download } from 'lucide-react';

export default function AuditScanner({
  fixtures,
  selectedTarget,
  setSelectedTarget,
  auditReport,
  isAuditing,
  onRunAudit,
}) {
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [engineFilter, setEngineFilter] = useState('ALL');

  const findings = auditReport?.findings || [];
  const summary = auditReport?.summary || { total: 0, critical: 0, high: 0, medium: 0, low: 0 };
  const status = auditReport?.status || 'IDLE';

  const filteredFindings = findings.filter(f => {
    if (severityFilter !== 'ALL' && f.severity?.toUpperCase() !== severityFilter) return false;
    if (engineFilter !== 'ALL' && f.engine?.toUpperCase() !== engineFilter) return false;
    return true;
  });

  const getStatusBadge = (st) => {
    switch (st) {
      case 'PASSED':
        return <span className="badge badge-pass"><CheckCircle2 size={12} /> SECURE (PASSED)</span>;
      case 'FLAGGED':
        return <span className="badge badge-medium"><AlertTriangle size={12} /> FLAGGED (SUSPICIOUS)</span>;
      case 'FAILED':
        return <span className="badge badge-fail"><XCircle size={12} /> COMPROMISED (FAILED)</span>;
      default:
        return <span className="badge badge-info">READY TO SCAN</span>;
    }
  };

  const getSeverityBadge = (sev) => {
    switch (sev?.toLowerCase()) {
      case 'critical':
        return <span className="badge badge-critical">CRITICAL</span>;
      case 'high':
        return <span className="badge badge-high">HIGH</span>;
      case 'medium':
        return <span className="badge badge-medium">MEDIUM</span>;
      case 'low':
        return <span className="badge badge-low">LOW</span>;
      default:
        return <span className="badge badge-info">{sev}</span>;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Target Selector & Scanner Controls */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.4rem', fontWeight: 700 }}>
              Live Target Security Audit
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Execute deep 4-engine inspection across AST static rules, prompt injection, kernel syscalls, and cryptographic drift.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <select
              value={selectedTarget}
              onChange={(e) => setSelectedTarget(e.target.value)}
              style={{
                background: '#0d1322',
                color: '#ffffff',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '10px 16px',
                fontSize: '0.875rem',
                minWidth: '280px',
                fontFamily: 'var(--font-mono)'
              }}
            >
              <optgroup label="Pre-Packaged Fixtures">
                {fixtures.map((fix) => (
                  <option key={fix.id} value={fix.entrypoint || fix.id}>
                    {fix.name} ({fix.expected_outcome})
                  </option>
                ))}
              </optgroup>
            </select>

            <button
              className="btn btn-primary"
              onClick={() => onRunAudit(selectedTarget)}
              disabled={isAuditing}
              style={{ minWidth: '150px' }}
            >
              <Play size={16} fill="currentColor" />
              <span>{isAuditing ? 'Auditing Engines...' : 'Execute Audit'}</span>
            </button>
          </div>
        </div>

        {/* 4-Engine Visual Pipeline Stepper */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginTop: '16px' }}>
          <div className="glass-card" style={{ borderColor: isAuditing ? 'var(--accent-cyan)' : 'var(--border-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>ENGINE S0</span>
              <span className="badge badge-info">AST & RULES</span>
            </div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Static Code & Secrets</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Bandit • AST Taint • Gitleaks</div>
          </div>

          <div className="glass-card" style={{ borderColor: isAuditing ? 'var(--accent-cyan)' : 'var(--border-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>ENGINE S1</span>
              <span className="badge badge-pass">QWEN3 JUDGE</span>
            </div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Metadata & Steganography</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Plane 14 Tag Filter • Add-Only AI</div>
          </div>

          <div className="glass-card" style={{ borderColor: isAuditing ? 'var(--accent-cyan)' : 'var(--border-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>ENGINE S2</span>
              <span className="badge badge-high">SANDBOX</span>
            </div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Dynamic Least-Capability</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Linux strace • Canary Tripwire</div>
          </div>

          <div className="glass-card" style={{ borderColor: isAuditing ? 'var(--accent-cyan)' : 'var(--border-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>ENGINE S3</span>
              <span className="badge badge-medium">DIFF PIN</span>
            </div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Cryptographic Integrity</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>3-Layer SHA-256 • Drift Watcher</div>
          </div>
        </div>
      </div>

      {/* Audit Verdict Banner & Metric Cards */}
      <div className="grid-4">
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '8px' }}>Security Verdict</div>
          <div style={{ fontSize: '1.25rem', marginBottom: '6px' }}>{getStatusBadge(status)}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
            Target: {auditReport?.target || 'None'}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '8px' }}>Critical Violations</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: summary.critical > 0 ? '#ef4444' : '#10b981' }}>
            {summary.critical}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Immediate exploit vectors</div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '8px' }}>High & Medium Risks</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: (summary.high + summary.medium) > 0 ? '#f59e0b' : '#10b981' }}>
            {summary.high + summary.medium}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Warnings & prompt anomalies</div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '8px' }}>Total Issues Caught</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#38bdf8' }}>
            {summary.total}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Across all 4 security layers</div>
        </div>
      </div>

      {/* Findings Explorer with Filter Controls */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.15rem', fontWeight: 700 }}>
              Detected Findings Log ({filteredFindings.length})
            </h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Click finding to inspect cryptographic evidence</span>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              style={{
                background: '#0d1322',
                color: '#ffffff',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '6px 12px',
                fontSize: '0.8rem',
              }}
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>

            <select
              value={engineFilter}
              onChange={(e) => setEngineFilter(e.target.value)}
              style={{
                background: '#0d1322',
                color: '#ffffff',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '6px 12px',
                fontSize: '0.8rem',
              }}
            >
              <option value="ALL">All Engines</option>
              <option value="S0">S0 Static</option>
              <option value="S1">S1 Metadata</option>
              <option value="S2">S2 Dynamic</option>
              <option value="S3">S3 Integrity</option>
            </select>
          </div>
        </div>

        {filteredFindings.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
            <CheckCircle2 size={40} color="#10b981" style={{ marginBottom: '12px' }} />
            <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc' }}>Zero Findings Detected</div>
            <div style={{ fontSize: '0.85rem' }}>No malicious injection, AST vulnerabilities, or schema drift detected. Server is clean!</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {filteredFindings.map((finding) => (
              <div
                key={finding.id}
                onClick={() => setSelectedFinding(finding)}
                className="glass-card"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  borderColor: selectedFinding?.id === finding.id ? 'var(--accent-cyan)' : 'var(--border-subtle)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ width: '48px', textAlign: 'center' }}>
                    <span className="badge badge-info">{finding.engine || 'S?'}</span>
                  </div>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <strong style={{ fontSize: '0.92rem', color: '#f8fafc' }}>{finding.category}</strong>
                      {getSeverityBadge(finding.severity)}
                      {finding.tool && (
                        <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                          Tool: {finding.tool}
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                      {finding.evidence ? (finding.evidence.length > 120 ? finding.evidence.substring(0, 120) + '...' : finding.evidence) : 'Evidence captured.'}
                    </div>
                  </div>
                </div>

                <ChevronRight size={18} color="var(--text-muted)" />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Detailed Finding Modal / Drawer */}
      {selectedFinding && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100,
          padding: '24px',
        }}
        onClick={() => setSelectedFinding(null)}
        >
          <div
            className="glass-panel"
            style={{ maxWidth: '780px', width: '100%', maxHeight: '85vh', overflowY: 'auto', padding: '32px' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <ShieldAlert size={28} color="#ef4444" />
                <div>
                  <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.3rem', fontWeight: 700 }}>
                    {selectedFinding.category}
                  </h3>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    ID: {selectedFinding.id} • Engine {selectedFinding.engine}
                  </div>
                </div>
              </div>
              <button className="btn btn-outline" onClick={() => setSelectedFinding(null)}>Close</button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="glass-card">
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>Claim vs Observed Evidence</div>
                <div style={{ fontSize: '0.88rem', color: '#f8fafc', marginBottom: '8px' }}>
                  <strong>Declared Claim:</strong> {selectedFinding.claim || 'Server claimed benign capability.'}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>Evidence Quote / Syscall Log:</div>
                <pre className="code-box" style={{ whiteSpace: 'pre-wrap', color: '#fca5a5' }}>
                  {selectedFinding.evidence}
                </pre>
              </div>

              {selectedFinding.remediation && (
                <div className="glass-card" style={{ borderColor: 'rgba(16, 185, 129, 0.3)' }}>
                  <div style={{ fontSize: '0.75rem', color: '#34d399', textTransform: 'uppercase', marginBottom: '4px' }}>Recommended Security Remediation</div>
                  <div style={{ fontSize: '0.85rem', color: '#e2e8f0' }}>{selectedFinding.remediation}</div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
