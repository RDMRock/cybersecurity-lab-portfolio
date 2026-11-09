# DNS spoofing and a controlled phishing simulation

**Source:** Assignment 5, Tasks 1–21. **Status:** documented lab redirection and a one-recipient simulation.

I connected DNS behavior, browser state, form submission, and campaign telemetry. The tests used my lab browser, a controlled inbox, and dummy form values.

| Tasks | Work | Evidence |
| --- | --- | --- |
| 1–4 | Served a sample site and used Bettercap to spoof a lookalike domain in the lab. | DNS lookup and browser captures showed the mapping and the local page. I distinguished a spoofed-response send log from a response the client actually accepted. |
| 5–7 | Used the Social-Engineer Toolkit's site-cloning exercise. | The cloned form reached the lab listener and captured dummy fields. |
| 8–9 | Tested tabnabbing and analyzed social-engineering scenarios. | The browser tab changed to the substituted page. Dummy submission was confirmed separately. A missing file and favicon error required troubleshooting. |
| 10–14 | Investigated caching, existing connections, and DNS/transport defenses. | A fresh lookup sometimes returned the real address despite send logs. The final reset and browser test reached the lab clone. |
| 15–20 | Configured Gophish, mail delivery, an email template, landing page, controlled recipient, and campaign. | A test message arrived. I corrected an SMTP sender-format error and checked that the landing form captured the intended fields. |
| 21 | Ran the controlled campaign and reviewed the recipient record. | One sent, opened, clicked, and submitted event was recorded. The expanded record contained the two dummy fields, and the browser followed the configured redirect. |

## What I learned from the evidence

A packet being sent does not prove that the client used it. DNS cache state, existing connections, resolver behavior, and browser state all affected the path. The writeup keeps the observed lookup and browser results separate from possible explanations.

The Gophish result demonstrates configuration and end-to-end telemetry for one controlled recipient. It is not an employee-awareness study, a phishing success-rate estimate, or evidence of testing other people.

The report also explains the roles of authenticated DNS transport, DNSSEC validation, certificate checks, HSTS, and network controls. These are distinct defenses with different assumptions, not interchangeable labels.

**Skills demonstrated:** DNS troubleshooting, browser investigation, controlled simulation setup, SMTP troubleshooting, and interpreting event telemetry. Public artifacts omit recipient details, credentials, and temporary tunnel URLs.
