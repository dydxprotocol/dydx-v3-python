from web3 import Web3

from dydx3.eth_signing import util
from dydx3.eth_signing.sign_off_chain_action import SignOffChainAction

EIP712_API_KEY_ACTION_STRUCT = [
    {'type': 'string', 'name': 'method'},
    {'type': 'string', 'name': 'requestPath'},
    {'type': 'string', 'name': 'body'},
    {'type': 'string', 'name': 'timestamp'},
]
EIP712_API_KEY_ACTION_STRUCT_STRING = (
    'dYdX(' +
    'string method,' +
    'string requestPath,' +
    'string body,' +
    'string timestamp' +
    ')'
)
EIP712_STRUCT_NAME = 'dYdX'


class SignApiKeyAction(SignOffChainAction):

    def get_eip712_struct(self):
        return EIP712_API_KEY_ACTION_STRUCT

    def get_eip712_struct_name(self):
        return EIP712_STRUCT_NAME

    def get_eip712_message(
        self,
        method,
        request_path,
        body,
        timestamp,
    ):
        return super(SignApiKeyAction, self).get_eip712_message(
            method=method,
            requestPath=request_path,
            body=body,
            timestamp=timestamp,
        )

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
                util.hash_string(EIP712_API_KEY_ACTION_STRUCT_STRING),
                util.hash_string(method),
                util.hash_string(request_path),
                util.hash_string(body),
                util.hash_string(timestamp),
            ],
        ]
        struct_hash = Web3.solidityKeccak(*data)
        return self.get_eip712_hash(struct_hash)
