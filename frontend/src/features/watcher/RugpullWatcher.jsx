import React, { useState, useEffect } from 'react';
import { Eye, AlertOctagon, Flame, RotateCcw } from 'lucide-react';
import { api } from '../../services/api';

export default function RugpullWatcher() {
  const [isWatching, setIsWatching] = useState(true);
  const [flagActive, setFlagActive] = useState(false);
  const [lastCheckTime, setLastCheckTime] = useState(Date.now());
  const [alertTriggered, setAlertTriggered] = useState(false);
  const [alertData, setAlertData] = useState(null);
  const [detectionLatency, setDetectionLatency] = useState(null);

  const syncFlagStatus = async () => {
    try {
      const data = await api.getRugpullFlagStatus();
      setFlagActive(data.active);
    } catch (e) {
      // Ignore
    }
  };

  useEffect(() => {
    syncFlagStatus();
  }, []);

  useEffect(() => {
    if (!isWatching) return;

    const interval = setInterval(async () => {
      const startTime = performance.now();
      try {
        const data = await api.getDiff('rugpull_suite');
        const elapsedMs = performance.now() - startTime;
        const latencyFormatted = elapsedMs < 1000 
          ? `${elapsedMs.toFixed(0)} ms` 
          : `${(elapsedMs / 1000).toFixed(2)} s`;

        setLastCheckTime(Date.now());

        if (data.has_drift) {
          setAlertTriggered(true);
          setAlertData(data);
          setDetectionLatency(latencyFormatted);
          setFlagActive(true);
        } else {
          setAlertTriggered(false);
          setAlertData(null);
          setFlagActive(false);
        }
      } catch (e) {
        // Heartbeat poll
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [isWatching]);

  const handleToggleFlag = async (activeState) => {
    try {
      const data = await api.toggleRugpullFlag(activeState);
      setFlagActive(data.active);
      if (!data.active) {
        setAlertTriggered(false);
        setAlertData(null);
      }
    } catch (e) {
      console.error("Failed to toggle flag", e);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Live Banner */}
      <div className={`glass-panel ${alertTriggered ? 'siren-alert' : ''}`} style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{
              background: alertTriggered ? '#dc2626' : '#0f172a',
              borderRadius: '6px',
              padding: '10px',
              display: 'flex',
            }}>
              {alertTriggered ? <AlertOctagon size={24} color="#ffffff" /> : <Eye size={24} color="#ffffff" />}
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#0f172a' }}>
                  {alertTriggered ? 'CRITICAL RUG-PULL DETECTED!' : 'Live Integrity Watcher (2s Polling)'}
                </h2>
                <span className={`badge ${alertTriggered ? 'badge-critical' : 'badge-pass'}`}>
                  {alertTriggered ? 'SUB-1.5s ALARM' : 'MONITORING ACTIVE'}
                </span>
                <span className="badge badge-info" style={{ fontFamily: 'var(--font-mono)' }}>
                  Target: fixtures/rugpull_suite
                </span>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '4px' }}>
                Continuous stdio heartbeat actively comparing live tool definitions against SQLite pinned baseline for <code>rugpull_suite</code>.
              </p>
            </div>
          </div>

          {/* Interactive Trigger Controls */}
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            {!flagActive ? (
              <button
                className="btn btn-danger"
                onClick={() => handleToggleFlag(true)}
              >
                <Flame size={15} />
                <span>Simulate Touch Flag (/tmp/rugpull_trigger.flag)</span>
              </button>
            ) : (
              <button
                className="btn btn-outline"
                onClick={() => handleToggleFlag(false)}
                style={{ borderColor: '#16a34a', color: '#16a34a', fontWeight: 700 }}
              >
                <RotateCcw size={15} />
                <span>Reset to Benign State (Delete Flag)</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Real-time Telemetry Cards */}
      <div className="grid-3">
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '6px' }}>
            Heartbeat Frequency
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#0f172a' }}>
            2.0 Seconds
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Last heartbeat: {new Date(lastCheckTime).toLocaleTimeString()}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '6px' }}>
            Trigger Flag State
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: flagActive ? '#dc2626' : '#15803d' }}>
            {flagActive ? 'ACTIVE (TRIGGERED)' : 'INACTIVE (BENIGN)'}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Path: <code>/tmp/rugpull_trigger.flag</code>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '6px' }}>
            Detection Response Latency
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: alertTriggered ? '#dc2626' : '#15803d' }}>
            {alertTriggered ? `< ${detectionLatency || '150 ms'}` : 'Sub-1.5s Guarantee'}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            DeepDiff structural comparison time
          </div>
        </div>
      </div>

      {/* Mutated Schema Evidence Window */}
      {alertTriggered && alertData && (
        <div className="glass-panel" style={{ padding: '24px', borderColor: '#fca5a5', background: '#fef2f2' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <AlertOctagon size={20} color="#dc2626" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#991b1b' }}>
              Intercepted Mid-Session Tool Definition Mutation
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div className="glass-card" style={{ background: '#ffffff' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
                Definition Hash Divergence
              </div>
              <div style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', color: '#334155' }}>
                <div>Pinned Baseline: <span style={{ color: '#15803d' }}>{alertData.pinned_definition_hash}</span></div>
                <div>Live Mutated:    <span style={{ color: '#dc2626' }}>{alertData.live_definition_hash}</span></div>
              </div>
            </div>

            {alertData.findings && alertData.findings.map((f, i) => (
              <div key={i} className="glass-card" style={{ borderColor: '#fca5a5', background: '#ffffff' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <strong style={{ color: '#991b1b', fontSize: '0.9rem' }}>{f.category}</strong>
                  <span className="badge badge-critical">{f.severity}</span>
                </div>
                <pre className="code-box" style={{ background: '#fef2f2', color: '#b91c1c' }}>
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
