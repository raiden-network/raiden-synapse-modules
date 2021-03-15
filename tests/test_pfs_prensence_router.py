import pytest
from eth_utils import to_checksum_address
from synapse.config import ConfigError  # type: ignore
from raiden_synapse_modules.pfs_presence_router import PFSPresenceRouter


def test_parse_config() -> None:
    with pytest.raises(ConfigError):
        PFSPresenceRouter.parse_config(
            {
                "ethereum_rpc": "bar"
            }
        )
    with pytest.raises(ConfigError):
        PFSPresenceRouter.parse_config(
            {
                "service_registry_address": "bar"
            }
        )
    with pytest.raises(ConfigError):
        PFSPresenceRouter.parse_config(
            {
                "service_registry_address": "bar",
                "ethereum_rpc": "foo"
            }
        )
    config = PFSPresenceRouter.parse_config(
        {
            "service_registry_address": "0x1234567890123456789012345678901234567890",
            "ethereum_rpc": "http://foo.bar"
        }
    )
    assert (
        to_checksum_address(
            config.service_registry_address
        ) == "0x1234567890123456789012345678901234567890"
    )
    assert config.ethereum_rpc == "http://foo.bar"
