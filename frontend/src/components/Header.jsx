import React from 'react';
import { Shield, Play, Activity, Flame, Award } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, onQuickAudit, isAuditing, selectedTarget, setSelectedTarget, fixtures }) {
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

      {/* 3 Simple Judge-Friendly Tabs */}
      <nav style={{ display: 'flex', gap: '8px' }}>
        <button
          className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          <Activity size={15} />
          <span>1. How Engines Work (Audit)</span>
        </button>

        <button
          className={`tab-btn ${activeTab === 'watcher' ? 'active' : ''}`}
          onClick={() => setActiveTab('watcher')}
        >
          <Flame size={15} />
          <span>2. Live Rug-Pull Demo</span>
        </button>

        <button
          className={`tab-btn ${activeTab === 'scorecard' ? 'active' : ''}`}
          onClick={() => setActiveTab('scorecard')}
        >
          <Award size={15} />
          <span>3. 7-Server Scorecard (100%)</span>
        </button>
      </nav>

      {/* Target Selector & Run Button */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <select
          value={selectedTarget}
          onChange={(e) => setSelectedTarget(e.target.value)}
          style={{ padding: '6px 12px', fontSize: '0.82rem', fontWeight: 600 }}
        >
          {fixtures.map((fix) => (
            <option key={fix.id} value={fix.entrypoint || fix.name}>
              {fix.name} ({fix.expected_outcome})
            </option>
          ))}
        </select>

        <button
          className="btn btn-primary"
          onClick={() => onQuickAudit(selectedTarget)}
          disabled={isAuditing}
          style={{ padding: '6px 14px', fontSize: '0.82rem' }}
        >
          <Play size={14} fill="currentColor" />
          <span>{isAuditing ? 'Auditing...' : 'Run Audit'}</span>
        </button>
      </div>
    </header>
  );
}
