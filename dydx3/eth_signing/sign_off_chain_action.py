from web3 import Web3

from dydx3.eth_signing import util

DOMAIN = 'dYdX'
VERSION = '1.0'
EIP712_DOMAIN_STRING_NO_CONTRACT = (
    'EIP712Domain(' +
    'string name,' +
    'string version,' +
    'uint256 chainId' +
    ')'
)


class SignOffChainAction(object):

    def __init__(self, signer, network_id):
        self.signer = signer
        self.network_id = network_id

    def get_hash(self, **message):
        raise NotImplementedError

    def get_eip712_struct(self):
        raise NotImplementedError

    def get_eip712_struct_name(self):
        raise NotImplementedError

    def sign(
        self,
        signer_address,
        **message,
    ):
        eip712_message = self.get_eip712_message(**message)
        message_hash = self.get_hash(**message)
        typed_signature = self.signer.sign(
            eip712_message,
            message_hash,
            signer_address,
        )
        return typed_signature

    def verify(
        self,
        typed_signature,
        expected_signer_address,
        **message,
    ):
        message_hash = self.get_hash(**message)
        signer = util.ec_recover_typed_signature(message_hash, typed_signature)
        return util.addresses_are_equal(signer, expected_signer_address)

    def get_eip712_message(
        self,
        **message,
    ):
        struct_name = self.get_eip712_struct_name()
        return {
            'types': {
                'EIP712Domain': [
                    {
                        'name': 'name',
                        'type': 'string',
                    },
                    {
                        'name': 'version',
                        'type': 'string',
                    },
                    {
                        'name': 'chainId',
                        'type': 'uint256',
                    },
                ],
                struct_name: self.get_eip712_struct(),
            },
            'domain': {
                'name': DOMAIN,
                'version': VERSION,
                'chainId': self.network_id,
            },
            'primaryType': struct_name,
            'message': message,
        }

    def get_eip712_hash(self, struct_hash):
        return Web3.solidityKeccak(
            [
                'bytes2',
                'bytes32',
                'bytes32',
            ],
            [
                '0x1901',
                self.get_domain_hash(),
                struct_hash,
            ]
        )

    def get_domain_hash(self):
        return Web3.solidityKeccak(
            [
                'bytes32',
                'bytes32',
                'bytes32',
                'uint256',
            ],
            [
                util.hash_string(EIP712_DOMAIN_STRING_NO_CONTRACT),
                util.hash_string(DOMAIN),
                util.hash_string(VERSION),
                self.network_id,
            ],
        )
