import React from 'react';
import { Box, Cpu, Database } from 'lucide-react';

export default function SystemHealth({ systemStatus }) {
  const docker = systemStatus?.docker || {};
  const ollama = systemStatus?.ollama || {};
  const db = systemStatus?.database || {};
  const engines = systemStatus?.engines || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Banner */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#0f172a' }}>
          Engines, Docker Sandbox & Integration Architecture
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
          Diagnostic telemetry across containerized kernel isolation, local open-weight AI judges, and modular integration-ready interfaces.
        </p>
      </div>

      {/* 3 Infrastructure Pillar Cards */}
      <div className="grid-3">
        {/* Docker Sandbox */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
            <Box size={22} color="#0f172a" />
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a' }}>Docker Sandbox</h3>
              <span className={`badge ${docker.daemon_running ? 'badge-pass' : 'badge-info'}`}>
                {docker.daemon_running ? 'DAEMON ONLINE' : 'CONTAINER HOST'}
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.82rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Image Name:</span>
              <code>{docker.image_name}</code>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Kernel Tracing:</span>
              <strong style={{ color: '#15803d' }}>Linux strace (openat, connect, execve)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Canary Secret:</span>
              <code>/tmp/canary_creds.env</code>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Silent Egress Sink:</span>
              <code>127.0.0.1:8080/sink</code>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Isolation Flags:</span>
              <span style={{ color: '#475569', fontSize: '0.75rem' }}>--network none --cap-add=SYS_PTRACE</span>
            </div>
          </div>
        </div>

        {/* Ollama Local AI */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
            <Cpu size={22} color="#0f172a" />
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a' }}>Local AI Judge</h3>
              <span className={`badge ${ollama.online ? 'badge-pass' : 'badge-info'}`}>
                {ollama.online ? 'OLLAMA READY' : 'OFFLINE GUARANTEE'}
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.82rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Endpoint:</span>
              <code>{ollama.endpoint}</code>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Open-Weight Model:</span>
              <strong style={{ color: '#0f172a' }}>Qwen3-4B / Qwen3-8B</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Inference Authority:</span>
              <strong style={{ color: '#15803d' }}>Add-Only (Cannot clear S1 flags)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Steganography:</span>
              <span>Plane 14 Unicode Tag Detector</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Cloud Dependency:</span>
              <strong style={{ color: '#15803d' }}>0.0% (100% Offline Airgapped)</strong>
            </div>
          </div>
        </div>

        {/* SQLite Database */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
            <Database size={22} color="#0f172a" />
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a' }}>Cryptographic Store</h3>
              <span className="badge badge-pass">SQLITE 3</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.82rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Database File:</span>
              <code>shadowprint.db</code>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Pinned Baselines:</span>
              <strong style={{ color: '#0f172a' }}>{db.pinned_servers_count} Servers</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Hashing Algorithm:</span>
              <strong>3-Layer SHA-256</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Diff Engine:</span>
              <span>DeepDiff with Character Escaping</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Storage Mode:</span>
              <span style={{ color: '#15803d' }}>Persistent ACID Local DB</span>
            </div>
          </div>
        </div>
      </div>

      {/* Integration-Ready Engine Modular Topology */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', marginBottom: '16px' }}>
          Modular Integration Topology
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
          {engines.map((eng) => (
            <div key={eng.id} className="glass-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <span className="badge badge-info">{eng.id}</span>
                <span className="badge badge-pass">{eng.status}</span>
              </div>
              <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#0f172a', marginBottom: '4px' }}>
                {eng.name}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '6px' }}>
                {eng.tools.map((t, idx) => (
                  <span key={idx} style={{
                    fontSize: '0.72rem',
                    background: '#f1f5f9',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    color: '#334155'
                  }}>
                    {t}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
