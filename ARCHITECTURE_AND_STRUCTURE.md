# Shadowprint — Complete Project Architecture & Structure Specification

> **Project:** Shadowprint — *Every server leaves a trace*  
> **Problem Statement:** PS02 — Model Context Protocol (MCP) Server Security Auditor  
> **Track:** Track 1: Open Weight AI & Open Source Tools  
> **Authors & Co-Builders:** Jasjyot Singh & Gaurang Udgirkar (Equal 50/50 Balance)  
> **Target Environment:** Python 3.12+ / 3.14, Docker Desktop (Windows WSL2 / Linux), Ollama (Local Qwen3)

---

## 1. Executive Overview

**Shadowprint** is an evidence-first, 100% offline, airgapped security auditor for Model Context Protocol (MCP) servers. Rather than treating security analysis as a single-point text prompt or a superficial static linter, Shadowprint constructs a verifiable **Four-Dimension Evidence Chain** for every audited tool:

$$\text{Claim (Metadata)} \longleftrightarrow \text{Code (Static AST)} \longleftrightarrow \text{Runtime (Kernel Syscalls)} \longleftrightarrow \text{Drift (Integrity Diff)}$$

### Core Guarantees:
1. **Zero Cloud Dependencies:** 100% offline; runs on local Ollama Qwen3 models (`127.0.0.1:11434`). Zero cloud API keys in codebase.
2. **Static Precedence Invariant:** Engine S0 static checks must pass before untrusted code or containerized runtime processes ever execute.
3. **Add-Only LLM Authority:** The local Qwen3 AI judge is mathematically forbidden from suppressing, dismissing, or downgrading any deterministic finding produced by static AST rules or Linux kernel syscall monitors.
4. **Clean Stdio Isolation:** All auxiliary diagnostic logs (`strace`, HTTP sink, supervisor output) redirect to disk files in `/obs/` so standard I/O remains 100% pure JSON-RPC without stderr corruption.

---

## 2. High-Level Architecture Diagram

