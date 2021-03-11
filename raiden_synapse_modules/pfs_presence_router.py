from typing import Dict, Iterable, Set

from eth_typing import Address
from synapse.config import ConfigError  # type: ignore
from synapse.handlers.presence import UserPresenceState  # type: ignore
from synapse.module_api import ModuleApi  # type: ignore


class PFSPresenceRouterConfig:
    def __init__(self):
        # Config options with their defaults
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
        self._config = config
        self._module_api = module_api
        self.registered_services: Dict[Address, int]

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
        config = PFSPresenceRouterConfig()
        assert config_dict is not None

        if True:
            pass
        else:
            raise ConfigError("Not properly configured")

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
