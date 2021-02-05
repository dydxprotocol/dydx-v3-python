from web3 import Web3
from web3.auto import w3
from dydx3 import constants

PREPEND_DEC = '\x19Ethereum Signed Message:\n32'
PREPEND_HEX = '\x19Ethereum Signed Message:\n\x20'


def is_valid_sig_type(
    sig_type,
):
    return sig_type in [
        constants.SIGNATURE_TYPE_DECIMAL,
        constants.SIGNATURE_TYPE_HEXADECIMAL,
        constants.SIGNATURE_TYPE_NO_PREPEND,
    ]


def ec_recover_typed_signature(
    hashVal,
    typed_signature,
):
    if len(strip_hex_prefix(typed_signature)) != 66 * 2:
        raise Exception('Unable to ecrecover signature: ' + typed_signature)

    sig_type = int(typed_signature[-2:], 16)
    prepended_hash = ''
    if sig_type == constants.SIGNATURE_TYPE_NO_PREPEND:
        prepended_hash = hashVal
    elif sig_type == constants.SIGNATURE_TYPE_DECIMAL:
        prepended_hash = Web3.solidityKeccak(
            ['string', 'bytes32'],
            [PREPEND_DEC, hashVal],
        )
    elif sig_type == constants.SIGNATURE_TYPE_HEXADECIMAL:
        prepended_hash = Web3.solidityKeccak(
            ['string', 'bytes32'],
            [PREPEND_HEX, hashVal],
        )
    else:
        raise Exception('Invalid signature type: ' + sig_type)

    if not prepended_hash:
        raise Exception('Invalid hash: ' + hashVal)

    signature = typed_signature[:-2]

    address = w3.eth.account.recoverHash(prepended_hash, signature=signature)
    return address


def create_typed_signature(
    signature,
    sig_type,
):
    if not is_valid_sig_type(sig_type):
        raise Exception('Invalid signature type: ' + sig_type)

    return fix_raw_signature(signature) + '0' + str(sig_type)


def fix_raw_signature(
    signature,
):
    stripped = strip_hex_prefix(signature)

    if len(stripped) != 130:
        raise Exception('Invalid raw signature: ' + signature)

    rs = stripped[:128]
    v = stripped[128: 130]

    if v == '00':
        return '0x' + rs + '1b'
    if v == '01':
        return '0x' + rs + '1c'
    if v in ['1b', '1c']:
        return '0x' + stripped

    raise Exception('Invalid v value: ' + v)

# ============ Byte Helpers ============


def strip_hex_prefix(input):
    if input.startswith('0x'):
        return input[2:]

    return input


def addresses_are_equal(
    address_one,
    address_two,
):
    if not address_one or not address_two:
        return False

    return (
        strip_hex_prefix(
            address_one
        ).lower() == strip_hex_prefix(address_two).lower()
    )


def hash_string(input):
    return Web3.solidityKeccak(['string'], [input])
