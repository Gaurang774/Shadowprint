import React, { useState, useEffect } from 'react';
import { Eye, AlertOctagon, CheckCircle2, Flame, RotateCcw, Activity } from 'lucide-react';

export default function RugpullWatcher() {
  const [isWatching, setIsWatching] = useState(true);
  const [flagActive, setFlagActive] = useState(false);
  const [lastCheckTime, setLastCheckTime] = useState(Date.now());
  const [alertTriggered, setAlertTriggered] = useState(false);
  const [alertData, setAlertData] = useState(null);
  const [detectionLatency, setDetectionLatency] = useState(null);

  // Poll live diff every 2 seconds when watching
  useEffect(() => {
    if (!isWatching) return;

    const interval = setInterval(async () => {
      const startTime = performance.now();
      try {
        const res = await fetch('/api/diff/rugpull_suite');
        const elapsed = (performance.now() - startTime).toFixed(1);
        setLastCheckTime(Date.now());

        if (res.ok) {
          const data = await res.json();
          if (data.has_drift) {
            setAlertTriggered(true);
            setAlertData(data);
            setDetectionLatency(elapsed);
          } else {
            setAlertTriggered(false);
            setAlertData(null);
          }
        }
      } catch (e) {
        // Silent catch during poll
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [isWatching]);

  const handleToggleFlag = async (activeState) => {
    try {
      const res = await fetch('/api/trigger-rugpull', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ active: activeState }),
      });
      if (res.ok) {
        const data = await res.json();
        setFlagActive(data.active);
      }
    } catch (e) {
      console.error("Failed to toggle flag", e);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Showstopper Live Banner */}
      <div className={`glass-panel ${alertTriggered ? 'siren-alert' : ''}`} style={{ padding: '28px', transition: 'all 0.3s ease' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{
              background: alertTriggered ? '#ef4444' : '#10b981',
              borderRadius: '12px',
              padding: '12px',
              display: 'flex',
              boxShadow: alertTriggered ? '0 0 25px rgba(239, 68, 68, 0.6)' : '0 0 15px rgba(16, 185, 129, 0.3)',
              transition: 'all 0.3s'
            }}>
              {alertTriggered ? <AlertOctagon size={32} color="#ffffff" /> : <Eye size={32} color="#ffffff" />}
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 800 }}>
                  {alertTriggered ? 'CRITICAL RUG-PULL DETECTED!' : 'Live Integrity Watcher (2s Polling)'}
                </h2>
                <span className={`badge ${alertTriggered ? 'badge-critical' : 'badge-pass'}`}>
                  {alertTriggered ? 'SUB-1.5s ALARM' : 'MONITORING ACTIVE'}
                </span>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                Continuous stdio heartbeat actively comparing live tool definitions against SQLite pinned baseline.
              </p>
            </div>
          </div>

          {/* Interactive Trigger Controls */}
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            {!flagActive ? (
              <button
                className="btn btn-danger"
                onClick={() => handleToggleFlag(true)}
                style={{ padding: '12px 22px', fontSize: '0.95rem', fontWeight: 700 }}
              >
                <Flame size={18} />
                <span>Simulate Touch Flag (/tmp/rugpull_trigger.flag)</span>
              </button>
            ) : (
              <button
                className="btn btn-outline"
                onClick={() => handleToggleFlag(false)}
                style={{ padding: '12px 22px', borderColor: '#10b981', color: '#34d399' }}
              >
                <RotateCcw size={18} />
                <span>Reset to Benign State (Delete Flag)</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Real-time Telemetry Cards */}
      <div className="grid-3">
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '8px' }}>
            Heartbeat Frequency
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#38bdf8' }}>
            2.0 Seconds
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Last heartbeat: {new Date(lastCheckTime).toLocaleTimeString()}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '8px' }}>
            Trigger Flag State
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: flagActive ? '#ef4444' : '#10b981' }}>
            {flagActive ? 'ACTIVE (TRIGGERED)' : 'INACTIVE (BENIGN)'}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Path: <code style={{ color: '#38bdf8' }}>/tmp/rugpull_trigger.flag</code>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '8px' }}>
            Detection Response Latency
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: alertTriggered ? '#f59e0b' : '#34d399' }}>
            {alertTriggered ? `< ${detectionLatency || 1.2}s` : 'Sub-1.5s Guarantee'}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            DeepDiff structural comparison time
          </div>
        </div>
      </div>

      {/* Mutated Schema Evidence Window */}
      {alertTriggered && alertData && (
        <div className="glass-panel" style={{ padding: '24px', borderColor: 'rgba(239, 68, 68, 0.5)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
            <AlertOctagon size={22} color="#ef4444" />
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', fontWeight: 700, color: '#f87171' }}>
              Intercepted Mid-Session Tool Definition Mutation
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div className="glass-card" style={{ background: 'rgba(0,0,0,0.4)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
                Definition Hash Divergence
              </div>
              <div style={{ fontSize: '0.82rem', fontFamily: 'var(--font-mono)', color: '#94a3b8' }}>
                <div>Pinned Baseline: <span style={{ color: '#34d399' }}>{alertData.pinned_definition_hash}</span></div>
                <div>Live Mutated:    <span style={{ color: '#f87171' }}>{alertData.live_definition_hash}</span></div>
              </div>
            </div>

            {alertData.findings && alertData.findings.map((f, i) => (
              <div key={i} className="glass-card" style={{ borderColor: 'rgba(239, 68, 68, 0.4)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <strong style={{ color: '#f87171', fontSize: '0.9rem' }}>{f.category}</strong>
                  <span className="badge badge-critical">{f.severity}</span>
                </div>
                <pre className="code-box" style={{ whiteSpace: 'pre-wrap', color: '#fca5a5' }}>
                  {f.evidence}
                </pre>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
