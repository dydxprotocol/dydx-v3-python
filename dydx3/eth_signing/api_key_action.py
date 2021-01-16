from web3 import Web3

from dydx3.eth_signing import util
from dydx3.eth_signing.sign_off_chain_action import SignOffChainAction

EIP712_OFF_CHAIN_ACTION_STRUCT_STRING = (
    'dYdX(' +
    'string method,' +
    'string requestPath,' +
    'string body,' +
    'string timestamp' +
    ')'
)


class SignApiKeyAction(SignOffChainAction):

    def get_hash(
        self,
        method,
        request_path,
        body,
        timestamp,
    ):
        data = [
            [
                'bytes32',
                'bytes32',
                'bytes32',
                'bytes32',
                'bytes32',
            ],
            [
                util.hash_string(EIP712_OFF_CHAIN_ACTION_STRUCT_STRING),
                util.hash_string(method),
                util.hash_string(request_path),
                util.hash_string(body),
                util.hash_string(timestamp),
            ],
        ]
        struct_hash = Web3.solidityKeccak(*data)
        return self.get_eip712_hash(struct_hash)
