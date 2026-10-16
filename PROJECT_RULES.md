# Shadowprint — Supreme Project Rules & Anti-Hallucination Constitution

> **Status:** Supreme Law  
> **Applies to:** All AI agents, contributors, and automated tooling across the entire codebase.  
> **Core Mandate:** Prevent architectural drift, eliminate AI hallucinations, enforce deterministic security boundaries, and guarantee a reproducible 10-hour hackathon build.

---

## 🏛️ PART 1: The Hard Rules (HR1 – HR8)

These rules are inviolable. Any pull request, automated commit, or agent response that violates a Hard Rule will be rejected immediately.

### HR1: The Locked Technology Stack (Forbidden vs. Required)

The tech stack is completely frozen. Agents are strictly forbidden from substituting, adding, or suggesting libraries from general training data.

| Component | Required Technology | Explicitly Forbidden (Hallucination Traps) |
|---|---|---|
| **Language & Host** | Python 3.10+ (Current runtime: 3.14.3) | No Node.js for auditor core; no unpinned shell scripts |
| **CLI & UI** | `typer` + `rich` | No `argparse`, `click` directly, or invented frameworks |
| **MCP Interface** | `mcp` (Official MCP Python SDK) | No raw WebSocket mocks or custom protocol reinventions |
| **Local LLM** | Ollama with `qwen3:8b` (fallback `qwen3:4b`) | **NO Cloud LLMs** (OpenAI, Anthropic, Gemini, Groq, Cohere) |
| **LLM Output** | Structured Pydantic JSON (`temperature=0`) | No free-form markdown, unparsed strings, or raw regex parsers |
| **Static AST Engine** | Bandit (`bandit -r <target> -f json`) | No home-brewed AST parsers replacing Bandit |
| **Static Taint Engine** | Semgrep (`mcp_taint_rules.yaml`) | No regex-only approximations for code taint |
| **Secret Detection** | Gitleaks (`gitleaks detect --source=<dir> --no-git`) | No home-brewed regex list replacing Gitleaks |
| **Dynamic Sandbox** | Docker (`--cap-drop ALL --cap-add SYS_PTRACE --security-opt seccomp=unconfined --network none`) | No direct host execution of untrusted MCP servers |
| **Syscall Monitor** | `strace -f -e trace=openat,connect,execve -o /obs/strace.log` | No eBPF or root-level host daemons requiring custom kernels |
| **Egress Sink** | In-container HTTP listener on `127.0.0.1:8080` logging to `/obs/sink.log` | No external webhooks or public requestbin endpoints |
| **Integrity Database**| SQLite 3 (`shadowprint.db`) via standard library | No MongoDB, PostgreSQL, pickled state files |
| **Differential Engine**| `deepdiff` (with non-printable & zero-width character escaping)| No naive string diffs or basic JSON equality checks |
| **Report Formats** | Rich Terminal Matrix, `output/shadowprint_report.md`, SARIF 2.1.0 (`results.sarif`) | No proprietary XML or incomplete custom JSON schemas |

---

### HR2: The 4 Inviolable System Invariants

1. **The Static Precedence Invariant (Zero Early Execution):**  
   Engine S0 must finish executing all file-level and AST checks before the target server process, package scripts (`setup.py`, `postinstall`), or live MCP clients are ever invoked. If S0 flags a critical flaw or hostile suppression, the target is blocked from dynamic execution unless explicitly overridden for authorized benchmark fixtures.
2. **Untrusted Target Boundary:**  
   Target source code, config files, MCP tool descriptions, parameter schemas, tool return values, and stderr output are treated strictly as **untrusted data**. They must never be executed via `eval()`, passed directly to shells, or trusted as truth.
3. **The Add-Only LLM Authority:**  
   The local open-weight model (Qwen3) can add heuristic findings and extract evidence quotes. **It is mathematically forbidden from clearing, suppressing, downgrading, or overriding any deterministic finding** produced by static rules, AST checks, or kernel syscall monitors.
