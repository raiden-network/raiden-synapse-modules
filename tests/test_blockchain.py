import pytest

from raiden_synapse_modules.service_address_listener import (
    read_initial_services_addresses,
    setup_contract_from_address,
    setup_event_filter,
)


@pytest.mark.parametrize("number_of_services", [2])
def test_service_registry(web3, service_registry_with_deposits, number_of_services):
    service_registry = service_registry_with_deposits
    assert service_registry is not None
    assert service_registry.functions.everMadeDepositsLen().call() == number_of_services
    registered_services = read_initial_services_addresses(service_registry, "latest")
    assert len(registered_services) == number_of_services


@pytest.mark.parametrize("number_of_services", [1])
def test_setup_contract_from_address(service_registry_with_deposits, number_of_services):
    address = service_registry_with_deposits.address
    service_registry = setup_contract_from_address(address, service_registry_with_deposits.web3)
    assert service_registry is not None
    assert service_registry.functions.everMadeDepositsLen().call() == number_of_services


@pytest.mark.parametrize("number_of_services", [0])
def test_setup_event_filter(service_registry_with_deposits):
    address = service_registry_with_deposits.address
    event_filter = setup_event_filter(address)
    assert event_filter["address"] == address
