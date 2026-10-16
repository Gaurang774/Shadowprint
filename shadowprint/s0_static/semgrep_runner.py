"""
Engine S0: Semgrep Taint Tracking Runner.
Executes custom taint analysis rules against MCP servers.
Includes a native AST fallback engine for airgapped environments where
the semgrep binary is not installed.
"""

import ast
import json
import os
import re
import shutil
import subprocess
import sys
from typing import List, Optional
import yaml

from shadowprint.models import Finding, Location

RULES_PATH = os.path.join(os.path.dirname(__file__), "rules", "mcp_taint_rules.yaml")


def _run_native_rule_checks(target_path: str, server_name: str) -> List[Finding]:
    """
    Fallback taint and pattern checker using Python AST when semgrep binary is absent.
    """
    findings: List[Finding] = []
    py_files = []
    target = os.path.abspath(target_path)
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
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            tree = ast.parse(content, filename=filepath)
        except Exception:
            continue

        rel_path = os.path.normpath(filepath).replace("\\", "/")

        for node in ast.walk(tree):
            # Check 1: subprocess call with shell=True
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    func_name = f"{node.func.value.id}.{node.func.attr}"

                if func_name in ("subprocess.run", "subprocess.Popen", "subprocess.call"):
                    for kw in node.keywords:
                        if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            findings.append(
                                Finding(
                                    id=f"SP-S0-SMP-{len(findings) + 1:03d}",
                                    engine="S0",
                                    target=server_name,
                                    tool="__server__",
                                    category="COMMAND_INJECTION",
                                    severity="high",
                                    assessment="FAIL",
                                    confidence="confirmed",
                                    evidence_basis="static",
                                    location=Location(file=rel_path, line=node.lineno, column=node.col_offset),
                                    evidence=f"[mcp-command-injection] subprocess call with shell=True detected on line {node.lineno}.",
                                    remediation="Replace shell=True with explicit argument list.",
                                    supporting_rules=["mcp-command-injection", "CWE-78"]
                                )
                            )

                # Check 2: pickle.loads call
                if func_name == "pickle.loads":
                    findings.append(
                        Finding(
                            id=f"SP-S0-SMP-{len(findings) + 1:03d}",
                            engine="S0",
                            target=server_name,
                            tool="__server__",
                            category="INSECURE_DESERIALIZATION",
                            severity="high",
                            assessment="FAIL",
                            confidence="confirmed",
                            evidence_basis="static",
                            location=Location(file=rel_path, line=node.lineno, column=node.col_offset),
                            evidence=f"[mcp-insecure-deserialization] Untrusted deserialization via pickle.loads on line {node.lineno}.",
                            remediation="Use safe serialization formats such as JSON or Protocol Buffers.",
                            supporting_rules=["mcp-insecure-deserialization", "CWE-502"]
                        )
                    )

                # Check 3: urllib.request.urlopen call
                if isinstance(node.func, ast.Attribute):
                    # Check for urllib.request.urlopen
                    attr_chain = []
                    curr = node.func
                    while isinstance(curr, ast.Attribute):
                        attr_chain.append(curr.attr)
                        curr = curr.value
                    if isinstance(curr, ast.Name):
                        attr_chain.append(curr.id)
                    attr_chain.reverse()
                    full_name = ".".join(attr_chain)
                    if full_name in ("urllib.request.urlopen", "urlopen"):
                        findings.append(
                            Finding(
                                id=f"SP-S0-SMP-{len(findings) + 1:03d}",
                                engine="S0",
                                target=server_name,
                                tool="__server__",
                                category="SSRF_UNSAFE_FETCH",
                                severity="medium",
                                assessment="FLAGGED",
                                confidence="confirmed",
                                evidence_basis="static",
                                location=Location(file=rel_path, line=node.lineno, column=node.col_offset),
                                evidence=f"[mcp-ssrf-urlopen] Unvalidated URL fetch via {full_name} on line {node.lineno}.",
                                remediation="Validate URL schemes and hostnames against an allowlist.",
                                supporting_rules=["mcp-ssrf-urlopen", "CWE-918"]
                            )
                        )

    return findings


def run_semgrep(target_path: str, server_name: str = "target_server") -> List[Finding]:
    """
    Executes Semgrep using custom MCP taint rules or falls back to native AST parser.
    """
    target = os.path.abspath(target_path)
    if not os.path.exists(target):
        return []

    semgrep_bin = shutil.which("semgrep")
    if semgrep_bin and os.path.exists(RULES_PATH):
        try:
            cmd = [
                semgrep_bin,
                "--config",
                RULES_PATH,
                "--json",
                "--quiet",
                target
            ]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            if proc.returncode in (0, 1) and proc.stdout:
                data = json.loads(proc.stdout)
                findings: List[Finding] = []
                for item in data.get("results", []):
                    check_id = item.get("check_id", "semgrep-rule")
                    extra = item.get("extra", {})
                    meta = extra.get("metadata", {})
                    category = meta.get("category", "STATIC_CODE_FLAW")
                    cwe = meta.get("cwe", "")
                    message = extra.get("message", "")
                    path = item.get("path", target)
                    start = item.get("start", {})
                    line = start.get("line")
                    col = start.get("col")

                    findings.append(
                        Finding(
                            id=f"SP-S0-SMP-{len(findings) + 1:03d}",
                            engine="S0",
                            target=server_name,
                            tool="__server__",
                            category=category,
                            severity="high" if extra.get("severity") == "ERROR" else "medium",
                            assessment="FAIL" if extra.get("severity") == "ERROR" else "FLAGGED",
                            confidence="confirmed",
                            evidence_basis="static",
                            location=Location(
                                file=os.path.normpath(path).replace("\\", "/"),
                                line=line,
                                column=col
                            ),
                            evidence=f"[{check_id}] {message}",
                            remediation=f"Remediate per rule {check_id}. {cwe}",
                            supporting_rules=[check_id] + ([cwe] if cwe else [])
                        )
                    )
                return findings
        except Exception:
            pass  # Fall through to native checker

    return _run_native_rule_checks(target_path, server_name)
