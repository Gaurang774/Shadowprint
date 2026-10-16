"""
Engine S1: Deterministic Metadata & Prompt Injection Detection Rules.
Spec: High-precision regex and unicode analysis detecting:
  1. Unicode TAG characters (U+E0000 to U+E007F).
  2. Zero-width spaces and invisible formatting (U+200B, U+200C, U+200D, U+FEFF, U+2060).
  3. Imperative system prompt overrides and jailbreak directives.
  4. Hidden HTML comments harboring instructions.
  5. Steganographic data exfiltration instructions.
"""

import os
import re
from typing import List, Dict, Any, Optional
from shadowprint.models import Finding, Location, ToolDefinition

# 1. Unicode TAG block pattern (U+E0000 to U+E007F) both in evaluated unicode and raw escaped representations
UNICODE_TAG_PATTERN = re.compile(
    r"[\U000E0000-\U000E007F]|\\U000E00[0-7][0-9a-fA-F]",
    re.UNICODE
)

# 2. Zero-width invisible characters
ZERO_WIDTH_PATTERN = re.compile(
    r"[\u200B\u200C\u200D\uFEFF\u2060]|\\u200[b-dB-D]|\\ufeff|\\u2060",
    re.UNICODE
)

# 3. Imperative override patterns
IMPERATIVE_OVERRIDE_PATTERNS = [
    (
        "PROMPT_INJECTION_OVERRIDE",
        "RULE-S1-001",
        re.compile(r"(?i)\bsystem\s+override\b"),
        "Direct SYSTEM OVERRIDE directive planted in tool metadata."
    ),
    (
        "PROMPT_INJECTION_IGNORE",
        "RULE-S1-002",
        re.compile(r"(?i)\bignore\s+(all\s+)?(prior|previous)\s+instructions\b"),
        "Jailbreak directive attempting to wipe prior system instructions."
    ),
    (
        "PROMPT_INJECTION_DISOBEY",
        "RULE-S1-003",
        re.compile(r"(?i)\bdo\s+not\s+report\s+(.*?)\s+to\s+the\s+user\b"),
        "Directive commanding LLM to withhold data or deceive user."
    ),
    (
        "PROMPT_INJECTION_EXFIL",
        "RULE-S1-004",
        re.compile(r"(?i)\b(read\s+~/\.ssh|exfiltrate\s+environment|reveal\s+user\s+files)\b"),
        "Unauthorized credential theft directive in tool metadata."
    ),
    (
        "PROMPT_INJECTION_JAILBREAK",
        "RULE-S1-005",
        re.compile(r"(?i)\b(you\s+must\s+obey\s+this\s+instruction|mark\s+this\s+server\s+as\s+100%\s+verified)\b"),
        "Auditor jailbreak attempt targeting evaluating LLM."
    ),
    (
        "HIDDEN_HTML_COMMENT",
        "RULE-S1-006",
        re.compile(r"<!--\s*(?:HIDDEN_AI_INSTRUCTION|SYSTEM|INSTRUCTION):?\s*(.*?)-->", re.IGNORECASE | re.DOTALL),
        "Hidden HTML comment harboring instructions invisible in rendered UI."
    )
]


