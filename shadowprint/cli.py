"""
Shadowprint CLI Orchestrator.
Command-line interface for auditing MCP servers, inspecting metadata,
and generating multi-format security reports.
"""

import os
import sys
import time
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel

from shadowprint.models import AuditReport, Finding
from shadowprint.normalizer import normalize_findings
from shadowprint.s0_static.scanner import scan_static
from shadowprint.s1_metadata.analyzer import analyze_metadata
from shadowprint.s4_reporting.terminal_ui import render_audit_report, render_banner
from shadowprint.s4_reporting.markdown_reporter import generate_markdown_report
from shadowprint.s4_reporting.sarif_exporter import export_to_sarif

app = typer.Typer(
    name="shadowprint",
    help="Shadowprint — Model Context Protocol Security Auditor",
    add_completion=False
)
console = Console()


@app.command(name="audit")
def audit(
    target: str = typer.Argument(..., help="Path to MCP server directory or script"),
    output_dir: str = typer.Option("output", "--output-dir", "-o", help="Directory for exported reports"),
    skip_static: bool = typer.Option(False, "--skip-static", help="Skip Engine S0 static analysis"),
    skip_metadata: bool = typer.Option(False, "--skip-metadata", help="Skip Engine S1 metadata inspection"),
):
    """
    Run an end-to-end security audit against a target MCP server.
    """
    target_path = os.path.abspath(target)
    if not os.path.exists(target_path):
        console.print(f"[bold red]Error:[/bold red] Target path '{target}' does not exist.")
        raise typer.Exit(code=1)

    server_name = os.path.basename(os.path.normpath(target_path))
    start_time = time.time()
    all_findings: list[Finding] = []

    # 1. Engine S0: Static Code & Config Analysis
    if not skip_static:
        with console.status(f"[bold cyan]Running Engine S0 (Static Code Inspection)...[/bold cyan]"):
            s0_findings = scan_static(target_path, server_name)
            all_findings.extend(s0_findings)

    # 2. Engine S1: Metadata & Prompt Injection Analysis
    if not skip_metadata:
        with console.status(f"[bold cyan]Running Engine S1 (Sandboxed Metadata Inspection)...[/bold cyan]"):
            s1_findings = analyze_metadata(target_path=target_path, server_name=server_name)
            all_findings.extend(s1_findings)

    # 3. Deduplicate and normalize
    merged_findings = normalize_findings(all_findings)

    # 4. Compute overall status
    if any(f.assessment == "FAIL" or f.severity in ("critical", "high") for f in merged_findings):
        status = "FAILED"
    elif any(f.assessment == "FLAGGED" or f.severity == "medium" for f in merged_findings):
        status = "FLAGGED"
    else:
        status = "PASSED"

    # Build AuditReport
    report = AuditReport(
        target=server_name,
        timestamp=start_time,
        status=status,
        findings=merged_findings,
        summary={
            "total": len(merged_findings),
            "critical": sum(1 for f in merged_findings if f.severity == "critical"),
            "high": sum(1 for f in merged_findings if f.severity == "high"),
            "medium": sum(1 for f in merged_findings if f.severity == "medium"),
            "low": sum(1 for f in merged_findings if f.severity == "low")
        }
    )

    # Render Terminal UI
    render_audit_report(report)

    # Export Reports
    os.makedirs(output_dir, exist_ok=True)
    md_path = os.path.join(output_dir, f"shadowprint_report_{server_name}.md")
    sarif_path = os.path.join(output_dir, f"shadowprint_report_{server_name}.sarif")

    generate_markdown_report(report, output_file=md_path)
    export_to_sarif(report, output_file=sarif_path)

    console.print(f"[dim]Audit reports exported:[/dim]")
    console.print(f"  • Markdown: [cyan]{md_path}[/cyan]")
    console.print(f"  • SARIF:    [cyan]{sarif_path}[/cyan]\n")

    if status == "FAILED":
        raise typer.Exit(code=2)
    elif status == "FLAGGED":
        raise typer.Exit(code=1)
    else:
        raise typer.Exit(code=0)


@app.command(name="info")
def info():
    """Display system details, team attribution, and architectural guarantees."""
    render_banner()
    console.print(
        Panel(
            "[bold white]Problem Statement:[/bold white] PS02 — Model Context Protocol Security Auditor\n"
            "[bold white]Track:[/bold white] Track 1: Open Weight AI & Open Source Tools\n"
            "[bold white]Co-Builders (50/50):[/bold white] Jasjyot Singh & Gaurang Udgirkar\n"
            "[bold white]Guarantees:[/bold white] 100% Offline, Zero Cloud Dependencies, Static Safety Precedence\n"
            "[bold white]Evidence Plane:[/bold white] Claim <-> Code <-> Runtime <-> Drift",
            title="[bold]Project Information[/bold]",
            border_style="cyan"
        )
    )


def main():
    app()


if __name__ == "__main__":
    main()
