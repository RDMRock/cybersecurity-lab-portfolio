# MCP tool hardening

This is the standalone implementation from Assignment 6 Task 19. It addresses the database injection, Git command injection, and file traversal demonstrated in Task 18. The implementation is preserved. The test file adds a temporary synthetic fixture so it does not depend on the original course databases.

## Run the ten regression tests

Use Python 3.11 or later in a virtual environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_task19_secure_servers.py
```

Run these commands from this directory. The suite creates and removes its own temporary SQLite database and public note. Git subprocesses are mocked in the valid-clone test. The tests do not need a live vulnerable service, credentials, or a real clone.

The checks cover SQL injection, normal field-limited lookup, literal wildcard handling, shell-payload rejection, an argument-list Git call, traversal rejection, a normal file read, rejection of a metadata URL, registration of all three tool groups, and the original attack inputs through FastMCP calls.

## Implementation

- `task19_secure_servers.py`: three FastMCP servers and their validation helpers.
- `test_task19_secure_servers.py`: ten test methods from the coursework, with fixture isolation added for this portfolio.
- `requirements.txt`: the versions used for the local portfolio check, not a claim that these will remain the latest versions.

The default runtime expects `mcp-security-lab/data/public`, `data/repos`, and a SQLite file under the configured root. A compatible `users` table needs `id`, `username`, and `role`. `MCP_LAB_ROOT` selects another prepared fixture. Running `python task19_secure_servers.py git`, `file`, or `db` starts the selected server over its default transport. The public test suite does not start a listening network service.

## Limits

This is a focused educational replacement, not a complete deployment. It has no per-caller authorization layer. Path resolution assumes trusted directory ownership and does not eliminate all concurrent symlink races. Git operations still need a restricted service account, trusted repository configuration, and resource controls. The URL allowlist is narrow but is not a complete network sandbox. Error responses expose implementation details. The ten checks do not establish that every function or edge case is secure.

See the [case study](../../case-studies/06-browser-security-and-mcp-hardening.md) and [validation record](../../docs/validation.md).
