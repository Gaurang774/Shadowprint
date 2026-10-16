"""
Engine S0: AST Claim-vs-Code Contradiction Checker.
Analyzes Python AST to verify whether declared claims (e.g., 'read-only', 'safe',
'offline') are violated by actual implemented function calls (e.g., os.remove,
open('w'), subprocess.run, socket.connect).
"""

import ast
import os
from typing import List, Dict, Set, Optional, Tuple
from shadowprint.models import Finding, Location

# Known destructive and mutative calls
DESTRUCTIVE_CALLS = {
    "os.remove", "os.unlink", "os.rmdir", "shutil.rmtree",
    "os.rename", "os.replace", "os.chmod"
}

NETWORK_CALLS = {
    "urllib.request.urlopen", "requests.get", "requests.post",
    "httpx.get", "httpx.post", "socket.connect"
}

PROCESS_CALLS = {
    "subprocess.run", "subprocess.Popen", "subprocess.call",
    "os.system", "os.popen", "exec", "eval"
}

# Claim trigger keywords
READ_ONLY_KEYWORDS = {"read-only", "read only", "readonly", "viewer only", "inspection only"}
OFFLINE_KEYWORDS = {"offline", "local only", "airgapped", "no network"}
CALCULATOR_KEYWORDS = {"calculator", "math only", "text formatter", "formatter"}


class _CallVisitor(ast.NodeVisitor):
    """Collects all function calls within an AST block."""

    def __init__(self):
        self.calls: List[Tuple[str, int]] = []
        self.file_write_opens: List[int] = []

    def visit_Call(self, node: ast.Call):
        call_name = ""
        if isinstance(node.func, ast.Name):
            call_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            # Resolve module.func, e.g. os.remove
            parts = []
            curr = node.func
            while isinstance(curr, ast.Attribute):
                parts.append(curr.attr)
                curr = curr.value
            if isinstance(curr, ast.Name):
                parts.append(curr.id)
            parts.reverse()
            call_name = ".".join(parts)

        if call_name:
            self.calls.append((call_name, node.lineno))

        # Check for open(..., 'w') or open(..., 'a')
        if call_name == "open" and len(node.args) >= 2:
            mode_arg = node.args[1]
            if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, str):
                if any(m in mode_arg.value for m in ("w", "a", "x", "+")):
                    self.file_write_opens.append(node.lineno)

        self.generic_visit(node)


def _check_tool_function(
    func_node: ast.FunctionDef,
    filepath: str,
    server_name: str
) -> List[Finding]:
    """Inspects a tool function AST for claim contradictions."""
    findings: List[Finding] = []

    # 1. Extract docstring and tool description
    docstring = ast.get_docstring(func_node) or ""
    tool_desc = ""

    # Check decorator args: @mcp.tool(description="...")
    for dec in func_node.decorator_list:
        if isinstance(dec, ast.Call):
            for kw in dec.keywords:
                if kw.arg == "description" and isinstance(kw.value, ast.Constant):
                    tool_desc = str(kw.value.value)

    combined_text = f"{tool_desc} {docstring}".lower()
    if not combined_text.strip():
        return []

    visitor = _CallVisitor()
    visitor.visit(func_node)

    rel_path = os.path.normpath(filepath).replace("\\", "/")
    tool_name = func_node.name

    # Check 1: 'Read-only' claim vs Destructive calls
    is_read_only = any(kw in combined_text for kw in READ_ONLY_KEYWORDS)
    if is_read_only:
        for call_name, line in visitor.calls:
            if call_name in DESTRUCTIVE_CALLS:
                findings.append(
                    Finding(
                        id=f"SP-S0-CLM-{len(findings) + 1:03d}",
                        engine="S0",
                        target=server_name,
                        tool=tool_name,
                        category="CLAIM_CODE_MISMATCH",
                        severity="high",
                        assessment="FAIL",
                        confidence="confirmed",
                        evidence_basis="static",
                        location=Location(file=rel_path, line=line),
                        claim=f"Tool claims to be read-only: '{tool_desc or docstring[:60]}'",
                        evidence=f"Function '{tool_name}' executes destructive call '{call_name}()' on line {line}.",
                        remediation="Remove destructive file/system modifications from read-only tools or re-scope capability declaration.",
                        supporting_rules=["AST_CLAIM_VS_CODE", "CWE-272"]
                    )
                )
        for line in visitor.file_write_opens:
            findings.append(
                Finding(
                    id=f"SP-S0-CLM-{len(findings) + 1:03d}",
                    engine="S0",
                    target=server_name,
                    tool=tool_name,
                    category="CLAIM_CODE_MISMATCH",
                    severity="high",
                    assessment="FAIL",
                    confidence="confirmed",
                    evidence_basis="static",
                    location=Location(file=rel_path, line=line),
                    claim=f"Tool claims to be read-only: '{tool_desc or docstring[:60]}'",
                    evidence=f"Function '{tool_name}' opens a file in write/append mode on line {line}.",
                    remediation="Prohibit write-mode file handles in read-only declared tools.",
                    supporting_rules=["AST_CLAIM_VS_CODE"]
                )
            )

    # Check 2: 'Offline' claim vs Network calls
    is_offline = any(kw in combined_text for kw in OFFLINE_KEYWORDS)
    if is_offline:
        for call_name, line in visitor.calls:
            if call_name in NETWORK_CALLS:
                findings.append(
                    Finding(
                        id=f"SP-S0-CLM-{len(findings) + 1:03d}",
                        engine="S0",
                        target=server_name,
                        tool=tool_name,
                        category="CLAIM_CODE_MISMATCH",
                        severity="high",
                        assessment="FAIL",
                        confidence="confirmed",
                        evidence_basis="static",
                        location=Location(file=rel_path, line=line),
                        claim=f"Tool claims to be offline: '{tool_desc or docstring[:60]}'",
                        evidence=f"Function '{tool_name}' performs outbound network request via '{call_name}' on line {line}.",
                        remediation="Disallow external socket or HTTP connections in tools claiming offline operation.",
                        supporting_rules=["AST_CLAIM_VS_CODE"]
                    )
                )

    # Check 3: 'Math / Formatter' claim vs Process Execution
    is_benign_utility = any(kw in combined_text for kw in CALCULATOR_KEYWORDS)
    if is_benign_utility:
        for call_name, line in visitor.calls:
            if call_name in PROCESS_CALLS:
                findings.append(
                    Finding(
                        id=f"SP-S0-CLM-{len(findings) + 1:03d}",
                        engine="S0",
                        target=server_name,
                        tool=tool_name,
                        category="CLAIM_CODE_MISMATCH",
                        severity="critical",
                        assessment="FAIL",
                        confidence="confirmed",
                        evidence_basis="static",
                        location=Location(file=rel_path, line=line),
                        claim=f"Tool claims benign utility '{tool_name}': '{tool_desc or docstring[:60]}'",
                        evidence=f"Function spawns system shell process via '{call_name}' on line {line}.",
                        remediation="Prohibit shell process invocation in formatting and math utilities.",
                        supporting_rules=["AST_CLAIM_VS_CODE", "CWE-78"]
                    )
                )

    return findings


def run_claim_checker(target_path: str, server_name: str = "target_server") -> List[Finding]:
    """
    Parses all Python files under target_path into AST trees and verifies
    claim vs code consistency.
    """
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

    all_findings: List[Finding] = []

    for file_path in py_files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source = f.read()
            tree = ast.parse(source, filename=file_path)
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                all_findings.extend(_check_tool_function(node, file_path, server_name))

    return all_findings
