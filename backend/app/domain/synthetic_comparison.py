"""Bounded deterministic comparison for I01.7; never a live quote service."""

import hashlib
import json
import os
import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, localcontext
from pathlib import Path

FIXTURE_PATH = Path(__file__).resolve().parents[3] / "data/synthetic/I01.7-market-comparison.json"
RESOURCE_URI = "synthetic://sokosignal/I01.7"
POLICY = "I01.7-synthetic-v1"


class ComparisonError(ValueError):
    def __init__(self, code: str, field: str, message: str):
        self.detail = {"code": code, "field": field, "message": message}
        super().__init__(message)


def reject(code: str, field: str, message: str):
    raise ComparisonError(code, field, message)


def decimal_string(value: str, field: str) -> Decimal:
    # Bound digits/scale before Decimal arithmetic; reject floats, exponents and non-finite values.
    if not isinstance(value, str) or not re.fullmatch(r"-?[0-9]{1,9}(\.[0-9]{1,6})?", value):
        reject(
            "invalid_decimal",
            field,
            "Use a finite decimal string, at most 9 integer and 6 fractional digits.",
        )
    return Decimal(value)


def load_fixture() -> tuple[dict, str]:
    fixture, digest, _ = load_snapshot()
    return fixture, digest


def load_snapshot() -> tuple[dict, str, dict | None]:
    if "SOKOSIGNAL_RETRIEVED_SNAPSHOT" in os.environ:
        from backend.app.domain.retrieved_snapshot import validate_snapshot

        # An absent, corrupt or unverified bundle fails; never fall back to local data.
        path = Path(os.environ["SOKOSIGNAL_RETRIEVED_SNAPSHOT"])
        return validate_snapshot(json.loads(path.read_text()))
    raw = FIXTURE_PATH.read_bytes()
    fixture = json.loads(raw)
    if fixture.get("synthetic") is not True or any(
        q.get("synthetic") is not True for q in fixture["quotes"]
    ):
        raise ValueError("I01.7 requires an explicitly synthetic fixture")
    return fixture, hashlib.sha256(raw).hexdigest(), None


def retrieve_quotes(filters: dict) -> dict:
    """Contract filters over the synthetic baseline; negative-test variants are excluded."""
    fixture, digest, provenance = load_snapshot()
    fields = ("commodity", "variant", "grade", "sale_basis")
    if set(filters) != {*fields, "market_ids", "as_of_date"}:
        reject("invalid_filters", "filters", "Provide the complete contracted search filters.")
    try:
        if date.fromisoformat(filters["as_of_date"]).isoformat() != filters["as_of_date"]:
            raise ValueError
    except (ValueError, TypeError):
        reject("invalid_date", "as_of_date", "Use an ISO YYYY-MM-DD date.")
    matches, exclusions = [], []
    for quote in fixture["quotes"]:
        reason = None
        if quote["quote_id"] not in fixture["default_request"]["quote_ids"]:
            reason = "negative_test_variant_not_market_evidence"
        elif (
            any(quote[field] != filters[field] for field in fields)
            or quote["market_id"] not in filters["market_ids"]
            or quote["observation_date"] != filters["as_of_date"]
        ):
            reason = "filter_mismatch"
        if reason:
            exclusions.append({"quote_id": quote["quote_id"], "reason": reason})
        else:
            matches.append(quote)
    return {
        "synthetic": True,
        "data_status": "synthetic",
        "label": fixture["label"],
        "snapshot_id": fixture["snapshot_id"],
        "snapshot_sha256": digest,
        **({"retrieval_provenance": provenance} if provenance is not None else {}),
        "policy_version": POLICY,
        "filters": filters,
        "quotes": matches,
        "source_manifests": [fixture["source"]],
        "exclusions": exclusions,
        "missing_data": not bool(matches),
    }


def advisory_for(comparison: dict) -> dict:
    """Small structured language for a model summary; no unchecked prose claims."""
    return {
        "synthetic": True,
        "currency": comparison["currency"],
        "net_proceeds": {
            row["market"]: row["estimated_net_proceeds"] for row in comparison["markets"]
        },
        "winner": comparison["winner"],
        "advantage_kes": comparison["advantage_kes"],
        "quote_ids": comparison["accepted_quote_ids"],
        "source_references": sorted({row["source_reference"] for row in comparison["markets"]}),
        "assumptions": comparison["assumptions"],
        "review_status": "PENDING_REVIEW",
    }


def validate_advisory(advisory: dict, comparison: dict) -> None:
    if json.dumps(advisory, sort_keys=True) != json.dumps(advisory_for(comparison), sort_keys=True):
        raise ValueError(
            "Advisory must match verified numbers, winner, assumptions, provenance, synthetic label and PENDING_REVIEW exactly."
        )


