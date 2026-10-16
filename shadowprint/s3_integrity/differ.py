"""
Shadowprint S3 Integrity Engine: Structural Differ with Non-Printable Escaping.
Owner: Gaurang Udgirkar [G]

Uses DeepDiff to detect schema, code, and behavioral drift against approved pins.
Conforms to ADR-005: Explicitly escapes invisible zero-width characters and Unicode TAGs
so covert injections are visually obvious in diff reports.
"""

import re
import json
from uuid import uuid4
from typing import List, Dict, Any, Optional
from deepdiff import DeepDiff

from shadowprint.models import Finding, Snapshot, Pin, BehaviorTuple

# Zero-width and TAG character lookup for visual replacement
SPECIAL_CHARS = {
    "\u200b": "[U+200B ZERO-WIDTH SPACE]",
    "\u200c": "[U+200C ZERO-WIDTH NON-JOINER]",
    "\u200d": "[U+200D ZERO-WIDTH JOINER]",
    "\ufeff": "[U+FEFF ZERO-WIDTH NO-BREAK SPACE]",
    "\u00a0": "[U+00A0 NO-BREAK SPACE]",
}


def escape_hidden_characters(text: str) -> str:
    """
    Renders invisible Unicode TAG and zero-width characters in explicit visible brackets.
    Handles both literal characters and escaped json unicode sequences.
    """
    if not isinstance(text, str):
        text = str(text)

    # 1. Replace explicit zero-width spaces and escaped json variants
    for char, visible in SPECIAL_CHARS.items():
        text = text.replace(char, visible)

    text = text.replace("\\u200b", "[U+200B ZERO-WIDTH SPACE]").replace("\\u200B", "[U+200B ZERO-WIDTH SPACE]")
    text = text.replace("\\u200c", "[U+200C ZERO-WIDTH NON-JOINER]").replace("\\u200C", "[U+200C ZERO-WIDTH NON-JOINER]")
    text = text.replace("\\u200d", "[U+200D ZERO-WIDTH JOINER]").replace("\\u200D", "[U+200D ZERO-WIDTH JOINER]")
    text = text.replace("\\ufeff", "[U+FEFF ZERO-WIDTH NO-BREAK SPACE]").replace("\\uFEFF", "[U+FEFF ZERO-WIDTH NO-BREAK SPACE]")

    # 2. Replace Plane 14 tag characters (\U000E0000 - \U000E007F)
    def tag_replacer(match):
        code_point = ord(match.group(0))
        return f"[U+{code_point:05X} UNICODE-TAG]"

    text = re.sub(r"[\U000E0000-\U000E007F]", tag_replacer, text)
    # Also handle escaped \uE000 or \U000E00...
    text = re.sub(r"\\u[eE]([0-9a-fA-F]{3})", r"[U+E\1 UNICODE-TAG]", text)
    text = re.sub(r"\\U000[eE]([0-9a-fA-F]{4})", r"[U+E\1 UNICODE-TAG]", text)
    return text


