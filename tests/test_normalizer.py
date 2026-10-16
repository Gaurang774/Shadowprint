"""
Unit tests for shadowprint.normalizer (Clustered Deduplication).
"""

import pytest
from shadowprint.models import Finding, Location
from shadowprint.normalizer import normalize_findings


def test_empty_findings():
    assert normalize_findings([]) == []


def test_no_duplicates():
    f1 = Finding(
        id="SP-S0-001",
        engine="S0",
        target="fixtures/vulnerable_runner",
        tool="ping_host",
        category="COMMAND_INJECTION",
        severity="high",
        assessment="FAIL",
        confidence="confirmed",
        evidence_basis="static",
        location=Location(file="fixtures/vulnerable_runner/server.py", line=32),
        evidence="subprocess.run(cmd, shell=True)",
        remediation="Avoid shell=True"
    )
    result = normalize_findings([f1])
    assert len(result) == 1
    assert result[0].id == "SP-S0-001"


def test_deduplication_cluster():
    # Two findings within line // 3 window (line 31 and line 32)
    f1 = Finding(
        id="SP-S0-001",
        engine="S0",
        target="fixtures/vulnerable_runner",
        tool="ping_host",
        category="COMMAND_INJECTION",
        severity="medium",
        assessment="FLAGGED",
        confidence="heuristic",
        evidence_basis="static",
        location=Location(file="fixtures/vulnerable_runner/server.py", line=31),
        evidence="subprocess.run",
        remediation="Avoid shell=True",
        supporting_rules=["B404"]
    )
    f2 = Finding(
        id="SP-S0-002",
        engine="S0",
        target="fixtures/vulnerable_runner",
        tool="ping_host",
        category="COMMAND_INJECTION",
        severity="high",
        assessment="FAIL",
        confidence="heuristic",
        evidence_basis="static",
        location=Location(file="fixtures/vulnerable_runner/server.py", line=32),
        evidence="subprocess.run(cmd, shell=True, capture_output=True)",
        remediation="Avoid shell=True and pass command arguments as a list.",
        supporting_rules=["B602"]
    )

    merged = normalize_findings([f1, f2])
    assert len(merged) == 1
    # Severity elevated to high
    assert merged[0].severity == "high"
    # Assessment elevated to FAIL
    assert merged[0].assessment == "FAIL"
    # Confidence elevated to corroborated (2 rules)
    assert merged[0].confidence == "corroborated"
    # Rules merged
    assert "B404" in merged[0].supporting_rules
    assert "B602" in merged[0].supporting_rules
    # Best evidence selected
    assert "capture_output=True" in merged[0].evidence
