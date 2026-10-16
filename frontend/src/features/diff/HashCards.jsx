import React from 'react';
import { Key, FileCode, Activity } from 'lucide-react';

export default function HashCards({ selectedPin }) {
  return (
    <div className="grid-3" style={{ marginBottom: '20px' }}>
      {/* Layer 1: Definition Hash */}
      <div className="glass-panel" style={{ padding: '20px', borderLeft: '4px solid #06b6d4' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Key size={16} color="#06b6d4" />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>LAYER 1 PIN</span>
          </div>
          <span className="badge badge-info">DEFINITION</span>
        </div>
        <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc', marginBottom: '6px' }}>
          Tool Schema SHA-256
        </div>
        <pre className="code-box" style={{ fontSize: '0.7rem', color: '#38bdf8' }}>
          {selectedPin?.definition_hash || 'Unpinned Baseline'}
        </pre>
        <div style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
          Canonical hash of all tool names, descriptions, and inputSchema JSON.
        </div>
      </div>

      {/* Layer 2: Artifact Hash */}
      <div className="glass-panel" style={{ padding: '20px', borderLeft: '4px solid #10b981' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileCode size={16} color="#10b981" />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>LAYER 2 PIN</span>
          </div>
          <span className="badge badge-pass">ARTIFACT</span>
        </div>
        <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc', marginBottom: '6px' }}>
          Source Tree SHA-256
        </div>
        <pre className="code-box" style={{ fontSize: '0.7rem', color: '#34d399' }}>
          {selectedPin?.artifact_hash || 'Unpinned Baseline'}
        </pre>
        <div style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
          Source code fingerprint ensuring server files are authentic and unmodified.
        </div>
      </div>

      {/* Layer 3: Behavior Hash */}
      <div className="glass-panel" style={{ padding: '20px', borderLeft: '4px solid #f59e0b' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={16} color="#f59e0b" />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>LAYER 3 PIN</span>
          </div>
          <span className="badge badge-medium">BEHAVIOR</span>
        </div>
        <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc', marginBottom: '6px' }}>
          Runtime Profile SHA-256
        </div>
        <pre className="code-box" style={{ fontSize: '0.7rem', color: '#fbbf24' }}>
          {selectedPin?.behavior_hash || 'Unpinned Baseline'}
        </pre>
        <div style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
          Dynamic hash of observed filesystem paths, network destinations, and canary access.
        </div>
      </div>
    </div>
  );
}
