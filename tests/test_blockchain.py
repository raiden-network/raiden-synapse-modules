def test_eth_tester(blockchain):
    assert blockchain.get_balance(
        blockchain.get_accounts()[0]
    ) == 1000000000000000000000000
