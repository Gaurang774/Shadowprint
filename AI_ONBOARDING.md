# Shadowprint — AI & Builder Onboarding Guide (Read This First)

> **MANDATORY CRASH COURSE:** Read this document before inspecting code, writing any module, or running commands. It establishes the single source of truth and prevents architectural hallucinations.

---

## ⚡ 60-Second Crash Course

**What is Shadowprint?**  
An evidence-first, 100% offline security auditor for Model Context Protocol (MCP) servers. It detects tool poisoning, hidden malicious capabilities, command injections, hardcoded secrets, and live rug-pulls across four dimensions:
$$\text{Claim} \longleftrightarrow \text{Code} \longleftrightarrow \text{Runtime} \longleftrightarrow \text{Drift}$$

**Who is building it?**  
* **Jasjyot Singh (Team Lead / Builder A):** S0 Static Code Analysis, S1 Metadata Regex/Deterministic Rules, Deduplication Normalizer, Unified Reporting & UI (S4: Markdown, Rich Terminal, SARIF 2.1.0), and CLI Orchestration.
* **Gaurang Udgirkar (Builder B):** Ollama & Local Qwen3-8B AI Judge (S1), Docker Sandboxing, Guarded MCP Client, S2 Dynamic Kernel Syscall Probing, S3 SQLite 3-Layer Pinning & Live Watcher.

---

## 🛑 The 4 Inviolable System Invariants

1. **Static Precedence Invariant (Zero Early Execution):** Engine S0 must complete and pass static safety checks *before* the target server process, package scripts (`setup.py`, `postinstall`), or live MCP clients are ever executed.
2. **Untrusted Target Boundary:** Source code, configuration files, MCP tool descriptions, schemas, tool returns, and stderr are treated strictly as untrusted data.
3. **Add-Only LLM Authority:** The local Qwen3 model (via Ollama) can only add heuristic findings or extract quotes. **It is mathematically forbidden from clearing, suppressing, or downgrading any deterministic finding from static rules or kernel syscall monitors.**
4. **Clean Stdio Isolation:** MCP JSON-RPC communicates over `stdout`. All background harnesses (`strace`, egress sink, supervisor logs) **must redirect strictly to disk files (`/obs/...`)**. Zero non-RPC text may touch `stdout`.

---

## 🧭 Ground Truth (Docs Lie; This Doesn't)

| Aspect | The Ground Truth | Forbidden Hallucinations |
|---|---|---|
| **Runtime & Host** | Python 3.10+ (Windows 11 host + Ubuntu container) | No unpinned Python 2 or legacy scripts |
| **Local LLM** | Ollama with `qwen3:8b` (fallback `qwen3:4b`) on `127.0.0.1:11434` | **NO cloud APIs** (No OpenAI, Anthropic, Gemini API keys in audit code) |
| **LLM Output** | Strict JSON schema via Pydantic (`temperature=0`) | No free-form markdown or unparsed strings |
| **CLI Framework** | Typer + Rich | No argparse, click, or invented CLI tools |
| **Dynamic Sandbox** | Docker with `--cap-drop ALL --cap-add SYS_PTRACE --security-opt seccomp=unconfined --network none` | Do not run untrusted targets directly on host |
| **Secret Detection** | Gitleaks (`gitleaks detect --source=<dir> --no-git`) | No home-brewed regex replacing Gitleaks |
| **Static Analysis** | Bandit AST (`-f json`) + Custom Semgrep YAML rules | Do not skip AST checks |
| **Integrity Hashes** | SQLite 3 (`shadowprint.db`) storing 3-layer SHA-256 (Definition, Artifact, Behavior) | No pickle, raw JSON files for persistent state |
| **Diff Engine** | `deepdiff` with non-printable/zero-width character escaping | No simple string comparison |
| **Rug-Pull Demo** | Stage trigger via touch file (`/tmp/rugpull_trigger.flag`) | No call counters (e.g., flip after 5 calls) |
| **Deduplication** | Cluster key: `(finding.file, finding.line // 3, finding.category)` | No arbitrary line grouping |
| **Output Formats** | Rich Terminal Matrix + `output/shadowprint_report.md` + SARIF 2.1.0 (`results.sarif`) | No non-standard JSON reports |

---

## 🎯 6 Benchmark Fixtures (Target Set)

| Fixture | Attack Vector / Behavior | Catching Engine | Expected Result |
|---|---|---|---|
| `fixtures/clean_notes` | Benign notes CRUD tool | None | **0 False Positives (Clean PASS)** |
| `fixtures/clean_fetch` | Minimal safe fetch server | None | **0 False Positives (Clean PASS)** |
| `fixtures/poisoned_weather` | Prompt injection in descriptions via Unicode TAGs | Engine S1 (Rules + Qwen3) | **FLAGGED / FAIL** |
| `fixtures/vulnerable_runner` | `shell=True` injection + hardcoded AWS key | Engine S0 (Bandit + Gitleaks) | **FAIL (Critical/High)** |
| `fixtures/exfil_calculator` | Canary key theft (`/tmp/canary_creds.env`) + egress | Engine S2 (Dynamic Prober) | **FAIL (Confirmed Exfil)** |
| `fixtures/rugpull_suite` | Definition flips on `/tmp/rugpull_trigger.flag` | Engine S3 (Live Watcher) | **RED ALERT (<1.5s)** |
| `fixtures/attack_the_auditor` | Hostile `#nosec` / `#nosemgrep` comments | S0/S1 Hardening | **TAMPER_ATTEMPT Flagged** |

---

## 🚀 Preflight Health Check Commands

Run these to verify local environment readiness before starting any engine:
```powershell
python --version                 # Verified: Python 3.14.3
docker ps                        # Verified: Docker 29.8+ daemon running
ollama list                      # Verified: qwen3:8b and qwen3:4b present
```
