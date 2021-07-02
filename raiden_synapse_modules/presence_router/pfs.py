import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Literal, Optional, Set, Union, cast
from urllib.parse import urlparse

from eth_typing import Address
from eth_utils import encode_hex, to_canonical_address, to_checksum_address
from hexbytes import HexBytes
from requests.exceptions import ReadTimeout
from synapse.config import ConfigError
from synapse.handlers.presence import UserPresenceState
from synapse.module_api import ModuleApi, run_in_background
from synapse.types import UserID
from web3 import Web3
from web3.exceptions import BlockNotFound, ExtraDataLengthError

from raiden_synapse_modules.presence_router.blockchain_support import (
    install_filters,
    read_initial_services_addresses,
    setup_contract_from_address,
)

log = logging.getLogger(__name__)


class WorkerType(Enum):
    MAIN = None
    FEDERATION_SENDER = "synapse.app.federation_sender"
    OTHER = "_other"


@dataclass
class PFSPresenceRouterConfig:
    service_registry_address: Address
    ethereum_rpc: str
    blockchain_sync: int


class PFSPresenceRouter:
    """An implementation of synapse.presence_router.PresenceRouter.
    Supports routing all presence to all registered service providers.

    Basic flow:
        - on startup
            - read all registered services
            - check for local service users
            - send ALL presences to local service users
        - every config.blockchain_sync_seconds
            - check for new filter hits (RegisteredService, Block)
        - on RegisteredService
            - update registered_services
            - recompile local service users
            - send ALL presences to new service users
        - on Block
            - check block.timestamp against next_expiry
        - on expired services
            - update registered_services
            - recompile local service users

    Args:
        config: A configuration object.
        module_api: An instance of Synapse's ModuleApi.
    """

    def __init__(self, config: PFSPresenceRouterConfig, module_api: ModuleApi):
        self._module_api: ModuleApi = module_api
        self._config: PFSPresenceRouterConfig = config

        self.web3 = self.setup_web3()
        self.registry = setup_contract_from_address(
            self._config.service_registry_address, self.web3
        )
        self.registered_services: Dict[Address, int] = read_initial_services_addresses(
            self.registry
        )
        if len(self.registered_services):
            self.next_expiry = min(self.registered_services.values())
        else:
            self.next_expiry = 0
        self.local_users: List[UserID] = []
        self.update_local_users()
        if self.worker_type is WorkerType.FEDERATION_SENDER:
            # The initial presence update only needs to be sent from within the
            # `federation_sender` worker process
            run_in_background(
                self.send_current_presences_to,
                self.local_users,
            )
        block_filter, event_filter = install_filters(self.registry)
        self.block_filter = block_filter
        self.event_filter = event_filter
        self._module_api._hs.get_clock().looping_call(
            self.check_filters, self._config.blockchain_sync * 1000
        )
        log.debug("Module setup done")

    @property
    def worker_type(self) -> WorkerType:
        """Return the type of worker we're running in"""
        try:
            return WorkerType(self._module_api._hs.config.worker_app)
        except ValueError:
            return WorkerType.OTHER

    @staticmethod
    def parse_config(config_dict: dict) -> PFSPresenceRouterConfig:
        """Parse a configuration dictionary from the homeserver config, do
        some validation and return a typed PFSPresenceRouterConfig.

        Args:
            config_dict: The configuration dictionary.

        Returns:
            A validated config object.
        """
        try:
            blockchain_sync = int(config_dict.get("blockchain_sync_seconds", "15"))
        except ValueError:
            raise ConfigError("`blockchain_sync_seconds` needs to be an integer")

        try:
            service_registry_address = to_canonical_address(
                to_checksum_address(config_dict.get("service_registry_address"))  # type: ignore
            )
        except (TypeError, ValueError):
            raise ConfigError("`service_registry_address` is not a valid address or missing")

        try:
            ethereum_rpc = config_dict.get("ethereum_rpc")
            parsed_ethereum_rpc = urlparse(ethereum_rpc)
            if not all([parsed_ethereum_rpc.scheme, parsed_ethereum_rpc.netloc]):
                raise ValueError()
        except ValueError:
            raise ConfigError("`ethereum_rpc` is not properly configured")

        return PFSPresenceRouterConfig(
            service_registry_address, ethereum_rpc, blockchain_sync  # type: ignore
        )

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
        destination_users: Dict[str, Set[UserPresenceState]] = {}
        for user in self.local_users:
            destination_users[user] = set(state_updates)
        return destination_users

    async def get_interested_users(self, user_id: str) -> Union[Set[str], Literal["ALL"]]:
        """
        Retrieve a list of users that `user_id` is interested in receiving the
        presence of. This will be in addition to those they share a room with.

        Optionally, the literal str "ALL" can be returned to indicate that this user
        should receive all incoming local and remote presence updates.

        Note that this method will only be called for local users.

        Args:
          user_id: A user requesting presence updates.

        Returns:
          A set of user IDs to return additional presence updates for, or "ALL" to return
          presence updates for all other users.
        """
        if user_id in self.local_users:
            return "ALL"
        else:
            return set()

    def setup_web3(self) -> Web3:
        provider = Web3.HTTPProvider(self._config.ethereum_rpc)
        web3 = Web3(provider)
        try:
            web3.eth.getBlock("latest")
        except ExtraDataLengthError:
            from web3.middleware import geth_poa_middleware

            web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return web3

    def check_filters(self) -> None:
        log.debug("Checking filters.")
        try:
            receipts = self.block_filter.get_new_entries()
            registered_services = self.event_filter.get_new_entries()
        except ReadTimeout:
            log.error("Connection error: timeout")
            return

        for receipt in receipts:
            blockhash = cast(HexBytes, receipt)
            self.on_new_block(blockhash)
        for registered_service in registered_services:
            self.on_registered_service(
                registered_service.args.service,  # type: ignore
                registered_service.args.valid_till,  # type: ignore
            )
        self.last_update = time.time()

    async def send_current_presences_to(self, users: List[UserID]) -> None:
        """Send all presences to users."""
        log.debug(f"Sending presences to {len(users)} users")
        await self._module_api.send_local_online_presence_to(users)

    def on_registered_service(self, service_address: Address, expiry: int) -> None:
        """Called, when there is a new RegisteredService event on the blockchain."""
        # service_address is already known, update the expiry
        log.debug("New registered service {to_checksum_address(service_address)}")
        if service_address in self.registered_services:
            self.registered_services[service_address] = expiry
        # new service, add and send current presences
        else:
            self.registered_services[service_address] = expiry
            local_user = self.to_local_user(service_address)
            if local_user is not None:
                self.local_users.append(local_user)
                if self.worker_type is WorkerType.FEDERATION_SENDER:
                    # The initial presence update only needs to be sent from within the
                    # `federation_sender` worker process
                    run_in_background(
                        self.send_current_presences_to,
                        [local_user],
                    )
        if len(self.registered_services):
            self.next_expiry = min(self.registered_services.values())

    def on_new_block(self, blockhash: HexBytes) -> None:
        """Called, when there is a new Block on the blockchain."""
        log.debug(f"New block {encode_hex(blockhash)}.")
        try:
            timestamp: int = self.web3.eth.getBlock(blockhash)["timestamp"]
            if timestamp > self.next_expiry:
                self.expire_services(timestamp)
                if len(self.registered_services):
                    self.next_expiry = min(self.registered_services.values())
        except BlockNotFound:
            log.debug(f"Block {encode_hex(blockhash)} not found.")

    def expire_services(self, timestamp: int) -> None:
        registered_services: Dict[Address, int] = {}
        for address, expiry in self.registered_services.items():
            if expiry > timestamp:
                registered_services[address] = expiry
        self.registered_services = registered_services
        self.update_local_users()

    def update_local_users(self) -> None:
        """Probe all `self.registered_services` addresses for a local UserID and update
        `self.local_users` accordingly.
        """
        local_users: List[UserID] = []
        for address in self.registered_services.keys():
            candidate = self.to_local_user(address)
            if candidate is not None:
                local_users.append(candidate)
        log.debug(f"Now {len(local_users)} users registered for presence updates.")
        self.local_users = local_users

    def to_local_user(self, address: Address) -> Optional[UserID]:
        """Create a UserID for a local user from a registered service address."""
        log.debug(f"Creating UserID for address {to_checksum_address(address)}")
        user_id = self._module_api.get_qualified_user_id(str(to_checksum_address(address)).lower())
        return user_id
