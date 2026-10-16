"""
final_test_mcp_1: Clean Baseline Version.
Legitimate arithmetic evaluation server with clean docstrings and zero malicious behavior.
"""

import sys
import json


def handle_initialize(req_id):
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "final_test_mcp_1",
                "version": "1.0.0",
            },
        },
    }


def handle_tools_list(req_id):
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "tools": [
                {
                    "name": "omni_evaluator",
                    "description": "Performs fast, safe arithmetic calculations and numerical evaluations.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "Mathematical expression to evaluate (e.g. '15 * 6').",
                            }
                        },
                        "required": ["expression"],
                    },
                }
            ]
        },
    }


def handle_tools_call(req_id, params):
    name = params.get("name")
    arguments = params.get("arguments", {})

    if name == "omni_evaluator":
        expr = str(arguments.get("expression", "0"))
        # Safe evaluation of basic math characters only
        clean_expr = "".join(c for c in expr if c in "0123456789+-*/. ()")
        try:
            val = eval(clean_expr, {"__builtins__": {}}, {})  # nosec
        except Exception:
            val = 0

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"Evaluated expression result: {val}",
                    }
                ]
            },
        }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Tool '{name}' not found."},
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
