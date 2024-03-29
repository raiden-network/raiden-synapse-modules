from typing import Callable

import pytest
from web3 import Web3
from web3.contract import Contract

from raiden_synapse_modules.presence_router.blockchain_support import (
    read_initial_services_addresses,
    setup_contract_from_address,
    install_filters,
)
from conftest import register_service


@pytest.mark.parametrize("number_of_services", [2])
def test_service_registry(
    web3: Web3, service_registry_with_deposits: Contract, number_of_services: int
) -> None:
    service_registry = service_registry_with_deposits
    assert service_registry is not None
    assert service_registry.functions.everMadeDepositsLen().call() == number_of_services
    registered_services = read_initial_services_addresses(service_registry, "latest")
    assert len(registered_services) == number_of_services


@pytest.mark.parametrize("number_of_services", [1])
def test_setup_contract_from_address(
    service_registry_with_deposits: Contract, number_of_services: int
) -> None:
    address = service_registry_with_deposits.address
    service_registry = setup_contract_from_address(
        address, service_registry_with_deposits.web3  # type: ignore
    )
    assert service_registry is not None
    assert service_registry.functions.everMadeDepositsLen().call() == number_of_services


@pytest.mark.parametrize("number_of_services", [0])
def test_install_filters(
    service_registry_with_deposits: Contract, custom_token: Contract, get_accounts: Callable
) -> None:
    block_filter, event_filter = install_filters(service_registry_with_deposits)
    assert block_filter.get_all_entries() == []
    assert event_filter.get_all_entries() == []
    account = get_accounts(1)[0]
    register_service(service_registry_with_deposits, custom_token, account)
    assert len(block_filter.get_all_entries()) == 4
    assert len(event_filter.get_all_entries()) == 1
    event = event_filter.get_all_entries()[0]
    assert event.args.service.lower() == account.lower()  # type: ignore
