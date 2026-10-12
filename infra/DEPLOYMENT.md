# Deployment boundary and pending owner choices

## Concrete local configuration

`run-local-demo.sh` runs one Uvicorn worker on `127.0.0.1:8000` and serves the
built React assets from the same origin. It requires the two locked Python
environments, `frontend/dist`, the ignored local officer verifier file and a
separate loopback Ollama process with the pinned model. SQLite, logs, token and
model files stay local and ignored. `README.md` gives exact setup commands.

This is the implemented deployment configuration. It avoids a public API and
does not change host networking, Docker security or global packages. A remote
host cannot safely use this unchanged: the model URL is loopback, tokens are
static, workflow locks are process-local and the data/publication rights review
is incomplete.

## Decisions before any public host

| Decision | Needed owner input |
|---|---|
| Hosting/account | Approved provider or institution-owned host, account owner and administrator. |
| Cost | Monthly spending ceiling for CPU/GPU, storage and traffic; no cost or speedup is inferred from this laptop run. |
| Exposure | Whether the UI is private to named officers, behind an institutional VPN, or public; API should remain private until identity and network review. |
| Rights | Historical KAMIS redistribution rights remain unresolved despite the repository now being public. Confirm rights before any real-data ingestion or reuse. |
| Identity/operations | Named officer roster, token/session lifecycle, TLS, backups and a shared durable resume lock or outbox for more than one worker. |

Fredrick manually made the repository public on 12 October 2026; anonymous
access was verified separately. No hosting account was created and no public
application port was opened. Public source code does not make this loopback
application a public service or resolve historical data rights.
