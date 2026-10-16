# Shadowprint — Antigravity Agent Directive Rules

> **CRITICAL DIRECTIVES:** This file is automatically loaded by the Antigravity IDE. It injects unbreakable guardrails into every agentic execution session.

## 🛑 NON-NEGOTIABLE CORE INVARIANTS
1. **Static Precedence Invariant:** Never launch target MCP servers or Docker sandboxes before Engine S0 static checks (Bandit, Semgrep, Gitleaks, hostile suppression) complete.
2. **Add-Only LLM Authority:** Ollama/Qwen3 is an add-only heuristic judge. It CANNOT suppress, downgrade, or dismiss findings flagged by deterministic regex, AST checks, or kernel syscalls.
3. **Clean Stdio Invariant:** MCP communication is stdio. In the sandbox, redirect strace to `/obs/strace.log` and sink to `/obs/sink.log`. NEVER output raw logs to stdout.
4. **Airgap Guarantee:** Zero cloud LLM APIs (no OpenAI/Anthropic/Gemini keys). Local Ollama (`127.0.0.1:11434`) only.
5. **Universal Schema Contract:** All findings anywhere in the codebase must strictly validate against `shadowprint/models.py` `Finding` Pydantic model.

## 🔒 LOCKED TECH STACK & CONFIGURATION
- **CLI:** Typer + Rich (`shadowprint audit`, `approve`, `watch`, `report`).
- **Static:** Bandit (`-f json`), Semgrep (`mcp_taint_rules.yaml`), Gitleaks (`detect --no-git`).
- **Dynamic:** Docker (`--cap-drop ALL --cap-add SYS_PTRACE --security-opt seccomp=unconfined --network none`).
- **Canary:** Plant `/tmp/canary_creds.env`, intercept in tool return, stdout, or sink.
- **Integrity:** SQLite 3 (`shadowprint.db`), 3-layer SHA-256 (definition, artifact, behavior), `deepdiff`.
- **Rug-Pull Trigger:** Live demo uses `/tmp/rugpull_trigger.flag`.
- **Deduplication Formula:** `(finding.file, finding.line // 3, finding.category)`.

## 👥 50/50 RESPONSIBILITY BOUNDARIES
- **Jasjyot Singh (Builder A):** S0 Static, S1 Metadata & Qwen3, Normalizer, CLI Orchestrator, Terminal UI, Markdown Reporter.
- **Gaurang Udgirkar (Builder B):** Models, Guarded MCP Client, S2 Prober & Syscalls, S3 SQLite & Watcher, SARIF Exporter, Docker sandbox.

## 📋 PRE-EXECUTION CHECKLIST
Always verify:
- Zero cloud API imports.
- Zero non-JSON-RPC stdout output in containers.
- 0 False Positives on `clean_notes`.
- 100% Core Recall on `scripts/test_manifest.py`.
