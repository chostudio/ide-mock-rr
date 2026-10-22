"""Natural-language deal request -> Quote, via the OpenAI API.

Not implemented yet. See README.md, Part 2.
"""
import os

from openai import OpenAI

DEFAULT_MODEL = os.environ.get("ROADRUNNER_MODEL", "gpt-4o-mini")


class ClarificationNeeded(Exception):
    """The request is too ambiguous to turn into a quote safely."""


class LLMUnavailable(Exception):
    """The model could not be reached after retries."""


class LLMOutputError(ValueError):
    """The model answered, but not with something we can use."""


def get_client():
    # reads OPENAI_API_KEY from the environment
    return OpenAI()


def parse_deal_request(text, catalog, client=None, model=None):
    """Turn free text like '60 seats for Acme on a 2 year deal, 10% off'
    into a roadrunner_cpq.models.Quote.

    `client` is injectable so tests can pass a fake (see tests/fakes.py).
    """
    raise NotImplementedError("TODO")
