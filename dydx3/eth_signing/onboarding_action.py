from web3 import Web3

from dydx3.eth_signing import util
from dydx3.eth_signing.sign_off_chain_action import SignOffChainAction

EIP712_OFF_CHAIN_ACTION_STRUCT_STRING = (
    'dYdX(' +
    'string action' +
    ')'
)


class SignOnboardingAction(SignOffChainAction):

    def get_hash(
        self,
        action,
    ):
        data = [
            [
                'bytes32',
                'bytes32',
            ],
            [
                util.hash_string(EIP712_OFF_CHAIN_ACTION_STRUCT_STRING),
                util.hash_string(action),
            ],
        ]
        struct_hash = Web3.solidityKeccak(*data)
        return self.get_eip712_hash(struct_hash)
