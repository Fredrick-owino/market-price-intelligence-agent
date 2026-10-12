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

## Concrete choice for a controlled demonstration (prepared, not enabled)

The existing Ubuntu machine can run the complete local demo: it has an
Intel i7-1165G7 (4 cores/8 threads), 14 GiB RAM, 292 GiB free disk, Intel Iris Xe
and no NVIDIA GPU. An actual 500 kg borrowed-Fetch/Qwen/API run reached review
in 147.214 seconds. That single run establishes feasibility on this machine,
not uptime, concurrent capacity or a latency guarantee. The machine must stay
powered, online and awake during a remote demonstration.

**Preferred bounded remote presentation:** after owner approval, put a
Cloudflare Tunnel from this machine to a dedicated hostname in an owner-controlled
Cloudflare domain. Apply a Cloudflare Access self-hosted application policy to
the *whole* hostname before enabling the route, allowing only named demo
participants. Keep Uvicorn and Ollama on `127.0.0.1`, one API worker, local
SQLite and ignored local credentials. Issue a separate, scoped demonstration
officer credential in ignored local configuration; do not reuse the automated
`test:local-demo-officer` credential remotely. The reviewer still needs the
app's officer credential and workflow permission. Cloudflare provides browser HTTPS;
`cloudflared` makes an outbound connection, so neither Ollama nor the database
needs an inbound port. A tunnel route without Access would expose the local app
to anyone with the hostname and is not acceptable here. Cloudflare documents
the [tunnel prerequisites](https://developers.cloudflare.com/tunnel/get-started/),
[published-route exposure](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/routing-to-tunnel/)
and [Access application policy](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/choose-application-type/).
Its [Zero Trust free plan](https://www.cloudflare.com/plans/zero-trust-services/)
currently lists $0 for up to 50 users, but a suitable domain and its renewal
cost are separate. No Cloudflare account, domain, route or Access policy has
been created or tested here.

**Hosted alternative:** one Runpod Secure Cloud GPU Pod with the unchanged
4-bit Qwen model, both locked Python environments, built frontend, one Uvicorn
worker, loopback Ollama and persistent private SQLite storage. Use the same
Access-protected HTTPS tunnel to reach only the app. The current
[Runpod price page](https://www.runpod.io/pricing) lists an RTX A5000
(24 GB VRAM, 25 GB RAM) at $0.27/hour and container disk at $0.10/GB/month;
48 hours of GPU uptime alone would be $12.96 before storage, tax or any other
charges. This is a listed rate, not a tested quote, availability guarantee or
performance measurement. Provisioning would require a Runpod account, payment
method, spending cap, region/availability choice, persistent volume sizing,
model download/digest verification, backup/restore and a fresh end-to-end test.
Do not use a public Pod HTTP endpoint for the reviewer API.

For either option the owner must choose: account and domain administrator;
exact demo audience and allowed identities; whether a browser-reachable
Access-protected hostname is authorized; time window; and a maximum spend
(including domain/hosting). Before exposure, test Access denial while signed
out, reviewer permission boundaries, service restart recovery, and the final
HTTPS origin. A public repository alone authorizes none of these actions.
