"""Host-created verified retrieval bundle, never accepted from model tool arguments.

This validates integrity and provenance consistency, not a cryptographic attestation
against a local actor able to replace the process, checkpoint or bundle file.
"""

import ipaddress
from datetime import datetime

from backend.app.mcp.borrowed_policy import (
    EXPECTED_BYTES,
    EXPECTED_SHA256,
    FIXTURE_COMMIT,
    FIXTURE_URL,
    HOST,
    ROBOTS_URL,
    RetrievalRejected,
    verify_fixture,
)

UPSTREAM_SOURCE_SHA = "f66dc973126c9251934fdb5355fa960529546660cad74147a6b31f725a79b358"


def validate_snapshot(snapshot):
    try:
        if set(snapshot) != {"body", "provenance"}:
            raise ValueError
        fixture = verify_fixture(snapshot["body"].encode("utf-8"))
        p = snapshot["provenance"]
        required = {
            "url": FIXTURE_URL,
            "commit": FIXTURE_COMMIT,
            "sha256": EXPECTED_SHA256,
            "bytes": EXPECTED_BYTES,
            "synthetic": True,
            "transport": "stdio",
            "distribution": "mcp-server-fetch",
            "distribution_version": "2026.8.18",
            "sdk_version": "1.30.0",
            "upstream_source_sha256": UPSTREAM_SOURCE_SHA,
        }
        if any(p.get(k) != v for k, v in required.items()):
            raise ValueError
        if p["evidence_mode"] not in {"actual_public_http_real_mcp", "mocked_http_real_mcp"}:
            raise ValueError
        if not p["run_id"] or datetime.fromisoformat(p["retrieved_at"]).tzinfo is None:
            raise ValueError
        robots, content = p["http"]
        if robots["url"] != ROBOTS_URL or content["url"] != FIXTURE_URL:
            raise ValueError
        if (
            content["http_status"] != 200
            or content["sha256"] != EXPECTED_SHA256
            or content["bytes"] != EXPECTED_BYTES
        ):
            raise ValueError
        if content["timestamp"] != p["retrieved_at"]:
            raise ValueError
        if (
            robots["http_status"] in (401, 403)
            or not 200 <= robots["http_status"] < 500
            or 300 <= robots["http_status"] < 400
        ):
            raise ValueError
        for request in p["http"]:
            if (
                request["proxy_used"] is not False
                or request["redirects_followed"] != 0
                or request["tls_hostname"] != HOST
            ):
                raise ValueError
            if (
                not request["resolved_ips"]
                or request["connected_ip"] not in request["resolved_ips"]
            ):
                raise ValueError
            for address in request["resolved_ips"]:
                ip = ipaddress.ip_address(address)
                if (
                    not ip.is_global
                    or ip.is_multicast
                    or ip.is_reserved
                    or getattr(ip, "ipv4_mapped", None)
                    or getattr(ip, "sixtofour", None)
                    or getattr(ip, "teredo", None)
                ):
                    raise ValueError
        return fixture, EXPECTED_SHA256, p
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise RetrievalRejected("invalid_retrieved_snapshot") from error
