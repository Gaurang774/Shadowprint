"""
Engine S0 Master Orchestrator: Static Code & Configuration Analysis.
Runs Bandit AST, Semgrep Taint, Gitleaks Secrets, Claim-vs-Code Checker,
and the Hostile Suppression Detection Gate. Normalizes and deduplicates all findings.
"""

import os
import re
from typing import List, Tuple
from shadowprint.models import Finding, Location
from shadowprint.normalizer import normalize_findings
from shadowprint.s0_static.bandit_runner import run_bandit
from shadowprint.s0_static.semgrep_runner import run_semgrep
from shadowprint.s0_static.gitleaks_runner import run_gitleaks
from shadowprint.s0_static.claim_code_checker import run_claim_checker

import tokenize

# Regex pattern for hostile inline scanner suppression directives
SUPPRESSION_PATTERN = re.compile(r"#\s*(nosec|nosemgrep|bandit:\s*ignore)\b", re.IGNORECASE)


def check_hostile_suppressions(target_path: str, server_name: str) -> List[Finding]:
    """
    Scans target source files for inline suppression directives (# nosec, # nosemgrep).
    In Shadowprint, inline suppressions on untrusted servers are flagged as TAMPER_ATTEMPT.
    Uses Python's tokenizer so docstrings/string literals are never mistakenly flagged.
    """
    findings: List[Finding] = []
    target = os.path.abspath(target_path)
    if not os.path.exists(target):
        return []

    py_files = []
    if os.path.isfile(target):
        if target.endswith(".py"):
            py_files.append(target)
    else:
        for root, _, files in os.walk(target):
            for f in files:
                if f.endswith(".py"):
                    py_files.append(os.path.join(root, f))

    for filepath in py_files:
        try:
            with open(filepath, "rb") as f:
                tokens = list(tokenize.tokenize(f.readline))
        except Exception:
            continue

        rel_path = os.path.normpath(filepath).replace("\\", "/")

        for toknum, tokval, (srow, scol), _, _ in tokens:
            if toknum == tokenize.COMMENT:
                match = SUPPRESSION_PATTERN.search(tokval)
                if match:
                    # Verify it's a directive (either whole comment or end of line directive)
                    directive = match.group(0).strip()
                    findings.append(
                        Finding(
                            id=f"SP-S0-TMP-{len(findings) + 1:03d}",
                            engine="S0",
                            target=server_name,
                            tool="__server__",
                            category="TAMPER_ATTEMPT",
                            severity="high",
                            assessment="FAIL",
                            confidence="confirmed",
                            evidence_basis="static",
                            location=Location(file=rel_path, line=srow, column=scol + 1),
                            evidence=f"Discovered inline scanner suppression directive '{directive}' on line {srow}: {tokval.strip()}",
                            remediation="Inline security scanner suppressions are prohibited on audited MCP servers. Audit the underlying code without suppressions.",
                            supporting_rules=["SUPPRESSION_DETECTION", "ANTI_TAMPER"]
                        )
                    )

    return findings


def scan_static(target_path: str, server_name: str = "target_server") -> List[Finding]:
    """
    Master entrypoint for Engine S0.
    1. Checks for hostile suppression tampering (#nosec, #nosemgrep).
    2. Runs Bandit AST security linter with --ignore-nosec.
    3. Runs Semgrep taint tracking rules.
    4. Runs Gitleaks secrets detection.
    5. Runs AST Claim-vs-Code contradiction checker.
    6. Clustered deduplication via normalizer.
    """
    all_findings: List[Finding] = []

    # 1. Hostile suppression detection
    tamper_findings = check_hostile_suppressions(target_path, server_name)
    all_findings.extend(tamper_findings)

    # 2. Bandit AST runner
    bandit_findings = run_bandit(target_path, server_name)
    all_findings.extend(bandit_findings)

    # 3. Semgrep taint runner
    semgrep_findings = run_semgrep(target_path, server_name)
    all_findings.extend(semgrep_findings)

    # 4. Gitleaks runner
    gitleaks_findings = run_gitleaks(target_path, server_name)
    all_findings.extend(gitleaks_findings)

    # 5. Claim vs code checker
    claim_findings = run_claim_checker(target_path, server_name)
    all_findings.extend(claim_findings)

    # 6. Deduplication and normalization
    return normalize_findings(all_findings)
