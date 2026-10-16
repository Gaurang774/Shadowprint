"""
Finding Normalizer and Clustered Deduplicator.
Spec: Groups multi-engine findings using the formula (file_key, line // 3, category).
When multiple scanners (Bandit, Semgrep, AST, Regex) report the same underlying flaw,
this normalizer merges them into a single authoritative Finding, preserving all
supporting rule IDs and elevating confidence.
"""

from typing import List, Dict, Tuple, Any
import os
from shadowprint.models import Finding, Location

# Precedence orders for merging
SEVERITY_ORDER = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
CONFIDENCE_ORDER = {"confirmed": 3, "corroborated": 2, "heuristic": 1}
ASSESSMENT_ORDER = {"FAIL": 4, "FLAGGED": 3, "NOT_ASSESSED": 2, "PASS": 1}


def _get_cluster_key(finding: Finding) -> Tuple[str, int, str]:
    """
    Computes cluster key (file, line // 3, category).
    Line numbers within 2 lines of each other fall into the same integer division bucket.
    """
    if finding.location and finding.location.file:
        file_key = os.path.normpath(finding.location.file).replace("\\", "/").lower()
    else:
        file_key = finding.target.lower().strip()

    line_bucket = 0
    if finding.location and finding.location.line is not None:
        line_bucket = finding.location.line // 3

    cat_key = finding.category.upper().strip()
    return (file_key, line_bucket, cat_key)


def normalize_findings(findings: List[Finding]) -> List[Finding]:
    """
    Deduplicates and normalizes a list of findings.
    - Clustered by (file, line // 3, category).
    - Preserves highest severity and assessment.
    - Upgrades confidence to 'corroborated' or 'confirmed' when multiple engines agree.
    - Merges supporting_rules into a deduplicated list.
    """
    if not findings:
        return []

    clusters: Dict[Tuple[str, int, str], List[Finding]] = {}
    for f in findings:
        key = _get_cluster_key(f)
        if key not in clusters:
            clusters[key] = []
        clusters[key].append(f)

    merged_findings: List[Finding] = []

    for key, cluster in clusters.items():
        if len(cluster) == 1:
            merged_findings.append(cluster[0])
            continue

        # Multiple findings in the same cluster -> merge them
        # 1. Highest severity
        highest_sev = max(cluster, key=lambda x: SEVERITY_ORDER.get(x.severity, 0)).severity

        # 2. Highest assessment
        highest_assess = max(cluster, key=lambda x: ASSESSMENT_ORDER.get(x.assessment, 0)).assessment

        # 3. Collect unique engines and rules
        engines = {f.engine for f in cluster}
        all_rules: List[str] = []
        for f in cluster:
            for r in f.supporting_rules:
                if r not in all_rules:
                    all_rules.append(r)

        # 4. Confidence elevation
        if len(engines) >= 2 or any(f.confidence == "confirmed" for f in cluster):
            final_conf = "confirmed"
        elif len(cluster) >= 2 or any(f.confidence == "corroborated" for f in cluster):
            final_conf = "corroborated"
        else:
            final_conf = "heuristic"

        # 5. Base representative finding: prefer one with exact line location
        representative = next((f for f in cluster if f.location and f.location.line), cluster[0])

        # 6. Best evidence: pick the longest or most specific evidence string
        best_evidence = max((f.evidence for f in cluster), key=len)
        best_remediation = max((f.remediation for f in cluster), key=len)

        merged = Finding(
            id=representative.id,
            engine=representative.engine,
            target=representative.target,
            tool=representative.tool,
            category=representative.category,
            severity=highest_sev,
            assessment=highest_assess,
            confidence=final_conf,
            evidence_basis=representative.evidence_basis,
            location=representative.location,
            claim=representative.claim or next((f.claim for f in cluster if f.claim), None),
            evidence=best_evidence,
            remediation=best_remediation,
            raw_result_ref=representative.raw_result_ref,
            supporting_rules=all_rules
        )
        merged_findings.append(merged)

    def sort_key(f: Finding):
        sev_rank = SEVERITY_ORDER.get(f.severity, 0)
        line_num = f.location.line if (f.location and f.location.line) else 0
        return (-sev_rank, f.target, line_num)

    merged_findings.sort(key=sort_key)
    return merged_findings
