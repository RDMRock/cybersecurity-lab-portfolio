# Web patch excerpts

These are the four focused patches documented as installed and retested in Assignment 7. They adapt supplied course handlers and are excerpts, not standalone applications.

| File | Change | Historical check |
| --- | --- | --- |
| [SQL lookup](task08-vulnerable-endpoint.js) | Bound the input to a SQL placeholder. | Normal lookup returned a user, injected input returned none. |
| [User data](task10-user-data-route.js) | Selected the identity from the authenticated token mapping. | A cross-user query returned only the token owner's record. |
| [Template](task12-ssti-route.py) | Used a fixed Jinja template with a data variable. | Former expression rendered literally. |
| [Deserialization](task14-deserialize-route.py) | Parsed JSON instead of pickle. | Normal JSON worked and former pickle input was rejected. |

The JavaScript routes require the course Express application, database promise, authorization middleware, and token mapping. The Python routes require a Flask app and its request/template imports.

The original scope is preserved. The user-data response still uses `resdb.user` where the database column is `username`, and the sample token design is not a production authentication scheme. The deserialization response still interpolates parsed data into HTML, catches broad exceptions, and exposes errors. It needs output encoding, size limits, and clearer response handling before broader reuse. These caveats do not erase the observed fixes, but they bound what each fix demonstrates.

Current portfolio checks are syntax checks. Full Docker retests are historical results from the report. See [the case study](../../case-studies/07-web-vulnerabilities-and-remediation.md).
