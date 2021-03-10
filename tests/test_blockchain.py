import pytest
from raiden_synapse_modules.service_address_listener import (
    read_initial_services_addresses
)


@pytest.mark.parametrize("number_of_services", [2])
def test_service_registry(web3, service_registry_with_deposits, number_of_services):
    service_registry = service_registry_with_deposits
    assert service_registry is not None
    assert service_registry.functions.everMadeDepositsLen().call() == number_of_services
    registered_services = read_initial_services_addresses(service_registry, "latest")
    assert len(registered_services) == number_of_services
