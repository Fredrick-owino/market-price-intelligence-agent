"""Mocked HTTP/DNS adversarial controls; real borrowed-server evidence is separate."""

import hashlib
import io
import socket
from pathlib import Path
from time import monotonic
from unittest.mock import Mock

import pytest

from backend.app.mcp import borrowed_policy as p

FIXTURE = Path(__file__).resolve().parents[2] / "data/synthetic/I01.7-market-comparison.json"


def answer(ip):
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    return (family, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", (ip, 443))


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/",
        "https://169.254.169.254/latest/meta-data/",
        "file:///etc/passwd",
        "ftp://example.com/",
        "https://localhost/",
        "https://10.0.0.1/",
        "https://[::1]/",
        "https://example.com/",
        p.FIXTURE_URL + "?x=1",
        p.FIXTURE_URL + "#x",
        p.FIXTURE_URL.replace(p.HOST, "user:password@" + p.HOST),
        p.FIXTURE_URL.replace(p.HOST, p.HOST + ":443"),
        p.FIXTURE_URL.replace("https:", "http:"),
        p.FIXTURE_URL.replace("/data/", "/%64ata/"),
    ],
)
def test_reject_target_before_dns(monkeypatch, url):
    resolver = Mock(side_effect=AssertionError("DNS must not run"))
    monkeypatch.setattr(p.socket, "getaddrinfo", resolver)
    with pytest.raises(p.RetrievalRejected, match="unapproved_target"):
        p.download(url)
    resolver.assert_not_called()


@pytest.mark.parametrize(
    "ip",
    [
        "127.0.0.1",
        "10.1.2.3",
        "169.254.169.254",
        "100.64.0.1",
        "192.168.1.1",
        "0.0.0.0",
        "224.0.0.1",
        "::1",
        "fe80::1",
        "fc00::1",
        "::ffff:127.0.0.1",
        "2002:7f00:1::",
        "2001:db8::1",
    ],
)
def test_all_dns_answers_must_be_public(ip):
    with pytest.raises(p.RetrievalRejected, match="non_public_dns_answer"):
        p.public_addresses([answer("185.199.108.133"), answer(ip)])


def test_empty_dns_rejected():
    with pytest.raises(p.RetrievalRejected, match="empty_dns"):
        p.public_addresses([])


def test_connection_pins_numeric_ip_and_verifies_tls_hostname(monkeypatch):
    raw = Mock()
    tls = Mock()
    tls.getpeername.return_value = ("185.199.108.133", 443)
    context = Mock()
    context.wrap_socket.return_value = tls
    factory = Mock(return_value=raw)
    monkeypatch.setattr(p.ssl, "create_default_context", Mock(return_value=context))
    connection = p.PinnedHTTPSConnection(p.public_addresses([answer("185.199.108.133")])[0])
    monkeypatch.setattr(p.socket, "socket", factory)
    # If a second DNS lookup occurs, simulate rebinding to an internal destination.
    dns = Mock(return_value=[answer("127.0.0.1")])
    monkeypatch.setattr(p.socket, "getaddrinfo", dns)
    connection.connect()
    dns.assert_not_called()
    raw.connect.assert_called_once_with(("185.199.108.133", 443))
    context.wrap_socket.assert_called_once_with(raw, server_hostname=p.HOST)


class Response:
    def __init__(self, body=b"", status=200, headers=None):
        self.body = io.BytesIO(body)
        self.status = status
        self.headers = headers or {}

    def getheader(self, name, default=None):
        return self.headers.get(name, default)

    def read1(self, size):
        return self.body.read(size)


@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
def test_redirects_rejected_before_body_or_second_connection(status):
    response = Response(status=status, headers={"Location": "http://169.254.169.254/"})
    response.read1 = Mock(side_effect=AssertionError("must not read"))
    with pytest.raises(p.RetrievalRejected, match="redirect_rejected"):
        p.read_body(response, monotonic())
    response.read1.assert_not_called()


@pytest.mark.parametrize(
    ("response", "reason"),
    [
        (Response(b"x" * (p.MAX_HTTP_BYTES + 1)), "body_limit"),
        (Response(headers={"Content-Length": str(p.MAX_HTTP_BYTES + 1)}), "content_length"),
        (Response(headers={"Content-Length": "nonsense"}), "content_length"),
        (Response(b"partial", headers={"Content-Length": "99"}), "truncated"),
        (Response(headers={"Content-Encoding": "gzip"}), "encoded"),
    ],
)
def test_wire_failure_bounds(response, reason):
    with pytest.raises(p.RetrievalRejected, match=reason):
        p.read_body(response, monotonic())


