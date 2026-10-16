"""
Shadowprint S2 Dynamic Prober: Burst Probe Sweep Orchestrator.
Owner: Gaurang Udgirkar [G]

Executes the 10-call Burst Probe Sweep across target MCP tools:
  1. Generates targeted benign and edge-case test payloads from inputSchema.
  2. Bounded execution via GuardedMCPClient over stdio.
  3. Scans outputs via OutputScanner.
  4. Parses kernel syscalls via SyscallParser from /obs/strace.log.
  5. Verifies canary access via CanaryTripwire.
  6. Evaluates capability claims via CapabilityModel.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from shadowprint.models import Finding, ToolDefinition, BehaviorTuple
from shadowprint.client.mcp_client import GuardedMCPClient
from shadowprint.s2_prober.syscall_parser import SyscallParser
from shadowprint.s2_prober.canary_tripwire import CanaryTripwire
from shadowprint.s2_prober.output_scanner import OutputScanner
from shadowprint.s2_prober.capability_model import CapabilityModel

logger = logging.getLogger("shadowprint.s2_prober.prober")


class DynamicProber:
    """Orchestrates dynamic probing sweeps and kernel observation inside the sandbox."""

    def __init__(self, target_server: str, obs_dir: Optional[Path] = None):
        self.target_server = target_server
        self.obs_dir = obs_dir or Path("/obs")
        self.output_scanner = OutputScanner(target_server)
        self.canary_tripwire = CanaryTripwire(target_server)
        self.capability_model = CapabilityModel(target_server)

    def generate_probe_inputs(self, tool: ToolDefinition) -> List[Dict[str, Any]]:
        """
        Synthesizes up to 3 bounded test inputs from the tool's inputSchema:
          1. Default/benign payload.
          2. Edge-case / empty payload.
          3. Probe trigger payload (testing if tool evaluates paths or commands).
        """
        schema = tool.inputSchema or {}
        properties = schema.get("properties", {})
        if not properties:
            return [{}]

        payload_benign: Dict[str, Any] = {}
        payload_edge: Dict[str, Any] = {}
        payload_canary: Dict[str, Any] = {}

        for prop_name, prop_meta in properties.items():
            prop_type = prop_meta.get("type", "string")

            if prop_type in ("number", "integer"):
                payload_benign[prop_name] = 42
                payload_edge[prop_name] = 0
                payload_canary[prop_name] = -1
            elif prop_type == "boolean":
                payload_benign[prop_name] = True
                payload_edge[prop_name] = False
                payload_canary[prop_name] = False
            elif prop_type == "array":
                payload_benign[prop_name] = ["test_item"]
                payload_edge[prop_name] = []
                payload_canary[prop_name] = ["/tmp/canary_creds.env"]
            else:
                # String properties
                payload_benign[prop_name] = "standard_input"
                payload_edge[prop_name] = ""
                # Attempt to probe if tool processes file paths
                payload_canary[prop_name] = "/tmp/canary_creds.env"

        return [payload_benign, payload_edge, payload_canary]

    async def run_sweep(
        self,
        client: GuardedMCPClient,
        tools: List[ToolDefinition],
        max_total_calls: int = 10,
    ) -> Tuple[List[Finding], Dict[str, BehaviorTuple]]:
        """
        Executes bounded burst tool sweeps, observes runtime behavior,
        and aggregates findings from all S2 detection engines.
        """
        all_findings: List[Finding] = []
        behaviors: Dict[str, BehaviorTuple] = {}
        tool_outputs: List[Dict[str, Any]] = []

        total_calls = 0

        # 1. Execute Burst Probe Sweep
        for tool in tools:
            if total_calls >= max_total_calls:
                break

            probe_payloads = self.generate_probe_inputs(tool)
            for payload in probe_payloads:
                if total_calls >= max_total_calls:
                    break

                try:
                    res = await client.call_tool(tool.name, payload)
                    tool_outputs.append(res)

                    # Output Exfiltration Scan on returned payload
                    output_findings = self.output_scanner.scan_output(tool.name, res)
                    all_findings.extend(output_findings)
                except Exception as e:
                    logger.debug(f"Tool {tool.name} probe call failed: {e}")

                total_calls += 1

        # 2. Collect & Parse strace Kernel Logs
        strace_file = self.obs_dir / "strace.log"
        strace_content = ""
        if strace_file.exists():
            strace_content = strace_file.read_text(encoding="utf-8", errors="replace")

        # 3. Collect HTTP Sink Logs
        sink_file = self.obs_dir / "sink.log"
        sink_content = ""
        if sink_file.exists():
            sink_content = sink_file.read_text(encoding="utf-8", errors="replace")

        # 4. Parse Behavioral Profiles & Tripwires
        for tool in tools:
            # Parse kernel syscall trace
            behavior = SyscallParser.parse_log(strace_content, tool_name=tool.name)
            behaviors[tool.name] = behavior

            # Canary Tripwire Analysis
            canary_findings = self.canary_tripwire.check_behavior(
                behavior=behavior,
                sink_log_content=sink_content,
                tool_outputs=tool_outputs,
            )
            all_findings.extend(canary_findings)

            # Capability Mismatch Analysis
            capability_findings = self.capability_model.evaluate(tool=tool, behavior=behavior)
            all_findings.extend(capability_findings)

        return all_findings, behaviors
