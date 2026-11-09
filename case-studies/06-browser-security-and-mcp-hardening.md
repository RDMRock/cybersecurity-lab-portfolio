# Browser security and MCP tool hardening

**Source:** Assignment 6, Tasks 1–19. **Status:** observed browser tests and implemented defensive code. Optional bonus tasks are not claimed.

## Browser investigation

| Tasks | Work | Observed outcome |
| --- | --- | --- |
| 1–3 | Reflected and stored XSS, followed by a cookie request to the course listener. | The browser displayed the test alerts, and the listener received the lab cookie value. |
| 4–5 | Hooked a demo page and a Kali-hosted page with BeEF. | The designated browser appeared online and moved offline when the relevant page closed. |
| 6–10 | Target-scoped ARP interception and HTTP response injection. | The HTTP alert executed. A handout URL redirected to HTTPS, where certificate trust blocked the attempt. |
| 11–12 | Located the actual proxy CA files and checked certificate fingerprints. | The trusted-proxy test delivered modified HTTPS content. Chrome CSP blocked an inline script until an additional, scoped lab policy change removed that obstacle. |
| 13–15 | Investigated failed and successful BeEF injection. | The HTTPS visit did not produce an online browser. On the HTTP test, Private Network Access and a malformed script tag were separate obstacles. After the scoped browser-policy change and HTML correction, the browser appeared online. |
| 16 | Compared BeEF's antivirus result with Windows Security Center. | No antivirus was detected or registered. This does not establish that every possible security tool was absent. |
| 17 | Displayed a fake update prompt. | Only the visual prompt was demonstrated. I did not click Install, execute a payload, or verify persistence in this task. |

The browser tests show why delivery, execution, and successful hooking need separate evidence. A `200 OK` for a script did not by itself prove that the browser ran it. The HTTPS result also depended on deliberate trust and policy changes inside the lab.

## MCP attack, patch, and regression checks

| Tool boundary | Original observation | Defensive change |
| --- | --- | --- |
| Database | An injected username returned all three seeded users and sensitive dummy fields. | Parameterized queries, a read-only database connection, and an explicit public-field projection. |
| Git | A repository argument reached a shell and returned the process user ID. | Validated URLs and repository paths, fixed argument lists, and `shell=False`. |
| Files | Traversal reached a private marker file I created for the test. | A public-directory boundary, resolved-path checks, bounded reads, and restricted URL fetching. |

I wrote standalone FastMCP replacements and integrated the controls into the course backend. The historical report records ten standalone tests and sixteen backend tests passing. This public repository includes the [standalone implementation and ten tests](../code/mcp-hardening/README.md). The sixteen backend tests are a historical report result, not a current rerun of the full course application.

The public test suite creates temporary synthetic data so it can run without sharing the course databases. Its valid Git operation is mocked. It exercises tool registration and calls as well as the helper functions.

These controls address the demonstrated cases. Deployment still needs caller authorization, least privilege, filesystem isolation, dependency maintenance, and resource limits. The sample is not a production security guarantee.

**Skills demonstrated:** browser-policy debugging, evidence-based failure analysis, secure Python implementation, and regression testing.
