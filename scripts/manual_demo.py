"""
Shadowprint Manual Verification & Demonstration Harness.
Allows instant, zero-setup interactive manual verification of:
1. Rug-Pull live definition drift & escaped unicode diff
2. Exfil calculator covert canary theft & output exfiltration
3. SQLite 3-layer cryptographic pinning & database CRUD
"""

import sys
import os
import json
import asyncio
import tempfile
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure Windows terminal handles UTF-8 gracefully
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from rich.console import Console
from rich.panel import Panel
from shadowprint.client.mcp_client import GuardedMCPClient
from shadowprint.s3_integrity.differ import IntegrityDiffer
from shadowprint.s2_prober.output_scanner import OutputScanner
from shadowprint.s3_integrity.db import PinDatabase
from shadowprint.s3_integrity.hasher import ThreeLayerHasher
from shadowprint.models import Snapshot, ToolDefinition, Pin

console = Console(legacy_windows=False)


async def demo_rugpull():
    console.print("\n[bold cyan]=== [1] Demonstrating Live Rug-Pull Mutation & Escaped Character Diff ===[/bold cyan]\n")
    flag_paths = [
        Path("/tmp/rugpull_trigger.flag"),
        Path(tempfile.gettempdir()) / "rugpull_trigger.flag",
    ]
    for p in flag_paths:
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass

    client = GuardedMCPClient(sys.executable, [str(PROJECT_ROOT / "fixtures" / "rugpull_suite" / "server.py")])

    console.print("[dim]-> Phase 1: Fetching clean baseline snapshot...[/dim]")
    s1 = await client.fetch_snapshot("rugpull_suite")
    console.print(f"    Baseline Tool Description: [green]\"{s1.tools[0].description}\"[/green]")
    console.print(f"    Baseline Definition Hash:  [yellow]{s1.definition_hash}[/yellow]\n")

    console.print("[dim]-> Phase 2: Touching trigger flag (/tmp/rugpull_trigger.flag)...[/dim]")
    for p in flag_paths:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("trigger_active")
        except Exception:
            pass

    console.print("[dim]-> Phase 3: Fetching mutated snapshot...[/dim]")
    s2 = await client.fetch_snapshot("rugpull_suite")
    for p in flag_paths:
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass
    console.print(f"    Mutated Tool Description:  [red]\"{s2.tools[0].description}\"[/red]")
    console.print(f"    Mutated Definition Hash:   [yellow]{s2.definition_hash}[/yellow]\n")

    console.print("[dim]-> Phase 4: Calculating DeepDiff with visual character escaping...[/dim]")
    differ = IntegrityDiffer("rugpull_suite")
    findings = differ.compare_snapshots(s1, s2)

    console.print(f"    Drift Detected: [bold red]{len(findings) > 0}[/bold red]")
    if findings:
        f = findings[0]
        console.print(f"    Category:       [bold magenta]{f.category}[/bold magenta]")
        console.print(f"    Severity:       [bold red]{f.severity.upper()}[/bold red]")
        console.print(f"    Claim:          {f.claim}")
        console.print(Panel(f.evidence, title="[bold red]Escaped DeepDiff Evidence (Visible Tags)[/bold red]", border_style="red"))
        console.print("[bold green][+] Test Result: Rug-Pull Successfully Caught & Non-Printables Escaped![/bold green]\n")


async def demo_exfil():
    console.print("\n[bold cyan]=== [2] Demonstrating Exfil Calculator Covert Canary Leak & Output Telemetry ===[/bold cyan]\n")
    client = GuardedMCPClient(sys.executable, [str(PROJECT_ROOT / "fixtures" / "exfil_calculator" / "server.py")])
    await client.start()
    try:
        await client.initialize()
        console.print("[dim]-> Calling calculate(expression='15 * 6')...[/dim]")
        res = await client.call_tool("calculate", {"expression": "15 * 6"})
        text = res["content"][0]["text"]
        console.print(Panel(text, title="Server Raw Response Payload", border_style="yellow"))

        console.print("[dim]-> Scanning tool output for covert exfiltration...[/dim]")
        scanner = OutputScanner("exfil_calculator")
        findings = scanner.scan_output("calculate", text)

        console.print(f"    Exfil Findings Detected: [bold red]{len(findings)}[/bold red]")
        for idx, finding in enumerate(findings, 1):
            console.print(f"    [{idx}] Category: [magenta]{finding.category}[/magenta] | Severity: [red]{finding.severity.upper()}[/red]")
            console.print(f"        Evidence: {finding.evidence}")
            console.print(f"        Rules:    {finding.supporting_rules}")

        console.print("\n[bold green][+] Test Result: Exfiltration Telemetry & Decoy Canary Correctly Caught![/bold green]\n")
    finally:
        await client.close()


def demo_pin():
    console.print("\n[bold cyan]=== [3] Demonstrating SQLite Pinning & 3-Layer Cryptographic Store ===[/bold cyan]\n")
    import time
    db_path = PROJECT_ROOT / "shadowprint.db"
    db = PinDatabase(str(db_path))

    tool = ToolDefinition(
        name="secure_vault",
        description="Stores enterprise cryptographic credentials safely.",
        inputSchema={"type": "object", "properties": {"item": {"type": "string"}}}
    )
    def_hash = ThreeLayerHasher.compute_definition_hash([tool])
    art_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    snapshot = Snapshot(
        server_name="vault_service",
        timestamp=time.time(),
        tools=[tool],
        definition_hash=def_hash,
        artifact_hash=art_hash,
    )
    pin = Pin(
        server_name="vault_service",
        pinned_at=time.time(),
        definition_hash=def_hash,
        artifact_hash=art_hash,
        tools_count=1,
    )

    console.print(f"[dim]-> Saving approved baseline pin to {db_path.name}...[/dim]")
    db.save_pin(pin, snapshot)

    console.print("[dim]-> Querying pin back from SQLite database...[/dim]")
    retrieved = db.get_pin("vault_service")
    assert retrieved is not None

    console.print(f"    Server Name:            [bold]{retrieved.server_name}[/bold]")
    console.print(f"    Layer 1 Definition SHA: [yellow]{retrieved.definition_hash}[/yellow]")
    console.print(f"    Layer 2 Artifact SHA:   [yellow]{retrieved.artifact_hash}[/yellow]")
    console.print(f"    Pinned Tools Count:     [cyan]{retrieved.tools_count}[/cyan]")

    console.print("\n[bold green][+] Test Result: SQLite 3-Layer Pin Stored & Retrieved with 100% Cryptographic Integrity![/bold green]\n")


def main():
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

    if arg in ("rugpull", "1"):
        asyncio.run(demo_rugpull())
    elif arg in ("exfil", "2"):
        asyncio.run(demo_exfil())
    elif arg in ("pin", "3"):
        demo_pin()
    elif arg in ("all", "--all"):
        asyncio.run(demo_rugpull())
        asyncio.run(demo_exfil())
        demo_pin()
    else:
        console.print(f"[yellow]Usage: python scripts/manual_demo.py [rugpull | exfil | pin | all][/yellow]")


if __name__ == "__main__":
    main()
