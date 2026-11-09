"""Secure replacements for the three MCP servers exploited in Task 18.

Run one server with ``python task19_secure_servers.py git|file|db``. The lab
data directory can be changed with MCP_LAB_ROOT before starting the process.
"""

from __future__ import annotations

import os
import re
import sqlite3
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.parse import urlsplit

import requests
from fastmcp import FastMCP


LAB_ROOT = Path(os.environ.get("MCP_LAB_ROOT", Path(__file__).parent / "mcp-security-lab")).resolve()
PUBLIC_ROOT = (LAB_ROOT / "data" / "public").resolve()
REPOS_ROOT = (LAB_ROOT / "data" / "repos").resolve()
DB_PATH = (LAB_ROOT / "mcp_lab_vulnerable.db").resolve()
MAX_TEXT = 50_000

git_mcp = FastMCP("SecureGitServer")
file_mcp = FastMCP("SecureFileServer")
db_mcp = FastMCP("SecureDatabaseServer")


def _safe_child(root: Path, raw: str) -> Path:
    """Confine a relative path to a trusted root, including through symlinks."""
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise ValueError("A nonempty relative path is required")
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("Absolute paths and parent traversal are forbidden")
    candidate = (root / path).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("Path escapes the allowed directory")
    return candidate


def _github_url(raw: str) -> str:
    """Allow HTTPS GitHub owner/repository URLs only."""
    if not isinstance(raw, str) or len(raw) > 300:
        raise ValueError("Invalid repository URL")
    parsed = urlsplit(raw)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "github.com"
        or parsed.port is not None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Only plain HTTPS GitHub repository URLs are allowed")
    parts = parsed.path.strip("/").split("/")
    if len(parts) != 2 or any(p in {"", ".", ".."} for p in parts):
        raise ValueError("Expected owner/repository")
    if not all(re.fullmatch(r"[A-Za-z0-9_.-]+", p) for p in parts):
        raise ValueError("Invalid repository name")
    return raw


def git_clone_secure(repo_url: str) -> dict:
    try:
        url = _github_url(repo_url)
        REPOS_ROOT.mkdir(parents=True, exist_ok=True)
        destination = REPOS_ROOT / f"repo_{uuid.uuid4().hex}"
        # An argument list and shell=False keep metacharacters as data.
        result = subprocess.run(
            ["git", "clone", "--", url, str(destination)],
            shell=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr,
                "path": str(destination) if result.returncode == 0 else None}
    except (ValueError, subprocess.TimeoutExpired, OSError) as exc:
        return {"success": False, "error": str(exc)}


_REVISION = r"(?:HEAD(?:~[0-9]+)?|[0-9a-fA-F]{7,40})"


def _revision_range(raw: str) -> str:
    if not isinstance(raw, str) or not re.fullmatch(rf"{_REVISION}(?:\.\.{_REVISION})?", raw):
        raise ValueError("Invalid Git revision range")
    return raw


def git_diff_secure(repo_path: str, commit_range: str = "HEAD~1..HEAD") -> dict:
    try:
        repository = _safe_child(REPOS_ROOT, repo_path)
        if not (repository / ".git").exists():
            raise ValueError("Repository not found under the allowed directory")
        revision = _revision_range(commit_range)
        result = subprocess.run(
            ["git", "-C", str(repository), "diff", revision], shell=False,
            capture_output=True, text=True, timeout=10,
        )
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
    except (ValueError, subprocess.TimeoutExpired, OSError) as exc:
        return {"success": False, "error": str(exc)}


def git_log_secure(repo_path: str, options: str = "--oneline") -> dict:
    try:
        repository = _safe_child(REPOS_ROOT, repo_path)
        if not (repository / ".git").exists():
            raise ValueError("Repository not found under the allowed directory")
        if options not in {"--oneline", "--pretty=oneline"}:
            raise ValueError("Unsupported log format")
        result = subprocess.run(
            ["git", "-C", str(repository), "log", options], shell=False,
            capture_output=True, text=True, timeout=10,
        )
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
    except (ValueError, subprocess.TimeoutExpired, OSError) as exc:
        return {"success": False, "error": str(exc)}


@git_mcp.tool()
def git_clone(repo_url: str) -> dict:
    """Clone an approved HTTPS GitHub repository into the lab repository directory."""
    return git_clone_secure(repo_url)


@git_mcp.tool()
def git_diff(repo_path: str, commit_range: str = "HEAD~1..HEAD") -> dict:
    """Show a validated revision range for a repository under the lab directory."""
    return git_diff_secure(repo_path, commit_range)


@git_mcp.tool()
def git_log(repo_path: str, options: str = "--oneline") -> dict:
    """Show a repository log in an approved format."""
    return git_log_secure(repo_path, options)


