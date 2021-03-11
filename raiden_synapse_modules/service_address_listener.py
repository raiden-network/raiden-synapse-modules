from typing import Dict, Tuple, cast

from eth_typing import Address
from eth_utils import to_checksum_address
from web3 import Web3
from web3._utils.filters import Filter
from web3.contract import Contract
from web3.types import BlockIdentifier

from raiden_contracts.constants import CONTRACT_SERVICE_REGISTRY, EVENT_REGISTERED_SERVICE
from raiden_contracts.contract_manager import ContractManager, contracts_precompiled_path


def setup_contract_from_address(service_registry_address: Address, w3: Web3) -> Contract:
    """
    Setup Contract object for the ServiceRegistry.sol contract at the given address.
    """
    service_registry: Contract
    abi = ContractManager(contracts_precompiled_path()).get_contract_abi(CONTRACT_SERVICE_REGISTRY)
    service_registry = w3.eth.contract(
        abi=abi, address=to_checksum_address(service_registry_address)
    )
    return service_registry


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


def install_filters(service_registry: Contract) -> Tuple[Filter, Filter]:
    """
    Install eth filters for new Block and `ServiceRegistry.sol::RegisteredService` events.
    """
    block_filter = service_registry.web3.eth.filter("latest")
    event_filter = getattr(service_registry.events, EVENT_REGISTERED_SERVICE).createFilter(
        fromBlock=0
    )
    return (block_filter, cast(Filter, event_filter))
