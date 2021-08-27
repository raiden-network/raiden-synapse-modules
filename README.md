# raiden-synapse-modules
synapse extensions for raiden

## PFSPresenceRouter

For `PFSPresenceRouter` configuration, add this to your `homeserver.yaml`:

```
presence:
    enabled: true
    presence_router:
      module: raiden_synapse_modules.pfs_presence_router.PFSPresenceRouter
      config:
        ethereum_rpc: ${ETH_RPC}
        service_registry_address: ${SERVICE_REGISTRY}
        blockchain_sync_seconds: 15
```

where
- `ETH_RPC` points to a valid ethereum rpc resource
- `SERVICE_REGISTRY` is the hex address of a `raiden_contracts` `ServiceRegistry.sol` deployment


### Publishing a new release

After bumping the version on [pyproject.toml](pyproject.toml), run `make publish`
