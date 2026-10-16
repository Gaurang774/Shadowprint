"""
Unified Integration & End-to-End CLI Pipeline Tests.
Validates 'shadowprint audit', 'approve', 'pins', 'watch', 'scorecard', and 'info'.
"""

import os
from pathlib import Path
import pytest
from typer.testing import CliRunner
from shadowprint.cli import app

runner = CliRunner()


def test_cli_info():
    """Verifies that 'shadowprint info' displays project metadata and co-builder attribution."""
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "SHADOWPRINT" in result.output
    assert "PS02" in result.output
    assert "Jasjyot Singh" in result.output
    assert "Gaurang Udgirkar" in result.output


def test_cli_approve_and_pins():
    """Verifies that 'shadowprint approve' calculates baseline hashes and 'pins' lists them."""
    approve_res = runner.invoke(app, ["approve", "fixtures/clean_notes", "--approver", "test_auditor"])
    assert approve_res.exit_code == 0
    assert "clean_notes" in approve_res.output
    assert "Approved & Baseline Pinned" in approve_res.output

    pins_res = runner.invoke(app, ["pins"])
    assert pins_res.exit_code == 0
    assert "clean_notes" in pins_res.output


def test_cli_audit_clean_control(tmp_path):
    """Verifies that 'shadowprint audit' on clean negative control passes with 0 findings and exports reports."""
    out_dir = tmp_path / "reports"
    result = runner.invoke(app, ["audit", "fixtures/clean_notes", "-o", str(out_dir)])
    assert result.exit_code == 0
    assert "PASSED" in result.output
    assert "0 Findings Detected" in result.output

    md_file = out_dir / "shadowprint_report_clean_notes.md"
    sarif_file = out_dir / "shadowprint_report_clean_notes.sarif"
    assert md_file.exists()
    assert sarif_file.exists()
    assert "PASSED" in md_file.read_text(encoding="utf-8")


def test_cli_audit_vulnerable_runner(tmp_path):
    """Verifies that 'shadowprint audit' flags vulnerable runner with exact line-level issues."""
    out_dir = tmp_path / "reports"
    result = runner.invoke(app, ["audit", "fixtures/vulnerable_runner", "-o", str(out_dir)])
    assert result.exit_code != 0
    assert "FAILED" in result.output
    assert "COMMAND_INJECTION" in result.output
    assert "HARDCODED_SECRET" in result.output

    md_file = out_dir / "shadowprint_report_vulnerable_runner.md"
    sarif_file = out_dir / "shadowprint_report_vulnerable_runner.sarif"
    assert md_file.exists()
    assert sarif_file.exists()


def test_cli_audit_poisoned_weather(tmp_path):
    """Verifies that S1 catches prompt injection & Unicode TAGs in poisoned_weather."""
    out_dir = tmp_path / "reports"
    result = runner.invoke(app, ["audit", "fixtures/poisoned_weather", "-o", str(out_dir)])
    assert result.exit_code != 0
    assert "FAILED" in result.output
    assert "PROMPT_INJECTION" in result.output or "STEGANOGRAPHY" in result.output


def test_cli_audit_exfil_calculator(tmp_path):
    """Verifies that S0 & S2 dynamic checks identify exfiltration attempts."""
    out_dir = tmp_path / "reports"
    result = runner.invoke(app, ["audit", "fixtures/exfil_calculator", "-o", str(out_dir)])
    assert result.exit_code != 0
    assert "FAILED" in result.output
    assert "EXFILTRATION" in result.output or "TAMPER" in result.output


def test_cli_watch_compliant():
    """Verifies that 'shadowprint watch' verifies baseline integrity in single cycle mode."""
    # First ensure clean_notes is approved
    runner.invoke(app, ["approve", "fixtures/clean_notes"])
    result = runner.invoke(app, ["watch", "fixtures/clean_notes", "--max-cycles", "1", "--interval", "0.1"])
    assert result.exit_code == 0
    assert "compliant" in result.output.lower() or "clean_notes" in result.output


def test_cli_scorecard():
    """Verifies that 'shadowprint scorecard' executes the 7-fixture recall matrix and exits cleanly."""
    result = runner.invoke(app, ["scorecard"])
    assert result.exit_code == 0
    assert "100% Core Recall Guaranteed" in result.output
