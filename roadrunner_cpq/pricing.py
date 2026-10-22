from decimal import Decimal, ROUND_HALF_UP

from .approvals import effective_discount_pct, load_policy, required_approvers
from .models import PricedLine, PricedQuote

# percent off the whole recurring line, by contract length
TERM_DISCOUNT = {12: Decimal("0"), 24: Decimal("5"), 36: Decimal("10")}


class DeprecatedSku(ValueError):
    pass


class QuantityError(ValueError):
    pass


def tier_price(sku, qty):
    price = sku.list_price
    for min_qty, tier in sorted(sku.tiers):
        if qty > min_qty:
            price = tier
    return price


def price_line(sku, line, term_months):
    unit = tier_price(sku, line.qty)
    factor = 1 if sku.one_time else term_months / 12
    line_d = float(line.discount_pct)
    term_d = 0 if sku.one_time else float(TERM_DISCOUNT[term_months])

    gross = float(unit) * line.qty * factor
    net = gross * (1 - (line_d + term_d) / 100)

    return PricedLine(
        sku=sku.sku,
        qty=line.qty,
        unit_price=unit,
        discount_pct=line.discount_pct,
        baseline_total=Decimal(str(round(gross, 2))),
        net_total=Decimal(str(round(net, 2))),
    )


def price_quote(catalog, quote, policy=None):
    if quote.term_months not in TERM_DISCOUNT:
        raise ValueError(f"unsupported term: {quote.term_months}")
    if not quote.lines:
        raise ValueError("quote has no lines")
    policy = policy or load_policy()

    priced = []
    for line in quote.lines:
        sku = catalog.get(line.sku)
        if line.qty <= 0:
            raise QuantityError(f"{line.sku}: qty must be positive")
        priced.append(price_line(sku, line, quote.term_months))

    baseline = sum(p.baseline_total for p in priced)
    net = sum(p.net_total for p in priced)
    eff = effective_discount_pct(priced)
    return PricedQuote(
        customer=quote.customer,
        term_months=quote.term_months,
        lines=tuple(priced),
        baseline_total=baseline,
        net_total=net,
        effective_discount_pct=eff,
        approvers=required_approvers(eff, policy),
    )
