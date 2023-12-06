from web3 import Web3

from dydx3 import Client
from dydx3.constants import NETWORK_ID_MAINNET
from dydx3.constants import NETWORK_ID_SEPOLIA

from tests.constants import DEFAULT_HOST

GANACHE_PRIVATE_KEY = (
    '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
)

EXPECTED_API_KEY_CREDENTIALS_MAINNET = {
    'key': '50fdcaa0-62b8-e827-02e8-a9520d46cb9f',
    'secret': 'rdHdKDAOCa0B_Mq-Q9kh8Fz6rK3ocZNOhKB4QsR9',
    'passphrase': '12_1LuuJMZUxcj3kGBWc',
}
EXPECTED_STARK_KEY_PAIR_WITH_Y_COORDINATE_MAINNET = {
    'public_key':
        '0x39d88860b99b1809a63add01f7dfa59676ae006bbcdf38ff30b6a69dcf55ed3',
    'public_key_y_coordinate':
        '0x2bdd58a2c2acb241070bc5d55659a85bba65211890a8c47019a33902aba8400',
    'private_key':
        '0x170d807cafe3d8b5758f3f698331d292bf5aeb71f6fd282f0831dee094ee891',
}
EXPECTED_API_KEY_CREDENTIALS_SEPOLIA = {
    'key': '30cb6046-8f4a-5677-a19c-a494ccb7c7e5',
    'secret': '4Yd_6JtH_-I2taoNQKAhkCifnVHQ2Unue88sIeuc',
    'passphrase': 'Db1GQK5KpI_qeddgjF66',
}
EXPECTED_STARK_KEY_PAIR_WITH_Y_COORDINATE_SEPOLIA = {
    'public_key':
        '0x15e2e074a7ac9e78edb2ee9f11a0c0c0a080c79758ab81616eea9c032c75265',
    'public_key_y_coordinate':
        '0x360408546b64238f80d7a8a336d7304d75f122a7e5bb22cbb7a14f550eac5a8',
    'private_key':
        '0x2d21c094fedea3e72bef27fbcdceaafd34e88fc4b7586859e26e98b21e63a60'
}


class TestOnboarding():

    def test_derive_stark_key_on_mainnet_from_web3(self):
        web3 = Web3()  # Connect to a local Ethereum node.
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_MAINNET,
            web3=web3,
        )
        signer_address = web3.eth.accounts[0]
        stark_key_pair_with_y_coordinate = client.onboarding.derive_stark_key(
            signer_address,
        )
        assert stark_key_pair_with_y_coordinate == \
            EXPECTED_STARK_KEY_PAIR_WITH_Y_COORDINATE_MAINNET

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

    def test_derive_stark_key_on_SEPOLIA_from_web3(self):
        web3 = Web3()  # Connect to a local Ethereum node.
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_SEPOLIA,
            web3=web3,
        )
        signer_address = web3.eth.accounts[0]
        stark_key_pair_with_y_coordinate = client.onboarding.derive_stark_key(
            signer_address,
        )
        assert stark_key_pair_with_y_coordinate == \
            EXPECTED_STARK_KEY_PAIR_WITH_Y_COORDINATE_SEPOLIA

    def test_recover_default_api_key_credentials_on_SEPOLIA_from_web3(self):
        web3 = Web3()  # Connect to a local Ethereum node.
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_SEPOLIA,
            web3=web3,
        )
        signer_address = web3.eth.accounts[0]
        api_key_credentials = (
            client.onboarding.recover_default_api_key_credentials(
                signer_address,
            )
        )
        assert api_key_credentials == EXPECTED_API_KEY_CREDENTIALS_SEPOLIA

    def test_derive_stark_key_on_mainnet_from_priv(self):
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_MAINNET,
            eth_private_key=GANACHE_PRIVATE_KEY,
            api_key_credentials={'key': 'value'},
        )
        signer_address = client.default_address
        stark_key_pair_with_y_coordinate = client.onboarding.derive_stark_key(
            signer_address,
        )
        assert stark_key_pair_with_y_coordinate == \
            EXPECTED_STARK_KEY_PAIR_WITH_Y_COORDINATE_MAINNET

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

    def test_derive_stark_key_on_SEPOLIA_from_priv(self):
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_SEPOLIA,
            eth_private_key=GANACHE_PRIVATE_KEY,
        )
        signer_address = client.default_address
        stark_key_pair_with_y_coordinate = client.onboarding.derive_stark_key(
            signer_address,
        )
        assert stark_key_pair_with_y_coordinate == \
            EXPECTED_STARK_KEY_PAIR_WITH_Y_COORDINATE_SEPOLIA

    def test_recover_default_api_key_credentials_on_SEPOLIA_from_priv(self):
        client = Client(
            host=DEFAULT_HOST,
            network_id=NETWORK_ID_SEPOLIA,
            eth_private_key=GANACHE_PRIVATE_KEY,
        )
        signer_address = client.default_address
        api_key_credentials = (
            client.onboarding.recover_default_api_key_credentials(
                signer_address,
            )
        )
        assert api_key_credentials == EXPECTED_API_KEY_CREDENTIALS_SEPOLIA
