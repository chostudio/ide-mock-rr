from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class Sku:
    sku: str
    name: str
    unit: str
    list_price: Decimal
    tiers: tuple = ()  # ((min_qty, Decimal price), ...) in no guaranteed order
    one_time: bool = False
    deprecated: bool = False
    max_qty: int | None = None
    aliases: tuple = ()


@dataclass
class Line:
    sku: str
    qty: int
    discount_pct: Decimal = Decimal("0")  # percent, so 7.5 means 7.5%


@dataclass
class Quote:
    customer: str
    term_months: int = 12
    lines: list = field(default_factory=list)


@dataclass(frozen=True)
class PricedLine:
    sku: str
    qty: int
    unit_price: Decimal
    discount_pct: Decimal
    baseline_total: Decimal
    net_total: Decimal


@dataclass(frozen=True)
class PricedQuote:
    customer: str
    term_months: int
    lines: tuple
    baseline_total: Decimal
    net_total: Decimal
    effective_discount_pct: Decimal
    approvers: tuple


def make_quote(customer, term_months=12, lines=[]):
    """Convenience constructor used by the CLI and the tests."""
    return Quote(customer, term_months, lines)
