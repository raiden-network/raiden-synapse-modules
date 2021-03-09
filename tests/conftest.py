import pytest
from eth_tester import EthereumTester  # type: ignore


@pytest.fixture(name="true_fixture")
def true_fixture():
    return True


@pytest.fixture(name="blockchain")
def blockchain():
    chain = EthereumTester()
    return chain
