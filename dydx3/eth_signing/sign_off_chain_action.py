from web3 import Web3

from dydx3.constants import SIGNATURE_TYPE_DECIMAL
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

    def sign(
        self,
        signer_address,
        **message,
    ):
        message_hash = self.get_hash(**message)
        raw_signature = self.signer.sign(message_hash, signer_address)
        return util.create_typed_signature(
            raw_signature,
            SIGNATURE_TYPE_DECIMAL,
        )

    def verify(
        self,
        typed_signature,
        expected_signer_address,
        **message,
    ):
        message_hash = self.get_hash(**message)
        signer = util.ec_recover_typed_signature(message_hash, typed_signature)
        return util.addresses_are_equal(signer, expected_signer_address)

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