4. **I/O Isolation (Clean Stdio Invariant):**  
   Because MCP communication relies on standard input/output (`stdio`), all background observation harnesses (`strace`, egress sinks, supervisor logs) must redirect strictly to disk files (`/obs/...`). Zero diagnostic text, banner text, or log statements may be emitted to `stdout`.

---

### HR3: Zero-Mock Architecture (Real Code, Real Runtimes)

* **No Mock MCP Servers in Audits:** All audits must run against real, functional MCP servers conforming to the JSON-RPC 2.0 specification over `stdio`.
* **No Synthetic Test Sleeps:** No artificial `time.sleep()` or synthetic mocks simulating detection.
* **Live Benchmark Verification:** All 6 benchmark fixtures (`clean_notes`, `clean_fetch`, `poisoned_weather`, `vulnerable_runner`, `exfil_calculator`, `rugpull_suite`, `attack_the_auditor`) must be verified against actual tool execution and real OS facilities.

---

### HR4: Universal Pydantic Schema Enforcement

* Every finding produced anywhere in Shadowprint must instantiate the frozen `Finding` schema in `shadowprint/models.py`.
* Unvalidated dictionaries or loose tuples are strictly prohibited across engine boundaries.
* Every finding must populate:
  - `id`: Unique identifier (e.g., `SP-S0-001`, `SP-S1-002`, `SP-S2-003`, `SP-S3-004`).
  - `engine`: Literal `S0`, `S1`, `S2`, or `S3`.
  - `target`: Target server or fixture identifier.
  - `tool`: Exact tool name under scrutiny (or `__server__` for server-level findings).
  - `category`: Canonical category (e.g., `command_injection`, `prompt_injection`, `canary_exfil`, `rugpull_drift`, `tamper_attempt`).
  - `severity`: `critical`, `high`, `medium`, `low`, `info`.
  - `assessment`: `FAIL`, `FLAGGED`, `PASS`, `NOT_ASSESSED`.
  - `confidence`: `confirmed`, `corroborated`, `heuristic`.
  - `evidence_basis`: `static`, `metadata`, `runtime_observed`, `diff`.
  - `location`: Dictionary with `file` and optional `line`.
  - `claim`: Declared capability or description text.
  - `evidence`: Exact offending string, syscall log line, or diff delta.
  - `remediation`: Concrete mitigation advice.
  - `raw_result_ref`: Relative path to raw tool output.

---

### HR5: The Five Mandatory Production Fixes

1. **Stdio Cleanliness:** The container entrypoint (`docker/entrypoint.sh`) redirects sink logs to `/obs/sink.log` and strace output to `/obs/strace.log`. Only `server.py` retains `stdout`.
2. **Windows Docker Desktop Compatibility:** Container launches must include:
   ```bash
   --cap-drop ALL --cap-add SYS_PTRACE --security-opt seccomp=unconfined --network none
   ```
