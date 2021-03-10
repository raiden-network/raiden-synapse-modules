from typing import Dict

from eth_typing import Address
from web3.contract import Contract
from web3.types import BlockIdentifier


def read_initial_services_addresses(
    service_registry: Contract, block_identifier: BlockIdentifier = "latest"
) -> Dict[Address, int]:
    """
    Read ethereum addresses for valid registered services from the ServiceRegistry contract.
    """
    if service_registry is not None:
        services_addresses: Dict[Address, int] = {}
        for index in range(
            service_registry.functions.everMadeDepositsLen().call(
                block_identifier=block_identifier
            )
        ):
            address = service_registry.functions.ever_made_deposits(index).call(
                block_identifier=block_identifier
            )
            if address is None:
                continue
            if service_registry.functions.hasValidRegistration(address).call(
                block_identifier=block_identifier
            ):
                functions = service_registry.functions
                services_addresses[address] = functions.service_valid_till(address).call(
                    block_identifier=block_identifier
                )
    return services_addresses