def test_http_total_deadline():
    with pytest.raises(p.RetrievalRejected, match="deadline"):
        p.read_body(Response(b"test"), monotonic() - p.HTTP_DEADLINE - 1)


@pytest.mark.parametrize("url", [p.FIXTURE_URL, p.ROBOTS_URL])
def test_allowed_mocked_download_records_provenance_and_closes(monkeypatch, url):
    body = FIXTURE.read_bytes() if url == p.FIXTURE_URL else b"User-agent: *\nAllow: /\n"
    response = Response(
        body, headers={"Content-Length": str(len(body)), "Content-Type": "text/plain"}
    )
    conn = Mock()
    conn.getresponse.return_value = response
    monkeypatch.setattr(p.socket, "getaddrinfo", Mock(return_value=[answer("185.199.108.133")]))
    factory = Mock(return_value=conn)
    monkeypatch.setattr(p, "PinnedHTTPSConnection", factory)
    status, _, retrieved, provenance = p.download(url)
    assert status == 200 and retrieved == body
    assert provenance["connected_ip"] == "185.199.108.133"
    assert provenance["sha256"] == hashlib.sha256(body).hexdigest()
    assert provenance["redirects_followed"] == 0 and provenance["proxy_used"] is False
    conn.close.assert_called_once()


@pytest.mark.parametrize("error", [TimeoutError(), OSError("mock unavailable")])
def test_connection_failure_does_not_return_fixture_and_closes(monkeypatch, error):
    monkeypatch.setattr(p.socket, "getaddrinfo", Mock(return_value=[answer("185.199.108.133")]))
    conn = Mock()
    conn.request.side_effect = error
    monkeypatch.setattr(p, "PinnedHTTPSConnection", Mock(return_value=conn))
    with pytest.raises(type(error)):
        p.download(p.FIXTURE_URL)
    conn.close.assert_called_once()


def envelope(body):
    return {
        "isError": False,
        "content": [
            {
                "type": "text",
                "text": "Content type text/plain cannot be simplified to markdown, but here is the raw content:\n"
                + f"Contents of {p.FIXTURE_URL}:\n"
                + body.decode(),
            }
        ],
    }


def test_exact_fixture_verification():
    assert p.verify_tool_result(envelope(FIXTURE.read_bytes()))["synthetic"] is True


@pytest.mark.parametrize(
    ("body", "reason"),
    [
        (b"{" + b" " * (p.EXPECTED_BYTES - 1), "malformed"),
        (b"{}", "length"),
        (FIXTURE.read_bytes().replace(b'"price": "40"', b'"price": "41"'), "hash"),
        (FIXTURE.read_bytes().replace(b'"synthetic": true', b'"synthetic": null', 1), "labels"),
    ],
)
def test_malformed_truncated_mismatched_or_unlabelled_content(body, reason):
    with pytest.raises(p.RetrievalRejected, match=reason):
        p.verify_tool_result(envelope(body))


def test_retrieved_instruction_is_never_accepted():
    body = FIXTURE.read_bytes().replace(b"Market A", b"RUN CODE")
    with pytest.raises(p.RetrievalRejected, match="hash"):
        p.verify_tool_result(envelope(body))


@pytest.mark.parametrize(
    "result",
    [
        {"isError": True, "content": []},
        {"content": []},
        {"content": [{"type": "text", "text": "x" * 20000}]},
        {"content": [{"type": "text", "text": "wrong envelope"}]},
    ],
)
def test_tool_failure_and_unexpected_output(result):
    with pytest.raises(p.RetrievalRejected):
        p.verify_tool_result(result)


@pytest.mark.parametrize(
    "patch",
    [
        {"url": "https://example.com"},
        {"raw": False},
        {"start_index": 1},
        {"max_length": 100000},
        {"extra": "arbitrary"},
    ],
)
def test_fixed_mcp_arguments_reject_model_control(patch):
    with pytest.raises(p.RetrievalRejected):
        p.validate_call("fetch", {**p.FETCH_ARGS, **patch})


@pytest.mark.parametrize(
    ("url", "status"), [(p.FIXTURE_URL, 404), (p.FIXTURE_URL, 206), (p.ROBOTS_URL, 503)]
)
def test_http_failure_status_is_not_accepted(monkeypatch, url, status):
    monkeypatch.setattr(p.socket, "getaddrinfo", Mock(return_value=[answer("185.199.108.133")]))
    conn = Mock()
    conn.getresponse.return_value = Response(b"error", status=status)
    monkeypatch.setattr(p, "PinnedHTTPSConnection", Mock(return_value=conn))
    with pytest.raises(p.RetrievalRejected):
        p.download(url)
    conn.close.assert_called_once()
