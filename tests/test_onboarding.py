from web3 import Web3

from dydx3 import Client

from tests.constants import DEFAULT_HOST


class TestOnboarding():

    def test_derive_stark_key(self):
        web3 = Web3()  # Connect to a local Ethereum node.
        client = Client(
            host=DEFAULT_HOST,
            web3=web3,
        )
        signer_address = web3.eth.accounts[0]
        stark_private_key = client.onboarding.derive_stark_key(signer_address)
        assert stark_private_key == (
            '0x1bb0389af265c56844fa79b1e586b36f535fee293f59768fdb61d3f280f05fb'
        )
