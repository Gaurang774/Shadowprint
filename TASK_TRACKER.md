# Shadowprint — Official Dual-Builder Task Tracker & 10-Hour Execution State

> **State of the World:** Real-time synchronized progress tracker across the 10-hour hackathon execution timeline.  
> **Shared Master Tracker:** This document is the single source of truth for both **Jasjyot Singh (JJ)** (`feat/jasjyot`) and **Gaurang Udgirkar** (`feat/gaurang`).  
> **Zero Merge Conflict Protocol:** Each builder works strictly within their own assigned file paths. Neither teammate edits the other's files.

---

## ⏱️ Timeline Phases Status (10-Hour Roadmap)

| Phase | Window | Stage & Objective | Status | Lead / Owners |
|---|---|---|---|---|
| **Phase 1** | 00:00 – 00:45 | Contracts Freeze (`shadowprint/models.py`), Preflight Checks & Git Setup | ✅ **100% COMPLETED** | Both (Jasjyot & Gaurang) |
| **Phase 2** | 00:45 – 03:00 | Parallel Deep Sprint 1 (S0/S1-Rules, Qwen3 AI Judge, Docker Sandbox, Guarded Client) | 🔄 **IN PROGRESS** (Gaurang 60% done; JJ active) | Independent Branches |
| **Phase 3** | 03:00 – 03:30 | **Integration Checkpoint 1:** Stdio Cleanliness Test & Merge `main` | ⏳ PENDING | Both (Together) |
| **Phase 4** | 03:30 – 05:30 | Parallel Deep Sprint 2 (S2 Prober/Syscalls, S3 Hashes/Watcher, S4 Reports/SARIF) | ⏳ PENDING | Independent Branches |
| **Phase 5** | 05:30 – 06:15 | **Integration Checkpoint 2:** Full Pipeline Wiring & Merge into `main` | ⏳ PENDING | Both (Together) |
| **Phase 6** | 06:15 – 07:30 | Live Rug-Pull & Scorecard Test (`scripts/test_manifest.py`, touch flag demo) | ⏳ PENDING | Both (Together) |
| **Phase 7** | 07:30 – 08:00 | **ABSOLUTE CODE FREEZE** (`git tag demo-v1` — Zero new code) | ⏳ PENDING | Both (Together) |
| **Phase 8** | 08:00 – 09:00 | Buffer Hour & Airgap Test (Emergency fixes, zero cloud verify, slide sync) | ⏳ PENDING | Both (Together) |
| **Phase 9** | 09:00 – 09:40 | Judging Rehearsals (2x 8-minute timed dress rehearsals) | ⏳ PENDING | Both (Together) |
| **Phase 10**| 09:40 – 10:00 | Backup Video Recording & Standby (`demo_backup.mp4`) | ⏳ PENDING | Both (Together) |

---

## 🤝 The Zero-Conflict Merging Protocol

To ensure 100% seamless merges at Phase 3 and Phase 5 with **ZERO Git merge conflicts**:
1. **Branch Isolation:**
   * Jasjyot commits exclusively to `feat/jasjyot`.
   * Gaurang commits exclusively to `feat/gaurang`.
2. **Strict File Boundaries:**
   * Jasjyot only modifies files in Section 1 below.
   * Gaurang only modifies files in Section 2 below.
   * Neither teammate edits `shadowprint/models.py` (FROZEN CONTRACT).
3. **Synchronizing with `main`:**
   Before merging or starting a new phase:
   ```bash
   git fetch origin
   git merge origin/main
   ```
4. **Integration Checkpoints:**
   At Phase 3 and Phase 5, both branches merge into `main` sequentially, run `scripts/test_manifest.py`, and push the unified state.

---

## 📁 File Delivery Matrix & Progress

