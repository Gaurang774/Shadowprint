"""
Comprehensive Unit & Integration Tests for Engine S0 Static Analysis.
Verifies Bandit, Semgrep, Gitleaks, Claim-Code Checker, and Hostile Suppression.
"""

import pytest
import os
from shadowprint.s0_static.bandit_runner import run_bandit
from shadowprint.s0_static.semgrep_runner import run_semgrep
from shadowprint.s0_static.gitleaks_runner import run_gitleaks
from shadowprint.s0_static.claim_code_checker import run_claim_checker
from shadowprint.s0_static.scanner import scan_static, check_hostile_suppressions


def test_clean_notes_zero_findings():
    """Negative Control Test: Clean server must produce 0 findings across all S0 runners."""
    target = "fixtures/clean_notes"
    assert run_bandit(target) == []
    assert run_semgrep(target) == []
    assert run_gitleaks(target) == []
    assert run_claim_checker(target) == []
    assert check_hostile_suppressions(target, "clean_notes") == []
    assert scan_static(target, "clean_notes") == []


def test_vulnerable_runner_bandit_findings():
    """Verifies Bandit catches command injection, pickle deserialization, and tmp file."""
    findings = run_bandit("fixtures/vulnerable_runner")
    categories = {f.category for f in findings}
    assert "COMMAND_INJECTION" in categories
    assert "INSECURE_DESERIALIZATION" in categories
    assert "SSRF_UNSAFE_FETCH" in categories


def test_vulnerable_runner_gitleaks():
    """Verifies Gitleaks catches the hardcoded AWS secret key."""
    findings = run_gitleaks("fixtures/vulnerable_runner")
    assert len(findings) >= 1
    assert any(f.category == "HARDCODED_SECRET" and "AWS" in f.evidence for f in findings)


def test_vulnerable_runner_claim_vs_code():
    """Verifies AST parser catches destructive call os.remove in 'read-only' declared tool."""
    findings = run_claim_checker("fixtures/vulnerable_runner")
    assert len(findings) == 1
    assert findings[0].category == "CLAIM_CODE_MISMATCH"
    assert findings[0].tool == "inspect_logs"
    assert "os.remove" in findings[0].evidence


def test_attack_the_auditor_hostile_suppression():
    """Verifies that hostile #nosec and #nosemgrep comments are flagged as TAMPER_ATTEMPT."""
    findings = check_hostile_suppressions("fixtures/attack_the_auditor", "attack_the_auditor")
    assert len(findings) >= 1
    assert all(f.category == "TAMPER_ATTEMPT" for f in findings)
    assert any("# nosec" in f.evidence for f in findings)


def test_scan_static_orchestration_and_deduplication():
    """Verifies that scan_static coordinates all runners and normalizes findings."""
    findings = scan_static("fixtures/vulnerable_runner", "vulnerable_runner")
    assert len(findings) > 0
    # Findings must be sorted with critical/high first
    severities = [f.severity for f in findings]
    assert severities[0] in ("critical", "high")
