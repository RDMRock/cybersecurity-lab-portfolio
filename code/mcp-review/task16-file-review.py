"""Task 16 review excerpt; proposed code is not installed in the lab."""
import os
from pathlib import Path


def vulnerable_read_file(filepath: str) -> dict:
    # VULNERABLE: existence is checked, but access is never authorized.
    if os.path.exists(filepath):
        with open(filepath, "r", errors="ignore") as f:
            content = f.read(50000)
        return {"success": True, "content": content,
                "path": os.path.abspath(filepath), "size": len(content)}
    return {"success": False, "error": "File not found"}


# PROPOSED: dedicate a non-sensitive directory to files this tool may read.
ALLOWED_DATA = Path("/srv/mcp-files").resolve()


def proposed_read_file(filepath: str) -> dict:
    supplied = Path(filepath)
    if supplied.is_absolute():
        raise ValueError("Absolute paths are not allowed")
    resolved = (ALLOWED_DATA / supplied).resolve(strict=True)
    # Reject ../ traversal and symlinks that resolve outside the allowed root.
    if not resolved.is_relative_to(ALLOWED_DATA) or not resolved.is_file():
        raise ValueError("Path outside readable files")
    with resolved.open("r", encoding="utf-8", errors="replace") as f:
        content = f.read(50000)
    return {"success": True, "content": content}
