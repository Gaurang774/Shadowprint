"""
Shadowprint S3 Integrity Engine: Live Rug-Pull Watcher Loop.
Owner: Gaurang Udgirkar [G]

Monitors running MCP servers in real-time with a 2-second polling loop.
Detects definition mutation, tool poisoning, and source code tampering:
  - Verifies live definition_hash against SQLite pinned baseline.
  - Triggers sub-1.5s red alert upon schema mutation (e.g., /tmp/rugpull_trigger.flag).
  - Emits confirmed Finding models with visible character diffs.
"""

import time
import asyncio
import logging
from pathlib import Path
from typing import List, Callable, Optional, Dict, Any

from shadowprint.models import Finding, Snapshot, Pin
from shadowprint.client.mcp_client import GuardedMCPClient
from shadowprint.s3_integrity.db import PinDatabase
from shadowprint.s3_integrity.differ import IntegrityDiffer
from shadowprint.s3_integrity.hasher import ThreeLayerHasher

logger = logging.getLogger("shadowprint.s3_integrity.watcher")


class LiveWatcher:
    """Continuously watches target MCP servers for live definition drift and rug-pulls."""

    def __init__(
        self,
        server_name: str,
        client: GuardedMCPClient,
        db: Optional[PinDatabase] = None,
        target_dir: Optional[Path] = None,
        poll_interval: float = 2.0,
        on_drift: Optional[Callable[[List[Finding]], None]] = None,
    ):
        self.server_name = server_name
        self.client = client
        self.db = db or PinDatabase()
        self.target_dir = target_dir
        self.poll_interval = poll_interval
        self.on_drift = on_drift
        self.differ = IntegrityDiffer(server_name)
        self._is_running = False

    async def check_once(self) -> List[Finding]:
        """
        Executes a single check cycle against the pinned baseline.
        Returns a list of drift Finding models (empty if server is intact).
        """
        findings: List[Finding] = []

        # 1. Retrieve pinned baseline
        pin = self.db.get_pin(self.server_name)
        if not pin:
            logger.warning(f"No approved baseline pin found in database for '{self.server_name}'")
            return findings

        pinned_snapshot = self.db.get_pin_snapshot(self.server_name)
        if not pinned_snapshot:
            return findings

        # 2. Fetch live snapshot from target server
        try:
            live_snapshot = await self.client.fetch_snapshot(self.server_name)
        except Exception as e:
            logger.error(f"Failed to fetch live snapshot from '{self.server_name}': {e}")
            return findings

        # 3. Check definition hash drift (Layer 1)
        if live_snapshot.definition_hash != pin.definition_hash:
            def_findings = self.differ.compare_snapshots(pinned_snapshot, live_snapshot)
            findings.extend(def_findings)

        # 4. Check artifact hash drift (Layer 2) if target directory is provided
        if self.target_dir and self.target_dir.exists():
            live_artifact_hash = ThreeLayerHasher.compute_artifact_hash(self.target_dir)
            if live_artifact_hash != pin.artifact_hash:
                art_findings = self.differ.compare_artifacts(pin.artifact_hash, live_artifact_hash)
                findings.extend(art_findings)

        return findings

    async def watch_loop(self, max_iterations: Optional[int] = None) -> List[Finding]:
        """
        Runs the live monitoring loop every poll_interval seconds.
        Calls on_drift callback immediately when drift is detected.
        """
        self._is_running = True
        iterations = 0
        all_drift_findings: List[Finding] = []

        logger.info(f"Starting live watcher on '{self.server_name}' (interval={self.poll_interval}s)")

        while self._is_running:
            start_time = time.time()
            drift_findings = await self.check_once()

            if drift_findings:
                elapsed = time.time() - start_time
                logger.critical(f"RUG-PULL DETECTED on '{self.server_name}' in {elapsed:.3f}s!")
                all_drift_findings.extend(drift_findings)

                if self.on_drift:
                    self.on_drift(drift_findings)

            iterations += 1
            if max_iterations and iterations >= max_iterations:
                break

            await asyncio.sleep(self.poll_interval)

        return all_drift_findings

    def stop(self) -> None:
        """Stops the live watcher loop."""
        self._is_running = False
