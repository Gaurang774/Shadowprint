# Shadowprint — Task Tracker & 10-Hour Execution State

> **State of the World:** Real-time progress tracker across the 10-hour hackathon execution timeline.

---

## ⏱️ Timeline Phases Status

| Phase | Window | Description | Status | Owner |
|---|---|---|---|---|
| **Phase 1** | 00:00 – 00:45 | Contracts & Preflight (Git setup, freeze `models.py`, environment checks) | ✅ COMPLETED | Both (Jasjyot & Gaurang) |
| **Phase 2** | 00:45 – 03:00 | Parallel Deep Sprint 1 (S0/S1 core, Docker sandbox, MCP client, Normalizer) | 🔄 READY TO START | Independent |
| **Phase 3** | 03:00 – 03:30 | Integration Checkpoint 1 (Git merge `main` + Stdio Cleanliness Test) | ⏳ PENDING | Both |
| **Phase 4** | 03:30 – 05:30 | Parallel Deep Sprint 2 (S1 Qwen3, S2 Syscalls/Canary, S3 SQLite/Watcher, S4 SARIF/MD) | ⏳ PENDING | Independent |
| **Phase 5** | 05:30 – 06:15 | Pipeline Wiring & Integration (`shadowprint audit` end-to-end on Fixtures 1–4) | ⏳ PENDING | Both |
| **Phase 6** | 06:15 – 07:30 | Live Rug-Pull & Scorecard Test (`scripts/test_manifest.py`, touch flag demo) | ⏳ PENDING | Both |
| **Phase 7** | 07:30 – 08:00 | Code Freeze (`git tag demo-v1`) | ⏳ PENDING | Both |
| **Phase 8** | 08:00 – 09:00 | Buffer Hour & Airgap Test (Emergency fixes, zero cloud verify, slide sync) | ⏳ PENDING | Both |
| **Phase 9** | 09:00 – 09:40 | Judging Rehearsals (2x 8-minute dry runs) | ⏳ PENDING | Both |
| **Phase 10**| 09:40 – 10:00 | Video Fallback & Standby (`demo_backup.mp4` recording) | ⏳ PENDING | Both |

---

## 📁 File Delivery Matrix & Progress

