"""
Engine S4: Rich Color-Coded Terminal Dashboard.
Renders executive-ready audit tables, status badges, evidence snippets,
and remediation guidance for command-line runs.
"""

from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from shadowprint.models import Finding, AuditReport

console = Console()

SEV_COLORS = {
    "critical": "bold red",
    "high": "bold red",
    "medium": "bold yellow",
    "low": "cyan",
    "info": "dim white"
}

STATUS_COLORS = {
    "PASSED": "bold green",
    "FLAGGED": "bold yellow",
    "FAILED": "bold red"
}


def render_banner():
    """Prints the official Shadowprint banner."""
    banner_text = Text()
    banner_text.append(" SHADOWPRINT ", style="bold white on blue")
    banner_text.append(" — Model Context Protocol Security Auditor\n", style="bold cyan")
    banner_text.append("  Every server leaves a trace. 100% Offline & Airgapped.", style="dim")
    console.print(Panel(banner_text, box=box.ROUNDED, border_style="blue"))


def render_audit_report(report: AuditReport):
    """
    Renders the complete audit report to standard output using Rich tables and panels.
    """
    render_banner()

    # 1. Header Overview Panel
    status_style = STATUS_COLORS.get(report.status, "bold white")
    status_badge = f"[{status_style}] {report.status} [/{status_style}]"

    crit_count = sum(1 for f in report.findings if f.severity == "critical")
    high_count = sum(1 for f in report.findings if f.severity == "high")
    med_count = sum(1 for f in report.findings if f.severity == "medium")
    low_count = sum(1 for f in report.findings if f.severity == "low")

    overview_table = Table.grid(padding=(0, 2))
    overview_table.add_column(style="bold")
    overview_table.add_column()
    overview_table.add_row("Target Server:", f"[bold white]{report.target}[/bold white]")
    overview_table.add_row("Audit Status:", status_badge)
    overview_table.add_row(
        "Findings Summary:",
        f"[bold red]{crit_count} Critical[/bold red] | [red]{high_count} High[/red] | [yellow]{med_count} Medium[/yellow] | [cyan]{low_count} Low[/cyan]"
    )

    console.print(Panel(overview_table, title="[bold]Audit Summary[/bold]", border_style="cyan", box=box.ROUNDED))

    # 2. Findings Detail Table
    if not report.findings:
        console.print(Panel("[bold green][PASS] 0 Findings Detected. Target server passed all security gates![/bold green]", border_style="green"))
        return

    findings_table = Table(
        title=f"Detailed Findings ({len(report.findings)} total)",
        box=box.HEAVY_EDGE,
        header_style="bold cyan",
        show_lines=True
    )
    findings_table.add_column("ID", style="bold", width=14)
    findings_table.add_column("Eng", width=5)
    findings_table.add_column("Severity", width=10)
    findings_table.add_column("Category", width=22)
    findings_table.add_column("Location", width=26)
    findings_table.add_column("Evidence & Remediation")

    for f in report.findings:
        sev_color = SEV_COLORS.get(f.severity, "white")
        sev_badge = f"[{sev_color}]{f.severity.upper()}[/{sev_color}]"

        loc_str = "-"
        if f.location:
            fname = f.location.file.split("/")[-1].split("\\")[-1]
            line_part = f":{f.location.line}" if f.location.line else ""
            loc_str = f"{fname}{line_part}"

        evidence_text = Text()
        evidence_text.append(f"{f.evidence}\n", style="white")
        evidence_text.append(f"Fix: {f.remediation}", style="dim italic")

        findings_table.add_row(
            f.id,
            f.engine,
            sev_badge,
            f.category,
            loc_str,
            evidence_text
        )

    console.print(findings_table)
    console.print()
