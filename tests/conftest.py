import pytest
from eth_tester import EthereumTester  # type: ignore

from raiden_contracts.tests.fixtures.base import (
    contract_source_manager,
    contracts_manager,
    ethereum_tester,
    patch_genesis_gas_limit,
    web3,
)
from raiden_contracts.tests.fixtures.contracts import (
    deploy_contract,
    deploy_contract_txhash,
    deploy_tester_contract,
)
from raiden_contracts.tests.fixtures.service_registry_fixtures import (
    service_registry
)
from raiden_contracts.tests.fixtures.token import (
    custom_token,
    custom_token_factory,
    token_args
)


@pytest.fixture(name="blockchain")
def blockchain():
    chain = EthereumTester()
    return chain
