"""
Shadowprint S2 Dynamic Prober: Canary Tripwire Verifier.
Owner: Gaurang Udgirkar [G]

Detects unauthorized access and covert exfiltration of decoy credentials:
  - Token: CANARY_KEY_98721X
  - Decoy File: /tmp/canary_creds.env
  - Secondary Token: sk-ant-canary-token-99128X
Monitors file read syscalls, in-container HTTP sink logs, and tool output streams.
"""

from uuid import uuid4
from typing import List, Dict, Any, Optional
from shadowprint.models import Finding, BehaviorTuple

CANARY_TOKENS = [
    "CANARY_KEY_98721X",
    "sk-ant-canary-token-99128X",
]
CANARY_FILEPATHS = [
    "/tmp/canary_creds.env",
    "/tmp/canary.env",
]


class CanaryTripwire:
    """Verifies whether decoy credentials were read, transmitted, or exfiltrated."""

    def __init__(self, target_server: str):
        self.target_server = target_server

    def check_behavior(
        self,
        behavior: BehaviorTuple,
        sink_log_content: Optional[str] = None,
        tool_outputs: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Finding]:
        """
        Evaluates syscall events, HTTP sink logs, and tool responses for canary tripwire triggers.
        Returns a list of critical confirmed Finding models.
        """
        findings: List[Finding] = []

        # 1. File Access Tripwire (Syscall level)
        for filepath in behavior.openat_paths:
            if any(target in filepath for target in CANARY_FILEPATHS) or behavior.canary_touched:
                findings.append(
                    Finding(
                        id=f"SP-S2-CANARY-FILE-{uuid4().hex[:6].upper()}",
                        engine="S2",
                        target=self.target_server,
                        tool=behavior.tool_name,
                        category="CREDENTIAL_ACCESS",
                        severity="critical",
                        assessment="FAIL",
                        confidence="confirmed",
                        evidence_basis="runtime_observed",
                        claim="Tool claimed legitimate execution without reading unauthorized environment secrets.",
                        evidence=f"Kernel syscall openat() observed accessing canary decoy credentials at: {filepath}",
                        remediation="Revoke environment access. Server actively inspected /tmp/canary_creds.env.",
                        supporting_rules=["S2-CANARY-FILE-READ", "CWE-200"],
                    )
                )
                break

        # 2. Network Sink Egress Tripwire (HTTP sink level)
        if sink_log_content:
            for token in CANARY_TOKENS:
                if token in sink_log_content:
                    findings.append(
                        Finding(
                            id=f"SP-S2-CANARY-EGRESS-{uuid4().hex[:6].upper()}",
                            engine="S2",
                            target=self.target_server,
                            tool=behavior.tool_name,
                            category="DATA_EXFILTRATION",
                            severity="critical",
                            assessment="FAIL",
                            confidence="confirmed",
                            evidence_basis="runtime_observed",
                            claim="Tool claimed no unauthorized network transmission of sensitive credentials.",
                            evidence=f"HTTP egress sink intercepted exfiltrated canary secret '{token}' in network payload.",
                            remediation="Block server execution immediately. Malicious credential exfiltration confirmed.",
                            supporting_rules=["S2-CANARY-SINK-INTERCEPT", "CWE-200", "CWE-918"],
                        )
                    )
                    break

        # 3. Direct Tool Output Tripwire (Response level)
        if tool_outputs:
            for item in tool_outputs:
                output_str = str(item)
                for token in CANARY_TOKENS:
                    if token in output_str:
                        findings.append(
                            Finding(
                                id=f"SP-S2-CANARY-OUTPUT-{uuid4().hex[:6].upper()}",
                                engine="S2",
                                target=self.target_server,
                                tool=behavior.tool_name,
                                category="DATA_LEAKAGE",
                                severity="critical",
                                assessment="FAIL",
                                confidence="confirmed",
                                evidence_basis="runtime_observed",
                                claim="Tool returns safe results without leaking environment variables.",
                                evidence=f"Decoy canary credential '{token}' detected in tool output payload.",
                                remediation="Audit tool response sanitization. Do not return environment secrets in output.",
                                supporting_rules=["S2-CANARY-OUTPUT-LEAK", "CWE-200"],
                            )
                        )
                        break

        return findings
