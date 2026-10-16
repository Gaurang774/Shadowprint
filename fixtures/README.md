# Benchmark Fixtures

This directory contains the 6 benchmark MCP server fixtures:

| Directory | Type | Planted Behavior / Flaw | Owner |
|---|---|---|---|
| `clean_notes/` | Benign CRUD | Honest notes tool; 0 false positives | Jasjyot |
| `clean_fetch/` | Benign Fetch | Minimal safe fetch; 0 false positives | Gaurang |
| `poisoned_weather/` | Malicious | Prompt injection in descriptions via Unicode TAGs | Jasjyot |
| `vulnerable_runner/` | Malicious | `shell=True` injection + hardcoded AWS secret | Jasjyot |
| `exfil_calculator/` | Malicious | Canary file theft (`/tmp/canary_creds.env`) + egress | Gaurang |
| `rugpull_suite/` | Malicious | Description mutated on `/tmp/rugpull_trigger.flag` | Gaurang |
| `attack_the_auditor/` | Malicious | Hostile `#nosec` / `#nosemgrep` suppression | Gaurang |
