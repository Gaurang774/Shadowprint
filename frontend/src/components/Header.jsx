import React from 'react';
import { Shield, Activity, Database, Eye, Award, Server } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, systemStatus, onQuickAudit, isAuditing }) {
  const dockerOnline = systemStatus?.docker?.daemon_running;
  const ollamaOnline = systemStatus?.ollama?.online;

  return (
    <header className="header-nav">
      <div className="brand-badge">
        <div style={{
          background: '#2563eb',
          borderRadius: '6px',
          padding: '6px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <Shield size={20} color="#ffffff" />
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

      {/* System Status Pills */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div className="glass-card" style={{ padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem' }}>
          <span className={`pulse-dot ${dockerOnline ? 'green' : 'cyan'}`}></span>
          <span style={{ color: 'var(--text-secondary)' }}>Docker:</span>
          <strong style={{ color: dockerOnline ? '#34d399' : '#60a5fa' }}>
            {dockerOnline ? 'SANDBOX READY' : 'CONTAINER'}
          </strong>
        </div>

        <div className="glass-card" style={{ padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem' }}>
          <span className={`pulse-dot ${ollamaOnline ? 'green' : 'cyan'}`}></span>
          <span style={{ color: 'var(--text-secondary)' }}>Qwen3 AI:</span>
          <strong style={{ color: ollamaOnline ? '#34d399' : '#60a5fa' }}>
            {ollamaOnline ? 'LOCAL (11434)' : 'OFFLINE JUDGE'}
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