### Shared Core & Configs
- [x] [PS.md](file:///d:/ShadowPrint/Shadowprint/PS.md) (Problem Statement PS02)
- [x] [info.md](file:///d:/ShadowPrint/Shadowprint/info.md) (50/50 Strategy & Timeline)
- [x] [archi.md](file:///d:/ShadowPrint/Shadowprint/archi.md) (Production Architecture Specification v1.4)
- [x] [AI_ONBOARDING.md](file:///d:/ShadowPrint/Shadowprint/AI_ONBOARDING.md) (Constitution / Ground Truth)
- [x] [PROJECT_RULES.md](file:///d:/ShadowPrint/Shadowprint/PROJECT_RULES.md) (Supreme Rules & Anti-Hallucination Checklist)
- [x] [.agents/rules/project_rules.md](file:///d:/ShadowPrint/Shadowprint/.agents/rules/project_rules.md) (Antigravity Directives)
- [x] [TASK_TRACKER.md](file:///d:/ShadowPrint/Shadowprint/TASK_TRACKER.md) (Execution State)
- [x] [WORK_LOG.md](file:///d:/ShadowPrint/Shadowprint/WORK_LOG.md) (Verifiable Progress Log & Checklists)
- [x] `requirements.txt` (Pinned exact modern dependencies)
- [x] `.gitignore` (Ignore `/obs`, `shadowprint.db`, `.venv`, `output/`)
- [x] `pyproject.toml` (Package definition & CLI entrypoint)
- [x] `shadowprint/models.py` (Universal data contracts: `Finding`, `Snapshot`, `Pin`, `BehaviorTuple`)
- [x] `scripts/preflight_check.py` (Environment & dependency validator)

### Builder A: Jasjyot Singh (Static S0, S1-Rules, All Reporting S4 & CLI)
- [ ] `shadowprint/cli.py` (Typer CLI orchestrator: `audit`, `approve`, `watch`, `report`)
- [ ] `shadowprint/normalizer.py` (Deduplication formula: `(file, line // 3, category)`)
- [ ] `shadowprint/s0_static/scanner.py` (S0 Static orchestrator & hostile suppression check)
- [ ] `shadowprint/s0_static/bandit_runner.py` (Bandit AST wrapper)
- [ ] `shadowprint/s0_static/semgrep_runner.py` (Semgrep taint tracking runner)
- [ ] `shadowprint/s0_static/gitleaks_runner.py` (Gitleaks secret detection)
- [ ] `shadowprint/s0_static/claim_code_checker.py` (AST claim vs code comparator)
- [ ] `shadowprint/s0_static/rules/mcp_taint_rules.yaml` (Custom Semgrep rules)
- [ ] `shadowprint/s1_metadata/analyzer.py` (S1 Metadata orchestrator)
- [ ] `shadowprint/s1_metadata/deterministic_rules.py` (High-precision Unicode TAG & prompt regex)
- [ ] `shadowprint/s4_reporting/markdown_reporter.py` (Markdown report generator)
- [ ] `shadowprint/s4_reporting/terminal_ui.py` (Rich matrix & live status cards)
- [ ] `shadowprint/s4_reporting/sarif_exporter.py` (SARIF 2.1.0 standard exporter — Jasjyot owns all reports!)
- [ ] `fixtures/clean_notes/server.py` (Fixture 1: Benign notes CRUD)
- [ ] `fixtures/poisoned_weather/server.py` (Fixture 2: Unicode TAG prompt injection)
- [ ] `fixtures/vulnerable_runner/server.py` (Fixture 3: `shell=True` + hardcoded AWS secret)
- [ ] `fixtures/attack_the_auditor/server.py` (Fixture 6: Hostile `#nosec` suppression)
- [ ] `scripts/trigger_rugpull.py` (Stage touch trigger script)

### Builder B: Gaurang Udgirkar (Ollama Qwen3, Runtime S2, S3 & Client)
- [x] `shadowprint/s1_metadata/qwen_judge.py` (Ollama Qwen3-8B caller, temperature 0, add-only Pydantic JSON judge)
- [x] `shadowprint/s1_metadata/prompt_guard.py` (Optional prompt injection pre-filter)
- [x] `shadowprint/client/mcp_client.py` (Guarded least-capability stdio client)
- [x] `docker/Dockerfile.sandbox` (Docker sandbox definition)
- [x] `docker/entrypoint.sh` (stdio cleanliness isolation harness)
- [x] `docker/sink.py` (Localhost HTTP sink on 127.0.0.1:8080)
- [ ] `shadowprint/s2_prober/prober.py` (Burst probe sweep loop)
- [ ] `shadowprint/s2_prober/capability_model.py` (Claim vs syscall capability model)
- [ ] `shadowprint/s2_prober/canary_tripwire.py` (Planted canary secret verifier)
- [ ] `shadowprint/s2_prober/syscall_parser.py` (strace log parser)
- [ ] `shadowprint/s2_prober/output_scanner.py` (Markdown exfiltration detector)
- [ ] `shadowprint/s3_integrity/db.py` (SQLite schema & queries)
- [ ] `shadowprint/s3_integrity/hasher.py` (3-layer SHA-256 calculator)
- [ ] `shadowprint/s3_integrity/watcher.py` (2-second polling loop)
- [ ] `shadowprint/s3_integrity/differ.py` (`deepdiff` with escaped non-printables)
- [ ] `fixtures/clean_fetch/server.py` (Fixture 1b: Clean fetch control)
- [ ] `fixtures/exfil_calculator/server.py` (Fixture 4: Obfuscated key theft + sink egress)
- [ ] `fixtures/rugpull_suite/server.py` (Fixture 5: Live touch flag definition flipper)
- [ ] `manifest/shadowprint_fixture_manifest.json` (Expected findings ground truth)
- [ ] `scripts/test_manifest.py` (Automated scorecard & recall validator)
- [x] `scripts/preflight_check.py` (Docker & Ollama sanity validator)

---

## 🎯 Benchmark Fixture Recall Matrix

| Fixture | Expected Caught Issues | Catching Engine | Pass Criteria | Status |
|---|---|---|---|---|
| `clean_notes` | None | None | 0 False Positives | ⏳ Not tested |
| `clean_fetch` | None | None | 0 False Positives | ⏳ Not tested |
| `poisoned_weather` | Prompt injection in description | S1 (Deterministic + Qwen3) | Caught & quoted | ⏳ Not tested |
| `vulnerable_runner` | `shell=True` + hardcoded AWS secret | S0 (Bandit + Gitleaks) | Exact line flagged | ⏳ Not tested |
| `exfil_calculator` | Canary file read + localhost egress | S2 (Syscall + Sink) | Exfil confirmed | ⏳ Not tested |
| `rugpull_suite` | Definition mutation upon flag touch | S3 (Watcher + Diff) | Alert in $<1.5$s | ⏳ Not tested |
| `attack_the_auditor` | `#nosec` / `#nosemgrep` bypass attempts | S0/S1 Hardening | `TAMPER_ATTEMPT` | ⏳ Not tested |
