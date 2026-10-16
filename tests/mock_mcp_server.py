"""
Minimal valid stdio MCP server for testing GuardedMCPClient.
"""

import sys
import json

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        text = line.strip()
        if not text:
            continue
        try:
            req = json.loads(text)
        except Exception:
            continue

        method = req.get("method")
        req_id = req.get("id")

        if method == "initialize":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "test-server", "version": "1.0.0"},
                },
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            pass

        elif method == "tools/list":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "calculate_tax",
                            "description": "Calculates tax based on income.",
                            "inputSchema": {"type": "object", "properties": {"income": {"type": "number"}}},
                        }
                    ]
                },
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": "Tax computed successfully."}]
                },
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "prompts/list":
            res = {"jsonrpc": "2.0", "id": req_id, "result": {"prompts": []}}
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "resources/list":
            res = {"jsonrpc": "2.0", "id": req_id, "result": {"resources": []}}
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
