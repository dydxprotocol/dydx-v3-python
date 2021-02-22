from web3 import Web3

from dydx3.constants import NETWORK_ID_MAINNET
from dydx3.eth_signing import util
from dydx3.eth_signing.sign_off_chain_action import SignOffChainAction

# On mainnet, include an extra onlySignOn parameter.
EIP712_ONBOARDING_ACTION_STRUCT = [
    {'type': 'string', 'name': 'action'},
    {'type': 'string', 'name': 'onlySignOn'},
]
EIP712_ONBOARDING_ACTION_STRUCT_STRING = (
    'dYdX(' +
    'string action,' +
    'string onlySignOn' +
    ')'
)
EIP712_ONBOARDING_ACTION_STRUCT_TESTNET = [
    {'type': 'string', 'name': 'action'},
]
EIP712_ONBOARDING_ACTION_STRUCT_STRING_TESTNET = (
    'dYdX(' +
    'string action' +
    ')'
)
EIP712_STRUCT_NAME = 'dYdX'

ONLY_SIGN_ON_DOMAIN_MAINNET = 'https://trade.dydx.exchange'


class SignOnboardingAction(SignOffChainAction):

    def get_eip712_struct(self):
        # On mainnet, include an extra onlySignOn parameter.
        if self.network_id == NETWORK_ID_MAINNET:
            return EIP712_ONBOARDING_ACTION_STRUCT
        else:
            return EIP712_ONBOARDING_ACTION_STRUCT_TESTNET

    def get_eip712_struct_name(self):
        return EIP712_STRUCT_NAME

    def get_eip712_message(
        self,
        **message,
    ):
        eip712_message = super(SignOnboardingAction, self).get_eip712_message(
            **message,
        )

        # On mainnet, include an extra onlySignOn parameter.
        if self.network_id == NETWORK_ID_MAINNET:
            eip712_message['message']['onlySignOn'] = (
                'https://trade.dydx.exchange'
            )

        return eip712_message

    def get_hash(
        self,
        action,
    ):
        # On mainnet, include an extra onlySignOn parameter.
        if self.network_id == NETWORK_ID_MAINNET:
            eip712_struct_str = EIP712_ONBOARDING_ACTION_STRUCT_STRING
        else:
            eip712_struct_str = EIP712_ONBOARDING_ACTION_STRUCT_STRING_TESTNET

        data = [
            [
                'bytes32',
                'bytes32',
            ],
            [
                util.hash_string(eip712_struct_str),
                util.hash_string(action),
            ],
        ]

        # On mainnet, include an extra onlySignOn parameter.
        if self.network_id == NETWORK_ID_MAINNET:
            data[0].append('bytes32')
            data[1].append(util.hash_string(ONLY_SIGN_ON_DOMAIN_MAINNET))

        struct_hash = Web3.solidityKeccak(*data)
        return self.get_eip712_hash(struct_hash)
