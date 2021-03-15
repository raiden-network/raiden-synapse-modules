from typing import Dict, Iterable, Set
from urllib.parse import urlparse

from eth_typing import Address
from eth_utils import to_canonical_address, to_checksum_address
from synapse.config import ConfigError  # type: ignore
from synapse.handlers.presence import UserPresenceState  # type: ignore
from synapse.module_api import ModuleApi  # type: ignore
from web3 import Web3

from raiden_synapse_modules.service_address_listener import (
    read_initial_services_addresses,
    setup_contract_from_address,
)


class PFSPresenceRouterConfig:
    def __init__(self):
        # Config options
        self.service_registry_address: Address
        self.ethereum_rpc: str


class PFSPresenceRouter:
    """An implementation of synapse.presence_router.PresenceRouter.
    Supports routing all presence to all registered service providers.

    Args:
        config: A configuration object.
        module_api: An instance of Synapse's ModuleApi.
    """

    def __init__(self, config: PFSPresenceRouterConfig, module_api: ModuleApi):
        self._module_api = module_api
        self._config = config

        provider = Web3.HTTPProvider(self._config.ethereum_rpc)
        self.web3 = Web3(provider)
        self.registry = setup_contract_from_address(
            self._config.service_registry_address, self.web3
        )
        self.registered_services: Dict[Address, int] = read_initial_services_addresses(
            self.registry
        )
        self.next_timeout = min(self.registered_services.values())

    @staticmethod
    def parse_config(config_dict: dict) -> PFSPresenceRouterConfig:
        """Parse a configuration dictionary from the homeserver config, do
        some validation and return a typed PFSPresenceRouterConfig.

        Args:
            config_dict: The configuration dictionary.

        Returns:
            A validated config object.
        """
        # Initialise a typed config object
        config = PFSPresenceRouterConfig()  # type: ignore
        service_registry_address = config_dict.get("service_registry_address")
        ethereum_rpc = config_dict.get("ethereum_rpc")

        if service_registry_address is None:
            raise ConfigError("`service_registry_address` not properly configured")
        else:
            try:
                config.service_registry_address = to_canonical_address(
                    to_checksum_address(service_registry_address)
                )
            except ValueError:
                raise ConfigError("`service_registry_address` is not a valid address")
        if ethereum_rpc is None:
            raise ConfigError("`ethereum_rpc` not properly configured")
        parsed = urlparse(ethereum_rpc)
        if not all([parsed.scheme, parsed.netloc]):
            raise ConfigError("`ethereum_rpc` is not properly configured")
        else:
            config.ethereum_rpc = ethereum_rpc

        return config

    async def get_users_for_states(
        self,
        state_updates: Iterable[UserPresenceState],
    ) -> Dict[str, Set[UserPresenceState]]:
        """Given an iterable of user presence updates, determine where each one
        needs to go.

        Args:
            state_updates: An iterable of user presence state updates.

        Returns:
          A dictionary of user_id -> set of UserPresenceState that the user should
          receive.
        """
        assert state_updates is not None
        destination_users: Dict[str, Set[UserPresenceState]] = {}

        return destination_users
