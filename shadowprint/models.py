"""
Shadowprint Universal Data Contracts (FROZEN CONTRACT).
This module defines the shared data models co-owned by Jasjyot Singh and Gaurang Udgirkar.
Neither teammate may modify these contracts without explicit agreement.
"""

from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field


class Location(BaseModel):
    """File and line coordinates for a detected finding."""
    file: str
    line: Optional[int] = None
    column: Optional[int] = None


class Finding(BaseModel):
    """
    Universal Finding Schema Contract.
    Conforms to Section 5 Universal Finding Schema in archi.md.
    """
    id: str = Field(..., description="Unique finding ID, e.g., SP-S0-001")
    engine: Literal["S0", "S1", "S2", "S3"] = Field(..., description="Detection engine identifier")
    target: str = Field(..., description="Target server or fixture name")
    tool: str = Field(default="__server__", description="Tool name under scrutiny or __server__")
    category: str = Field(..., description="Finding category, e.g., command_injection, prompt_injection")
    severity: Literal["critical", "high", "medium", "low", "info"] = Field(..., description="Severity level")
    assessment: Literal["FAIL", "FLAGGED", "PASS", "NOT_ASSESSED"] = Field(..., description="Verdict status")
    confidence: Literal["confirmed", "corroborated", "heuristic"] = Field(..., description="Confidence level")
    evidence_basis: Literal["static", "metadata", "runtime_observed", "diff"] = Field(..., description="Evidence source")
    location: Optional[Location] = Field(default=None, description="Source code location if applicable")
    claim: Optional[str] = Field(default=None, description="Declared capability or description text")
    evidence: str = Field(..., description="Offending code string, log excerpt, or diff")
    remediation: str = Field(..., description="Prescribed fix or mitigation guidance")
    raw_result_ref: Optional[str] = Field(default=None, description="Path or reference to raw runner output")
    supporting_rules: List[str] = Field(default_factory=list, description="Associated rule IDs or lint codes")


class ToolDefinition(BaseModel):
    """Normalized MCP tool representation."""
    name: str
    description: Optional[str] = ""
    inputSchema: Dict[str, Any] = Field(default_factory=dict)
    annotations: Optional[Dict[str, Any]] = None


class Snapshot(BaseModel):
    """Server metadata snapshot retrieved during inspection."""
    server_name: str
    timestamp: float
    tools: List[ToolDefinition] = Field(default_factory=list)
    prompts: List[Dict[str, Any]] = Field(default_factory=list)
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    definition_hash: str = Field(..., description="SHA-256 of canonical tool definitions")
    artifact_hash: Optional[str] = Field(default=None, description="SHA-256 tree hash of source code")


class BehaviorTuple(BaseModel):
    """Runtime behavior profile observed during Engine S2 dynamic probing."""
    tool_name: str
    openat_paths: List[str] = Field(default_factory=list)
    connect_addrs: List[str] = Field(default_factory=list)
    execve_cmds: List[str] = Field(default_factory=list)
    canary_touched: bool = False
    behavior_hash: str = Field(..., description="SHA-256 hash of recorded syscalls")


class Pin(BaseModel):
    """Approved baseline state stored in SQLite."""
    server_name: str
    pinned_at: float
    definition_hash: str
    artifact_hash: str
    behavior_hash: Optional[str] = None
    approved_by: str = "auditor"
    tools_count: int = 0


class AuditReport(BaseModel):
    """Unified audit report wrapping all findings and snapshot metadata."""
    target: str
    timestamp: float
    status: Literal["PASSED", "FLAGGED", "FAILED"]
    findings: List[Finding] = Field(default_factory=list)
    snapshot: Optional[Snapshot] = None
    summary: Dict[str, int] = Field(default_factory=dict)
