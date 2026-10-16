# Shadowprint — Official Balanced Work Division & 10-Hour Timeline

**Project:** Shadowprint — *Every server leaves a trace*  
**Problem Statement:** PS02 — Model Context Protocol (MCP) Server Security Auditor  
**Team Members:** Jasjyot Singh & Gaurang Udgirkar (Equal 50/50 Co-Builders)  
**Execution Structure:** 8 Hours Active Dev & Integration + 2 Hours Dedicated Buffer & Rehearsal

---

## The 50/50 Equalization Strategy (Zero Overburden)

To ensure neither person is overburdened, the workload is split cleanly into two equal domains:
* **Jasjyot Singh:** Owns **Static Code Analysis (S0), Metadata Prompt-Injection Analysis (S1), Deduplication Normalizer, Terminal/Markdown Reporting (S4), and CLI Orchestration**.
* **Gaurang Udgirkar:** Owns **Docker Sandboxing, Guarded MCP Client, Dynamic Kernel Syscall Probing (S2), SQLite 3-Layer Pinning & Live Watcher (S3), and SARIF Exporter**.

Neither teammate is blocked by the other because **Jasjyot develops in pure Python host space** (testing S0/S1 with static code & mock snapshots), while **Gaurang develops in container & protocol space** (testing S2/S3 with Docker & live server scripts). They are linked only by the frozen `shadowprint/models.py`.

---

