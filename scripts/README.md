# Shadowprint Validation & Demo Scripts

- `preflight_check.py`: Verifies Docker Desktop `SYS_PTRACE`, Ollama Qwen3 models, and Python packages.
- `test_manifest.py`: Validates all 6 fixtures against `shadowprint_fixture_manifest.json` for 100% recall.
- `trigger_rugpull.py`: Presentation stage trigger touching `/tmp/rugpull_trigger.flag`.
