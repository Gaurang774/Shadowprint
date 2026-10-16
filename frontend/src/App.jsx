import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SimpleEngineDashboard from './features/simple_audit/SimpleEngineDashboard';
import RugpullWatcher from './features/watcher/RugpullWatcher';
import ScorecardMatrix from './features/scorecard/ScorecardMatrix';
import { api } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('audit');
  const [fixtures, setFixtures] = useState([]);
  const [selectedTarget, setSelectedTarget] = useState('fixtures/poisoned_weather');
  const [auditReport, setAuditReport] = useState(null);
  const [isAuditing, setIsAuditing] = useState(false);

  // Load fixtures and auto-run initial audit on poisoned_weather
  useEffect(() => {
    const initData = async () => {
      try {
        const fixturesData = await api.getFixtures();
        setFixtures(fixturesData);
        if (fixturesData.length > 0) {
          const initial = fixturesData.find(f => f.name === 'poisoned_weather') || fixturesData[0];
          const initialPath = initial.entrypoint || initial.name;
          setSelectedTarget(initialPath);
          handleRunAudit(initialPath);
        }
      } catch (e) {
        console.error("Failed to load fixtures", e);
      }
    };

    initData();
  }, []);

  const handleRunAudit = async (targetPath) => {
    const target = targetPath || selectedTarget;
    if (!target) return;

    setIsAuditing(true);
    try {
      const report = await api.runAudit(target);
      setAuditReport(report);
    } catch (e) {
      console.error("Audit call failed", e);
    } finally {
      setIsAuditing(false);
    }
  };

  return (
    <div>
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onQuickAudit={handleRunAudit}
        isAuditing={isAuditing}
        selectedTarget={selectedTarget}
        setSelectedTarget={(val) => {
          setSelectedTarget(val);
          handleRunAudit(val);
        }}
        fixtures={fixtures}
      />

      <main className="main-container">
        {activeTab === 'audit' && (
          <SimpleEngineDashboard
            auditReport={auditReport}
            isAuditing={isAuditing}
            selectedTarget={selectedTarget}
          />
        )}

        {activeTab === 'watcher' && (
          <RugpullWatcher />
        )}

        {activeTab === 'scorecard' && (
          <ScorecardMatrix />
        )}
      </main>
    </div>
  );
}
