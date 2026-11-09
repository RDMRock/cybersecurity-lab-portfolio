# Network interception, TLS, and RAG poisoning

**Source:** Assignment 4, Tasks 1–16. **Status:** documented lab-browser and packet observations.

I used my designated Windows browser and Kali VM to compare what an on-path observer could see under different transport and trust conditions.

| Tasks | Work | Result |
| --- | --- | --- |
| 1–3 | Recorded the baseline ARP table, enabled target-scoped spoofing, and checked it again. | The gateway entry changed to Kali's MAC address. |
| 4–5 | Submitted a controlled form over HTTP and HTTPS and inspected Wireshark captures. | HTTP exposed the form data. The HTTPS HTTP-POST filter remained empty, while port 443 traffic showed protected payloads, including QUIC. |
| 6–9 | Tested an HTTP-to-HTTPS downgrade scenario. | The packaged SSLStrip failed with a Python string/bytes error. A separate Python 3 implementation relayed the controlled test and rewrote a redirect so the browser landed on HTTP. |
| 10–14 | Configured transparent mitmproxy and installed its CA in the lab browser. | The proxy displayed readable HTTPS request paths and responses. The browser certificate viewer showed the lab proxy as issuer. |
| 15–16 | Uploaded a poisoned document to the course RAG application and asked a related question. | The application returned the document's rates, injected instructions, and six demo user records with passwords. |

## What the TLS experiment establishes

The transparent proxy result depended on the lab browser trusting the proxy CA. It does not show that arbitrary HTTPS traffic can be decrypted without changing trust. Similarly, the downgrade test began with HTTP and a controlled redirect. It does not establish a general bypass of HSTS or modern browser protections.

I kept the initial SSLStrip failure because it explains why a different implementation was used and avoids claiming that the first command worked.

## What the RAG experiment establishes

The uploaded bulletin combined ordinary mortgage information with an instruction hidden in an HTML comment. The course interface reported poisoning and success scores, but the returned demo records were the concrete disclosure evidence. The analyzer's low threat score disagreed with that observed output.

The result is specific to the teaching application's retrieval and response behavior. It is not a finding against a production bank or proof that all retrieval-augmented systems behave the same way.

**Skills demonstrated:** packet analysis, protocol comparison, certificate inspection, tool troubleshooting, and evaluating untrusted retrieved content.
