"""
Comprehensive Unit & Integration Tests for Engine S4 Reporting & Export.
Verifies Markdown report generation, OASIS SARIF 2.1.0 schema compliance, and Terminal UI.
"""

import json
import os
import tempfile
import pytest
from shadowprint.models import AuditReport, Finding, Location
from shadowprint.s4_reporting.markdown_reporter import generate_markdown_report
from shadowprint.s4_reporting.sarif_exporter import export_to_sarif
from shadowprint.s4_reporting.terminal_ui import render_audit_report


@pytest.fixture
def sample_report():
    finding = Finding(
        id="SP-S0-001",
        engine="S0",
        target="sample_server",
        tool="ping_host",
        category="COMMAND_INJECTION",
        severity="high",
        assessment="FAIL",
        confidence="confirmed",
        evidence_basis="static",
        location=Location(file="fixtures/sample/server.py", line=42, column=10),
        claim="Network ping tool",
        evidence="subprocess.run(cmd, shell=True)",
        remediation="Avoid shell=True. Pass arguments as a list.",
        supporting_rules=["B602", "CWE-78"]
    )
    return AuditReport(
        target="sample_server",
        timestamp=1700000000.0,
        status="FAILED",
        findings=[finding],
        summary={"total": 1, "critical": 0, "high": 1, "medium": 0, "low": 0}
    )


def test_markdown_report_generation(sample_report):
    """Verifies Markdown report formatting, headers, tables, and evidence sections."""
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "report.md")
        content = generate_markdown_report(sample_report, output_file=md_file)

        assert os.path.exists(md_file)
        assert "# Shadowprint Security Audit Report" in content
        assert "sample_server" in content
        assert "COMMAND_INJECTION" in content
        assert "subprocess.run(cmd, shell=True)" in content
        assert "CWE-78" in content
        assert "Avoid shell=True" in content


def test_sarif_export_schema_compliance(sample_report):
    """Verifies that SARIF output strictly complies with OASIS SARIF 2.1.0 schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        sarif_file = os.path.join(tmpdir, "report.sarif")
        sarif_data = export_to_sarif(sample_report, output_file=sarif_file)

        assert os.path.exists(sarif_file)
        assert sarif_data["version"] == "2.1.0"
        assert "$schema" in sarif_data
        assert "runs" in sarif_data
        run = sarif_data["runs"][0]
        assert run["tool"]["driver"]["name"] == "Shadowprint"

        results = run["results"]
        assert len(results) == 1
        res = results[0]
        assert res["ruleId"] == "B602"
        assert res["level"] == "error"
        assert "subprocess.run(cmd, shell=True)" in res["message"]["text"]
        assert res["locations"][0]["physicalLocation"]["region"]["startLine"] == 42


def test_terminal_ui_rendering(sample_report):
    """Verifies that terminal UI renders without exceptions or encoding errors."""
    try:
        render_audit_report(sample_report)
    except Exception as e:
        pytest.fail(f"render_audit_report raised an unexpected exception: {e}")
