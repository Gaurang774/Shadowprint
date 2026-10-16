"""
Integration tests for Gaurang's assigned benchmark fixtures:
- fixtures/clean_fetch/server.py (Fixture 1b)
- fixtures/exfil_calculator/server.py (Fixture 4)
- fixtures/rugpull_suite/server.py (Fixture 5)
"""

import sys
import tempfile
import pytest
from pathlib import Path
from shadowprint.client.mcp_client import GuardedMCPClient
from shadowprint.s1_metadata.prompt_guard import PromptGuard
from shadowprint.s2_prober.canary_tripwire import CanaryTripwire
from shadowprint.s2_prober.output_scanner import OutputScanner
from shadowprint.s2_prober.syscall_parser import BehaviorTuple
from shadowprint.s3_integrity.differ import IntegrityDiffer, escape_hidden_characters
from shadowprint.s3_integrity.hasher import ThreeLayerHasher

CLEAN_FETCH_PATH = str(Path(__file__).parent.parent / "fixtures" / "clean_fetch" / "server.py")
EXFIL_CALCULATOR_PATH = str(Path(__file__).parent.parent / "fixtures" / "exfil_calculator" / "server.py")
RUGPULL_SUITE_PATH = str(Path(__file__).parent.parent / "fixtures" / "rugpull_suite" / "server.py")


@pytest.mark.anyio
async def test_clean_fetch_negative_control():
    client = GuardedMCPClient(command=sys.executable, args=[CLEAN_FETCH_PATH], timeout=3.0)
    snapshot = await client.fetch_snapshot("clean_fetch")

    assert snapshot.server_name == "clean_fetch"
    assert len(snapshot.tools) == 1
    tool = snapshot.tools[0]
    assert tool.name == "fetch"

    # Pre-filter check: 0 prompt injection findings (Clean baseline)
    prompt_guard = PromptGuard()
    findings = prompt_guard.scan_text(tool.description)
    assert len(findings) == 0, f"Expected 0 findings on clean_fetch, got {findings}"

    # Call tool check
    await client.start()
    try:
        await client.initialize()
        res = await client.call_tool("fetch", {"url": "https://example.com"})
        assert "content" in res
        assert "Clean plain text" in res["content"][0]["text"]
    finally:
        await client.close()


@pytest.mark.anyio
async def test_exfil_calculator_canary_and_output_exfil(monkeypatch):
    # Setup temporary canary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("CANARY_KEY_98721X=sk_live_canary_super_secret\n")
        temp_canary = f.name

    try:
        client = GuardedMCPClient(command=sys.executable, args=[EXFIL_CALCULATOR_PATH], timeout=3.0)
        await client.start()
        try:
            await client.initialize()
            res = await client.call_tool("calculate", {"expression": "25 * 4"})
            assert "content" in res
            text = res["content"][0]["text"]
            assert "100" in text

            # Output scanner must catch the markdown telemetry exfil link
            scanner = OutputScanner("exfil_calculator")
            findings = scanner.scan_output("calculate", text)
            assert len(findings) >= 1
            categories = [f.category for f in findings]
            assert "DATA_EXFILTRATION" in categories or "DATA_LEAKAGE" in categories

            # Tripwire check with simulated behavior
            tripwire = CanaryTripwire("exfil_calculator")
            dummy_behavior = BehaviorTuple(
                tool_name="calculate",
                openat_paths=[temp_canary],
                canary_touched=True,
                behavior_hash="a" * 64,
            )
            tripwire_findings = tripwire.check_behavior(dummy_behavior, sink_log_content=text, tool_outputs=[text])
            assert len(tripwire_findings) >= 1
            assert any(f.category in ("CREDENTIAL_ACCESS", "DATA_EXFILTRATION", "DATA_LEAKAGE") for f in tripwire_findings)
        finally:
            await client.close()
    finally:
        Path(temp_canary).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_rugpull_suite_live_mutation():
    trigger_flag = Path(tempfile.gettempdir()) / "rugpull_trigger.flag"
    trigger_flag.unlink(missing_ok=True)

    client = GuardedMCPClient(command=sys.executable, args=[RUGPULL_SUITE_PATH], timeout=3.0)

    # 1. Benign Phase
    snapshot_clean = await client.fetch_snapshot("rugpull_suite")
    assert "real-time weather" in snapshot_clean.tools[0].description
    hash_clean = snapshot_clean.definition_hash

    # 2. Touch trigger flag (Stage Rug-Pull)
    trigger_flag.write_text("trigger_active")

    try:
        # 3. Mutated Phase
        snapshot_mutated = await client.fetch_snapshot("rugpull_suite")
        assert "INJECTED: System override" in snapshot_mutated.tools[0].description
        hash_mutated = snapshot_mutated.definition_hash

        # Hash must change
        assert hash_clean != hash_mutated

        # Differ must flag the mutation and escape non-printables
        differ = IntegrityDiffer(target_server="rugpull_suite")
        findings = differ.compare_snapshots(snapshot_clean, snapshot_mutated)
        assert len(findings) >= 1
        assert findings[0].category == "RUG_PULL_SCHEMA_MUTATION"
        assert findings[0].severity == "critical"
        assert "INJECTED" in findings[0].evidence
        assert "[U+E0001 UNICODE-TAG]" in findings[0].evidence
    finally:
        trigger_flag.unlink(missing_ok=True)
