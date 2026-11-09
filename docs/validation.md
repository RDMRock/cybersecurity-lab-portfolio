# Validation record

Portfolio preparation date: November 8, 2026. These checks were run against the public copy, separately from the historical lab results.

| Check | Result | Boundary |
| --- | --- | --- |
| Standalone MCP suite | **10 tests passed** using FastMCP 3.4.0 and requests 2.32.5. | Temporary synthetic SQLite/file fixture. Valid Git subprocess call mocked. No live network service or full course backend was started. |
| Python files | All included Python files parsed successfully. | Syntax validation does not execute proposed review snippets or Flask route excerpts. |
| JavaScript routes | Both route files passed `node --check`. | Requires the original application context for behavioral execution. |
| Selected screenshots | All three inspected visually. | Original captures retained, not regenerated. |
| Public-file review | Checked included text for student numbers, local personal paths, personal email addresses, and common token/private-key patterns. | Automated patterns supplemented the selected-file review; they are not a proof that arbitrary data would be safe to publish. |
| Relative links | All repository-relative Markdown links resolve. | External links identify source repositories or related portfolio pages. |

The ten checks cover the published standalone implementation. The source report's sixteen backend tests and the Docker/browser before-and-after results are historical observations. They were not rerun during portfolio preparation. No lab exploitation, phishing delivery, or remote system change was performed for this publication.
