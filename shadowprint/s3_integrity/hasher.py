"""
Shadowprint S3 Integrity Engine: 3-Layer Cryptographic Hasher.
Owner: Gaurang Udgirkar [G]

Computes the 3-layer SHA-256 security fingerprint (ADR-005):
  - Layer 1 (Definition Hash): Canonical JSON serialization of tool names, descriptions, schemas.
  - Layer 2 (Artifact Hash): Merkle-composite SHA-256 of all source files (.py, .json, .toml, .yaml).
  - Layer 3 (Behavior Hash): Normalized composite hash of observed kernel syscall sequences.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
from shadowprint.models import ToolDefinition, BehaviorTuple

# Directories and files excluded from artifact hash
IGNORED_DIRS = {
    ".git", "__pycache__", ".venv", "venv", ".pytest_cache",
    "obs", "output", "dist", "build", ".egg-info",
}
SOURCE_EXTENSIONS = {
    ".py", ".json", ".yaml", ".yml", ".toml", ".sh", ".env", ".txt", ".md",
}


class ThreeLayerHasher:
    """Calculates independent cryptographic hashes across definition, artifact, and behavior."""

    @staticmethod
    def compute_definition_hash(tools: List[ToolDefinition]) -> str:
        """
        Layer 1: Canonical SHA-256 of tool schemas, descriptions, and parameter definitions.
        Sorted by tool name with key sorting and whitespace stripping.
        """
        raw_defs = [
            {
                "name": t.name,
                "description": (t.description or "").strip(),
                "inputSchema": t.inputSchema or {},
            }
            for t in sorted(tools, key=lambda x: x.name)
        ]
        canonical_json = json.dumps(raw_defs, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    @staticmethod
    def compute_artifact_hash(directory: Union[str, Path]) -> str:
        """
        Layer 2: Composite Merkle-style SHA-256 of all source code files in the directory.
        Ignores virtual environments, git metadata, and observation output logs.
        """
        dir_path = Path(directory)
        if not dir_path.is_dir():
            if dir_path.is_file():
                # Single file target
                return hashlib.sha256(dir_path.read_bytes()).hexdigest()
            return "0" * 64

        file_hashes: List[str] = []

        # Recursively scan files in deterministic lexicographical order
        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.endswith(".egg-info")]

            for file in sorted(files):
                file_path = Path(root) / file
                if file_path.suffix.lower() in SOURCE_EXTENSIONS or file in ("Dockerfile", "Makefile"):
                    try:
                        rel_path = file_path.relative_to(dir_path).as_posix()
                        content = file_path.read_bytes()
                        content_sha = hashlib.sha256(content).hexdigest()
                        file_hashes.append(f"{rel_path}:{content_sha}")
                    except Exception:
                        continue

        if not file_hashes:
            return "0" * 64

        # Hash the combined sorted list of relative path and content hashes
        composite_content = "\n".join(sorted(file_hashes)).encode("utf-8")
        return hashlib.sha256(composite_content).hexdigest()

    @staticmethod
    def compute_behavior_hash(behaviors: Dict[str, BehaviorTuple]) -> str:
        """
        Layer 3: Composite SHA-256 of normalized kernel syscall traces across all probed tools.
        """
        if not behaviors:
            return "0" * 64

        canonical_data = [
            {
                "tool_name": tool_name,
                "openat": sorted(b.openat_paths),
                "connect": sorted(b.connect_addrs),
                "execve": sorted(b.execve_cmds),
                "canary_touched": b.canary_touched,
            }
            for tool_name, b in sorted(behaviors.items(), key=lambda item: item[0])
        ]
        canonical_json = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
