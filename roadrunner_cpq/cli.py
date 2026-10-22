import argparse
import sys
from decimal import Decimal

from .catalog import load_catalog
from .models import Line, make_quote
from .pricing import price_quote


def render(pq):
    out = [f"Quote for {pq.customer} ({pq.term_months} months)"]
    for l in pq.lines:
        out.append(
            f"  {l.sku:<10} x{l.qty:<5} @ {l.unit_price:>9}  "
            f"-{l.discount_pct}%  = {l.net_total:>12}"
        )
    out.append(f"  baseline {pq.baseline_total}  net {pq.net_total}")
    out.append(f"  effective discount {pq.effective_discount_pct}%")
    out.append("  approvers: " + (", ".join(pq.approvers) or "none"))
    return "\n".join(out)


def main(argv=None):
    p = argparse.ArgumentParser(prog="roadrunner_cpq")
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("quote", help="structured quote: SKU:QTY[:DISCOUNT_PCT] ...")
    q.add_argument("--customer", required=True)
    q.add_argument("--term", type=int, default=12)
    q.add_argument("lines", nargs="+")

    a = sub.add_parser("ask", help="natural-language quote request")
    a.add_argument("text")

    args = p.parse_args(argv)
    catalog = load_catalog()

    if args.cmd == "quote":
        quote = make_quote(args.customer, args.term)
        for spec in args.lines:
            parts = spec.split(":")
            disc = Decimal(parts[2]) if len(parts) > 2 else Decimal("0")
            quote.lines.append(Line(parts[0], int(parts[1]), disc))
        print(render(price_quote(catalog, quote)))
        return 0

    # TODO (Part 2): wire parse_deal_request in here
    print("ask: not implemented", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
