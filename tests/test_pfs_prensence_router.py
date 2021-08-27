from unittest.mock import MagicMock

import pytest
from eth_utils import to_checksum_address
from requests.exceptions import ReadTimeout
from synapse.config import ConfigError

from raiden_synapse_modules.presence_router.pfs import PFSPresenceRouter


def test_parse_config() -> None:
    with pytest.raises(ConfigError):
        PFSPresenceRouter.parse_config({"ethereum_rpc": "bar"})
    with pytest.raises(ConfigError):
        PFSPresenceRouter.parse_config({"service_registry_address": "bar"})
    with pytest.raises(ConfigError):
        PFSPresenceRouter.parse_config({"service_registry_address": "bar", "ethereum_rpc": "foo"})
    config = PFSPresenceRouter.parse_config(
        {
            "service_registry_address": "0x1234567890123456789012345678901234567890",
            "ethereum_rpc": "http://foo.bar",
        }
    )
    assert (
        to_checksum_address(config.service_registry_address)
        == "0x1234567890123456789012345678901234567890"
    )
    assert config.ethereum_rpc == "http://foo.bar"
    with pytest.raises(ConfigError):
        PFSPresenceRouter.parse_config(
            {
                "service_registry_address": "0x1234567890123456789012345678901234567890",
                "ethereum_rpc": "http://foo.bar",
                "blockchain_sync_seconds": "foo",
            }
        )
    assert config.blockchain_sync == 15


def test_handle_eth_connection_timeout(presence_router: PFSPresenceRouter) -> None:
    """Regression test for https://github.com/raiden-network/raiden-synapse-modules/issues/9"""
    presence_router.block_filter = MagicMock()
    presence_router.block_filter.get_new_entries = MagicMock(side_effect=ReadTimeout)
    try:
        presence_router._check_filters_once()
    except ReadTimeout:
        pytest.fail("Unexpected ReadTimeout")
