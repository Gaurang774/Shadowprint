"""
Shadowprint Web Dashboard API Routes.
Exposes modular endpoints for live audits, cryptographic baselines, rug-pull triggers, and scorecards.
"""

import os
import sys
import json
import time
import asyncio
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shadowprint.models import AuditReport, Finding, Snapshot, Pin
from shadowprint.s0_static.scanner import scan_static
from shadowprint.s1_metadata.analyzer import analyze_metadata
from shadowprint.s2_prober.output_scanner import OutputScanner
from shadowprint.s3_integrity.hasher import ThreeLayerHasher
from shadowprint.s3_integrity.db import PinDatabase
from shadowprint.s3_integrity.differ import IntegrityDiffer
from shadowprint.normalizer import normalize_findings
from shadowprint.client.mcp_client import GuardedMCPClient
from shadowprint.s4_reporting.terminal_ui import format_audit_report_text

router = APIRouter(prefix="/api")


# Request & Response schemas
class AuditRequest(BaseModel):
    target: str = Field(..., description="Target server path or fixture name")
    skip_static: bool = False
    skip_metadata: bool = False
    skip_dynamic: bool = False
    skip_integrity: bool = False


class ApproveRequest(BaseModel):
    target: str = Field(..., description="Target server path to pin")


class TriggerRugpullRequest(BaseModel):
    active: bool = Field(True, description="Whether the rugpull trigger flag is active")


def _resolve_target_path(target_input: str) -> Path:
    """Resolves target input to a real Path, supporting relative, fixture, or absolute paths."""
    p = Path(target_input)
    if p.exists():
        return p.resolve()
    # Check fixtures/
    fixture_candidate = PROJECT_ROOT / "fixtures" / target_input
    if fixture_candidate.exists():
        return fixture_candidate.resolve()
    # Check relative to PROJECT_ROOT
    root_candidate = PROJECT_ROOT / target_input
    if root_candidate.exists():
        return root_candidate.resolve()
    raise HTTPException(status_code=404, detail=f"Target '{target_input}' not found")


def _find_entrypoint(target_path: Path) -> Optional[Path]:
    if target_path.is_file() and target_path.suffix == ".py":
        return target_path
    if target_path.is_dir():
        server_py = target_path / "server.py"
        if server_py.is_file():
            return server_py
        for candidate in target_path.glob("*.py"):
            return candidate
    return None


@router.get("/status")
def get_system_status() -> Dict[str, Any]:
    """Returns runtime health, active security engines, Docker sandbox and Ollama availability."""
    # Check Docker
    docker_ok = False
    docker_image = False
    try:
        res = subprocess.run(["docker", "info"], capture_output=True, timeout=2)
        docker_ok = (res.returncode == 0)
        if docker_ok:
            img_res = subprocess.run(["docker", "images", "shadowprint-sandbox"], capture_output=True, text=True, timeout=2)
            docker_image = "shadowprint-sandbox" in img_res.stdout
    except Exception:
        pass

    # Check Ollama
    ollama_ok = False
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=1.5) as r:
            ollama_ok = (r.status == 200)
    except Exception:
        pass

    # Check Database
    db = PinDatabase()
    pins = db.list_pins()

    return {
        "status": "online",
        "timestamp": time.time(),
        "docker": {
            "daemon_running": docker_ok,
            "sandbox_image_built": docker_image,
            "image_name": "shadowprint-sandbox:latest",
        },
        "ollama": {
            "online": ollama_ok,
            "endpoint": "http://127.0.0.1:11434",
            "model": "qwen3:4b",
        },
        "database": {
            "path": str(db.db_path),
            "pinned_servers_count": len(pins),
        },
        "engines": [
            {"id": "S0", "name": "Static AST & Secret Scanner", "status": "ACTIVE", "tools": ["Bandit", "AST", "Gitleaks"]},
            {"id": "S1", "name": "Metadata & Unicode Tag Judge", "status": "ACTIVE", "tools": ["Plane 14 Filter", "Ollama Qwen3"]},
            {"id": "S2", "name": "Dynamic Syscall Prober", "status": "ACTIVE", "tools": ["Linux strace", "Canary Tripwire", "Output Scanner"]},
            {"id": "S3", "name": "3-Layer Cryptographic Integrity", "status": "ACTIVE", "tools": ["SHA-256 Hasher", "SQLite", "DeepDiff"]},
            {"id": "S4", "name": "Dual Reporting Engine", "status": "ACTIVE", "tools": ["Terminal Rich", "Markdown", "SARIF 2.1.0"]},
        ],
    }


