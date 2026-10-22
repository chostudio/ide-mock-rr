from decimal import Decimal as D

import pytest

from roadrunner_cpq.models import Line, make_quote
from roadrunner_cpq.pricing import (
    DeprecatedSku, QuantityError, price_quote, tier_price,
)


def priced(catalog, lines, term=12, customer="Acme"):
    q = make_quote(customer, term)
    q.lines.extend(lines)
    return price_quote(catalog, q)


def test_single_seat_no_discount(catalog):
    pq = priced(catalog, [Line("RR-PLAT", 1)])
    assert pq.net_total == D("1200.00")


def test_tier_price_boundaries(catalog):
    plat = catalog.get("RR-PLAT")
    assert tier_price(plat, 1) == D("1200.00")
    assert tier_price(plat, 49) == D("1200.00")
    assert tier_price(plat, 50) == D("1080.00")
    assert tier_price(plat, 200) == D("960.00")


def test_term_discount_compounds_with_line_discount(catalog):
    # 10 seats * 1200 * 2 years = 24000; -10% line, then -5% term
    pq = priced(catalog, [Line("RR-PLAT", 10, D("10"))], term=24)
    assert pq.net_total == D("20520.00")


def test_rounds_half_up_to_cents(catalog):
    # 500 * 2 = 1000; * 0.9975 = 997.5; * 0.95 = 947.625
    pq = priced(catalog, [Line("RR-AGENT", 1, D("0.25"))], term=24)
    assert pq.net_total == D("947.63")


def test_one_time_services_ignore_term(catalog):
    pq = priced(catalog, [Line("RR-IMPL", 1, D("10"))], term=36)
    assert pq.net_total == D("13500.00")


def test_sku_lookup_is_case_and_space_insensitive(catalog):
    pq = priced(catalog, [Line("  rr-plat ", 2)])
    assert pq.net_total == D("2400.00")


def test_deprecated_sku_rejected(catalog):
    with pytest.raises(DeprecatedSku):
        priced(catalog, [Line("RR-LEGACY", 5)])


def test_max_qty_enforced(catalog):
    with pytest.raises(QuantityError):
        priced(catalog, [Line("RR-SSO", 2)])


def test_nonpositive_qty_rejected(catalog):
    with pytest.raises(QuantityError):
        priced(catalog, [Line("RR-PLAT", 0)])


def test_make_quote_instances_do_not_share_lines():
    a = make_quote("A")
    a.lines.append(Line("RR-SSO", 1))
    b = make_quote("B")
    assert b.lines == []
