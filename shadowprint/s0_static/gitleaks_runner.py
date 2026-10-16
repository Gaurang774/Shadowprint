"""
Engine S0: Gitleaks Secrets Detection Runner.
Detects hardcoded cloud credentials, API tokens, and private keys.
Features a built-in offline regex engine fallback for airgapped environments
where the external gitleaks binary may not be installed.
"""

import json
import os
import re
import shutil
import subprocess
from typing import List, Tuple
from shadowprint.models import Finding, Location

# High-precision patterns for secret detection
SECRET_PATTERNS: List[Tuple[str, str, str, str]] = [
    # (Category, Rule ID, Regex, Description)
    (
        "AWS_ACCESS_KEY",
        "SEC-AWS-001",
        r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16,}",
        "Hardcoded AWS Access Key ID"
    ),
    (
        "AWS_SECRET_KEY",
        "SEC-AWS-002",
        r"(?i)(?:aws_secret_access_key|aws_secret_key|secret_key)\s*[:=]\s*['\"]([A-Za-z0-9/+=]{40})['\"]",
        "Hardcoded AWS Secret Access Key"
    ),
    (
        "OPENAI_API_KEY",
        "SEC-OAI-001",
        r"sk-(?:proj-)?[A-Za-z0-9_-]{32,}",
        "Hardcoded OpenAI API Key"
    ),
    (
        "ANTHROPIC_API_KEY",
        "SEC-ANT-001",
        r"sk-ant-[A-Za-z0-9_-]{32,}",
        "Hardcoded Anthropic API Key"
    ),
    (
        "GITHUB_TOKEN",
        "SEC-GH-001",
        r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}",
        "Hardcoded GitHub Personal Access Token"
    ),
    (
        "PRIVATE_KEY",
        "SEC-KEY-001",
        r"-----BEGIN (?:RSA|EC|DSA|OPENSSH|PGP) PRIVATE KEY-----",
        "Unencrypted Private Key Block"
    ),
    (
        "GENERIC_SECRET_ASSIGNMENT",
        "SEC-GEN-001",
        r"(?i)(?:api_key|apikey|secret_token|auth_token)\s*=\s*['\"][A-Za-z0-9_\-\.]{20,}['\"]",
        "Generic High-Entropy Credential Assignment"
    )
]


def _mask_secret(val: str) -> str:
    """Masks secret value for safe reporting."""
    if len(val) <= 8:
        return "****"
    return f"{val[:4]}...{val[-4:]} [REDACTED]"


def _scan_file_regex(filepath: str, server_name: str) -> List[Finding]:
    """Scans a single file using built-in high-precision regexes."""
    findings: List[Finding] = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return []

    for line_idx, line in enumerate(lines, start=1):
        for cat, rule_id, pattern, desc in SECRET_PATTERNS:
            for match in re.finditer(pattern, line):
                matched_str = match.group(0)
                # Mask secret in evidence
                masked = _mask_secret(matched_str)
                rel_path = os.path.normpath(filepath).replace("\\", "/")

                finding = Finding(
                    id=f"SP-S0-SEC-{len(findings) + 1:03d}",
                    engine="S0",
                    target=server_name,
                    tool="__server__",
                    category="HARDCODED_SECRET",
                    severity="critical" if "AWS" in cat or "KEY" in cat else "high",
                    assessment="FAIL",
                    confidence="confirmed",
                    evidence_basis="static",
                    location=Location(file=rel_path, line=line_idx, column=match.start() + 1),
                    evidence=f"[{rule_id}] {desc}: {masked}",
                    remediation="Remove hardcoded credentials from source code. Load secrets from environment variables or a secure vault.",
                    supporting_rules=[rule_id, "CWE-798"]
                )
                findings.append(finding)

    return findings


def run_gitleaks(target_path: str, server_name: str = "target_server") -> List[Finding]:
    """
    Scans target_path for hardcoded secrets.
    Attempts to use the gitleaks executable if available, falling back to
    the embedded regex engine.
    """
    target = os.path.abspath(target_path)
    if not os.path.exists(target):
        return []

    # Check if gitleaks binary is present on system PATH
    gitleaks_bin = shutil.which("gitleaks")
    if gitleaks_bin:
        findings: List[Finding] = []
        try:
            report_file = os.path.join(os.environ.get("TEMP", "/tmp"), "gitleaks_report.json")
            cmd = [
                gitleaks_bin,
                "detect",
                "--no-git",
                "--source",
                target,
                "--report-path",
                report_file,
                "--report-format",
                "json"
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
            if os.path.exists(report_file):
                with open(report_file, "r", encoding="utf-8", errors="ignore") as rf:
                    data = json.load(rf)
                for item in data:
                    secret_val = item.get("Secret", "")
                    masked = _mask_secret(secret_val)
                    rule = item.get("RuleID", "gitleaks-secret")
                    file_path = item.get("File", target)
                    line = item.get("StartLine")

                    findings.append(
                        Finding(
                            id=f"SP-S0-GLK-{len(findings) + 1:03d}",
                            engine="S0",
                            target=server_name,
                            tool="__server__",
                            category="HARDCODED_SECRET",
                            severity="critical",
                            assessment="FAIL",
                            confidence="confirmed",
                            evidence_basis="static",
                            location=Location(
                                file=os.path.normpath(file_path).replace("\\", "/"),
                                line=line
                            ),
                            evidence=f"[{rule}] Discovered hardcoded secret: {masked}",
                            remediation="Rotate exposed credential immediately and replace with environment variable injection.",
                            supporting_rules=[rule, "CWE-798"]
                        )
                    )
                try:
                    os.remove(report_file)
                except Exception:
                    pass
                return findings
        except Exception:
            pass  # Fall through to native scanner

    # Embedded native scanner fallback
    all_findings: List[Finding] = []
    if os.path.isfile(target):
        all_findings.extend(_scan_file_regex(target, server_name))
    else:
        for root, _, files in os.walk(target):
            for file in files:
                if file.endswith((".py", ".json", ".env", ".yaml", ".yml", ".toml", ".txt")):
                    fp = os.path.join(root, file)
                    all_findings.extend(_scan_file_regex(fp, server_name))

    return all_findings