def read_file_secure(filepath: str) -> dict:
    try:
        path = _safe_child(PUBLIC_ROOT, filepath)
        if not path.is_file():
            raise ValueError("Public file not found")
        with path.open("r", encoding="utf-8", errors="replace") as stream:
            content = stream.read(MAX_TEXT)
        return {"success": True, "content": content, "path": str(path), "size": len(content)}
    except (ValueError, OSError) as exc:
        return {"success": False, "error": str(exc)}


def write_file_secure(filepath: str, content: str) -> dict:
    try:
        if not isinstance(content, str) or len(content) > MAX_TEXT:
            raise ValueError("Text content exceeds the allowed size")
        path = _safe_child(PUBLIC_ROOT, filepath)
        if not path.parent.is_dir():
            raise ValueError("Public parent directory does not exist")
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW
        descriptor = os.open(path, flags, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
        return {"success": True, "path": str(path), "bytes_written": len(content)}
    except (ValueError, OSError) as exc:
        return {"success": False, "error": str(exc)}


def list_directory_secure(directory: str = ".") -> dict:
    try:
        path = _safe_child(PUBLIC_ROOT, directory)
        if not path.is_dir():
            raise ValueError("Public directory not found")
        names = sorted(child.name for child in path.iterdir())
        return {"success": True, "files": names, "count": len(names), "path": str(path)}
    except (ValueError, OSError) as exc:
        return {"success": False, "error": str(exc)}


def fetch_url_secure(url: str) -> dict:
    try:
        parsed = urlsplit(url)
        # A fixed host allowlist prevents requests to loopback and cloud metadata.
        if (parsed.scheme != "https" or parsed.hostname not in {"example.com", "www.example.com"}
                or parsed.port is not None or parsed.username is not None or parsed.password is not None):
            raise ValueError("URL is outside the approved HTTPS hosts")
        with requests.get(url, timeout=5, allow_redirects=False, stream=True) as response:
            content = response.raw.read(10_000, decode_content=True).decode("utf-8", errors="replace")
            return {"success": True, "status_code": response.status_code, "content": content}
    except (ValueError, requests.RequestException) as exc:
        return {"success": False, "error": str(exc)}


@file_mcp.tool()
def read_file(filepath: str) -> dict:
    """Read a text file within the public lab directory."""
    return read_file_secure(filepath)


@file_mcp.tool()
def write_file(filepath: str, content: str) -> dict:
    """Write a bounded text file within the public lab directory."""
    return write_file_secure(filepath, content)


@file_mcp.tool()
def list_directory(directory: str = ".") -> dict:
    """List a directory within the public lab directory."""
    return list_directory_secure(directory)


@file_mcp.tool()
def fetch_url(url: str) -> dict:
    """Fetch a bounded response from an approved HTTPS documentation host."""
    return fetch_url_secure(url)


def _valid_search(raw: str) -> str:
    if not isinstance(raw, str) or not raw or len(raw) > 128 or "\x00" in raw:
        raise ValueError("A search string of 1 to 128 characters is required")
    return raw


def _db_rows(query: str, value: str) -> list[dict]:
    # Read-only SQLite plus placeholders prevent stacked or predicate injection.
    with sqlite3.connect(DB_PATH.as_uri() + "?mode=ro", uri=True) as connection:
        rows = connection.execute(query, (value,)).fetchall()
    # The original server exposed password, API key, and secret_data fields.
    return [{"id": row[0], "username": row[1], "role": row[2]} for row in rows]


def query_users_secure(username: str) -> dict:
    try:
        rows = _db_rows("SELECT id, username, role FROM users WHERE username = ?", _valid_search(username))
        return {"success": True, "results": rows, "row_count": len(rows)}
    except (ValueError, sqlite3.Error) as exc:
        return {"success": False, "error": str(exc)}


def search_users_secure(search_term: str) -> dict:
    try:
        # instr treats %, _, and quotes as literal characters.
        rows = _db_rows("SELECT id, username, role FROM users WHERE instr(username, ?) > 0", _valid_search(search_term))
        return {"success": True, "results": rows, "count": len(rows)}
    except (ValueError, sqlite3.Error) as exc:
        return {"success": False, "error": str(exc)}


@db_mcp.tool()
def query_users(username: str) -> dict:
    """Look up one user by exact username without exposing credential fields."""
    return query_users_secure(username)


@db_mcp.tool()
def search_users(search_term: str) -> dict:
    """Find users by literal substring without exposing credential fields."""
    return search_users_secure(search_term)


if __name__ == "__main__":
    servers = {"git": git_mcp, "file": file_mcp, "db": db_mcp}
    if len(sys.argv) != 2 or sys.argv[1] not in servers:
        raise SystemExit("Usage: python task19_secure_servers.py git|file|db")
    servers[sys.argv[1]].run()
