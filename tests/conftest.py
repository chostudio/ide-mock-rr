import pytest

from roadrunner_cpq.catalog import load_catalog


@pytest.fixture(scope="session")
def catalog():
    return load_catalog()
