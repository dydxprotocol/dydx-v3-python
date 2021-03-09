import ctypes
import json
import math
import os
import secrets
from typing import Optional, Tuple

from dydx3.starkex.starkex_resources.python_signature import (
    inv_mod_curve_size,
)

# Get STARK curve parameters.
PEDERSEN_HASH_POINT_FILENAME = os.path.join(
    os.path.dirname(__file__),
    'pedersen_params.json',
)
PEDERSEN_PARAMS = json.load(open(PEDERSEN_HASH_POINT_FILENAME))
EC_ORDER = PEDERSEN_PARAMS['EC_ORDER']
FIELD_PRIME = PEDERSEN_PARAMS['FIELD_PRIME']
N_ELEMENT_BITS_ECDSA = math.floor(math.log(FIELD_PRIME, 2))
assert N_ELEMENT_BITS_ECDSA == 251

OUTPUT_BUFFER_SIZE = 251

# Global variable for the loaded path to the C++ shared library.
CPP_LIB_PATH = None


def get_cpp_lib(crypto_c_exports_path):
    global CPP_LIB_PATH
    CPP_LIB_PATH = ctypes.cdll.LoadLibrary(
        os.path.abspath(crypto_c_exports_path),
    )
    # Configure argument and return types.
    CPP_LIB_PATH.Hash.argtypes = [ctypes.c_void_p for _ in range(3)]
    CPP_LIB_PATH.Verify.argtypes = [ctypes.c_void_p for _ in range(4)]
    CPP_LIB_PATH.Verify.restype = bool
    CPP_LIB_PATH.Sign.argtypes = [ctypes.c_void_p for _ in range(4)]


def check_cpp_lib_path() -> bool:
    return CPP_LIB_PATH is not None


#########
# ECDSA #
#########

# A type for the digital signature.
ECSignature = Tuple[int, int]


#################
# CPP WRAPPERS #
#################

def cpp_hash(left, right) -> int:
    res = ctypes.create_string_buffer(OUTPUT_BUFFER_SIZE)
    if CPP_LIB_PATH.Hash(
        int_to_bytes(left),
        int_to_bytes(right),
        res,
    ) != 0:
        raise ValueError(res.raw.rstrip(b'\00'))
    return bytes_to_int(res.raw[:32])


def cpp_sign(msg_hash, priv_key, seed: Optional[int] = 32) -> ECSignature:
    """
    Note that this uses the secrets module to generate cryptographically strong
    random numbers. Also note that the same seed will produce a different
    signature compared with the sign function in python_signature.py.
    """
    res = ctypes.create_string_buffer(OUTPUT_BUFFER_SIZE)
    random_bytes = secrets.token_bytes(seed)
    if CPP_LIB_PATH.Sign(
        int_to_bytes(priv_key),
        int_to_bytes(msg_hash),
        random_bytes,
        res,
    ) != 0:
        raise ValueError(res.raw.rstrip(b'\00'))
    r = bytes_to_int(res.raw[:32])
    w = bytes_to_int(res.raw[32:64])
    s = inv_mod_curve_size(w)
    return r, s


def cpp_verify(msg_hash, r, s, stark_key) -> bool:
    w = inv_mod_curve_size(s)
    if not (1 <= stark_key < 2 ** N_ELEMENT_BITS_ECDSA):
        raise ValueError('stark_key = {}'.format(stark_key))
    if not (1 <= msg_hash < 2 ** N_ELEMENT_BITS_ECDSA):
        raise ValueError('msg_hash = {}'.format(msg_hash))
    if not (1 <= r < 2 ** N_ELEMENT_BITS_ECDSA):
        raise ValueError('r = {}'.format(r))
    if not (1 <= w < EC_ORDER):
        raise ValueError('w = {}'.format(w))
    return CPP_LIB_PATH.Verify(
        int_to_bytes(stark_key),
        int_to_bytes(msg_hash),
        int_to_bytes(r),
        int_to_bytes(w),
    )

###########
# HELPERS #
###########


def int_to_bytes(x):
    return x.to_bytes(32, 'little', signed=False),


def bytes_to_int(b):
    return int.from_bytes(b, 'little', signed=False)