# PART 1: Balanced File-by-File Work Distribution

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                EQUAL 50/50 FILE RESPONSIBILITY MATRIX                                              │
├─────────────────────────┬─────────────────────────────────────────────────┬────────────────────────────────────────┤
│ Target Directory / File │ BUILDER: Jasjyot Singh                          │ BUILDER: Gaurang Udgirkar              │
│                         │ Detection, Metadata, Normalizer & UI            │ Runtime, Probing, Integrity & SARIF    │
├─────────────────────────┼─────────────────────────────────────────────────┼────────────────────────────────────────┤
│ ROOT & CONFIGS          │ • `README.md` (Project pitch & demo guide)      │ • `requirements.txt` (Pinned deps)     │
│                         │ • `Makefile` (make audit, make check)           │ • `.gitignore` (obs/, output/, .venv)  │
├─────────────────────────┼─────────────────────────────────────────────────┼────────────────────────────────────────┤
│ shadowprint/ (Core)     │ • `shadowprint/cli.py` (Typer CLI orchestrator) │ • `shadowprint/models.py` (CO-OWNED:   │
│                         │ • `shadowprint/normalizer.py` (Deduplication)   │    Frozen together in first 30 mins)   │
├─────────────────────────┼─────────────────────────────────────────────────┼────────────────────────────────────────┤
│ shadowprint/s0_static/  │ • `s0_static/scanner.py` (Orchestrator)         │                                        │
│                         │ • `s0_static/bandit_runner.py` (AST checks)     │               [NONE]                   │
│                         │ • `s0_static/semgrep_runner.py` (Taint tracker) │      (Zero static code overlap)        │
│                         │ • `s0_static/gitleaks_runner.py` (Secrets)      │                                        │
│                         │ • `s0_static/claim_code_checker.py` (AST match) │                                        │
│                         │ • `s0_static/rules/mcp_taint_rules.yaml`        │                                        │
├─────────────────────────┼─────────────────────────────────────────────────┼────────────────────────────────────────┤
│ shadowprint/s1_metadata/│ • `s1_metadata/analyzer.py` (Orchestrator)      │                                        │
│                         │ • `s1_metadata/deterministic_rules.py` (TAGs)   │               [NONE]                   │
│                         │ • `s1_metadata/qwen_judge.py` (Ollama JSON)     │      (Zero metadata code overlap)      │
│                         │ • `s1_metadata/prompt_guard.py` (Stretch prefit)│                                        │
├─────────────────────────┼─────────────────────────────────────────────────┼────────────────────────────────────────┤
│ shadowprint/s2_prober/  │                                                 │ • `s2_prober/prober.py` (Sweep loop)   │
│                         │                     [NONE]                      │ • `s2_prober/capability_model.py`      │
│                         │          (Zero Docker/prober overlap)           │ • `s2_prober/canary_tripwire.py`       │
│                         │                                                 │ • `s2_prober/syscall_parser.py` (strace)│
│                         │                                                 │ • `s2_prober/output_scanner.py` (Exfil)│
├─────────────────────────┼─────────────────────────────────────────────────┼────────────────────────────────────────┤
│ shadowprint/s3_integrity│                                                 │ • `s3_integrity/db.py` (SQLite store)  │
│                         │                     [NONE]                      │ • `s3_integrity/hasher.py` (3-layer SHA│
│                         │   (Transferred to Gaurang for balance!)         │ • `s3_integrity/watcher.py` (Polling)  │
│                         │                                                 │ • `s3_integrity/differ.py` (deepdiff)  │
├─────────────────────────┼─────────────────────────────────────────────────┼────────────────────────────────────────┤
│ shadowprint/s4_reporting│ • `s4_reporting/markdown_reporter.py` (Report)  │ • `s4_reporting/sarif_exporter.py`     │
│                         │ • `s4_reporting/terminal_ui.py` (Rich matrix)   │   (SARIF 2.1.0 standard exporter)      │
├─────────────────────────┼─────────────────────────────────────────────────┼────────────────────────────────────────┤
│ shadowprint/client/     │                     [NONE]                      │ • `client/mcp_client.py` (Guarded      │
│                         │                                                 │    least-cap stdio client, bounds)     │
├─────────────────────────┼─────────────────────────────────────────────────┼────────────────────────────────────────┤
│ docker/ (Sandbox)       │                     [NONE]                      │ • `docker/Dockerfile.sandbox`          │
│                         │                                                 │ • `docker/entrypoint.sh` (stdio isolate│
│                         │                                                 │ • `docker/sink.py` (Localhost HTTP sink│
├─────────────────────────┼─────────────────────────────────────────────────┼────────────────────────────────────────┤
│ fixtures/ (Test Suite)  │ • `fixtures/clean_notes/server.py` (F1)         │ • `fixtures/clean_fetch/server.py` (F1b│
│                         │ • `fixtures/poisoned_weather/server.py` (F2)    │ • `fixtures/exfil_calculator/server.py`│
│                         │ • `fixtures/vulnerable_runner/server.py` (F3)   │ • `fixtures/rugpull_suite/server.py`   │
│                         │                                                 │ • `fixtures/attack_the_auditor/server.`│
├─────────────────────────┼─────────────────────────────────────────────────┼────────────────────────────────────────┤
│ manifest/ & scripts/    │ • Slide deck presentation & demo narration      │ • `manifest/shadowprint_fixture_...json│
│                         │ • `scripts/trigger_rugpull.py` (Demo trigger)   │ • `scripts/test_manifest.py` (Scorecard│
│                         │                                                 │ • `scripts/preflight_check.py`         │
└─────────────────────────┴─────────────────────────────────────────────────┴────────────────────────────────────────┘
```

---

# PART 2: Official 10-Hour Timeline (8h Dev + 2h Buffer)

```
00:00 ─── [PHASE 1: Contracts & Preflight] ──────── (Both Together - Setup Git & Models)
00:45 ─── [PHASE 2: Parallel Deep Sprint 1] ─────── (Independent Coding - Zero Waiting)
03:00 ─── [PHASE 3: Integration Checkpoint 1] ───── (Git Merge main + Stdio Protocol Test)
03:30 ─── [PHASE 4: Parallel Deep Sprint 2] ─────── (Independent Coding - Zero Waiting)
05:30 ─── [PHASE 5: Full Pipeline Wiring & Merge] ─ (Wire S0 -> S1 -> S2 -> S3 -> S4 in CLI)
06:15 ─── [PHASE 6: Live Rug-Pull & Scorecard] ───── (Verify Touch Flag & Manifest Score)
07:30 ─── [PHASE 7: ABSOLUTE CODE FREEZE (demo-v1)] (Tag Commit demo-v1 - No New Code!)
══════════════════════════════════════════════════════════════════════════════════════════
08:00 ─── [PHASE 8: BUFFER HOUR] ────────────────── (Emergency Fixes, Airgap Test, Slides)
09:00 ─── [PHASE 9: REHEARSAL & DRY-RUNS] ───────── (2x Rehearsals of 8-Min Script)
09:40 ─── [PHASE 10: VIDEO FALLBACK & STANDBY] ──── (Record Backup Video - Ready to Demo)
10:00 ─── [COMPLETED & READY FOR JUDGES]
```

---

### Hour-by-Hour Execution Plan

#### ⏱️ Phase 1: Setup, Contracts Freeze & Preflight (00:00 – 00:45) · TOGETHER
* **00:00 – 00:20 (Git Setup & Contract Freeze):**
  * Initialize repository and create equal feature branches: `feat/jasjyot` and `feat/gaurang`.
  * Co-write and freeze `shadowprint/models.py` (`Finding`, `Snapshot`, `Pin`, `BehaviorTuple`). 
  * Commit to `main`. **Neither teammate touches this file after minute 45.**
* **00:20 – 00:45 (Preflight Sanity Check):**
  * Jasjyot: Pull and test Ollama model: `ollama run qwen3:8b "ping"`.
  * Gaurang: Verify Windows Docker Desktop with `docker run --rm --cap-add SYS_PTRACE --security-opt seccomp=unconfined ubuntu strace ls`.

---

#### ⏱️ Phase 2: Parallel Deep Sprint 1 (00:45 – 03:00) · 2h 15m (INDEPENDENT)
* **Jasjyot (`feat/jasjyot`):**
  * Build `fixtures/clean_notes`, `fixtures/poisoned_weather`, `fixtures/vulnerable_runner`.
  * Build `s0_static/` wrappers: Bandit JSON runner, Semgrep taint rules, Gitleaks secrets runner.
  * Build `normalizer.py`: Implement the deduplication formula `(file, line // 3, category)`.
  * Build `s1_metadata/deterministic_rules.py`: High-precision regex for Unicode TAGs (`\uE000`), zero-width spaces, and imperatives.
* **Gaurang (`feat/gaurang`):**
  * Build `docker/Dockerfile.sandbox`, `docker/entrypoint.sh` (with `stdio` isolation), `docker/sink.py`.
  * Build `client/mcp_client.py`: Guarded least-capability client (stdio, size limits, rejects sampling/elicitation).
  * Build `fixtures/exfil_calculator`: Obfuscated key-theft tool that reads `/tmp/canary_creds.env`.
  * Build `fixtures/clean_fetch`: Clean negative control fixture.
  * Test: Boot a container and verify that `strace` logs cleanly to `/obs/strace.log` without corrupting stdout.

---

#### ⏱️ Phase 3: Integration Checkpoint 1 & Git Merge (03:00 – 03:30) · 30m · TOGETHER
* **Action:**
  1. Merge `feat/jasjyot` and `feat/gaurang` into `main`.
  2. **The Stdio Cleanliness Test:** Gaurang's `mcp_client.py` connects to Jasjyot's `clean_notes` inside Docker.
  3. **Verify:** Client successfully executes `tools/list` with zero `JSONDecodeError`. Any Git conflicts or path differences are resolved immediately.

---

#### ⏱️ Phase 4: Parallel Deep Sprint 2 (03:30 – 05:30) · 2h 00m (INDEPENDENT)
* **Jasjyot (`feat/jasjyot`):**
  * Complete `s1_metadata/qwen_judge.py`: Ollama Qwen3-8B caller with temperature 0 and add-only JSON parsing.
  * Build `s4_reporting/markdown_reporter.py` generating `output/shadowprint_report.md`.
  * Build `s4_reporting/terminal_ui.py`: Color-coded Rich terminal tables and live status cards.
  * Prepare `scripts/trigger_rugpull.py` to touch `/tmp/rugpull_trigger.flag`.
* **Gaurang (`feat/gaurang`):**
  * Complete `s2_prober/`: `capability_model.py` (claim vs. syscalls) and `canary_tripwire.py`.
  * Implement the 10-call Burst Probe Sweep in `prober.py`.
  * Build Engine S3 (`s3_integrity/`): `db.py` (SQLite schema), `hasher.py` (3-layer SHA-256), `watcher.py` (2s polling loop), `differ.py` (`deepdiff` with escaped Unicode).
  * Build `fixtures/rugpull_suite` and `fixtures/attack_the_auditor`.
  * Build `s4_reporting/sarif_exporter.py` (converting `Finding` objects to SARIF 2.1.0).

---

#### ⏱️ Phase 5: Pipeline Integration & Merge (05:30 – 06:15) · 45m · TOGETHER
* **Action:**
  1. Merge both branches into `main`. Resolve any minor import conflicts.
  2. Wire `shadowprint/cli.py`:
     ```python
     # shadowprint audit <path>
     s0_findings = run_s0(path)
     snapshot = run_s1_snapshot(path)
     s1_findings = run_s1_analysis(snapshot)
     s2_findings = run_s2_probe(path)
     all_findings = normalize_and_dedup(s0_findings + s1_findings + s2_findings)
     generate_markdown_and_sarif(all_findings)
     ```
  3. Run `shadowprint audit` end-to-end on Fixtures 1, 2, 3, and 4. Verify that findings match expectations.

---

#### ⏱️ Phase 6: Live Rug-Pull & Scorecard (06:15 – 07:30) · 1h 15m
* **Jasjyot:**
  * Polish CLI output: Ensure color badges (`CRITICAL` in red, `CLEAN` in green) pop on terminal.
  * Rehearse verbal script and slide sync.
* **Gaurang:**
  * Run and test `scripts/test_manifest.py`: Validates all 6 fixtures against `shadowprint_fixture_manifest.json` to prove 100% core recall.
  * Test live rug-pull transition: Run `shadowprint watch rugpull_suite` in Terminal 1, trigger via `scripts/trigger_rugpull.py` in Terminal 2, and verify that the red alert appears in $<1.5$ seconds.

---

#### ⏱️ Phase 7: ABSOLUTE CODE FREEZE (07:30 – 08:00) · 30m · TOGETHER
* **Action:**
  1. Run automated test suite: `pytest` or `python scripts/test_manifest.py`.
  2. Commit and tag: **`git tag demo-v1`**.
  3. **STRICT RULE:** Development is officially closed. No new features, no refactoring.

---

### 🛡️ THE 2-HOUR BUFFER & REHEARSAL BLOCK (08:00 – 10:00)

#### ⏱️ Phase 8: Emergency Buffer & Hardening (08:00 – 09:00) · 1h 00m
* **Buffer Utility:** If S2 Docker or Git merges were delayed, this hour absorbs the slip without panic.
* **The Airgap Test:** Disconnect Wi-Fi completely. Run `shadowprint audit` to prove zero external cloud calls.
* **Encoding Check:** Ensure Windows Terminal is in UTF-8 mode (`chcp 65001`) so Unicode TAGs render cleanly without crashes.
* **Slide Sync:** Ensure slide deck metrics match the final fixture manifest output.

#### ⏱️ Phase 9: Demo Rehearsals (09:00 – 09:40) · 40m
* **Action:** Conduct **two full, uninterrupted dry-runs** of the 8-minute judging presentation:
  * *Run 1 (09:00 – 09:20):* Rehearse live commands and verbal script. Identify awkward pauses or terminal switching delays.
  * *Run 2 (09:20 – 09:40):* Timed dress rehearsal (exactly 8 minutes) with Gaurang triggering the live rug-pull on cue.

#### ⏱️ Phase 10: Video Fallback & Standby (09:40 – 10:00) · 20m
* **Action:**
  1. Record a high-resolution screen capture of the entire clean terminal demo run (`demo_backup.mp4`).
  2. Save a copy on a USB drive and local desktop. If your laptop or projector freezes during live judging, you play the video immediately.
  3. Take a breath, relax, and wait for judging. You are 100% prepared.
