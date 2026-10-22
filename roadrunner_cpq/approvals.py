import json
from decimal import Decimal
from pathlib import Path

DEFAULT_POLICY = Path(__file__).resolve().parent.parent / "data" / "approval_policy.json"


def load_policy(path=DEFAULT_POLICY):
    raw = json.loads(Path(path).read_text())
    return [(Decimal(t["up_to"]), t["approver"]) for t in raw["tiers"]]


def effective_discount_pct(priced_lines):
    if not priced_lines:
        return Decimal("0")
    avg = sum(pl.discount_pct for pl in priced_lines) / len(priced_lines)
    return avg.quantize(Decimal("0.01"))


def required_approvers(effective_pct, policy):
    """Cumulative chain: every approver whose tier lies below the discount."""
    chain = []
    lower = Decimal("-1")
    for up_to, approver in policy:
        if effective_pct >= lower and approver:
            chain.append(approver)
        lower = up_to
    return tuple(chain)
