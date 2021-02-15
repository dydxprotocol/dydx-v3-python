import os

from web3 import Web3

from dydx3.constants import OFF_CHAIN_ONBOARDING_ACTION
from dydx3.eth_signing import SignWithWeb3
from dydx3.eth_signing import SignWithKey
from dydx3.eth_signing import SignOnboardingAction
from tests.constants import DEFAULT_NETWORK_ID

MOCK_KEY = '0x0f29b00db328c986c87a9e05c776bcdcccec82a50d3b707bf00aeef3f195054e'
NETWORK_ID = int(os.environ.get('NETWORK_ID', DEFAULT_NETWORK_ID))


class TestSignOffChainAction():

    def test_sign_via_local_node_no_expiration(self):
        web3 = Web3()  # Connect to a local Ethereum node.
        signer = SignWithWeb3(web3)
        signer_address = web3.eth.accounts[0]

        action_signer = SignOnboardingAction(signer, NETWORK_ID)
        signature = action_signer.sign(
            signer_address,
            action=OFF_CHAIN_ONBOARDING_ACTION,
        )
        assert action_signer.verify(
            signature,
            signer_address,
            action=OFF_CHAIN_ONBOARDING_ACTION,
        )

    def test_sign_via_account_no_expiration(self):
        web3 = Web3(None)
        web3_account = web3.eth.account.create()
        signer = SignWithKey(web3_account.key)
        signer_address = web3_account.address

        action_signer = SignOnboardingAction(signer, NETWORK_ID)
        signature = action_signer.sign(
            signer_address,
            action=OFF_CHAIN_ONBOARDING_ACTION,
        )
        assert action_signer.verify(
            signature,
            signer_address,
            action=OFF_CHAIN_ONBOARDING_ACTION,
        )

    def test_sign_via_private_key_no_expiration(self):
        signer = SignWithKey(MOCK_KEY)
        signer_address = signer.address

        action_signer = SignOnboardingAction(signer, NETWORK_ID)
        signature = action_signer.sign(
            signer_address,
            action=OFF_CHAIN_ONBOARDING_ACTION,
        )
        assert action_signer.verify(
            signature,
            signer_address,
            action=OFF_CHAIN_ONBOARDING_ACTION,
        )
