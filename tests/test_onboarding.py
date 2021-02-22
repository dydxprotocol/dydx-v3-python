from web3 import Web3

from dydx3 import Client
from dydx3.constants import NETWORK_ID_MAINNET
from dydx3.constants import NETWORK_ID_ROPSTEN

from tests.constants import DEFAULT_HOST

GANACHE_PRIVATE_KEY = (
    '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
)

EXPECTED_API_KEY_CREDENTIALS_MAINNET = {
    'key': '50fdcaa0-62b8-e827-02e8-a9520d46cb9f',
    'secret': 'rdHdKDAOCa0B_Mq-Q9kh8Fz6rK3ocZNOhKB4QsR9',
    'passphrase': '12_1LuuJMZUxcj3kGBWc',
}
EXPECTED_STARK_PRIVATE_KEY_MAINNET = (
    '0x170d807cafe3d8b5758f3f698331d292bf5aeb71f6fd282f0831dee094ee891'
)
EXPECTED_API_KEY_CREDENTIALS_ROPSTEN = {
    'key': '9c1d91a5-0a30-1ed4-2d3d-b840a479b965',
    'secret': 'hHYEswFe5MHMm8gFb81Jas9b7iLQUicsVv5YBRMY',
    'passphrase': '9z5Ew7m2DLQd87Xlk7Hd',
}
EXPECTED_STARK_PRIVATE_KEY_ROPSTEN = (
    '0x50505654b282eb3debadddeddfa1bc76545a6837dcd59d7d41f6a282a4bbccc'
)


class TestOnboarding():

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

    def test_derive_stark_key_on_mainnet_from_priv(self):
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_MAINNET,
            eth_private_key=GANACHE_PRIVATE_KEY,
            api_key_credentials={'key': 'value'},
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
