"""docctl-mcp: an MCP server that audits construction document folders."""
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from docctl_mcp.naming import check_naming as _check_naming

PROJECT_ROOT = Path(__file__).resolve().parents[2] / "sample_project"
DOCS = PROJECT_ROOT / "documents"

mcp = MCPServer("docctl", version="0.1.0")


@mcp.tool()
def check_naming(filename: str) -> dict:
    """Check one filename against the project's ISO 19650-style naming convention.
    Returns whether it is compliant and a list of human-readable errors."""
    errors = _check_naming(filename)
    return {"filename": filename, "compliant": not errors, "errors": errors}


@mcp.tool()
def list_documents(only_problems: bool = False) -> list[dict]:
    """List all documents in the project folder with their naming check result.
    Set only_problems=True to return only non-compliant files."""
    results = []
    for f in sorted(DOCS.iterdir()):
        errors = _check_naming(f.name)
        if only_problems and not errors:
            continue
        results.append({"filename": f.name, "compliant": not errors, "errors": errors})
    return results


if __name__ == "__main__":
    mcp.run()