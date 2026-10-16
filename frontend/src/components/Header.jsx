import React from 'react';
import { Shield, Activity, Database, Cpu, Terminal, Eye, Award, Server } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, systemStatus, onQuickAudit, isAuditing }) {
  const dockerOnline = systemStatus?.docker?.daemon_running;
  const ollamaOnline = systemStatus?.ollama?.online;
  const pinsCount = systemStatus?.database?.pinned_servers_count ?? 0;

  return (
    <header className="header-nav">
      <div className="brand-badge">
        <div style={{
          background: 'linear-gradient(135deg, #0284c7, #06b6d4)',
          borderRadius: '10px',
          padding: '8px',
          display: 'flex',
          boxShadow: '0 0 15px rgba(6, 182, 212, 0.4)'
        }}>
          <Shield size={24} color="#ffffff" />
        </div>
        <div>
          <div className="brand-title">SHADOWPRINT</div>
          <div className="brand-subtitle">MCP Security Auditor • PS02</div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav style={{ display: 'flex', gap: '6px' }}>
        <button
          className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          <Activity size={16} />
          <span>Audit Scanner</span>
        </button>

        <button
          className={`tab-btn ${activeTab === 'diff' ? 'active' : ''}`}
          onClick={() => setActiveTab('diff')}
        >
          <Database size={16} />
          <span>S3 Baseline & Diff</span>
        </button>

        <button
          className={`tab-btn ${activeTab === 'watcher' ? 'active' : ''}`}
          onClick={() => setActiveTab('watcher')}
        >
          <Eye size={16} />
          <span>Rug-Pull Watcher</span>
        </button>

        <button
          className={`tab-btn ${activeTab === 'scorecard' ? 'active' : ''}`}
          onClick={() => setActiveTab('scorecard')}
        >
          <Award size={16} />
          <span>Scorecard (100%)</span>
        </button>

        <button
          className={`tab-btn ${activeTab === 'health' ? 'active' : ''}`}
          onClick={() => setActiveTab('health')}
        >
          <Server size={16} />
          <span>Engines & Docker</span>
        </button>
      </nav>

      {/* System Status Telemetry Pills */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div className="glass-card" style={{ padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem' }}>
          <span className={`pulse-dot ${dockerOnline ? 'green' : 'cyan'}`}></span>
          <span style={{ color: 'var(--text-secondary)' }}>Docker:</span>
          <strong style={{ color: dockerOnline ? '#34d399' : '#38bdf8' }}>
            {dockerOnline ? 'SANDBOX READY' : 'CONTAINER'}
          </strong>
        </div>

        <div className="glass-card" style={{ padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem' }}>
          <span className={`pulse-dot ${ollamaOnline ? 'green' : 'cyan'}`}></span>
          <span style={{ color: 'var(--text-secondary)' }}>Qwen3 AI:</span>
          <strong style={{ color: ollamaOnline ? '#34d399' : '#38bdf8' }}>
            {ollamaOnline ? 'LOCAL (11434)' : 'OFFLINE JUDGE'}
          </strong>
        </div>

        <button
          className="btn btn-primary"
          onClick={onQuickAudit}
          disabled={isAuditing}
          style={{ padding: '6px 16px', fontSize: '0.82rem' }}
        >
          <Terminal size={14} />
          <span>{isAuditing ? 'Auditing...' : 'Run Audit'}</span>
        </button>
      </div>
    </header>
  );
}
