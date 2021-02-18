import decimal
import hashlib

from web3 import Web3

from dydx3.constants import ASSET_RESOLUTION
from dydx3.eth_signing.util import strip_hex_prefix
from dydx3.starkex.constants import ORDER_FIELD_BIT_LENGTHS
from dydx3.starkex.starkex_resources.signature import get_random_private_key
from dydx3.starkex.starkex_resources.signature import (
    private_key_to_ec_point_on_stark_curve,
)
from dydx3.starkex.starkex_resources.signature import private_to_stark_key

BIT_MASK_250 = (2 ** 250) - 1
NONCE_UPPER_BOUND_EXCLUSIVE = 1 << ORDER_FIELD_BIT_LENGTHS['nonce']
DECIMAL_CTX_ROUND_DOWN = decimal.Context(rounding=decimal.ROUND_DOWN)
DECIMAL_CTX_ROUND_UP = decimal.Context(rounding=decimal.ROUND_UP)
DECIMAL_CTX_EXACT = decimal.Context(
    traps=[
        decimal.Inexact,
        decimal.DivisionByZero,
        decimal.InvalidOperation,
        decimal.Overflow,
    ],
)


def bytes_to_int(x):
    """Convert a bytestring to an int."""
    return int(x.hex(), 16)


def int_to_hex_32(x):
    """Normalize to a 32-byte hex string without 0x prefix."""
    padded_hex = hex(x)[2:].rjust(64, '0')
    if len(padded_hex) != 64:
        raise ValueError('Input does not fit in 32 bytes')
    return padded_hex


def serialize_signature(r, s):
    """Convert a signature from an r, s pair to a 32-byte hex string."""
    return int_to_hex_32(r) + int_to_hex_32(s)


def deserialize_signature(signature):
    """Convert a signature from a 32-byte hex string to an r, s pair."""
    if len(signature) != 128:
        raise ValueError(
            'Invalid serialized signature, expected hex string of length 128',
        )
    return int(signature[:64], 16), int(signature[64:], 16)


def to_quantums_exact(human_amount, asset):
    """Convert a human-readable amount to an integer amount of quantums.

    If the provided human_amount is not a multiple of the quantum size,
    an exception will be raised.
    """
    return _to_quantums_helper(human_amount, asset, DECIMAL_CTX_EXACT)


def to_quantums_round_down(human_amount, asset):
    """Convert a human-readable amount to an integer amount of quantums.

    If the provided human_amount is not a multiple of the quantum size,
    the result will be rounded down to the nearest integer.
    """
    return _to_quantums_helper(human_amount, asset, DECIMAL_CTX_ROUND_DOWN)


def to_quantums_round_up(human_amount, asset):
    """Convert a human-readable amount to an integer amount of quantums.

    If the provided human_amount is not a multiple of the quantum size,
    the result will be rounded up to the nearest integer.
    """
    return _to_quantums_helper(human_amount, asset, DECIMAL_CTX_ROUND_UP)


def _to_quantums_helper(human_amount, asset, ctx):
    try:
        amount_dec = ctx.create_decimal(human_amount)
        resolution_dec = ctx.create_decimal(ASSET_RESOLUTION[asset])
        quantums = (amount_dec * resolution_dec).to_integral_exact(context=ctx)
    except decimal.Inexact:
        raise ValueError(
            'Amount {} is not a multiple of the quantum size {}'.format(
                human_amount,
                1 / float(ASSET_RESOLUTION[asset]),
            ),
        )
    return int(quantums)


def nonce_from_client_id(client_id):
    """Generate a nonce deterministically from an arbitrary string."""
    message = hashlib.sha256()
    message.update(client_id.encode())  # Encode as UTF-8.
    return int(message.digest().hex(), 16) % NONCE_UPPER_BOUND_EXCLUSIVE


def get_transfer_erc20_fact(
    recipient,
    token_decimals,
    human_amount,
    token_address,
    salt,
):
    token_amount = float(human_amount) * (10 ** token_decimals)
    if not token_amount.is_integer():
        raise ValueError(
            'Amount {} has more precision than token decimals {}'.format(
                human_amount,
                token_decimals,
            )
        )
    hex_bytes = Web3.solidityKeccak(
        [
            'address',
            'uint256',
            'address',
            'uint256',
        ],
        [
            recipient,
            int(token_amount),
            token_address,
            salt,
        ],
    )
    return bytes(hex_bytes)


def fact_to_condition(fact_registry_address, fact):
    """Generate the condition, signed as part of a conditional transfer."""
    if not isinstance(fact, bytes):
        raise ValueError('fact must be a byte-string')
    data = bytes.fromhex(strip_hex_prefix(fact_registry_address)) + fact
    return int(Web3.keccak(data).hex(), 16) & BIT_MASK_250


def message_to_hash(message_string):
    """Generate a hash deterministically from an arbitrary string."""
    message = hashlib.sha256()
    message.update(message_string.encode())  # Encode as UTF-8.
    return int(message.digest().hex(), 16) >> 5


def generate_private_key_hex_unsafe():
    """Generate a STARK key using the Python builtin random module."""
    return hex(get_random_private_key())


def private_key_from_bytes(data):
    """Generate a STARK key deterministically from binary data."""
    if not isinstance(data, bytes):
        raise ValueError('Input must be a byte-string')
    return hex(int(Web3.keccak(data).hex(), 16) >> 5)


def private_key_to_public_hex(private_key_hex):
    """Given private key as hex string, return the public key as hex string."""
    private_key_int = int(private_key_hex, 16)
    return hex(private_to_stark_key(private_key_int))


def private_key_to_public_key_pair_hex(private_key_hex):
    """Given private key as hex string, return the public x, y pair as hex."""
    private_key_int = int(private_key_hex, 16)
    x, y = private_key_to_ec_point_on_stark_curve(private_key_int)
    return [hex(x), hex(y)]
