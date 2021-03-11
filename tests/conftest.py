from typing import Callable

import pytest
from eth_tester import EthereumTester  # type: ignore
from eth_typing import Address
from web3.contract import Contract
from web3.types import TxParams

from raiden_contracts.tests.fixtures.base import (
    auto_revert_chain,
    contract_source_manager,
    contracts_manager,
    create_account,
    ethereum_tester,
    get_accounts,
    patch_genesis_gas_limit,
    web3,
)
from raiden_contracts.tests.fixtures.contracts import (
    deploy_contract,
    deploy_contract_txhash,
    deploy_tester_contract,
)
from raiden_contracts.tests.fixtures.service_registry_fixtures import service_registry
from raiden_contracts.tests.fixtures.token import custom_token, custom_token_factory, token_args
from raiden_contracts.tests.utils.constants import SERVICE_DEPOSIT
from raiden_contracts.tests.utils.contracts import call_and_transact


@pytest.fixture(name="number_of_services", scope="function")
def three():
    return 3


@pytest.fixture(name="service_registry_with_deposits", scope="function")
def service_registry_with_deposits(
    service_registry: Contract,  # noqa: F811
    custom_token: Contract,  # noqa: F811
    get_accounts: Callable,  # noqa: F811
    number_of_services: int,
) -> Contract:
    accounts = get_accounts(number_of_services)
    for account in accounts:
        register_service(service_registry, custom_token, account)
    return service_registry


def register_service(
    service_registry: Contract,  # noqa: F811
    token: Contract,
    account: Address
) -> None:
    sender: TxParams = {"from": account}
    call_and_transact(token.functions.mint(SERVICE_DEPOSIT), sender)
    call_and_transact(token.functions.approve(service_registry.address, SERVICE_DEPOSIT), sender)
    call_and_transact(service_registry.functions.deposit(SERVICE_DEPOSIT), sender)


@pytest.fixture(name="blockchain")
def blockchain():
    chain = EthereumTester()
    return chain
