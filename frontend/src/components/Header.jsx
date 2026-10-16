import React from 'react';
import { Shield, Activity, Database, Eye, Award, Server } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, systemStatus, onQuickAudit, isAuditing }) {
  const dockerOnline = systemStatus?.docker?.daemon_running;
  const ollamaOnline = systemStatus?.ollama?.online;

  return (
    <header className="header-nav">
      <div className="brand-badge">
        <div style={{
          background: '#0f172a',
          borderRadius: '4px',
          padding: '6px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <Shield size={18} color="#ffffff" />
        </div>
        <div>
          <div className="brand-title">SHADOWPRINT</div>
          <div className="brand-subtitle">MCP Security Auditor • PS02</div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav style={{ display: 'flex', gap: '4px' }}>
        <button
          className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          <Activity size={15} />
          <span>Audit Scanner</span>
        </button>

        <button
          className={`tab-btn ${activeTab === 'diff' ? 'active' : ''}`}
          onClick={() => setActiveTab('diff')}
        >
          <Database size={15} />
          <span>S3 Baseline & Diff</span>
        </button>

        <button
          className={`tab-btn ${activeTab === 'watcher' ? 'active' : ''}`}
          onClick={() => setActiveTab('watcher')}
        >
          <Eye size={15} />
          <span>Rug-Pull Watcher</span>
        </button>

        <button
          className={`tab-btn ${activeTab === 'scorecard' ? 'active' : ''}`}
          onClick={() => setActiveTab('scorecard')}
        >
          <Award size={15} />
          <span>Scorecard (100%)</span>
        </button>

        <button
          className={`tab-btn ${activeTab === 'health' ? 'active' : ''}`}
          onClick={() => setActiveTab('health')}
        >
          <Server size={15} />
          <span>Engines & Docker</span>
        </button>
      </nav>

      {/* Clean Status Pills */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div className="glass-card" style={{ padding: '4px 10px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem' }}>
          <span className={`pulse-dot ${dockerOnline ? 'green' : 'cyan'}`}></span>
          <span style={{ color: 'var(--text-secondary)' }}>Docker:</span>
          <strong style={{ color: dockerOnline ? '#15803d' : '#0f172a' }}>
            {dockerOnline ? 'ONLINE' : 'HOST'}
          </strong>
        </div>

        <div className="glass-card" style={{ padding: '4px 10px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem' }}>
          <span className={`pulse-dot ${ollamaOnline ? 'green' : 'cyan'}`}></span>
          <span style={{ color: 'var(--text-secondary)' }}>Qwen3 AI:</span>
          <strong style={{ color: ollamaOnline ? '#15803d' : '#0f172a' }}>
            {ollamaOnline ? 'LOCAL' : 'OFFLINE'}
          </strong>
        </div>

        <button
          className="btn btn-primary"
          onClick={onQuickAudit}
          disabled={isAuditing}
          style={{ padding: '6px 14px', fontSize: '0.82rem' }}
        >
          <span>{isAuditing ? 'Auditing...' : 'Run Audit'}</span>
        </button>
      </div>
    </header>
  );
}
