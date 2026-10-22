from decimal import Decimal as D

from roadrunner_cpq.models import Line, make_quote
from roadrunner_cpq.pricing import price_quote


def approvers(catalog, lines, term=12):
    q = make_quote("Acme", term)
    q.lines.extend(lines)
    return price_quote(catalog, q).approvers


def test_no_discount_needs_nobody(catalog):
    assert approvers(catalog, [Line("RR-PLAT", 10)]) == ()


def test_exactly_ten_percent_needs_nobody(catalog):
    assert approvers(catalog, [Line("RR-PLAT", 10, D("10"))]) == ()


def test_just_over_ten_needs_manager(catalog):
    assert approvers(catalog, [Line("RR-PLAT", 10, D("10.5"))]) == ("sales_manager",)


def test_exactly_twenty_stops_at_manager(catalog):
    assert approvers(catalog, [Line("RR-PLAT", 10, D("20"))]) == ("sales_manager",)


def test_twenty_five_needs_manager_and_vp(catalog):
    assert approvers(catalog, [Line("RR-PLAT", 10, D("25"))]) == (
        "sales_manager", "vp_sales",
    )


def test_over_thirty_needs_cfo(catalog):
    assert approvers(catalog, [Line("RR-AGENT", 10, D("30.01"))]) == (
        "sales_manager", "vp_sales", "cfo",
    )


def test_discount_is_weighted_by_dollars_not_averaged(catalog):
    # 12000 undiscounted + 15000 at 20% off => 3000 / 27000 = 11.11%
    lines = [Line("RR-PLAT", 10), Line("RR-IMPL", 1, D("20"))]
    assert approvers(catalog, lines) == ("sales_manager",)


def test_term_discount_counts_toward_total(catalog):
    # 24 month term alone is 5%; with 6% line discount it is 10.70%
    assert approvers(catalog, [Line("RR-PLAT", 10)], term=24) == ()
    assert approvers(catalog, [Line("RR-PLAT", 10, D("6"))], term=24) == (
        "sales_manager",
    )
