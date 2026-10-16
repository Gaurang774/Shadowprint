"""
Engine S1 Master Orchestrator: Metadata & Prompt Injection Analysis.
Combines deterministic regex/unicode rules with optional local AI judge quotes.
Strictly enforces the Add-Only Authority Invariant: LLM cannot suppress or downgrade
deterministic findings.
"""

from typing import List, Optional
from shadowprint.models import Finding, ToolDefinition
from shadowprint.normalizer import normalize_findings
from shadowprint.s1_metadata.deterministic_rules import (
    scan_source_metadata,
    scan_tool_definitions,
    check_metadata_string
)


def analyze_metadata(
    target_path: Optional[str] = None,
    tools: Optional[List[ToolDefinition]] = None,
    server_name: str = "target_server",
    ai_judge_findings: Optional[List[Finding]] = None
) -> List[Finding]:
    """
    Executes S1 metadata and prompt injection analysis.
    1. Runs deterministic unicode and prompt rules on source files (if provided).
    2. Runs deterministic rules on live ToolDefinition schemas (if provided).
    3. Incorporates any AI judge findings adhering to Add-Only Invariant.
    4. Normalizes and deduplicates findings.
    """
    all_findings: List[Finding] = []

    # 1. Scan source metadata
    if target_path:
        source_findings = scan_source_metadata(target_path, server_name)
        all_findings.extend(source_findings)

    # 2. Scan live tool schemas
    if tools:
        tool_findings = scan_tool_definitions(tools, server_name)
        all_findings.extend(tool_findings)

    # 3. Add-Only AI Judge findings (if provided by Gaurang's Qwen3 judge)
    if ai_judge_findings:
        for jf in ai_judge_findings:
            # Ensure AI findings cannot have higher authority than deterministic confirmed rules
            if jf.confidence != "confirmed":
                jf.confidence = "heuristic"
            all_findings.append(jf)

    # 4. Normalize and deduplicate
    return normalize_findings(all_findings)