```
                              ┌─────────────────────────────────────────────────────────┐
                              │               TARGET MCP SERVER REPOSITORY              │
                              │       Source Code, Tool Schemas, Prompts, Configs       │
                              └────────────────────────────┬────────────────────────────┘
                                                           │
                                                           ▼
                                      ┌────────────────────────────────────────┐
                                      │      AUDIT ORCHESTRATOR (CLI)          │
                                      │      shadowprint/cli.py                │
                                      └────────────────────┬───────────────────┘
                                                           │
                                                           ▼
                                      ┌────────────────────────────────────────┐
                                      │  ENGINE S0: STATIC CODE ANALYSIS       │
                                      │  • Bandit AST Security Linter          │
                                      │  • Semgrep Taint Tracking              │
                                      │  • Gitleaks Secrets Detection          │
                                      │  • Hostile #nosec Suppression Detector │
                                      │  • AST Claim vs Code Checker           │
                                      └────────────────────┬───────────────────┘
                                                           │
                                              Passed S0 Safety Gate?
                                              ├── [CRITICAL / TAMPER] ──► Block Runtime / Emit Early Report
                                              └── [PASS / SAFE]
                                                           │
                                                           ▼
                           ┌───────────────────────────────────────────────────────────────┐
                           │            THROWAWAY DOCKER SANDBOX (s2_prober)               │
                           │   Flags: --network none --cap-add SYS_PTRACE                 │
                           │          --security-opt seccomp=unconfined                    │
                           │                                                               │
                           │   ┌───────────────────────────────────────────────────────┐   │
                           │   │  Supervisor (entrypoint.sh)                           │   │
                           │   │  • Background HTTP Sink (127.0.0.1:8080) -> /obs/sink │   │
                           │   │  • Planted Canary Secret -> /tmp/canary_creds.env     │   │
                           │   │  • strace Kernel Monitor -> /obs/strace.log           │   │
                           │   │  • Target Server Process (stdout = pure JSON-RPC)     │   │
                           │   └───────────────────────────┬───────────────────────────┘   │
                           └───────────────────────────────┼───────────────────────────────┘
                                                           │ Clean Stdio JSON-RPC
                                                           ▼
                                      ┌────────────────────────────────────────┐
                                      │       GUARDED MCP STDIO CLIENT         │
                                      │       shadowprint/client/mcp_client.py │
                                      │       (Bounded Timeouts, Max 1MB)      │
                                      └────────────────────┬───────────────────┘
                                                           │
                              ┌────────────────────────────┴───────────────────────────┐
                              ▼                                                        ▼
         ┌────────────────────────────────────────┐               ┌────────────────────────────────────────┐
         │  ENGINE S1: METADATA & PROMPT ANALYSIS │               │   ENGINE S2: DYNAMIC PROBER & KERNEL   │
         │  • Deterministic Rules: Unicode TAGs   │               │   • 10-call Burst Probe Sweep          │
         │    (\uE000), Zero-Width, Imperatives   │               │   • Linux strace parser (openat,       │
         │  • Ollama Qwen3-8B AI Judge (Add-Only) │               │     connect, execve)                   │
         │  • Prompt Guard Injection Pre-filter   │               │   • Canary Key Access Tripwire         │
         │                                        │               │   • Output Exfiltration Regex Scanner  │
         │                                        │               │   • Capability Mismatch Detector       │
         └────────────────────┬───────────────────┘               └────────────────────┬───────────────────┘
                              │                                                        │
                              └────────────────────────────┬───────────────────────────┘
                                                           │
                                                           ▼
                                      ┌────────────────────────────────────────┐
                                      │   ENGINE S3: INTEGRITY & PIN-AND-DIFF  │
                                      │   • 3-Layer SHA-256 Fingerprint:       │
                                      │     1. definition_hash (Tool schema)   │
                                      │     2. artifact_hash (Source files)    │
                                      │     3. behavior_hash (Syscall trace)   │
                                      │   • SQLite Persistent Store (.db)      │
                                      │   • Live Watcher Loop (tools/listChanged│
                                      │     + 2s polling on /tmp trigger flag) │
                                      │   • deepdiff with Escaped Non-Printable│
                                      └────────────────────┬───────────────────┘
                                                           │
                                                           ▼
                                      ┌────────────────────────────────────────┐
                                      │       FINDING NORMALIZER & DEDUP       │
                                      │       shadowprint/normalizer.py        │
                                      │       Formula: (file, line // 3, cat)  │
                                      └────────────────────┬───────────────────┘
                                                           │
                                                           ▼
                                      ┌────────────────────────────────────────┐
                                      │   ENGINE S4: UNIFIED MULTI-REPORTER    │
                                      │   • Rich Color-Coded Terminal UI       │
                                      │   • Markdown: output/shadowprint_...md │
                                      │   • OASIS SARIF 2.1.0 JSON Standard    │
                                      └────────────────────────────────────────┘
```

---

## 3. Deep Dive into the 5 Detection Engines

