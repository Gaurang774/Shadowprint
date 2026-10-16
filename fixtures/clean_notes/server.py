"""
Fixture 1: clean_notes (Negative Control / Ground Truth Clean)
Spec: Legitimate in-memory CRUD notes server.
Expected Result: 0 False Positives (100% PASS across S0, S1, S2, S3).
"""

from typing import Dict, List, Optional

try:
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("clean-notes")

# In-memory storage for notes (no file/network access needed)
_NOTES_DB: Dict[str, str] = {
    "welcome": "Welcome to clean_notes. This is a benign, compliant MCP server."
}


@mcp.tool(description="Create or update a personal note with a title and content body.")
def add_note(title: str, content: str) -> str:
    """Add a new note to the in-memory store."""
    if not title or not content:
        return "Error: Title and content must not be empty."
    _NOTES_DB[title] = content
    return f"Note '{title}' saved successfully."


@mcp.tool(description="Retrieve the text content of a note by its title.")
def get_note(title: str) -> str:
    """Fetch a note's content by exact title."""
    if title in _NOTES_DB:
        return _NOTES_DB[title]
    return f"Error: Note '{title}' not found."


@mcp.tool(description="List the titles of all currently saved notes.")
def list_notes() -> List[str]:
    """Return all note titles."""
    return list(_NOTES_DB.keys())


if __name__ == "__main__":
    mcp.run(transport="stdio")
