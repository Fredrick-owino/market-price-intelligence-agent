# Borrowed Fetch pin

Distribution: mcp-server-fetch 2026.8.18, separately locked with uv.
Official repository: https://github.com/modelcontextprotocol/servers/tree/main/src/fetch
Reviewed server source commit: 956d36f8a148908b2e2394669ef5ae1f1230c9e9.
server.py SHA-256: f66dc973126c9251934fdb5355fa960529546660cad74147a6b31f725a79b358.
Wheel SHA-256: 6642df733a1032e7f37d0f13849af8a944d46c02420d2c070cc14e0948f8fcc2.

UPSTREAM-LICENSE is the exact MIT notice from that wheel (Anthropic, PBC, 2024).
The inspected source project version (0.6.3) and current root licence differ
from the wheel metadata; no whole-release source-to-wheel equivalence is claimed.
Only server.py was compared byte-for-byte. See the I01.10 run reports.

The official server uses MCP >=1.29.0,<2 and cannot share SokoSignal's MCP 2.3.0
environment. Its upstream implementation follows redirects, reads content before
slicing, and does not constrain DNS destinations. SokoSignal's version-checked
launcher wraps its MCP tool handler and both HTTP paths. It is an adapted upstream
server, not an assertion that stock Fetch enforces these controls.

From the project root, reproduce the separate environment:

```sh
uv sync --project infra/borrowed-fetch --locked --python python3.12 --no-python-downloads
```

Never add this server's SDK requirements to the application environment. The
client runs with the unchanged application environment and starts this isolated
server over stdio. The launcher is backend.app.mcp.borrowed_server; the experiment
client is backend.app.mcp.borrowed_client. No URL or model configuration is accepted.
