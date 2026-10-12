# ADR 0003 — local officer bearer review

Date: 12 October 2026. Owner: Fredrick Onyango. Review: solo; independent review pending.
Scope: I01.12 synthetic local demo only.

## Decision

The API accepts one high entropy bearer token per named officer. An ignored local
JSON file holds only SHA-256 token verifiers, officer IDs and explicit workflow ID
allowlists. The plaintext token stays in separate ignored local configuration.
The API derives identity and permission from that verifier; request bodies cannot
choose a reviewer or role. Constant-time digest comparison rejects unknown tokens.
There is no login, cookie, session endpoint, account registration or identity
platform. The contract's proposed session route is deferred by this explicit
local-only choice. A new process reloads the local config at startup.

Use one Uvicorn worker bound to `127.0.0.1`. Local file permissions and host access
are part of this demo boundary. A static token has no expiry, browser CSRF is not
applicable to the Authorization header, and the API has no public exposure or
production identity assurance. Public or multi-user deployment requires a new
authentication and network review, token rotation/expiry, rate limits, TLS and a
shared distributed resume lock or transactional outbox.

The existing simulated CLI identity remains explicitly simulated for regression
evidence. The new HTTP path uses a separate authenticated decision mode and audit
event; no model tool receives a token or officer authority.
