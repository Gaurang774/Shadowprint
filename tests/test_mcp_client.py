"""
Unit tests for GuardedMCPClient in shadowprint/client/mcp_client.py.
"""

import sys
import pytest
from pathlib import Path
from shadowprint.client.mcp_client import GuardedMCPClient
from shadowprint.models import Snapshot, ToolDefinition

MOCK_SERVER_SCRIPT = str(Path(__file__).parent / "mock_mcp_server.py")


@pytest.mark.anyio
async def test_mcp_client_handshake_and_tools():
    client = GuardedMCPClient(command=sys.executable, args=[MOCK_SERVER_SCRIPT], timeout=3.0)
    await client.start()
    try:
        init_res = await client.initialize()
        assert init_res["protocolVersion"] == "2024-11-05"

        tools = await client.list_tools()
        assert len(tools) == 1
        assert isinstance(tools[0], ToolDefinition)
        assert tools[0].name == "calculate_tax"

        call_res = await client.call_tool("calculate_tax", {"income": 50000})
        assert "content" in call_res
        assert call_res["content"][0]["text"] == "Tax computed successfully."
    finally:
        await client.close()


@pytest.mark.anyio
async def test_mcp_client_fetch_snapshot():
    client = GuardedMCPClient(command=sys.executable, args=[MOCK_SERVER_SCRIPT], timeout=3.0)
    snapshot = await client.fetch_snapshot("test_server")
    assert isinstance(snapshot, Snapshot)
    assert snapshot.server_name == "test_server"
    assert len(snapshot.tools) == 1
    assert snapshot.tools[0].name == "calculate_tax"
    # definition_hash must be non-empty SHA-256
    assert len(snapshot.definition_hash) == 64