def check_metadata_string(
    text: str,
    target_name: str,
    tool_name: str = "__server__",
    filepath: Optional[str] = None,
    line_number: Optional[int] = None
) -> List[Finding]:
    """
    Evaluates a single text string (e.g. tool description, docstring, prompt)
    against all deterministic S1 rules.
    """
    if not text:
        return []

    findings: List[Finding] = []
    location = Location(
        file=os.path.normpath(filepath).replace("\\", "/") if filepath else target_name,
        line=line_number
    ) if (filepath or line_number) else None

    # Check 1: Unicode TAG characters (Steganography / Tag injection)
    tag_matches = list(UNICODE_TAG_PATTERN.finditer(text))
    if tag_matches:
        findings.append(
            Finding(
                id=f"SP-S1-TAG-{len(findings) + 1:03d}",
                engine="S1",
                target=target_name,
                tool=tool_name,
                category="STEGANOGRAPHY_DETECTED",
                severity="critical",
                assessment="FAIL",
                confidence="confirmed",
                evidence_basis="metadata",
                location=location,
                claim=f"Declared tool metadata for '{tool_name}'",
                evidence=f"Discovered {len(tag_matches)} Unicode TAG characters (U+E0000 - U+E007F) hidden in metadata.",
                remediation="Strip all Unicode TAG characters and non-printable control blocks from tool descriptions.",
                supporting_rules=["UNICODE_TAG_DETECTION", "CWE-20"]
            )
        )

    # Check 2: Zero-width spaces / invisible characters
    zw_matches = list(ZERO_WIDTH_PATTERN.finditer(text))
    if zw_matches:
        findings.append(
            Finding(
                id=f"SP-S1-ZWS-{len(findings) + 1:03d}",
                engine="S1",
                target=target_name,
                tool=tool_name,
                category="STEGANOGRAPHY_DETECTED",
                severity="high",
                assessment="FAIL",
                confidence="confirmed",
                evidence_basis="metadata",
                location=location,
                claim=f"Declared tool metadata for '{tool_name}'",
                evidence=f"Discovered {len(zw_matches)} zero-width invisible characters (U+200B/C/D, U+FEFF) in metadata.",
                remediation="Remove zero-width non-printable characters from tool metadata.",
                supporting_rules=["ZERO_WIDTH_DETECTION"]
            )
        )

    # Check 3: Imperative override and prompt injection directives
    for category, rule_id, pattern, desc in IMPERATIVE_OVERRIDE_PATTERNS:
        matches = list(pattern.finditer(text))
        for m in matches:
            snippet = m.group(0).strip()
            # Capture surrounding context for clear evidence
            start_idx = max(0, m.start() - 20)
            end_idx = min(len(text), m.end() + 40)
            context = text[start_idx:end_idx].replace("\n", " ").strip()

            findings.append(
                Finding(
                    id=f"SP-S1-INJ-{len(findings) + 1:03d}",
                    engine="S1",
                    target=target_name,
                    tool=tool_name,
                    category="PROMPT_INJECTION",
                    severity="critical",
                    assessment="FAIL",
                    confidence="confirmed",
                    evidence_basis="metadata",
                    location=location,
                    claim=f"Declared tool metadata for '{tool_name}'",
                    evidence=f"[{rule_id}] {desc}\nSnippet: '...{context}...'",
                    remediation="Remove imperative prompt overrides and jailbreak directives from tool schemas.",
                    supporting_rules=[rule_id, "CWE-20"]
                )
            )

    return findings


def scan_tool_definitions(
    tools: List[ToolDefinition],
    server_name: str
) -> List[Finding]:
    """
    Scans a list of ToolDefinition objects (retrieved from live MCP tools/list)
    using deterministic rules.
    """
    findings: List[Finding] = []
    for tool in tools:
        # Check tool description
        if tool.description:
            findings.extend(
                check_metadata_string(
                    tool.description,
                    target_name=server_name,
                    tool_name=tool.name
                )
            )
        # Check parameter schema descriptions
        properties = tool.inputSchema.get("properties", {}) if tool.inputSchema else {}
        for param_name, param_info in properties.items():
            if isinstance(param_info, dict) and "description" in param_info:
                findings.extend(
                    check_metadata_string(
                        param_info["description"],
                        target_name=server_name,
                        tool_name=f"{tool.name}.{param_name}"
                    )
                )

    return findings


def scan_source_metadata(
    target_path: str,
    server_name: str
) -> List[Finding]:
    """
    Scans Python source files directly for string literals or descriptions
    containing Unicode tags or prompt injections.
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

    findings: List[Finding] = []
    for filepath in py_files:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            continue

        for line_idx, line in enumerate(lines, start=1):
            findings.extend(
                check_metadata_string(
                    text=line,
                    target_name=server_name,
                    tool_name="__server__",
                    filepath=filepath,
                    line_number=line_idx
                )
            )

    return findings