class IntegrityDiffer:
    """Compares live server state against approved pinned baselines."""

    def __init__(self, target_server: str):
        self.target_server = target_server

    def compare_snapshots(
        self,
        pinned_snapshot: Snapshot,
        live_snapshot: Snapshot,
    ) -> List[Finding]:
        """
        Calculates deep structural differences between approved and live Snapshots.
        Emits critical Finding models upon schema, parameter, or description drift.
        """
        findings: List[Finding] = []

        # 1. Definition Hash Comparison
        if pinned_snapshot.definition_hash != live_snapshot.definition_hash:
            pinned_tools = {t.name: t.model_dump() for t in pinned_snapshot.tools}
            live_tools = {t.name: t.model_dump() for t in live_snapshot.tools}

            diff = DeepDiff(pinned_tools, live_tools, ignore_order=True)
            diff_str = escape_hidden_characters(json.dumps(diff.to_dict(), indent=2))

            # Detect added or removed tools
            added_tools = set(live_tools.keys()) - set(pinned_tools.keys())
            removed_tools = set(pinned_tools.keys()) - set(live_tools.keys())

            summary_notes: List[str] = []
            if added_tools:
                summary_notes.append(f"Added tool(s): {', '.join(added_tools)}")
            if removed_tools:
                summary_notes.append(f"Removed tool(s): {', '.join(removed_tools)}")
            if "values_changed" in diff:
                summary_notes.append("Tool descriptions or parameter schemas mutated")

            evidence_summary = "; ".join(summary_notes) if summary_notes else "Live tool schemas drifted from baseline"

            findings.append(
                Finding(
                    id=f"SP-S3-RUGPULL-DEF-{uuid4().hex[:6].upper()}",
                    engine="S3",
                    target=self.target_server,
                    tool=", ".join(added_tools or live_tools.keys()),
                    category="RUG_PULL_SCHEMA_MUTATION",
                    severity="critical",
                    assessment="FAIL",
                    confidence="confirmed",
                    evidence_basis="diff",
                    claim=f"Approved baseline definition hash: {pinned_snapshot.definition_hash[:16]}...",
                    evidence=f"{evidence_summary}.\nDeepDiff Detail:\n{diff_str[:500]}",
                    remediation="Block server execution. Re-audit and approve changes before allowing agents to invoke mutated tools.",
                    supporting_rules=["S3-DEFINITION-DRIFT", "CWE-1007"],
                )
            )

        return findings

    def compare_artifacts(self, pinned_hash: str, live_hash: str) -> List[Finding]:
        """
        Emits finding if target server source code files mutated on disk.
        """
        findings: List[Finding] = []
        if pinned_hash != live_hash:
            findings.append(
                Finding(
                    id=f"SP-S3-TAMPER-SRC-{uuid4().hex[:6].upper()}",
                    engine="S3",
                    target=self.target_server,
                    category="SOURCE_CODE_TAMPERING",
                    severity="high",
                    assessment="FAIL",
                    confidence="confirmed",
                    evidence_basis="diff",
                    claim=f"Approved source code artifact hash: {pinned_hash[:16]}...",
                    evidence=f"Live source code artifact hash changed to: {live_hash[:16]}...",
                    remediation="Target source code was modified after approval. Review git diff and re-run S0 static audit.",
                    supporting_rules=["S3-ARTIFACT-DRIFT", "CWE-353"],
                )
            )
        return findings

    def compare_behaviors(
        self,
        pinned_behaviors: Dict[str, BehaviorTuple],
        live_behaviors: Dict[str, BehaviorTuple],
    ) -> List[Finding]:
        """
        Emits finding if live runtime syscall traces diverge from approved baseline.
        """
        findings: List[Finding] = []
        for tool_name, live_b in live_behaviors.items():
            if tool_name not in pinned_behaviors:
                continue

            pinned_b = pinned_behaviors[tool_name]
            if pinned_b.behavior_hash != live_b.behavior_hash:
                diff = DeepDiff(pinned_b.model_dump(), live_b.model_dump())
                diff_str = escape_hidden_characters(str(diff))

                findings.append(
                    Finding(
                        id=f"SP-S3-DRIFT-BEH-{uuid4().hex[:6].upper()}",
                        engine="S3",
                        target=self.target_server,
                        tool=tool_name,
                        category="BEHAVIOR_MUTATION",
                        severity="high",
                        assessment="FLAGGED",
                        confidence="confirmed",
                        evidence_basis="diff",
                        claim=f"Approved behavior hash: {pinned_b.behavior_hash[:16]}...",
                        evidence=f"Live kernel syscalls mutated.\nDiff: {diff_str[:400]}",
                        remediation="Investigate unexpected file or network syscall divergence from pinned baseline.",
                        supporting_rules=["S3-BEHAVIOR-DRIFT", "CWE-1007"],
                    )
                )

        return findings
