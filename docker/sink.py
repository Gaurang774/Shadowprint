"""
Shadowprint In-Container HTTP Sink.
Owner: Gaurang Udgirkar [G]

A lightweight HTTP sink running inside the sandbox on 127.0.0.1:8080.
Captures unauthorized egress or exfiltration attempts (GET/POST/PUT/DELETE)
and records headers, query parameters, and payloads into /obs/sink.log.
Conforms strictly to ADR-003: Never writes to stdout.
"""

import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure log directory exists
OBS_DIR = Path("/obs")
OBS_DIR.mkdir(parents=True, exist_ok=True)
SINK_LOG_PATH = OBS_DIR / "sink.log"

# Configure silent logger strictly writing to /obs/sink.log
logger = logging.getLogger("shadowprint_sink")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(SINK_LOG_PATH, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
logger.addHandler(file_handler)


class SilentSinkHandler(BaseHTTPRequestHandler):
    """Silent HTTP handler capturing all requests and logging exfiltrated data."""

    def _log_request(self, method: str):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8", errors="replace") if content_length > 0 else ""
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            event = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": method,
                "path": parsed_url.path,
                "query": query_params,
                "headers": dict(self.headers),
                "body": body,
                "client_address": self.client_address[0],
            }

            logger.info(json.dumps(event))

            # Return 200 OK with minimal JSON
            response_data = json.dumps({"status": "received", "length": content_length}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response_data)))
            self.end_headers()
            self.wfile.write(response_data)
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_response(500)
            self.end_headers()

    def do_GET(self):
        self._log_request("GET")

    def do_POST(self):
        self._log_request("POST")

    def do_PUT(self):
        self._log_request("PUT")

    def do_DELETE(self):
        self._log_request("DELETE")

    def log_message(self, format, *args):
        # Override to suppress standard BaseHTTPRequestHandler stderr logging
        pass


def run_sink(host: str = "0.0.0.0", port: int = 8080):
    """Starts the silent HTTP sink server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, SilentSinkHandler)
    logger.info(f"Silent HTTP sink listening on {host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Sink stopped by keyboard interrupt.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    run_sink(host=host, port=port)
