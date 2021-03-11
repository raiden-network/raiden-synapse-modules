from typing import Dict

from eth_typing import Address
from eth_utils import to_checksum_address
from web3 import Web3
from web3.contract import Contract
from web3.types import BlockIdentifier

from raiden_contracts.constants import CONTRACT_SERVICE_REGISTRY
from raiden_contracts.contract_manager import ContractManager, contracts_precompiled_path


def setup_contract_from_address(service_registry_address: Address, w3: Web3) -> Contract:
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
