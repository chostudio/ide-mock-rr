# roadrunner_cpq

A small quote engine for an enterprise sales team: price a deal, work out who
has to approve the discount, and (Part 2) accept deal requests written in plain
English using the OpenAI API.

You have 60 minutes and any AI tooling you like. You will be asked to explain
your changes, so read what the AI writes before you accept it.

```
pip install -r requirements.txt
python -m pytest
python -m roadrunner_cpq quote --customer Acme --term 24 RR-PLAT:60:10 RR-SSO:1
```

Set `OPENAI_API_KEY` to try the real model. The tests never need it: they use
`tests/fakes.py`.

## Business rules

**Catalog** (`data/catalog.json`). Prices are USD, stored as strings. SKU codes
are case-insensitive and surrounding whitespace is ignored. Deprecated SKUs
cannot be quoted. `max_qty`, when present, is a hard limit per line. Recurring
SKUs are priced per year; one-time SKUs (services) are charged once whatever
the term.

**Volume tiers.** Once a line's quantity reaches a tier's `min_qty`, the tier
price applies to *every* unit on that line (not just the units above the
threshold). Tier pricing is not a discount.

**Discounts.** A line may carry a `discount_pct` (percent, so `7.5` is 7.5%).
Recurring lines also get a term discount: 12 months 0%, 24 months 5%, 36 months
10%. The term discount compounds with the line discount; it does not add to it.
Term discounts do not apply to one-time SKUs.

**Totals.** A recurring line is `tier price x qty x (term / 12)`, then the line
discount, then the term discount. Round each line to the cent, half up. The
quote total is the sum of the rounded lines.

**Approvals.** The effective discount is the dollar-weighted discount across
the whole quote: `(baseline - net) / baseline`, where baseline is the line
totals before any discount, and net is after both discounts. Round it to two
decimals, then look it up in `data/approval_policy.json`. A discount *up to and
including* a tier's `up_to` stays in that tier. The approval chain is
cumulative: a 25% discount needs the sales manager and the VP.

## Part 1: get the tests green

Some tests fail. Fix the code, not the tests. The suite is not exhaustive, so
if you find something that disagrees with the rules above, fix that too and
add a test for it.

## Part 2: natural-language quotes

Implement `parse_deal_request` in `roadrunner_cpq/llm.py` and wire it into
`python -m roadrunner_cpq ask "..."`, for example:

> 60 platform seats and SSO for Acme on a 2 year deal, they want 10% off

The result must go through the same `price_quote` path as a structured quote,
and the CLI should print the quote and the approval chain.

Treat the model as an unreliable component that sits between the customer's
text and our money. Decide what it is allowed to decide.

Add tests with `FakeClient`. Be ready to talk through your failure modes.

## Stretch

`explain(priced_quote)` returns a two-sentence summary for the sales rep,
written by the model. Every dollar figure in it must match the quote.
