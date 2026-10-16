import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import BaselineDiffViewer from './features/diff/BaselineDiffViewer';
import AuditScanner from './features/scanner/AuditScanner';
import RugpullWatcher from './features/watcher/RugpullWatcher';
import ScorecardMatrix from './features/scorecard/ScorecardMatrix';
import SystemHealth from './features/telemetry/SystemHealth';
import { api } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('diff');
  const [systemStatus, setSystemStatus] = useState(null);
  const [fixtures, setFixtures] = useState([]);
  const [selectedTarget, setSelectedTarget] = useState('fixtures/rugpull_suite');
  const [auditReport, setAuditReport] = useState(null);
  const [isAuditing, setIsAuditing] = useState(false);

  // Fetch initial system status & fixtures
  useEffect(() => {
    const initData = async () => {
      try {
        const [statusRes, fixturesRes] = await Promise.all([
          fetch('/api/status'),
          fetch('/api/fixtures'),
        ]);

        if (statusRes.ok) {
          const statusData = await statusRes.json();
          setSystemStatus(statusData);
        }

        if (fixturesRes.ok) {
          const fixturesData = await fixturesRes.json();
          setFixtures(fixturesData);
          if (fixturesData.length > 0) {
            setSelectedTarget(fixturesData[0].entrypoint || fixturesData[0].name);
          }
        }
      } catch (e) {
        console.error("Failed to load initial system status", e);
      }
    };

    initData();
  }, []);

  // Run audit against a target
  const handleRunAudit = async (targetPath) => {
    const target = targetPath || selectedTarget;
    if (!target) return;

    setIsAuditing(true);
    try {
      const res = await fetch('/api/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target }),
      });

      if (res.ok) {
        const report = await res.json();
        setAuditReport(report);
      } else {
        const err = await res.json();
        alert(`Audit failed: ${err.detail || 'Unknown error'}`);
      }
    } catch (e) {
      console.error("Audit call failed", e);
    } finally {
      setIsAuditing(false);
    }
  };

  // Run quick audit on current target
  const handleQuickAudit = () => {
    setActiveTab('audit');
    handleRunAudit(selectedTarget);
  };

  return (
    <div>
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemStatus={systemStatus}
        onQuickAudit={handleQuickAudit}
        isAuditing={isAuditing}
      />

      <main className="main-container">
        {activeTab === 'audit' && (
          <AuditScanner
            fixtures={fixtures}
            selectedTarget={selectedTarget}
            setSelectedTarget={setSelectedTarget}
            auditReport={auditReport}
            isAuditing={isAuditing}
            onRunAudit={handleRunAudit}
          />
        )}

        {activeTab === 'diff' && (
          <BaselineDiffViewer fixtures={fixtures} />
        )}

        {activeTab === 'watcher' && (
          <RugpullWatcher />
        )}

        {activeTab === 'scorecard' && (
          <ScorecardMatrix />
        )}

        {activeTab === 'health' && (
          <SystemHealth systemStatus={systemStatus} />
        )}
      </main>
    </div>
  );
}
