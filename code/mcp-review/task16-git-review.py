"""Task 16 review excerpt; proposed code is not installed in the lab."""
import subprocess
from pathlib import Path


def vulnerable_git_log(repo_path: str, options: str = "--oneline") -> dict:
    # VULNERABLE: both user-controlled fields become shell syntax.
    cmd = f"cd {repo_path} && git log {options} 2>&1"
    result = subprocess.run(cmd, shell=True, capture_output=True,
                            text=True, timeout=5)
    return {"success": True, "output": result.stdout}


# PROPOSED: choose from supported operations; never accept raw CLI options.
ALLOWED_REPOS = Path("/srv/mcp-repos").resolve()
LOG_MODES = {"oneline": ["--oneline"], "stat": ["--stat"]}


def proposed_git_log(repo_path: str, mode: str = "oneline") -> dict:
    if mode not in LOG_MODES:
        raise ValueError("Unsupported log mode")
    repo = (ALLOWED_REPOS / repo_path).resolve(strict=True)
    if not repo.is_relative_to(ALLOWED_REPOS) or not repo.is_dir():
        raise ValueError("Repository outside allowed directory")
    # Argument list and shell=False keep '; id' as data, not a command.
    result = subprocess.run(
        ["git", "-C", str(repo), "log", *LOG_MODES[mode]],
        shell=False, capture_output=True, text=True, timeout=5, check=True)
    return {"success": True, "output": result.stdout}
