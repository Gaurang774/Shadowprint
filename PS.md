PS02 — MCP Server Security Auditor
Description
The Model Context Protocol (MCP) lets agents use external tools served by MCP servers, which
people often install from GitHub with little review. Since agents read each tool's description to
decide what to do, a malicious description can secretly instruct the agent (tool poisoning);
servers can also carry normal bugs, hidden extra powers, or change their tools after approval
(rug pull). Build a scanner that catches these issues before a server is trusted. It should include
a static scanner reading handler source for command injection, unsafe deserialization,
hardcoded secrets, and unnecessary file/network access; a description analyzer using an
open-weight model to flag text in tool names/descriptions/schemas aimed at the AI rather than
the user; a dynamic prober that runs the server in a container, calls every tool with test inputs,
and flags behavior mismatched with its description; a pin-and-diff system that fingerprints the
approved tool list and alerts on later changes; and a report with ID, severity, evidence, and fix
per finding. Teams must build their own test set: write or fork 3–5 small MCP servers (a mix of
clean and deliberately vulnerable/poisoned ones) to scan against, since no servers will be
provided. Scoring is self-demonstrated — the demo must show the scanner correctly flagging
the planted issues in your own test servers, plus catching a live rug-pull when a tool definition is
changed mid-demo.
Tools & Technologies
Official MCP Python SDK and MCP Inspector for connecting/testing; Node.js with the MCP
TypeScript SDK if building/running TS servers; Semgrep (custom rules), Bandit, and ESLint
security plugins for static analysis; Gitleaks for secret detection; Qwen3-8B/4B via Ollama plus
Prompt Guard 2 for description analysis; Docker sandboxing with strace and mitmproxy for
dynamic probing; SHA-256 fingerprinting in SQLite with deepdiff for pin-and-diff; SARIF 2.1.0 or
a simple Markdown report; a Typer CLI with an optional FastAPI + React web view.