def money(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f")


def compare(request: dict) -> dict:
    fixture, digest, provenance = load_snapshot()
    if request["snapshot_id"] != fixture["snapshot_id"]:
        reject(
            "unknown_snapshot", "snapshot_id", "Use the snapshot exposed by the synthetic resource."
        )
    if request["policy_version"] != POLICY:
        reject("unsupported_policy", "policy_version", "Use I01.7-synthetic-v1.")
    quantity = decimal_string(request["quantity"], "quantity")
    if quantity <= 0:
        reject("invalid_quantity", "quantity", "Quantity must be positive.")
    loss = decimal_string(request["loss_fraction"], "loss_fraction")
    if not Decimal(0) <= loss < Decimal(1):
        reject("invalid_loss", "loss_fraction", "Loss must be at least zero and less than one.")
    if request["unit"] != "kg":
        reject(
            "incompatible_unit",
            "unit",
            "Only confirmed kg quantities are supported; no sack conversion inferred.",
        )
    try:
        as_of = date.fromisoformat(request["as_of_date"])
    except ValueError:
        reject("invalid_date", "as_of_date", "Use an ISO YYYY-MM-DD date.")
    if as_of.isoformat() != request["as_of_date"]:
        reject("invalid_date", "as_of_date", "Use an ISO YYYY-MM-DD date.")
    ids = request["quote_ids"]
    if len(ids) != 2 or len(set(ids)) != 2:
        reject("invalid_quote_selection", "quote_ids", "Select two distinct fixture quotes.")
    index = {q["quote_id"]: q for q in fixture["quotes"]}
    if any(qid not in index for qid in ids):
        reject(
            "unknown_quote",
            "quote_ids",
            "Every quote ID must resolve in the selected synthetic snapshot.",
        )
    quotes = [index[qid] for qid in ids]
    if quotes[0]["market_id"] == quotes[1]["market_id"]:
        reject("invalid_quote_selection", "quote_ids", "Select two distinct markets.")
    for q in quotes:
        if q["original_unit"] != "kg" or q["unit_weight_kg"] != "1":
            reject(
                "incompatible_unit",
                "quote_ids",
                "Quote unit is not confirmed kg; no unknown sack conversion.",
            )
        if q["grade"] in (None, "", "unknown"):
            reject("unknown_grade", "quote_ids", "Unknown grade cannot be assumed comparable.")
        if q["observation_date"] != as_of.isoformat():
            reject(
                "incomparable_date",
                "as_of_date",
                "Experiment policy requires each observation on the exact as-of date.",
            )
        if not q["capacity_confirmed"] or quantity > decimal_string(
            q["capacity_kg"], "capacity_kg"
        ):
            reject(
                "unconfirmed_capacity",
                "quantity",
                "Requested input quantity exceeds confirmed synthetic capacity or capacity is unconfirmed.",
            )
    for field in ("commodity", "variant", "grade", "sale_basis", "currency", "observation_date"):
        if quotes[0][field] != quotes[1][field]:
            reject("incomparable_quotes", field, f"Quotes must have identical {field}.")
    if quotes[0]["currency"] != "KES":
        reject("unsupported_currency", "currency", "This experiment supports KES only.")
    with localcontext() as context:
        context.prec = 40
        sellable = quantity * (1 - loss)
        rows = []
        net_values = []
        for q in quotes:
            gross = decimal_string(q["price"], "price") * sellable
            costs = {
                key: q[key] for key in ("transport_total", "handling_total", "market_fees_total")
            }
            missing = [key for key, value in costs.items() if value is None]
            total_cost = None if missing else sum(decimal_string(v, k) for k, v in costs.items())
            net = None if total_cost is None else gross - total_cost
            net_values.append(net)
            rows.append(
                {
                    "quote_id": q["quote_id"],
                    "market_id": q["market_id"],
                    "market": q["market"],
                    "source_id": q["source_id"],
                    "source_reference": q["source_reference"],
                    "normalized_price_per_kg": q["price"],
                    "sellable_kg": format(sellable, "f"),
                    "gross_proceeds": money(gross),
                    "costs": costs,
                    "missing_costs": missing,
                    "total_cost": None if total_cost is None else money(total_cost),
                    "estimated_net_proceeds": None if net is None else money(net),
                }
            )
        winner = None
        advantage = None
        complete = all(value is not None for value in net_values)
        tie = None
        if complete:
            rounded = [Decimal(row["estimated_net_proceeds"]) for row in rows]
            tie = rounded[0] == rounded[1]
            if not tie:
                winner = rows[0 if rounded[0] > rounded[1] else 1]["market"]
            advantage = money(abs(rounded[0] - rounded[1]))
    return {
        "synthetic": True,
        "data_status": "synthetic",
        "label": fixture["label"],
        "snapshot_id": fixture["snapshot_id"],
        "snapshot_sha256": digest,
        **({"retrieval_provenance": provenance} if provenance is not None else {}),
        "policy_version": POLICY,
        "currency": "KES",
        "as_of_date": as_of.isoformat(),
        "loss_fraction": request["loss_fraction"],
        "accepted_quote_ids": ids,
        "excluded_quotes": [],
        "markets": rows,
        "ranking_basis": "estimated_net_proceeds" if complete else "gross_only_no_net_ranking",
        "winner": winner,
        "advantage_kes": advantage,
        "tie": tie,
        "assumptions": fixture["assumptions"],
        "limitations": [
            "Synthetic transport spike only; no model, delivery or officer approval implemented."
        ],
    }
