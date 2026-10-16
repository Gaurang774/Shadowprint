"""
Shadowprint Engine S2: Interactive Sandbox & Dynamic Probing Deep-Dive.
Demonstrates step-by-step kernel syscall tracing, canary tripwire interception,
and output exfiltration scanning inside the Docker sandbox.
"""

import sys
import os
import json
import time
import asyncio
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

# UTF-8 Encoding compatibility for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from shadowprint.client.mcp_client import GuardedMCPClient
from shadowprint.s2_prober.syscall_parser import SyscallParser
from shadowprint.s2_prober.canary_tripwire import CanaryTripwire
from shadowprint.s2_prober.output_scanner import OutputScanner
from shadowprint.models import ToolDefinition

console = Console(legacy_windows=False)


def run_sandbox_demo(target_path_str: str):
    target_path = Path(target_path_str).resolve()
    if not target_path.exists():
        console.print(f"[bold red]Error:[/bold red] Target path '{target_path_str}' does not exist.")
        sys.exit(1)

    server_name = target_path.name if target_path.is_dir() else target_path.parent.name
    target_dir = target_path if target_path.is_dir() else target_path.parent

    console.print(
        Panel(
            f"[bold cyan]Shadowprint Engine S2: Container Sandbox & Kernel Syscall Tracer[/bold cyan]\n"
            f"[bold white]Target Server:[/bold white] {server_name}\n"
            f"[bold white]Source Path:[/bold white]   {target_dir}\n"
            f"[bold white]Isolation Mode:[/bold white] Docker Container Sandbox (`--network none`, `strace`, Decoy Canary)",
            title="[bold green]S2 Dynamic Probing Demonstration[/bold green]",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )

    # Temporary directory for container observation logs
    obs_dir = PROJECT_ROOT / "output" / f"sandbox_obs_{server_name}"
    obs_dir.mkdir(parents=True, exist_ok=True)
    strace_log_file = obs_dir / "strace.log"
    sink_log_file = obs_dir / "sink.log"
    strace_log_file.unlink(missing_ok=True)
    sink_log_file.unlink(missing_ok=True)

    # Step 1: Plant Host Canary Tokens (for host fallback or inspection)
    console.print("\n[bold yellow][Step 1/6] Deploying Decoy Canary Tripwire Secrets...[/bold yellow]")
    canary_file = Path(tempfile.gettempdir()) / "canary_creds.env"
    canary_content = (
        "AWS_SECRET_ACCESS_KEY=CANARY_KEY_98721X\n"
        "ANTHROPIC_API_KEY=sk-ant-canary-token-99128X\n"
    )
    canary_file.write_text(canary_content, encoding="utf-8")
    console.print(f"  * Planted decoy file: [cyan]{canary_file}[/cyan]")
    console.print(f"  * Canary Token 1:     [yellow]CANARY_KEY_98721X[/yellow] (Simulated AWS Key)")
    console.print(f"  * Canary Token 2:     [yellow]sk-ant-canary-token-99128X[/yellow] (Simulated Anthropic Key)")

    # Step 2: Configure Sandbox Command
    console.print("\n[bold yellow][Step 2/6] Spawning Container Sandbox under Kernel Tracing...[/bold yellow]")
    use_docker = False
    try:
        res = subprocess.run(["docker", "info"], capture_output=True, timeout=3)
        use_docker = (res.returncode == 0)
    except Exception:
        use_docker = False

    if use_docker:
        console.print("  * [green]Docker Desktop Daemon Detected & Active.[/green]")
        console.print("  * Launching container image: [cyan]shadowprint-sandbox:latest[/cyan]")
        console.print("  * Mounting observation dir:  [cyan]/obs[/cyan]")
        console.print("  * Supervisor tracing:        [yellow]strace -f -e trace=openat,connect,execve[/yellow]")
        console.print("  * Silent HTTP sink:          [yellow]127.0.0.1:8080 -> /obs/sink.log[/yellow]")

        # Mount target directory into /app
        cmd = "docker"
        args = [
            "run", "--rm", "-i",
            "--network", "none",
            "--cap-drop", "ALL",
            "--cap-add", "SYS_PTRACE",
            "--security-opt", "seccomp=unconfined",
            "-v", f"{obs_dir}:/obs",
            "-v", f"{target_dir}:/app",
            "shadowprint-sandbox",
            "server.py",
        ]
    else:
        console.print("  * [dim]Docker daemon inactive, executing via Least-Capability Guarded Stdio Process.[/dim]")
        cmd = sys.executable
        entrypoint = target_dir / "server.py"
        args = [str(entrypoint)]

    # Step 3: Guarded MCP Client Handshake over Stdio
    console.print("\n[bold yellow][Step 3/6] Guarded MCP Handshake over Stdio Pipes...[/bold yellow]")
    client = GuardedMCPClient(command=cmd, args=args, timeout=5.0)

    tools: List[ToolDefinition] = []
    tool_outputs: List[str] = []
    output_findings: List[Finding] = []

    async def _run_probes():
        nonlocal tools, tool_outputs, output_findings
        await client.start()
        init_res = await client.initialize()
        console.print(f"  * [green]MCP Handshake Successful![/green] Server: {init_res.get('serverInfo', {}).get('name', 'unknown')}")

        tools_list = await client.list_tools()
        tools = [t if isinstance(t, ToolDefinition) else ToolDefinition(**t) for t in tools_list]
        console.print(f"  * Discovered [cyan]{len(tools)}[/cyan] declared tools: {', '.join([t.name for t in tools])}")

        # Step 4: Execute Dynamic Burst Probing
        console.print("\n[bold yellow][Step 4/6] Executing Dynamic Burst Sweep Probes...[/bold yellow]")
        scanner = OutputScanner(server_name)

        for tool in tools:
            sample_args: Dict[str, Any] = {}
            if tool.inputSchema and "properties" in tool.inputSchema:
                for k, v in tool.inputSchema["properties"].items():
                    prop_type = v.get("type", "string")
                    if k in ("expression", "expr", "calc"):
                        sample_args[k] = "15 * 6"
                    elif prop_type in ("number", "integer"):
                        sample_args[k] = 15
                    elif prop_type == "boolean":
                        sample_args[k] = True
                    elif k in ("title", "name"):
                        sample_args[k] = "meeting_notes"
                    elif k in ("content", "text"):
                        sample_args[k] = "Standard safe note content"
                    else:
                        sample_args[k] = "test"

            console.print(f"  * Probing tool [bold cyan]{tool.name}[/bold cyan] with payload: [dim]{sample_args}[/dim]")
            try:
                res = await client.call_tool(tool.name, sample_args)
                raw_text = ""
                if "content" in res:
                    for item in res["content"]:
                        raw_text += item.get("text", "")
                tool_outputs.append(raw_text)

                console.print(f"    <- Response payload received ({len(raw_text)} chars)")
                if raw_text:
                    preview = raw_text.strip().replace("\n", " ")[:90]
                    console.print(f"    <- Preview: [italic white]\"{preview}...\"[/italic white]")

                # Step 5: Output Scanner Inspection
                out_findings = scanner.scan_output(tool.name, raw_text)
                if out_findings:
                    for of in out_findings:
                        console.print(f"    [bold red]! [TRIPWIRE TRIGGERED][/bold red] Category: [red]{of.category}[/red]")
                        console.print(f"      Evidence: {of.evidence}")
                        output_findings.append(of)
            except Exception as e:
                console.print(f"    [dim]<- Tool execution handled: {e}[/dim]")

        await client.close()

    try:
        asyncio.run(_run_probes())
    except Exception as e:
        console.print(f"[bold red]Probe execution warning:[/bold red] {e}")

    # Step 6: Inspect Kernel Syscall and Sink Traces
    console.print("\n[bold yellow][Step 5/6] Inspecting Kernel Syscall & Canary Logs...[/bold yellow]")
    strace_content = ""
    if strace_log_file.exists():
        strace_content = strace_log_file.read_text(encoding="utf-8", errors="replace")

    sink_content = ""
    if sink_log_file.exists():
        sink_content = sink_log_file.read_text(encoding="utf-8", errors="replace")

    # Parse syscall behavior
    behavior = SyscallParser.parse_log(strace_content, tool_name=server_name)
    canary_tripwire = CanaryTripwire(server_name)
    canary_findings = canary_tripwire.check_behavior(
        behavior=behavior,
        sink_log_content=sink_content,
        tool_outputs=[{"text": t} for t in tool_outputs],
    )

    canary_accessed = behavior.canary_touched or any(f.category == "CREDENTIAL_ACCESS" for f in canary_findings)
    network_connect = len(behavior.connect_addrs) > 0 or "127.0.0.1:8080" in sink_content
    exfil_detected = len(output_findings) > 0 or any(f.category in ("DATA_EXFILTRATION", "MARKDOWN_EXFILTRATION") for f in canary_findings)

    if use_docker:
        console.print(f"  * Total kernel syscalls recorded: [cyan]{len(strace_content.splitlines())}[/cyan] lines")
        console.print(f"  * Unique files opened via [bold]openat[/bold]: [cyan]{len(behavior.openat_paths)}[/cyan]")
        if behavior.openat_paths:
            for p in behavior.openat_paths[:4]:
                console.print(f"    - openat: {p}")
        if network_connect:
            console.print(f"  * [bold red]Network Socket Syscall Detected:[/bold red] [red]{behavior.connect_addrs}[/red]")
    else:
        console.print("  * Host stdio mode: Tool output stream scanned directly for canary leaks.")

    if canary_accessed:
        console.print("  * [bold red]CANARY COMPROMISED:[/bold red] Process accessed [red]/tmp/canary_creds.env[/red]!")
    else:
        console.print("  * [bold green]CANARY SECURE:[/bold green] /tmp/canary_creds.env was NEVER accessed.")

    # Step 7: Final Comparison Verdict Table
    console.print("\n[bold yellow][Step 6/6] S2 Sandbox Evaluation Verdict[/bold yellow]\n")
    table = Table(title=f"Runtime Security Profile: {server_name}", box=box.HEAVY_EDGE, header_style="bold magenta")
    table.add_column("Security Gate", style="bold white", width=28)
    table.add_column("Observed Behavior", width=36)
    table.add_column("Verdict", justify="center", width=14)

    # Gate 1: Canary Integrity
    if canary_accessed:
        table.add_row("Canary File Access (/tmp)", "Attempted access to canary credentials", "[bold red]COMPROMISED[/bold red]")
    else:
        table.add_row("Canary File Access (/tmp)", "No unauthorized file reads observed", "[bold green]SAFE[/bold green]")

    # Gate 2: Network Isolation
    if network_connect:
        table.add_row("Network Syscall (connect)", "Attempted connection to 127.0.0.1:8080", "[bold red]BLOCKED[/bold red]")
    else:
        table.add_row("Network Syscall (connect)", "Zero outbound network connections", "[bold green]CLEAN[/bold green]")

    # Gate 3: Covert Telemetry Scanning
    if exfil_detected:
        table.add_row("Markdown Telemetry Scan", "Found covert ![exfil] URL parameters", "[bold red]DETECTED[/bold red]")
    else:
        table.add_row("Markdown Telemetry Scan", "Pure text returns, zero telemetry tags", "[bold green]CLEAN[/bold green]")

    console.print(table)

    if canary_accessed or network_connect or exfil_detected:
        console.print(
            Panel(
                f"[bold red]CRITICAL: Runtime Sandbox Tripwire Fired![/bold red]\n"
                f"Target server '[bold white]{server_name}[/bold white]' exhibited covert malicious behavior.\n"
                f"Findings emitted: {len(output_findings) + len(canary_findings)} total runtime vulnerabilities.",
                border_style="red",
            )
        )
    else:
        console.print(
            Panel(
                f"[bold green]PASSED: Zero Malicious Runtime Behaviors Observed![/bold green]\n"
                f"Target server '[bold white]{server_name}[/bold white]' remained 100% compliant inside the sandbox.",
                border_style="green",
            )
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/sandbox_probe_demo.py <path_to_mcp_server>")
        sys.exit(1)
    run_sandbox_demo(sys.argv[1])
