/**
 * Shadowprint Centralized API Service Layer.
 * Decouples network communication and state management from presentation components.
 */

export const api = {
  // System status and health
  async getStatus() {
    const res = await fetch('/api/status');
    if (!res.ok) throw new Error('Failed to fetch status');
    return res.json();
  },

  // Fixtures manifest
  async getFixtures() {
    const res = await fetch('/api/fixtures');
    if (!res.ok) throw new Error('Failed to fetch fixtures');
    return res.json();
  },

  // Execute full audit
  async runAudit(target) {
    const res = await fetch('/api/audit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Audit execution failed');
    }
    return res.json();
  },

  // S3 Baseline Pins
  async getPins() {
    const res = await fetch('/api/pins');
    if (!res.ok) throw new Error('Failed to fetch pins');
    return res.json();
  },

  // S3 Baseline Approval
  async approveBaseline(target) {
    const res = await fetch('/api/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Approval failed');
    }
    return res.json();
  },

  // S3 Cryptographic Diff
  async getDiff(serverName) {
    const res = await fetch(`/api/diff/${serverName}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to compute diff');
    }
    return res.json();
  },

  // Rug-Pull simulation flag
  async toggleRugpullFlag(active) {
    const res = await fetch('/api/trigger-rugpull', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ active }),
    });
    if (!res.ok) throw new Error('Failed to toggle flag');
    return res.json();
  },

  // Benchmark Scorecard
  async getScorecard() {
    const res = await fetch('/api/scorecard');
    if (!res.ok) throw new Error('Failed to run scorecard');
    return res.json();
  },
};
