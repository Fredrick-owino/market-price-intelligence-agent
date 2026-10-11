"""Fixed public synthetic target. Retrieved content is data, never agent instructions."""

import hashlib
import http.client
import ipaddress
import json
import socket
import ssl
from time import monotonic
from urllib.parse import urlsplit

HOST = "raw.githubusercontent.com"
FIXTURE_COMMIT = "4f86aeafef2cb1b8d84ba7ed3a6aff6d218998fc"
FIXTURE_URL = (
    f"https://{HOST}/Fredrick-owino/sokosignal-demo-fixtures/{FIXTURE_COMMIT}"
    "/data/synthetic/I01.7-market-comparison.json"
)
ROBOTS_URL = f"https://{HOST}/robots.txt"
EXPECTED_SHA256 = "01d764fe7226c8dd9d8cde68a70ccc5658b83876cbc6bed4c79078941396f9ef"
EXPECTED_BYTES = 9196
MAX_HTTP_BYTES = 32768
HTTP_TIMEOUT = 10
HTTP_DEADLINE = 15
FETCH_ARGS = {"url": FIXTURE_URL, "raw": True, "max_length": 12000, "start_index": 0}


class RetrievalRejected(ValueError):
    """A fixed, non-sensitive reason safe to retain in evidence."""


def validate_call(name, arguments):
    if name != "fetch" or arguments != FETCH_ARGS:
        raise RetrievalRejected("fixed_fetch_arguments_required")


def validate_url(url):
    # Exact bytes deliberately reject aliases, userinfo, ports, query, fragments and encodings.
    if url not in (FIXTURE_URL, ROBOTS_URL):
        raise RetrievalRejected("unapproved_target")


def public_addresses(answers):
    addresses = []
    for family, kind, protocol, _, address in answers:
        ip = ipaddress.ip_address(address[0])
        if (
            family not in (socket.AF_INET, socket.AF_INET6)
            or kind != socket.SOCK_STREAM
            or not ip.is_global
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
            or getattr(ip, "ipv4_mapped", None) is not None
            or getattr(ip, "sixtofour", None) is not None
            or getattr(ip, "teredo", None) is not None
        ):
            raise RetrievalRejected("non_public_dns_answer")
        addresses.append((family, protocol, address))
    if not addresses:
        raise RetrievalRejected("empty_dns_answer")
    return addresses


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Connect to the already-validated numeric address; TLS authenticates HOST."""

    def __init__(self, destination):
        super().__init__(HOST, 443, timeout=HTTP_TIMEOUT, context=ssl.create_default_context())
        self.destination = destination

    def connect(self):
        family, protocol, address = self.destination
        raw = socket.socket(family, socket.SOCK_STREAM, protocol)
        try:
            raw.settimeout(HTTP_TIMEOUT)
            # socket.connect consumes the numeric sockaddr, with no hostname re-resolution.
            raw.connect(address)
            self.sock = self._context.wrap_socket(raw, server_hostname=HOST)
            if ipaddress.ip_address(self.sock.getpeername()[0]) != ipaddress.ip_address(address[0]):
                raise RetrievalRejected("peer_address_mismatch")
        except BaseException:
            raw.close()
            if self.sock is not None:
                self.sock.close()
            raise


def read_body(response, started):
    if 300 <= response.status < 400:
        raise RetrievalRejected("redirect_rejected")
    if response.getheader("Content-Encoding", "identity").lower() != "identity":
        raise RetrievalRejected("encoded_body_rejected")
    length = response.getheader("Content-Length")
    if length is not None and (not length.isdigit() or int(length) > MAX_HTTP_BYTES):
        raise RetrievalRejected("invalid_or_excessive_content_length")
    body = bytearray()
    while True:
        if monotonic() - started > HTTP_DEADLINE:
            raise RetrievalRejected("http_deadline_exceeded")
        chunk = response.read1(min(4096, MAX_HTTP_BYTES + 1 - len(body)))
        if not chunk:
            break
        body.extend(chunk)
        if len(body) > MAX_HTTP_BYTES:
            raise RetrievalRejected("body_limit_exceeded")
    if length is not None and len(body) != int(length):
        raise RetrievalRejected("truncated_http_body")
    return bytes(body)


def download(url):
    """One GET, one DNS resolution, one pinned connection, no retries/proxies/redirects."""
    validate_url(url)
    started = monotonic()
    answers = public_addresses(socket.getaddrinfo(HOST, 443, type=socket.SOCK_STREAM))
    connection = PinnedHTTPSConnection(answers[0])
    try:
        connection.request(
            "GET",
            urlsplit(url).path,
            headers={
                "Host": HOST,
                "Accept-Encoding": "identity",
                "User-Agent": "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)",
            },
        )
        response = connection.getresponse()
        body = read_body(response, started)
        if url == FIXTURE_URL and response.status != 200:
            raise RetrievalRejected("fixture_http_status_rejected")
        if url == ROBOTS_URL and response.status >= 500:
            raise RetrievalRejected("robots_server_failure")
        # JSON fixture has no non-ASCII bytes; lossless UTF-8 is required at both boundaries.
        body.decode("utf-8", errors="strict")
        return (
            response.status,
            {"content-type": response.getheader("Content-Type", "")},
            body,
            {
                "url": url,
                "resolved_ips": [a[2][0] for a in answers],
                "connected_ip": answers[0][2][0],
                "tls_hostname": HOST,
                "http_status": response.status,
                "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
                "elapsed_seconds": round(monotonic() - started, 6),
                "redirects_followed": 0,
                "proxy_used": False,
            },
        )
    finally:
        connection.close()


def verify_fixture(body):
    if len(body) != EXPECTED_BYTES:
        raise RetrievalRejected("fixture_length_mismatch")
    try:
        value = json.loads(body)
    except (ValueError, UnicodeError) as error:
        raise RetrievalRejected("malformed_fixture") from error
    if not isinstance(value, dict) or (
        value.get("synthetic") is not True
        or value.get("data_status") != "synthetic"
        or not str(value.get("label", "")).startswith("SYNTHETIC ONLY")
        or not isinstance(value.get("quotes"), list)
        or len(value["quotes"]) != 8
        or any(
            not isinstance(q, dict) or q.get("synthetic") is not True
            for q in value.get("quotes", [])
        )
    ):
        raise RetrievalRejected("synthetic_labels_missing")
    if hashlib.sha256(body).hexdigest() != EXPECTED_SHA256:
        raise RetrievalRejected("fixture_hash_mismatch")
    return value


def verify_tool_result(result):
    if result.get("isError"):
        raise RetrievalRejected("borrowed_tool_failed")
    blocks = result.get("content", [])
    if len(blocks) != 1 or blocks[0].get("type") != "text":
        raise RetrievalRejected("unexpected_tool_content")
    text = blocks[0].get("text", "")
    if len(text.encode()) > 16384:
        raise RetrievalRejected("tool_output_limit_exceeded")
    marker = f"Contents of {FIXTURE_URL}:\n"
    # Official raw=True server always adds a type prefix before this marker.
    prefix, found, payload = text.partition(marker)
    if (
        not found
        or not prefix.startswith("Content type ")
        or not prefix.endswith(" cannot be simplified to markdown, but here is the raw content:\n")
    ):
        raise RetrievalRejected("unexpected_tool_envelope")
    return verify_fixture(payload.encode("utf-8"))