### Engine S0: Static Code & Configuration Analysis
* **Owner:** Jasjyot Singh (`feat/jasjyot`)
* **Role:** Pre-execution inspection of Python AST, imported packages, hardcoded secrets, and taint paths.
* **Components:**
  1. `s0_static/bandit_runner.py`: Wraps Bandit with strict JSON output, targeting AST security flaws (`B301` pickle, `B602` subprocess `shell=True`, `B310` URL opening).
  2. `s0_static/semgrep_runner.py`: Taint tracking using custom rules ([s0_static/rules/mcp_taint_rules.yaml](file:///d:/ShadowPrint/Shadowprint/shadowprint/s0_static/rules/mcp_taint_rules.yaml)) tracing tainted tool parameters to execution sinks (`exec`, `eval`, `system`).
  3. `s0_static/gitleaks_runner.py`: Offline regex-based secret scanning for high-entropy tokens (AWS keys, OpenAI/Anthropic credentials, private keys).
  4. `s0_static/claim_code_checker.py`: AST parser comparing tool claims (e.g. `read_only=True`) against implemented AST function calls (e.g. calls to `os.remove` or `open(..., 'w')`).
  5. `s0_static/scanner.py`: Master orchestrator. **Detects hostile suppression comments** (`#nosec`, `#nosemgrep`) and flags them as `TAMPER_ATTEMPT`.

---

### Engine S1: Metadata & Prompt Injection Analysis
* **Co-Owned:** Jasjyot Singh (Deterministic Rules & Orchestrator) & Gaurang Udgirkar (Ollama Qwen3 AI Judge)
* **Role:** Analyzes tool descriptions, parameter schemas, and system prompt text for prompt injection, jailbreaks, hidden instructions, and unicode steganography.
* **Components:**
  1. `s1_metadata/deterministic_rules.py` [Jasjyot]: High-precision regex detecting:
     * Unicode TAG characters (`\uE000` – `\uE07F`).
     * Zero-width spaces and invisible characters (`\u200B`, `\u200C`, `\uFEFF`).
     * Second-person imperative override patterns (*"Ignore previous instructions"*, *"You must now act as"*).
  2. `s1_metadata/qwen_judge.py` [Gaurang]: Local Ollama Qwen3-8B caller enforcing `temperature=0` and structured Pydantic JSON parsing. Follows the **Add-Only Authority Invariant** (can flag new heuristic quotes, cannot clear deterministic findings).
  3. `s1_metadata/prompt_guard.py` [Gaurang]: Fast optional pre-filter for direct injection patterns.
  4. `s1_metadata/analyzer.py` [Jasjyot]: Merges deterministic rule hits and Qwen3 quotes into unified [Finding](file:///d:/ShadowPrint/Shadowprint/shadowprint/models.py#L19-L33) objects.

---

### Engine S2: Dynamic Prober & Kernel Syscall Sandbox
* **Owner:** Gaurang Udgirkar (`feat/gaurang`)
* **Role:** Executes the target server inside an isolated throwaway Docker container, capturing actual runtime kernel syscalls and detecting covert data exfiltration.
* **Components:**
  1. `docker/Dockerfile.sandbox`: Minimal `python:3.12-slim` image with Linux `strace` installed.
  2. `docker/entrypoint.sh`: Supervisor script redirecting all strace and background HTTP sink output to `/obs/`, ensuring pure JSON-RPC on `stdout`.
  3. `docker/sink.py`: Localhost HTTP sink on `127.0.0.1:8080` capturing egress HTTP requests and logging headers/payloads.
  4. `shadowprint/client/mcp_client.py`: Guarded least-capability stdio client querying `tools/list` and executing bounded tool calls (max 5s timeout).
  5. `s2_prober/syscall_parser.py`: Parses `/obs/strace.log` into structured syscall events: `openat` (file access), `connect` (network egress), `execve` (process execution).
  6. `s2_prober/canary_tripwire.py`: Verifies whether decoy credentials (`CANARY_KEY_98721X` in `/tmp/canary_creds.env`) were read or leaked.
  7. `s2_prober/output_scanner.py`: Inspects tool outputs for Markdown exfil syntax (`![exfil](http://.../?leak=...)`), HTML script tags, or base64 blobs.
  8. `s2_prober/capability_model.py`: Detects capability mismatches (e.g., claiming to be an "offline text formatter" while calling `connect()` to an external IP).
  9. `s2_prober/prober.py`: Runs a 10-call Burst Probe Sweep, gathers logs, evaluates tripwires, and outputs findings.

---

### Engine S3: Integrity & Pin-and-Diff Engine
* **Owner:** Gaurang Udgirkar (`feat/gaurang`)
* **Role:** Detects runtime tool poisoning, metadata drift, and live "rug-pull" mutations by comparing approved baseline pins against live server state.
* **Components:**
  1. `s3_integrity/db.py`: SQLite storage layer (`shadowprint.db`) for persisting approved [Pin](file:///d:/ShadowPrint/Shadowprint/shadowprint/models.py#L58-L67) records.
  2. `s3_integrity/hasher.py`: Computes 3-layer cryptographic fingerprint:
     * `definition_hash`: SHA-256 of canonical tool JSON schema.
     * `artifact_hash`: Merkle-style SHA-256 of server source files.
     * `behavior_hash`: Normalized SHA-256 of syscall trace sequence.
  3. `s3_integrity/differ.py`: Deep structural diffing via `deepdiff` with explicit hexadecimal escaping for zero-width and non-printable characters.
  4. `s3_integrity/watcher.py`: 2-second polling loop + notification listener raising immediate red alerts upon live definition mutations.

---

### Engine S4: Unified Reporting & Export
* **Owner:** Jasjyot Singh (`feat/jasjyot`)
* **Role:** Consolidates normalized findings into multi-format, executive-ready, and CI/CD-compatible reports.
* **Components:**
  1. `s4_reporting/terminal_ui.py`: Rich color-coded terminal dashboard with status badges (`CRITICAL`, `HIGH`, `MEDIUM`, `CLEAN`), evidence tables, and summary counts.
  2. `s4_reporting/markdown_reporter.py`: Generates complete Markdown audit reports (`output/shadowprint_report.md`) with remediation steps, evidence snippets, and tool cards.
  3. `s4_reporting/sarif_exporter.py`: Official OASIS SARIF 2.1.0 standard JSON exporter mapping findings to canonical CWE categories (CWE-78, CWE-798, CWE-200, CWE-20).

---

## 4. Universal Data Contracts (`shadowprint/models.py`)

All 5 engines exchange data strictly through the frozen Pydantic contracts in [shadowprint/models.py](file:///d:/ShadowPrint/Shadowprint/shadowprint/models.py):

```python
class Finding(BaseModel):
    id: str                                  # e.g. "SHADOW-S0-001"
    engine: Literal["S0", "S1", "S2", "S3"]   # Originating engine
    target: str                              # Server name or filepath
    tool: Optional[str] = None               # Specific tool name
    category: str                            # e.g. "COMMAND_INJECTION", "PROMPT_INJECTION"
    severity: Literal["critical", "high", "medium", "low", "info"]
    assessment: Literal["FAIL", "FLAGGED", "PASS", "NOT_ASSESSED"]
    confidence: Literal["confirmed", "corroborated", "heuristic"]
    evidence_basis: Literal["static", "metadata", "runtime_observed", "diff"]
    location: Optional[Location] = None      # file, line, col
    claim: Optional[str] = None              # What the tool claimed in its description
    evidence: str                            # Exact quote, code line, or syscall snippet
    remediation: Optional[str] = None        # Concrete fix recommendation
    raw_result_ref: Optional[Dict[str, Any]] # Raw tool output / AST dict

class Snapshot(BaseModel):
    server_name: str
    timestamp: float
    tools: List[ToolDefinition]
    prompts: List[Dict[str, Any]]
    resources: List[Dict[str, Any]]
    definition_hash: str                     # Layer 1 SHA-256
    artifact_hash: Optional[str] = None      # Layer 2 SHA-256

class Pin(BaseModel):
    server_name: str
    approved_at: float
    definition_hash: str
    artifact_hash: str
    behavior_hash: Optional[str] = None      # Layer 3 SHA-256
    snapshot_json: str
    behavior_json: Optional[str] = None
```

---

## 5. Exhaustive Project Directory Tree & Ownership

```
d:\ShadowPrint\Shadowprint/
│
├── .agents/
│   └── rules/
│       └── project_rules.md                   # Auto-loaded Antigravity IDE directives
│
├── docker/                                    # [GAURANG] Sandbox Environment
│   ├── README.md                              # Container setup guide
│   ├── Dockerfile.sandbox                     # python:3.12-slim + strace sandbox
│   ├── entrypoint.sh                          # Supervisor isolating strace & sink to /obs/
│   └── sink.py                                # Localhost HTTP sink on 127.0.0.1:8080
│
├── fixtures/                                  # Benchmark Test Suite
│   ├── README.md                              # Fixtures guide
│   ├── clean_notes/                           # [JASJYOT] Fixture 1: Benign CRUD (0 False Positives)
│   │   └── server.py
│   ├── clean_fetch/                           # [GAURANG] Fixture 1b: Benign Fetch (0 False Positives)
│   │   └── server.py
│   ├── poisoned_weather/                      # [JASJYOT] Fixture 2: Unicode TAG Prompt Injection
│   │   └── server.py
│   ├── vulnerable_runner/                     # [JASJYOT] Fixture 3: shell=True + AWS Hardcoded Secret
│   │   └── server.py
│   ├── exfil_calculator/                      # [GAURANG] Fixture 4: Covert Key Theft + Sink Egress
│   │   └── server.py
│   ├── rugpull_suite/                         # [GAURANG] Fixture 5: Touch Flag Definition Mutation
│   │   └── server.py
│   └── attack_the_auditor/                    # [JASJYOT] Fixture 6: Hostile #nosec Suppression Bypass
│       └── server.py
│
├── manifest/                                  # [GAURANG] Benchmark Ground Truth
│   ├── README.md
│   └── shadowprint_fixture_manifest.json      # Ground truth scorecard for all fixtures
│
├── scripts/                                   # Automation & Stage Demos
│   ├── README.md
│   ├── preflight_check.py                     # [GAURANG] System sanity validator (Docker, Ollama, deps)
│   ├── test_manifest.py                       # [GAURANG] Automated 100% recall scorecard validator
│   └── trigger_rugpull.py                     # [JASJYOT] Stage demo trigger (touch /tmp flag)
│
├── shadowprint/                               # Core Python Package
│   ├── __init__.py
│   ├── cli.py                                 # [JASJYOT] Typer CLI: audit, approve, watch, report
│   ├── models.py                              # [CO-OWNED] Universal frozen Pydantic contracts
│   ├── normalizer.py                          # [JASJYOT] Clustered deduplication (file, line // 3, cat)
│   │
│   ├── client/                                # [GAURANG] Protocol Space
│   │   ├── __init__.py
│   │   └── mcp_client.py                      # Guarded least-capability stdio MCP client
│   │
│   ├── s0_static/                             # [JASJYOT] Engine S0: Static Code Analysis
│   │   ├── __init__.py
│   │   ├── scanner.py                         # S0 master orchestrator & hostile suppression check
│   │   ├── bandit_runner.py                   # Bandit AST linter runner (-f json)
│   │   ├── semgrep_runner.py                  # Semgrep taint tracking runner
│   │   ├── gitleaks_runner.py                 # Offline Gitleaks secret scanner
│   │   ├── claim_code_checker.py              # AST claim vs code matcher
│   │   └── rules/
│   │       └── mcp_taint_rules.yaml           # Custom YAML rules for MCP sinks
│   │
│   ├── s1_metadata/                           # Engine S1: Metadata & Prompt Injection
│   │   ├── __init__.py
│   │   ├── analyzer.py                        # [JASJYOT] S1 master orchestrator
│   │   ├── deterministic_rules.py             # [JASJYOT] Unicode TAG, zero-width, regex rules
│   │   ├── qwen_judge.py                      # [GAURANG] Ollama Qwen3-8B Pydantic JSON judge
│   │   └── prompt_guard.py                    # [GAURANG] Optional prompt injection pre-filter
│   │
│   ├── s2_prober/                             # [GAURANG] Engine S2: Dynamic Prober & Syscalls
│   │   ├── __init__.py
│   │   ├── prober.py                          # 10-call Burst Probe Sweep orchestrator
│   │   ├── capability_model.py                # Tool claim vs observed syscall capability check
│   │   ├── canary_tripwire.py                 # Planted decoy secret verifier (CANARY_KEY_98721X)
│   │   ├── syscall_parser.py                  # strace log parser (openat, connect, execve)
│   │   └── output_scanner.py                  # Markdown & HTML exfiltration regex detector
│   │
│   ├── s3_integrity/                          # [GAURANG] Engine S3: Pinning & Diffing
│   │   ├── __init__.py
│   │   ├── db.py                              # SQLite persistence layer (shadowprint.db)
│   │   ├── hasher.py                          # 3-layer SHA-256 fingerprint calculator
│   │   ├── watcher.py                         # 2-second live polling loop for rug-pulls
│   │   └── differ.py                          # deepdiff with non-printable character escaping
│   │
│   └── s4_reporting/                          # [JASJYOT] Engine S4: Reporting & UI
│       ├── __init__.py
│       ├── terminal_ui.py                     # Rich color-coded terminal dashboard & cards
│       ├── markdown_reporter.py               # output/shadowprint_report.md generator
│       └── sarif_exporter.py                  # Official OASIS SARIF 2.1.0 standard exporter
│
├── tests/                                     # Automated Test Suite
│   ├── __init__.py
│   └── test_models.py                         # Unit tests for Pydantic models & deduplication
│
├── .gitignore                                 # Ignores /obs, shadowprint.db, .venv, output/
├── AI_ONBOARDING.md                           # 60-second crash course & ground truth table
├── ARCHITECTURE_AND_STRUCTURE.md              # THIS DOCUMENT: Architecture & Structure Spec
├── ENGINEERING_DECISIONS.md                   # Architectural Decision Records (ADR 001 - 011)
├── info.md                                    # 50/50 Strategy & 10-Hour Timeline
├── Makefile                                   # Dev targets (preflight, audit, test)
├── PROJECT_RULES.md                           # Supreme Constitution & Anti-Hallucination Gate
├── PS.md                                      # Problem Statement PS02
├── pyproject.toml                             # Package definition & CLI entrypoint
├── README.md                                  # Project pitch & judge demo guide
├── requirements.txt                           # Pinned exact modern dependencies
├── reviced_timeline.md                        # Master revised 10-hour timeline
├── TASK_TRACKER.md                            # Real-time task checklist
└── WORK_LOG.md                                # Verifiable progress and test execution log
```

---

## 6. Benchmark Scenarios & Ground Truth Target Recall

| ID | Fixture Directory | Planted Flaw / Attack Vector | Target Engine | Expected Audit Outcome | Owner |
|---|---|---|---|---|---|
| **F1** | `fixtures/clean_notes` | Benign notes CRUD tool | None | **0 False Positives** (CLEAN) | Jasjyot |
| **F1b** | `fixtures/clean_fetch` | Benign fetch tool | None | **0 False Positives** (CLEAN) | Gaurang |
| **F2** | `fixtures/poisoned_weather` | Prompt injection via Unicode TAGs (`\uE000`) | S1 (Regex + Qwen3) | Injection quote extracted & flagged `CRITICAL` | Jasjyot |
| **F3** | `fixtures/vulnerable_runner` | `subprocess.Popen(shell=True)` + hardcoded AWS key | S0 (Bandit + Gitleaks) | Exact line-level findings (CWE-78, CWE-798) | Jasjyot |
| **F4** | `fixtures/exfil_calculator` | Reads `/tmp/canary_creds.env` & sends to HTTP sink | S2 (Syscall + Sink) | `openat` & `connect` flagged `CRITICAL` exfil | Gaurang |
| **F5** | `fixtures/rugpull_suite` | Definition flips upon `/tmp/rugpull_trigger.flag` touch | S3 (Watcher + Diff) | Instant red alert in $<1.5$s with character diff | Gaurang |
| **F6** | `fixtures/attack_the_auditor` | Malicious `#nosec` / `#nosemgrep` suppression comments | S0 Scanner Hardening | Suppressions flagged as `TAMPER_ATTEMPT` | Jasjyot |

---

## 7. Git Workflow & Branch Isolation

To guarantee zero merge conflicts and allow both builders to code simultaneously at full speed:

* **`main`:** Contains strictly the shared project foundation (documentation, configurations, frozen models, package skeletons). **Zero experimental or incomplete code.**
* **`feat/jasjyot`:** Dedicated feature branch for Jasjyot Singh. Commits only to S0, S1-Rules, S4, CLI, and assigned fixtures.
* **`feat/gaurang`:** Dedicated feature branch for Gaurang Udgirkar. Commits only to Docker, MCP Client, S1-Qwen, S2, S3, and assigned fixtures.
* **Checkpoint Merges:** Merged into `main` at Phase 3 (Minute 180) and Phase 5 (Minute 330) after passing `scripts/test_manifest.py`.
