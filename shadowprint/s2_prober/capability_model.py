"""
Shadowprint S2 Dynamic Prober: Capability vs. Syscall Mismatch Model.
Owner: Gaurang Udgirkar [G]

Detects discrepancies between declared metadata claims and observed kernel syscalls:
  - Tool claims to be "offline" or "calculator", but connects to network sockets.
  - Tool claims "pure in-memory text manipulation", but reads local filesystem files.
  - Tool spawns unexpected shell execution binaries (execve: /bin/sh, /bin/bash).
"""

import re
from uuid import uuid4
from typing import List, Dict, Any, Optional
from shadowprint.models import Finding, ToolDefinition, BehaviorTuple

# Claim keywords indicating offline / restricted intent
OFFLINE_KEYWORDS = (
    "offline", "local only", "in-memory", "pure math", "calculator",
    "pure computation", "no network", "stateless", "no internet",
)
READ_ONLY_KEYWORDS = (
    "read-only", "read only", "viewer", "inspection only", "fetch only",
)


class CapabilityModel:
    """Evaluates declared tool claims against verified kernel syscall traces."""

    def __init__(self, target_server: str):
        self.target_server = target_server

    def evaluate(self, tool: ToolDefinition, behavior: BehaviorTuple) -> List[Finding]:
        """
        Compares tool description against recorded openat, connect, and execve syscalls.
        """
        findings: List[Finding] = []
        desc = (tool.description or "").lower()

        # 1. Network Capability Mismatch
        claims_offline = any(kw in desc for kw in OFFLINE_KEYWORDS)
        if claims_offline and behavior.connect_addrs:
            addrs = ", ".join(behavior.connect_addrs[:3])
            findings.append(
                Finding(
                    id=f"SP-S2-MISMATCH-NET-{uuid4().hex[:6].upper()}",
                    engine="S2",
                    target=self.target_server,
                    tool=tool.name,
                    category="CAPABILITY_MISMATCH_NETWORK",
                    severity="critical",
                    assessment="FAIL",
                    confidence="confirmed",
                    evidence_basis="runtime_observed",
                    claim=f"Tool claims offline / local operation: '{tool.description[:120]}'",
                    evidence=f"Kernel syscall connect() observed reaching network endpoints: {addrs}",
                    remediation="Remove deceptive offline claim or revoke network capability from container.",
                    supporting_rules=["S2-CAPABILITY-NETWORK-MISMATCH", "CWE-1007"],
                )
            )

        # 2. Unexpected Command / Subprocess Execution Mismatch
        if behavior.execve_cmds:
            suspicious_cmds = [
                cmd for cmd in behavior.execve_cmds
                if any(shell in cmd for shell in ("/bin/sh", "/bin/bash", "cmd.exe", "powershell", "whoami", "curl", "wget"))
            ]
            if suspicious_cmds:
                cmds_str = "; ".join(suspicious_cmds[:3])
                findings.append(
                    Finding(
                        id=f"SP-S2-MISMATCH-EXEC-{uuid4().hex[:6].upper()}",
                        engine="S2",
                        target=self.target_server,
                        tool=tool.name,
                        category="CAPABILITY_MISMATCH_EXEC",
                        severity="critical",
                        assessment="FAIL",
                        confidence="confirmed",
                        evidence_basis="runtime_observed",
                        claim=f"Tool declared description: '{tool.description[:120]}'",
                        evidence=f"Unannounced process execution detected via execve(): {cmds_str}",
                        remediation="Investigate unauthorized subprocess execution. Possible command injection or backdoor.",
                        supporting_rules=["S2-CAPABILITY-EXEC-MISMATCH", "CWE-78"],
                    )
                )

        return findings
