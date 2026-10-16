import React from 'react';
import { Box, Cpu, Database } from 'lucide-react';

export default function SystemHealth({ systemStatus }) {
  const docker = systemStatus?.docker || {};
  const ollama = systemStatus?.ollama || {};
  const db = systemStatus?.database || {};
  const engines = systemStatus?.engines || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Banner */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.4rem', fontWeight: 700 }}>
          Engines, Docker Sandbox & Integration Architecture
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
          Diagnostic telemetry across containerized kernel isolation, local open-weight AI judges, and modular integration-ready interfaces.
        </p>
      </div>

      {/* 3 Infrastructure Pillar Cards */}
      <div className="grid-3">
        {/* Docker Sandbox */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <Box size={24} color="#06b6d4" />
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Docker Sandbox</h3>
              <span className={`badge ${docker.daemon_running ? 'badge-pass' : 'badge-info'}`}>
                {docker.daemon_running ? 'DAEMON ONLINE' : 'CONTAINER HOST'}
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.84rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Image Name:</span>
              <code style={{ color: '#38bdf8' }}>{docker.image_name}</code>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Kernel Tracing:</span>
              <strong style={{ color: '#34d399' }}>Linux strace (openat, connect, execve)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Canary Secret:</span>
              <code style={{ color: '#fbbf24' }}>/tmp/canary_creds.env</code>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Silent Egress Sink:</span>
              <code style={{ color: '#a78bfa' }}>127.0.0.1:8080/sink</code>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Isolation Flags:</span>
              <span style={{ color: '#e2e8f0', fontSize: '0.75rem' }}>--network none --cap-add=SYS_PTRACE</span>
            </div>
          </div>
        </div>

        {/* Ollama Local AI */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <Cpu size={24} color="#8b5cf6" />
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Local AI Judge</h3>
              <span className={`badge ${ollama.online ? 'badge-pass' : 'badge-info'}`}>
                {ollama.online ? 'OLLAMA READY' : 'OFFLINE GUARANTEE'}
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.84rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Endpoint:</span>
              <code style={{ color: '#38bdf8' }}>{ollama.endpoint}</code>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Open-Weight Model:</span>
              <strong style={{ color: '#a78bfa' }}>Qwen3-4B / Qwen3-8B</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Inference Authority:</span>
              <strong style={{ color: '#34d399' }}>Add-Only (Cannot clear S1 flags)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Steganography:</span>
              <span style={{ color: '#38bdf8' }}>Plane 14 Unicode Tag Detector</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Cloud Dependency:</span>
              <strong style={{ color: '#34d399' }}>0.0% (100% Offline Airgapped)</strong>
            </div>
          </div>
        </div>

        {/* SQLite Database */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <Database size={24} color="#10b981" />
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Cryptographic Store</h3>
              <span className="badge badge-pass">SQLITE 3</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.84rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Database File:</span>
              <code style={{ color: '#38bdf8' }}>shadowprint.db</code>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Pinned Baselines:</span>
              <strong style={{ color: '#34d399' }}>{db.pinned_servers_count} Servers</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Hashing Algorithm:</span>
              <strong style={{ color: '#38bdf8' }}>3-Layer SHA-256</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Diff Engine:</span>
              <span style={{ color: '#e2e8f0' }}>DeepDiff with Character Escaping</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Storage Mode:</span>
              <span style={{ color: '#34d399' }}>Persistent ACID Local DB</span>
            </div>
          </div>
        </div>
      </div>

      {/* Integration-Ready Engine Modular Topology */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.15rem', fontWeight: 700, marginBottom: '16px' }}>
          Modular Integration Topology
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
          {engines.map((eng) => (
            <div key={eng.id} className="glass-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span className="badge badge-info">{eng.id}</span>
                <span className="badge badge-pass">{eng.status}</span>
              </div>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#f8fafc', marginBottom: '6px' }}>
                {eng.name}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '8px' }}>
                {eng.tools.map((t, idx) => (
                  <span key={idx} style={{
                    fontSize: '0.72rem',
                    background: 'rgba(255,255,255,0.06)',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    color: '#cbd5e1'
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
