#!/bin/bash
# Shadowprint Sandbox Entrypoint Supervisor
# Owner: Gaurang Udgirkar [G]
# Conforms to ADR-003: Clean Stdio Isolation

set -e

# Ensure observation directory exists
mkdir -p /obs

# 1. Start localhost HTTP sink silently in background
# All sink output is redirected strictly to /obs/sink.log
python3 /opt/sink.py > /obs/sink.log 2>&1 &
SINK_PID=$!

# 2. Plant decoy canary secret token in standard discovery locations
echo "AWS_SECRET_ACCESS_KEY=CANARY_KEY_98721X" > /tmp/canary_creds.env
echo "ANTHROPIC_API_KEY=sk-ant-canary-token-99128X" >> /tmp/canary_creds.env
chmod 644 /tmp/canary_creds.env

# Clean up background sink on exit
cleanup() {
    kill $SINK_PID 2>/dev/null || true
}
trap cleanup EXIT INT TERM

if [ "$#" -eq 0 ]; then
    echo "No target command provided to entrypoint.sh" >&2
    exit 1
fi

# 3. Launch target MCP server under Linux strace
# ONLY the target process retains file descriptor 1 (stdout) for pure MCP JSON-RPC
strace -f -e trace=openat,connect,execve -o /obs/strace.log python3 "$@"
STATUS=$?

cleanup
exit $STATUS
