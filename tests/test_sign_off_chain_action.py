from web3 import Web3

from dydx3.eth_signing.action import generate_onboarding_action
from dydx3.eth_signing import SignWithWeb3
from dydx3.eth_signing import SignWithKey
from dydx3.eth_signing import sign_off_chain_action
from dydx3.eth_signing import off_chain_action_signature_is_valid

MOCK_ACTION = generate_onboarding_action()
MOCK_KEY = '0x0f29b00db328c986c87a9e05c776bcdcccec82a50d3b707bf00aeef3f195054e'


class TestSignOffChainAction():

    def test_sign_via_local_node_no_expiration(self):
        web3 = Web3()  # Connect to a local Ethereum node.
        signer = SignWithWeb3(web3)
        signer_address = web3.eth.accounts[0]
        signature = sign_off_chain_action(
            signer,
            signer_address,
            MOCK_ACTION,
        )
        assert off_chain_action_signature_is_valid(
            signature,
            signer_address,
            MOCK_ACTION,
        )

    def test_sign_via_account_no_expiration(self):
        web3 = Web3(None)
        web3_account = web3.eth.account.create()
        signer = SignWithKey(web3_account.key)
        signer_address = web3_account.address
        signature = sign_off_chain_action(
            signer,
            signer_address,
            MOCK_ACTION,
        )
        assert off_chain_action_signature_is_valid(
            signature,
            signer_address,
            MOCK_ACTION,
        )

    def test_sign_via_private_key_no_expiration(self):
        signer = SignWithKey(MOCK_KEY)
        signature = sign_off_chain_action(
            signer,
            signer.address,
            MOCK_ACTION,
        )
        assert off_chain_action_signature_is_valid(
            signature,
            signer.address,
            MOCK_ACTION,
        )