3. **Single-Profile Snapshot Default:** Fast single snapshot execution for live judging. `--differential` multi-profile querying is an optional CLI flag.
4. **Deterministic Stage Trigger for Rug-Pull:** The `rugpull_suite` fixture toggles its malicious payload upon existence of `/tmp/rugpull_trigger.flag`, ensuring $<1.5\text{s}$ live detection during demo.
5. **Clustered Line Deduplication:** Normalizer must apply the cluster key:
   $$\text{key} = (\text{file},\; \text{line} // 3,\; \text{category})$$

---

### HR6: Offline-Only Airgap Guarantee

* Shadowprint must function with 100% fidelity without an active internet connection.
* Audit execution must never attempt outbound network requests to third-party APIs.
* Ollama must run locally on `127.0.0.1:11434`.

---

### HR7: Equal 50/50 Division & Git Collaboration Workflow (Jasjyot & Gaurang)

The codebase is split cleanly between two co-builders. Code within one builder's domain must not be modified by the other without an explicit integration merge.

#### 1. Branching & Isolation Rules:
* **The Shared Foundation on `main`:** Only the initial project skeleton, `.gitignore`, `requirements.txt`, `README.md`, and frozen `shadowprint/models.py` are committed directly to `main`.
* **Builder Branches:**
  - Jasjyot develops exclusively in branch `feat/jasjyot`.
  - Gaurang develops exclusively in branch `feat/gaurang`.
* **Zero Direct Push to `main`:** Once initial skeleton is pushed, no one pushes directly to `main`. All updates merge via Pull Requests after passing tests.
* **Keep Updated:** Before starting new work or big changes:
  ```bash
  git fetch origin
  git merge origin/main
  ```
* **Forbidden Git Actions:** Never edit each other's files simultaneously. Never commit generated files (`/obs`, `/results`, `shadowprint.db`, `.venv`).

#### 2. File & Module Ownership Breakdown:
* **Jasjyot Singh's Modules (`feat/jasjyot`):**
  - `shadowprint/cli.py` (Typer CLI orchestrator)
  - `shadowprint/normalizer.py` (Finding deduplication)
  - `shadowprint/s0_static/*` (Bandit AST, Semgrep taint, Gitleaks, suppression check)
  - `shadowprint/s1_metadata/*` (Deterministic regex, Qwen3 Ollama judge)
  - `shadowprint/s4_reporting/markdown_reporter.py`
  - `shadowprint/s4_reporting/terminal_ui.py`
  - `fixtures/clean_notes/*`, `fixtures/poisoned_weather/*`, `fixtures/vulnerable_runner/*`
  - `scripts/trigger_rugpull.py`
* **Gaurang Udgirkar's Modules (`feat/gaurang`):**
  - `shadowprint/models.py` (Shared contract — frozen together)
  - `shadowprint/client/mcp_client.py` (Guarded least-capability stdio client)
  - `shadowprint/s2_prober/*` (Burst probe, capability model, canary tripwire, strace parser)
  - `shadowprint/s3_integrity/*` (SQLite store, 3-layer SHA-256, watcher loop, deepdiff)
  - `shadowprint/s4_reporting/sarif_exporter.py` (SARIF 2.1.0 standard exporter)
  - `docker/*` (`Dockerfile.sandbox`, `entrypoint.sh`, `sink.py`)
  - `fixtures/clean_fetch/*`, `fixtures/exfil_calculator/*`, `fixtures/rugpull_suite/*`, `fixtures/attack_the_auditor/*`
  - `scripts/test_manifest.py`, `scripts/preflight_check.py`, `manifest/*`

---

### HR8: Live Truth Verification Gate

* `scripts/test_manifest.py` is the ultimate arbiter of correctness.
* The test suite validates all 6 fixtures against `manifest/shadowprint_fixture_manifest.json`.
* Target standard: **100% Core Recall** on planted issues and **0 False Positives** on clean baselines.

---

## 💻 PART 2: Coding Rules (CR1 – CR6)

### CR1: CLI Subcommand Contracts (`shadowprint/cli.py`)
The Typer CLI exposes exactly four primary subcommands:
* `shadowprint audit <path>`: Executes full pipeline (S0 $\rightarrow$ S1 $\rightarrow$ S2 $\rightarrow$ S3 $\rightarrow$ S4). Supports flags:
  - `--skip-dynamic`: Runs S0 and S1 only (for untrusted third-party code).
  - `--differential`: Runs multi-profile client snapshots.
  - `--json`: Outputs raw JSON to stdout.
* `shadowprint approve <path>`: Stores/updates baseline pins in `shadowprint.db`.
* `shadowprint watch <path>`: Runs live monitoring loop (polling every 2s) and alerts on changes.
* `shadowprint report <path>`: Re-generates Markdown and SARIF reports from existing run data.

---

### CR2: S0 Static Inspection Rules (`shadowprint/s0_static/`)
1. **Hostile Suppression Inspection:** Scan target files for `# nosec`, `# nosemgrep`, `.gitleaksignore`. Flag every occurrence as `TAMPER_ATTEMPT` (`severity="high"`).
2. **Bandit Execution:** Run via subprocess `bandit -r <target> -f json --exit-zero`. Map Bandit issue types (B301, B602, B310, etc.) to canonical categories.
3. **Semgrep Execution:** Run with custom rule pack `mcp_taint_rules.yaml`. Track untrusted `@mcp.tool()` arguments to sinks (`os.system`, `subprocess`, `open`).
4. **Gitleaks Execution:** Run via `gitleaks detect --source=<target> --no-git --report-format=json`.

---

### CR3: S1 Prompt Isolation & Ollama Integration (`shadowprint/s1_metadata/`)
1. Prompts for Qwen3 must be isolated immutable constants in `s1_metadata/qwen_judge.py`.
2. Requests to Ollama must use `temperature=0` and specify `format="json"`.
3. Deterministic regex rules must check for:
   - Unicode TAG characters (`\U000E0000`–`\U000E007F`).
   - Zero-width spaces (`\u200B`, `\u200C`, `\u200D`, `\uFEFF`).
   - Hidden HTML comments (`<!-- ... -->`).
   - Second-person imperatives (`"You must"`, `"Assistant shall"`, `"Ignore previous directions"`).
4. **Authority Invariant:** If deterministic rules flag an issue, Qwen3 output cannot dismiss it.

---

### CR4: S2 Dynamic Probing Protocol (`shadowprint/s2_prober/`)
1. **Canary Placement:** Plant `/tmp/canary_creds.env` with known unique entropy `CANARY_KEY_98721X`.
2. **Strace Syscall Parsing:** Filter for `openat` referencing `/tmp` or sensitive files, `connect` targeting non-localhost, and `execve`.
3. **Burst Probe Sweep:** Send up to 10 rapid calls with test/fuzz vectors (`; id;`, `../../etc/passwd`).
4. **Exfil Detection:** Scan tool returns, stdout, stderr, and sink logs for canary tokens.

---

### CR5: S3 Fingerprinting & Watcher (`shadowprint/s3_integrity/`)
1. Store 3-layer SHA-256 fingerprint in SQLite:
   - `definition_hash`: Canonical tool names, descriptions, parameter schemas.
   - `artifact_hash`: Merkle/tree hash of server source files.
   - `behavior_hash`: Hash of recorded syscall tuples from S2.
2. Watcher queries `tools/list` every 2 seconds.
3. Upon hash mismatch, run `deepdiff` with explicit character escaping and emit a red terminal alert.

---

### CR6: S4 Unified Reporting (`shadowprint/s4_reporting/`)
1. Normalize and deduplicate findings using `(file, line // 3, category)`.
2. Generate `output/shadowprint_report.md` with executive summary, findings table, and remediation advice.
3. Generate valid SARIF 2.1.0 in `output/results.sarif` mapping findings to CWE IDs.

---

## 🛡️ PART 3: The Pre-Commit Anti-Hallucination Checklist

Before saving, committing, or declaring any phase complete, verify:

```markdown
- [ ] Are all cloud LLM API calls absent? (Local Ollama Qwen3 only)
- [ ] Does Qwen3 have strictly add-only authority? (Cannot suppress deterministic findings)
- [ ] Are container stdout outputs 100% clean JSON-RPC? (All strace/sink logs go to /obs/)
- [ ] Is Engine S0 running before the target process or container executes?
- [ ] Are Windows Docker flags exact? (--cap-drop ALL --cap-add SYS_PTRACE --security-opt seccomp=unconfined --network none)
- [ ] Is the rug-pull trigger using /tmp/rugpull_trigger.flag? (No call counters)
- [ ] Is deduplication clustering by (file, line // 3, category)?
- [ ] Are all findings validating against shadowprint/models.py Finding schema?
- [ ] Are SQLite operations contained in shadowprint.db?
- [ ] Is deepdiff configured to escape non-printable and Unicode TAG characters?
- [ ] Does clean_notes produce 0 false positives?
- [ ] Does python scripts/test_manifest.py pass with 100% core recall?
```
