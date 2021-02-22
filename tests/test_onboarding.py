from web3 import Web3

from dydx3 import Client
from dydx3.constants import NETWORK_ID_MAINNET
from dydx3.constants import NETWORK_ID_ROPSTEN

from tests.constants import DEFAULT_HOST

GANACHE_PRIVATE_KEY = (
    '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
)

EXPECTED_API_KEY_CREDENTIALS_MAINNET = {
    'key': '958080b0-000a-01aa-4012-6bbfebf173ee',
    'secret': 'hEIsyT920WaI6LyKBEZCVwhObQk1q7GTIhCD1H2D',
    'passphrase': 'Y6uac-42KTvgVy3238GP',
}
EXPECTED_STARK_PRIVATE_KEY_MAINNET = (
    '0x24a8f3cbd1b565a1e9eb4278ab456e88c89f0a901b8c4d00dca82a75f97df95'
)
EXPECTED_API_KEY_CREDENTIALS_ROPSTEN = {
    'key': '75ec2627-35b3-6e53-e5be-a9cfe90afb26',
    'secret': 'bzc8HTbdPnMGdZV5dlEkchEzFCihlTPL3Bmk9ucH',
    'passphrase': 'XCy5fS635D2mwbnyJwhK',
}
EXPECTED_STARK_PRIVATE_KEY_ROPSTEN = (
    '0x645d65a6007f87b2e1c6c9aec0ab405cb89ad6d426eb0c312321a55391a46c6'
)


class TestOnboarding():

    def test_derive_stark_key_on_mainnet_from_priv(self):
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_MAINNET,
            eth_private_key=GANACHE_PRIVATE_KEY,
        )
        signer_address = client.default_address
        stark_private_key = client.onboarding.derive_stark_key(signer_address)
        assert stark_private_key == EXPECTED_STARK_PRIVATE_KEY_MAINNET

    def test_recover_default_api_key_credentials_on_mainnet_from_priv(self):
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_MAINNET,
            eth_private_key=GANACHE_PRIVATE_KEY,
        )
        signer_address = client.default_address
        api_key_credentials = (
            client.onboarding.recover_default_api_key_credentials(
                signer_address,
            )
        )
        assert api_key_credentials == EXPECTED_API_KEY_CREDENTIALS_MAINNET

    def test_derive_stark_key_on_mainnet_from_web3(self):
        web3 = Web3()  # Connect to a local Ethereum node.
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_MAINNET,
            web3=web3,
        )
        signer_address = web3.eth.accounts[0]
        stark_private_key = client.onboarding.derive_stark_key(signer_address)
        assert stark_private_key == EXPECTED_STARK_PRIVATE_KEY_MAINNET

    def test_recover_default_api_key_credentials_on_mainnet_from_web3(self):
        web3 = Web3()  # Connect to a local Ethereum node.
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_MAINNET,
            web3=web3,
        )
        signer_address = web3.eth.accounts[0]
        api_key_credentials = (
            client.onboarding.recover_default_api_key_credentials(
                signer_address,
            )
        )
        assert api_key_credentials == EXPECTED_API_KEY_CREDENTIALS_MAINNET

    def test_derive_stark_key_on_ropsten_from_priv(self):
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_ROPSTEN,
            eth_private_key=GANACHE_PRIVATE_KEY,
        )
        signer_address = client.default_address
        stark_private_key = client.onboarding.derive_stark_key(signer_address)
        assert stark_private_key == EXPECTED_STARK_PRIVATE_KEY_ROPSTEN

    def test_recover_default_api_key_credentials_on_ropsten_from_priv(self):
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_ROPSTEN,
            eth_private_key=GANACHE_PRIVATE_KEY,
        )
        signer_address = client.default_address
        api_key_credentials = (
            client.onboarding.recover_default_api_key_credentials(
                signer_address,
            )
        )
        assert api_key_credentials == EXPECTED_API_KEY_CREDENTIALS_ROPSTEN

    def test_derive_stark_key_on_ropsten_from_web3(self):
        web3 = Web3()  # Connect to a local Ethereum node.
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_ROPSTEN,
            web3=web3,
        )
        signer_address = web3.eth.accounts[0]
        stark_private_key = client.onboarding.derive_stark_key(signer_address)
        assert stark_private_key == EXPECTED_STARK_PRIVATE_KEY_ROPSTEN

    def test_recover_default_api_key_credentials_on_ropsten_from_web3(self):
        web3 = Web3()  # Connect to a local Ethereum node.
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_ROPSTEN,
            web3=web3,
        )
        signer_address = web3.eth.accounts[0]
        api_key_credentials = (
            client.onboarding.recover_default_api_key_credentials(
                signer_address,
            )
        )
        assert api_key_credentials == EXPECTED_API_KEY_CREDENTIALS_ROPSTEN
