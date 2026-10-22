import json
from decimal import Decimal
from pathlib import Path

from .models import Sku

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "catalog.json"


class UnknownSku(ValueError):
    pass


class Catalog:
    def __init__(self, skus):
        self._by_code = {s.sku: s for s in skus}

    def get(self, code):
        try:
            return self._by_code[code]
        except KeyError:
            raise UnknownSku(code)

    def find_by_alias(self, alias):
        needle = alias.lower()
        return [
            s for s in self._by_code.values()
            if needle in [a.lower() for a in s.aliases]
        ]

    def all(self):
        return list(self._by_code.values())


def load_catalog(path=DEFAULT_PATH):
    raw = json.loads(Path(path).read_text())
    skus = []
    for r in raw["skus"]:
        skus.append(Sku(
            sku=r["sku"],
            name=r["name"],
            unit=r["unit"],
            list_price=Decimal(r["list_price"]),
            tiers=tuple((int(q), Decimal(p)) for q, p in r.get("tiers", [])),
            one_time=r.get("one_time", False),
            deprecated=r.get("deprecated", False),
            max_qty=r.get("max_qty"),
            aliases=tuple(r.get("aliases", [])),
        ))
    return Catalog(skus)
