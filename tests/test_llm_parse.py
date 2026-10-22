import json

from roadrunner_cpq.llm import parse_deal_request
from tests.fakes import FakeClient


def test_parses_a_simple_request(catalog):
    reply = json.dumps({
        "customer": "Acme",
        "term_months": 24,
        "lines": [{"sku": "RR-PLAT", "qty": 60, "discount_pct": 10}],
    })
    quote = parse_deal_request(
        "60 platform seats for Acme, two years, 10% off", catalog,
        client=FakeClient(reply),
    )
    assert quote.customer == "Acme"
    assert quote.term_months == 24
    assert [(l.sku, l.qty) for l in quote.lines] == [("RR-PLAT", 60)]
