# MCP secure code review

These Assignment 7 Task 16 excerpts reproduce the vulnerable file-read and shell-command operations, then propose replacements. **The proposed code was not installed or retested in the running lab.**

- [File access review](task16-file-review.py): resolve the requested file and enforce a dedicated readable root.
- [Git review](task16-git-review.py): restrict repository paths and log modes and invoke Git with a fixed argument list.

The code depends on trusted directory ownership, per-caller authorization, and least-privilege execution. Concurrent path changes, repository configuration, output limits, and detailed error handling require additional review. The vulnerable functions are included to explain the source review and should not be exposed as services.

Course source: [MCP Security Lab](https://github.com/sfucybersecurity/cmpt782/tree/MCP_Security_Lab), tested checkout `600f80f` as recorded in the assignment.