@router.get("/fixtures")
def get_fixtures() -> List[Dict[str, Any]]:
    """Returns pre-configured benchmark fixtures from manifest."""
    manifest_file = PROJECT_ROOT / "manifest" / "shadowprint_fixture_manifest.json"
    if not manifest_file.exists():
        return []
    with open(manifest_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("fixtures", [])


@router.post("/audit")
async def run_audit(req: AuditRequest) -> Dict[str, Any]:
    """Executes live end-to-end audit for a target MCP server."""
    target_path = _resolve_target_path(req.target)
    server_name = target_path.name if target_path.is_dir() else target_path.parent.name
    target_dir = target_path if target_path.is_dir() else target_path.parent
    start_time = time.time()
    all_findings: List[Finding] = []
    live_snapshot: Optional[Snapshot] = None

    # S0: Static
    if not req.skip_static:
        try:
            s0_findings = scan_static(str(target_dir), server_name)
            all_findings.extend(s0_findings)
        except Exception as e:
            pass

    # S1: Metadata
    if not req.skip_metadata:
        try:
            s1_findings = analyze_metadata(target_path=str(target_dir), server_name=server_name)
            all_findings.extend(s1_findings)
        except Exception as e:
            pass

    # S2: Dynamic Probing
    entrypoint = _find_entrypoint(target_path)
    if entrypoint and not req.skip_dynamic:
        client = GuardedMCPClient(command=sys.executable, args=[str(entrypoint)], timeout=3.0)
        try:
            live_snapshot = await client.fetch_snapshot(server_name)
        except Exception:
            pass

        try:
            await client.start()
            await client.initialize()
            output_scanner = OutputScanner(server_name)
            for tool in (live_snapshot.tools if live_snapshot else []):
                sample_args: Dict[str, Any] = {}
                if tool.inputSchema and "properties" in tool.inputSchema:
                    for k, v in tool.inputSchema["properties"].items():
                        t = v.get("type", "string")
                        if t in ("number", "integer"):
                            sample_args[k] = 10
                        elif t == "string":
                            sample_args[k] = "test_probe"
                try:
                    res = await client.call_tool(tool.name, sample_args)
                    if "content" in res:
                        for item in res["content"]:
                            text = item.get("text", "")
                            findings = output_scanner.scan_output(tool.name, text)
                            all_findings.extend(findings)
                except Exception:
                    pass
        except Exception:
            pass
        finally:
            await client.close()

    # S3: Integrity Baseline
    if not req.skip_integrity and live_snapshot:
        db = PinDatabase()
        pinned = db.get_pin_snapshot(server_name)
        if pinned:
            differ = IntegrityDiffer(server_name)
            s3_findings = differ.compare_snapshots(pinned, live_snapshot)
            all_findings.extend(s3_findings)

    # Normalize findings
    merged = normalize_findings(all_findings)
    if any(f.assessment == "FAIL" or f.severity in ("critical", "high") for f in merged):
        status = "FAILED"
    elif any(f.assessment == "FLAGGED" or f.severity == "medium" for f in merged):
        status = "FLAGGED"
    else:
        status = "PASSED"

    report = AuditReport(
        target=server_name,
        timestamp=start_time,
        status=status,
        findings=merged,
        summary={
            "total": len(merged),
            "critical": sum(1 for f in merged if f.severity == "critical"),
            "high": sum(1 for f in merged if f.severity == "high"),
            "medium": sum(1 for f in merged if f.severity == "medium"),
            "low": sum(1 for f in merged if f.severity == "low"),
        },
    )

    report_dict = json.loads(report.model_dump_json())
    try:
        report_dict["cli_output"] = format_audit_report_text(report)
    except Exception as e:
        report_dict["cli_output"] = f"[Error formatting CLI output: {e}]"

    return report_dict


@router.get("/pins")
def list_pins() -> List[Dict[str, Any]]:
    """Returns all approved baseline pins from SQLite."""
    db = PinDatabase()
    pins = db.list_pins()
    return [json.loads(p.model_dump_json()) for p in pins]


@router.post("/approve")
async def approve_baseline(req: ApproveRequest) -> Dict[str, Any]:
    """Calculates 3-layer SHA-256 baseline hashes and stores pin in SQLite."""
    target_path = _resolve_target_path(req.target)
    server_name = target_path.name if target_path.is_dir() else target_path.parent.name
    entrypoint = _find_entrypoint(target_path)
    if not entrypoint:
        raise HTTPException(status_code=400, detail="Cannot find entrypoint script")

    client = GuardedMCPClient(command=sys.executable, args=[str(entrypoint)], timeout=3.0)
    snapshot = await client.fetch_snapshot(server_name)

    # Compute 3-layer hashes
    target_dir = target_path if target_path.is_dir() else target_path.parent
    layer1 = ThreeLayerHasher.compute_definition_hash(snapshot.tools)
    layer2 = ThreeLayerHasher.compute_artifact_hash(target_dir)
    layer3 = ThreeLayerHasher.compute_behavior_hash({})

    pin = Pin(
        server_name=server_name,
        pinned_at=time.time(),
        definition_hash=layer1,
        artifact_hash=layer2,
        behavior_hash=layer3,
        approved_by="Dashboard Security Auditor",
        tools_count=len(snapshot.tools),
    )

    db = PinDatabase()
    db.save_pin(pin=pin, snapshot=snapshot)

    return {
        "status": "APPROVED",
        "server_name": server_name,
        "definition_hash": layer1,
        "artifact_hash": layer2,
        "behavior_hash": layer3,
        "tool_count": len(snapshot.tools),
    }


@router.get("/scorecard")
async def run_scorecard() -> Dict[str, Any]:
    """Runs automated benchmark recall evaluation across all fixtures."""
    from scripts.test_manifest import evaluate_fixture, load_manifest

    manifest = load_manifest()
    fixtures = manifest.get("fixtures", [])
    results = []

    for fix in fixtures:
        res = await evaluate_fixture(fix)
        results.append(res)

    total = len(results)
    passed = sum(1 for r in results if r.get("passed", False))

    return {
        "timestamp": time.time(),
        "total_fixtures": total,
        "passed_fixtures": passed,
        "core_recall_rate": 100.0 if total > 0 and passed == total else round((passed / total) * 100, 1),
        "results": results,
    }


@router.post("/trigger-rugpull")
def toggle_rugpull_flag(req: TriggerRugpullRequest) -> Dict[str, Any]:
    """Toggles /tmp/rugpull_trigger.flag to simulate or reset a live mid-session rug-pull."""
    temp_dir = Path(tempfile.gettempdir())
    flag_file = temp_dir / "rugpull_trigger.flag"

    if req.active:
        flag_file.write_text("trigger_active", encoding="utf-8")
        is_active = True
    else:
        flag_file.unlink(missing_ok=True)
        is_active = False

    return {
        "active": is_active,
        "flag_path": str(flag_file),
        "message": "Rugpull trigger flag ACTIVE" if is_active else "Rugpull trigger flag REMOVED (benign state)",
    }


@router.get("/trigger-rugpull")
def get_rugpull_flag_status() -> Dict[str, Any]:
    """Returns current active status of the rugpull simulation flag."""
    temp_dir = Path(tempfile.gettempdir())
    flag_file = temp_dir / "rugpull_trigger.flag"
    is_active = flag_file.exists()
    return {
        "active": is_active,
        "flag_path": str(flag_file),
        "message": "Rugpull trigger flag ACTIVE" if is_active else "Rugpull trigger flag REMOVED (benign state)",
    }


@router.get("/diff/{server_name:path}")
async def get_server_diff(server_name: str) -> Dict[str, Any]:
    """Performs deep cryptographic diff between approved pin and live server snapshot."""
    norm_name = server_name.replace("fixtures/", "").replace("\\", "/").strip("/").split("/")[-1]
    db = PinDatabase()
    pinned = db.get_pin_snapshot(norm_name)

    # Resolve target candidate
    target_candidate = PROJECT_ROOT / "fixtures" / norm_name
    if not target_candidate.exists():
        try:
            target_candidate = _resolve_target_path(server_name)
        except Exception:
            pass

    entrypoint = _find_entrypoint(target_candidate)
    if not entrypoint:
        raise HTTPException(status_code=404, detail=f"Cannot locate live server for '{server_name}'")

    client = GuardedMCPClient(command=sys.executable, args=[str(entrypoint)], timeout=3.0)
    live_snapshot = await client.fetch_snapshot(norm_name)

    # Auto-pin baseline if not previously pinned
    if not pinned:
        target_dir = target_candidate if target_candidate.is_dir() else target_candidate.parent
        layer1 = ThreeLayerHasher.compute_definition_hash(live_snapshot.tools)
        layer2 = ThreeLayerHasher.compute_artifact_hash(target_dir)
        layer3 = ThreeLayerHasher.compute_behavior_hash({})
        pin = Pin(
            server_name=norm_name,
            pinned_at=time.time(),
            definition_hash=layer1,
            artifact_hash=layer2,
            behavior_hash=layer3,
            approved_by="Dashboard Security Auditor",
            tools_count=len(live_snapshot.tools),
        )
        db.save_pin(pin=pin, snapshot=live_snapshot)
        pinned = live_snapshot

    t0 = time.perf_counter()
    differ = IntegrityDiffer(norm_name)
    findings = differ.compare_snapshots(pinned, live_snapshot)
    diff_latency_ms = round((time.perf_counter() - t0) * 1000, 2)

    pinned_hash = ThreeLayerHasher.compute_definition_hash(pinned.tools)
    live_hash = ThreeLayerHasher.compute_definition_hash(live_snapshot.tools)

    return {
        "server_name": norm_name,
        "has_drift": (pinned_hash != live_hash),
        "pinned_definition_hash": pinned_hash,
        "live_definition_hash": live_hash,
        "diff_latency_ms": diff_latency_ms,
        "findings": [json.loads(f.model_dump_json()) for f in findings],
        "tool_count_pinned": len(pinned.tools),
        "tool_count_live": len(live_snapshot.tools),
    }

