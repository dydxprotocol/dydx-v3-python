import datetime

import dateparser as dp
from web3 import Web3

from dydx3 import constants
from dydx3.eth_signing import util

DOMAIN = 'dYdX'
VERSION = '1.0'
# TODO: NETWORK_ID should be configurable.
NETWORK_ID = 1
EIP712_DOMAIN_STRING_NO_CONTRACT = (
    'EIP712Domain(' +
    'string name,' +
    'string version,' +
    'uint256 chainId' +
    ')'
)
EIP712_OFF_CHAIN_ACTION_STRUCT_STRING = (
    'dYdX(' +
    'string action,' +
    'string expiration' +
    ')'
)


def get_domain_hash():
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
            NETWORK_ID,
        ],
    )


def sign_off_chain_action(
    signer,
    signer_address,
    action,
    expiration=None,
):
    message_hash = get_off_chain_action_hash(action, expiration)
    raw_signature = signer.sign(message_hash, signer_address)
    return util.create_typed_signature(
        raw_signature,
        constants.SIGNATURE_TYPE_DECIMAL,
    )


def off_chain_action_signature_is_valid(
    typed_signature,
    expected_signer_address,
    action,
    expiration=None
):
    message_hash = get_off_chain_action_hash(action, expiration)
    signer = util.ec_recover_typed_signature(
        message_hash,
        typed_signature,
    )
    return (
        util.addresses_are_equal(signer, expected_signer_address)
        and (
            dp.parse(
                expiration,
                settings={'TIMEZONE': 'UTC'},
            ) > datetime.datetime.now('UTC') if expiration else True
        )
    )


def get_off_chain_action_hash(
    action,
    expiration=None,
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
    if expiration:
        data[0].append('bytes32')
        data[1].append(
            util.hash_string(
                str(dp.parse(expiration, settings={'TIMEZONE': 'UTC'})),
            ),
        )
    struct_hash = Web3.solidityKeccak(data[0], data[1])
    return get_eip712_hash(struct_hash)


def get_eip712_hash(struct_hash):
    return Web3.solidityKeccak(
        [
            'bytes2',
            'bytes32',
            'bytes32',
        ],
        [
            '0x1901',
            get_domain_hash(),
            struct_hash,
        ]
    )
