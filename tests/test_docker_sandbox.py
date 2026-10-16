"""
Unit tests for docker/sink.py and container sandbox isolation.
"""

import os
import json
import time
import subprocess
import urllib.request
import threading
from pathlib import Path
from http.server import HTTPServer

from docker.sink import SilentSinkHandler, SINK_LOG_PATH


def test_sink_handler_captures_post_request(tmp_path):
    # Temporarily redirect SINK_LOG_PATH to tmp_path
    log_file = tmp_path / "test_sink.log"
    import docker.sink
    docker.sink.SINK_LOG_PATH = log_file

    # Reconfigure logger handler for test
    docker.sink.logger.handlers.clear()
    import logging
    handler = logging.FileHandler(log_file, encoding="utf-8")
    docker.sink.logger.addHandler(handler)

    # Start test server on dynamic port
    server = HTTPServer(("127.0.0.1", 0), SilentSinkHandler)
    port = server.server_port
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    time.sleep(0.1)

    # Send test HTTP POST
    url = f"http://127.0.0.1:{port}/exfil?key=CANARY_KEY_98721X"
    payload = json.dumps({"stolen_creds": "canary_value"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST", headers={"Content-Type": "application/json"})

    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        resp_data = json.loads(response.read().decode("utf-8"))
        assert resp_data["status"] == "received"

    server.shutdown()
    handler.close()

    # Verify sink.log contents
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "CANARY_KEY_98721X" in content
    assert "stolen_creds" in content


def test_docker_container_stdio_cleanliness(tmp_path):
    # Test that container outputs strictly pure stdout without strace leakage
    obs_dir = tmp_path / "obs"
    obs_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "docker", "run", "--rm", "-i",
        "--network", "none",
        "--cap-drop", "ALL",
        "--cap-add", "SYS_PTRACE",
        "--security-opt", "seccomp=unconfined",
        "-v", f"{obs_dir}:/obs",
        "shadowprint-sandbox",
        "-c", "print('PURE_MCP_JSON_RPC')",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    assert result.returncode == 0
    # stdout must be ONLY the output string, no strace headers or sink messages
    assert result.stdout.strip() == "PURE_MCP_JSON_RPC"

    # Verify strace wrote to /obs/strace.log on disk
    strace_log = obs_dir / "strace.log"
    assert strace_log.exists()
    assert "execve" in strace_log.read_text(encoding="utf-8", errors="replace")