### 🌐 Shared Foundation & Project Governance (Complete)
- [x] [PS.md](file:///d:/ShadowPrint/Shadowprint/PS.md) — Problem Statement PS02 (MCP Security Auditor)
- [x] [AI_ONBOARDING.md](file:///d:/ShadowPrint/Shadowprint/AI_ONBOARDING.md) — 60-Second Crash Course & Ground Truth Table
- [x] [PROJECT_RULES.md](file:///d:/ShadowPrint/Shadowprint/PROJECT_RULES.md) — The Supreme Constitution & Anti-Hallucination Checklist
- [x] [.agents/rules/project_rules.md](file:///d:/ShadowPrint/Shadowprint/.agents/rules/project_rules.md) — Antigravity Auto-Loaded Directives
- [x] [ENGINEERING_DECISIONS.md](file:///d:/ShadowPrint/Shadowprint/ENGINEERING_DECISIONS.md) — 11 Architecture Decision Records (ADRs)
- [x] [ARCHITECTURE_AND_STRUCTURE.md](file:///d:/ShadowPrint/Shadowprint/ARCHITECTURE_AND_STRUCTURE.md) — Complete System Architecture & Repository Map
- [x] [info.md](file:///d:/ShadowPrint/Shadowprint/info.md) / [reviced_timeline.md](file:///d:/ShadowPrint/Shadowprint/reviced_timeline.md) — Master Balanced 50/50 Strategy & 10-Hour Timeline
- [x] [WORK_LOG.md](file:///d:/ShadowPrint/Shadowprint/WORK_LOG.md) — Verifiable Evidence & Test Progress Log
- [x] [requirements.txt](file:///d:/ShadowPrint/Shadowprint/requirements.txt) — Pinned exact modern dependencies
- [x] [.gitignore](file:///d:/ShadowPrint/Shadowprint/.gitignore) — Ignores `/obs`, `shadowprint.db`, `.venv`, `output/`
- [x] [Makefile](file:///d:/ShadowPrint/Shadowprint/Makefile) — Developer workflow targets (`make preflight`, `make audit`, `make test`)
- [x] [pyproject.toml](file:///d:/ShadowPrint/Shadowprint/pyproject.toml) — Package definition & CLI entrypoint
- [x] [shadowprint/models.py](file:///d:/ShadowPrint/Shadowprint/shadowprint/models.py) — Universal frozen Pydantic contracts (`Finding`, `Snapshot`, `Pin`, `BehaviorTuple`)
- [x] [scripts/preflight_check.py](file:///d:/ShadowPrint/Shadowprint/scripts/preflight_check.py) — Automated environment sanity validator (Docker, Ollama, Python)

---

### 👤 SECTION 1: Jasjyot Singh (JJ) — Branch: `feat/jasjyot`
> **Domain:** Host Python Space · Static AST Analysis (S0), Metadata Regex (S1), CLI Orchestration, and All Reporting (S4: Markdown, Rich Terminal UI, SARIF 2.1.0).

#### Engine S0: Static Code & Config Inspection
- [ ] `shadowprint/s0_static/scanner.py` — S0 Master orchestrator & hostile `#nosec` / `#nosemgrep` suppression detection
- [ ] `shadowprint/s0_static/bandit_runner.py` — Bandit AST linter runner (`-f json`, flags `B301`, `B602`, `B310`)
- [ ] `shadowprint/s0_static/semgrep_runner.py` — Semgrep taint tracking runner for untrusted tool arguments
- [ ] `shadowprint/s0_static/gitleaks_runner.py` — Offline Gitleaks scanner for API keys, AWS tokens, secrets
- [ ] `shadowprint/s0_static/claim_code_checker.py` — AST comparator checking declared tool claims vs implemented code
- [ ] `shadowprint/s0_static/rules/mcp_taint_rules.yaml` — Custom YAML taint rules for MCP execution sinks

#### Engine S1: Metadata Deterministic Rules & Normalizer
- [ ] `shadowprint/s1_metadata/deterministic_rules.py` — High-precision regex for Unicode TAGs (`\uE000`), zero-width spaces, and imperative overrides
- [ ] `shadowprint/s1_metadata/analyzer.py` — S1 Master orchestrator merging deterministic rule findings with Qwen3 quotes
- [ ] `shadowprint/normalizer.py` — Clustered deduplication formula `(file, line // 3, category)`

#### Engine S4: Unified Reporting & CLI
- [ ] `shadowprint/cli.py` — Typer CLI orchestrator (`shadowprint audit`, `approve`, `watch`, `report`)
- [ ] `shadowprint/s4_reporting/terminal_ui.py` — Rich color-coded terminal dashboard, status cards, and summary table
- [ ] `shadowprint/s4_reporting/markdown_reporter.py` — Complete Markdown report generator (`output/shadowprint_report.md`)
- [ ] `shadowprint/s4_reporting/sarif_exporter.py` — Official OASIS SARIF 2.1.0 JSON exporter with CWE mappings

#### Assigned Test Fixtures & Stage Scripts
- [ ] `fixtures/clean_notes/server.py` — **Fixture 1:** Benign notes CRUD tool (0 False Positives control)
- [ ] `fixtures/poisoned_weather/server.py` — **Fixture 2:** Unicode TAG prompt injection in description
- [ ] `fixtures/vulnerable_runner/server.py` — **Fixture 3:** `subprocess.Popen(shell=True)` + hardcoded AWS key
- [ ] `fixtures/attack_the_auditor/server.py` — **Fixture 6:** Malicious `#nosec` / `#nosemgrep` suppression bypass
- [ ] `scripts/trigger_rugpull.py` — Demo trigger touching `/tmp/rugpull_trigger.flag` on command

---

### 👤 SECTION 2: Gaurang Udgirkar — Branch: `feat/gaurang`
> **Domain:** Container & Protocol Space · Local Ollama Qwen3 AI Judge, Docker Sandboxing, Guarded MCP Client, Dynamic Prober (S2), SQLite Integrity & Diffing (S3).

#### Engine S1: Local Offline Ollama Qwen3 AI Judge
- [x] `shadowprint/s1_metadata/prompt_guard.py` — Fast heuristic & Plane 14 Unicode TAG injection pre-filter (**TESTED & PASSED**)
- [x] `shadowprint/s1_metadata/qwen_judge.py` — Offline Ollama Qwen3 caller, `temperature=0`, `format="json"`, Add-Only Authority (**TESTED & PASSED**)

#### Container Sandbox & Guarded MCP Stdio Client
- [x] `docker/sink.py` — In-container silent HTTP sink on `127.0.0.1:8080` logging strictly to `/obs/sink.log` (**TESTED & PASSED**)
- [x] `docker/entrypoint.sh` — Supervisor script with background sink cleanup, canary planting, and clean stdio strace redirection (**TESTED & PASSED**)
- [x] `docker/Dockerfile.sandbox` — `shadowprint-sandbox:latest` container image with Linux `strace` (**BUILT & VERIFIED**)
- [x] `shadowprint/client/mcp_client.py` — Guarded least-capability stdio client with 5s timeout, sampling rejection, and Layer 1 definition hashing (**TESTED & PASSED**)

#### Engine S2: Dynamic Prober & Kernel Syscall Sandbox
- [ ] `shadowprint/s2_prober/syscall_parser.py` — Parses `/obs/strace.log` for kernel events (`openat`, `connect`, `execve`)
- [ ] `shadowprint/s2_prober/canary_tripwire.py` — Verifies if `/tmp/canary_creds.env` or `CANARY_KEY_98721X` was accessed or leaked
- [ ] `shadowprint/s2_prober/output_scanner.py` — Scans tool returns for Markdown exfiltration (`![exfil](http://.../?key=...)`), HTML, or base64
- [ ] `shadowprint/s2_prober/capability_model.py` — Flags mismatches between declared capabilities vs observed syscalls
- [ ] `shadowprint/s2_prober/prober.py` — 10-call Burst Probe Sweep orchestrator returning structured [Finding](file:///d:/ShadowPrint/Shadowprint/shadowprint/models.py#L19-L33) objects

#### Engine S3: Integrity & Pin-and-Diff Engine
- [ ] `shadowprint/s3_integrity/hasher.py` — 3-layer SHA-256 fingerprint calculator (`definition_hash`, `artifact_hash`, `behavior_hash`)
- [ ] `shadowprint/s3_integrity/db.py` — SQLite persistence layer (`shadowprint.db`) for baseline [Pin](file:///d:/ShadowPrint/Shadowprint/shadowprint/models.py#L58-L67) records
- [ ] `shadowprint/s3_integrity/differ.py` — Deep structural diff via `deepdiff` with character escaping for zero-width / invisible characters
- [ ] `shadowprint/s3_integrity/watcher.py` — 2-second live polling loop raising instant red alerts upon definition drift

#### Assigned Test Fixtures & Scorecard Validator
- [ ] `fixtures/clean_fetch/server.py` — **Fixture 1b:** Benign fetch tool (0 False Positives control)
- [ ] `fixtures/exfil_calculator/server.py` — **Fixture 4:** Obfuscated key theft + sink egress tool
- [ ] `fixtures/rugpull_suite/server.py` — **Fixture 5:** Dynamic schema mutation evaluated upon `/tmp/rugpull_trigger.flag` touch
- [ ] `manifest/shadowprint_fixture_manifest.json` — Expected findings ground truth for all 7 fixtures
- [ ] `scripts/test_manifest.py` — Automated scorecard validator proving 100% core recall

---

## 🎯 Benchmark Fixture Recall Matrix

| Fixture | Expected Caught Issues | Catching Engine | Pass Criteria | Status | Assigned Builder |
|---|---|---|---|---|---|
| `clean_notes` | None | None | **0 False Positives** (CLEAN) | ⏳ Not tested | Jasjyot |
| `clean_fetch` | None | None | **0 False Positives** (CLEAN) | ⏳ Not tested | Gaurang |
| `poisoned_weather` | Prompt injection in description via Unicode TAGs | S1 (Regex + Qwen3) | Caught & exact quote extracted | ⏳ Not tested | Jasjyot |
| `vulnerable_runner` | `subprocess.Popen(shell=True)` + hardcoded AWS secret | S0 (Bandit + Gitleaks) | Exact line-level findings | ⏳ Not tested | Jasjyot |
| `exfil_calculator` | Canary file read + localhost sink egress | S2 (Syscall + Sink) | Exfiltration confirmed & flagged | ⏳ Not tested | Gaurang |
| `rugpull_suite` | Definition mutation upon flag touch | S3 (Watcher + Diff) | Red alert in $<1.5$s with char diff | ⏳ Not tested | Gaurang |
| `attack_the_auditor` | `#nosec` / `#nosemgrep` suppression comments | S0 Scanner Hardening | Suppressions flagged as `TAMPER_ATTEMPT` | ⏳ Not tested | Jasjyot |
