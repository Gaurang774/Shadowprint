"""
Clean Fetch MCP Server (Benchmark Fixture 1b - Negative Control).
Implements a benign, safe URL fetch tool with 0 vulnerabilities and 0 false positives.
"""

import sys
import json
import logging

logging.basicConfig(level=logging.INFO, stream=sys.stderr)


def handle_initialize(req_id):
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "clean_fetch",
                "version": "1.0.0"
            }
        }
    }


def handle_tools_list(req_id):
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "tools": [
                {
                    "name": "fetch",
                    "description": "Safely retrieves plain-text content from allowed HTTP/HTTPS URLs.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to fetch content from."
                            }
                        },
                        "required": ["url"]
                    }
                }
            ]
        }
    }


def handle_tools_call(req_id, params):
    name = params.get("name")
    arguments = params.get("arguments", {})

    if name == "fetch":
        url = arguments.get("url", "")
        # Benign simulated response without external egress or dangerous syscalls
        content_text = f"Content preview for {url}: OK (200) - Clean plain text."
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": content_text
                    }
                ]
            }
        }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32601,
            "message": f"Tool '{name}' not found."
        }
    }


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue

        method = req.get("method")
        req_id = req.get("id")

        if method == "initialize":
            res = handle_initialize(req_id)
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            res = handle_tools_list(req_id)
        elif method == "tools/call":
            res = handle_tools_call(req_id, req.get("params", {}))
        elif method == "prompts/list":
            res = {"jsonrpc": "2.0", "id": req_id, "result": {"prompts": []}}
        elif method == "resources/list":
            res = {"jsonrpc": "2.0", "id": req_id, "result": {"resources": []}}
        elif method == "ping":
            res = {"jsonrpc": "2.0", "id": req_id, "result": {}}
        else:
            if req_id is not None:
                res = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}
            else:
                continue

        sys.stdout.write(json.dumps(res) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
