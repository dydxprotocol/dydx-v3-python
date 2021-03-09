import ctypes
import secrets
import os
from typing import Optional, Tuple
import json
import math
from dydx3.starkex.starkex_resources.python_signature import (
    inv_mod_curve_size,
)

PEDERSEN_HASH_POINT_FILENAME = os.path.join(
    os.path.dirname(__file__), 'pedersen_params.json')
PEDERSEN_PARAMS = json.load(open(PEDERSEN_HASH_POINT_FILENAME))

EC_ORDER = PEDERSEN_PARAMS['EC_ORDER']

FIELD_PRIME = PEDERSEN_PARAMS['FIELD_PRIME']

N_ELEMENT_BITS_ECDSA = math.floor(math.log(FIELD_PRIME, 2))
assert N_ELEMENT_BITS_ECDSA == 251


CPP_LIB_PATH = None
OUT_BUFFER_SIZE = 251

def get_cpp_lib(crypto_c_exports_path):
    global CPP_LIB_PATH
    CPP_LIB_PATH = ctypes.cdll.LoadLibrary(os.path.abspath(crypto_c_exports_path))
    # Configure argument and return types.
    CPP_LIB_PATH.Hash.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    CPP_LIB_PATH.Verify.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    CPP_LIB_PATH.Verify.restype = bool
    CPP_LIB_PATH.Sign.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]

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
    res = ctypes.create_string_buffer(OUT_BUFFER_SIZE)
    if CPP_LIB_PATH.Hash(
            left.to_bytes(32, 'little', signed=False),
            right.to_bytes(32, 'little', signed=False),
            res) != 0:
        raise ValueError(res.raw.rstrip(b'\00'))
    return int.from_bytes(res.raw[:32], 'little', signed=False)


def cpp_sign(msg_hash, priv_key, seed: Optional[int] = 32) -> ECSignature:
    """
    Note that this uses the secrets module to generate cryptographically strong random numbers.
    Note that the same seed will give a different signature compared with the sign function in
    signature.py.
    """
    res = ctypes.create_string_buffer(OUT_BUFFER_SIZE)
    random_bytes = secrets.token_bytes(seed)
    if CPP_LIB_PATH.Sign(
            priv_key.to_bytes(32, 'little', signed=False),
            msg_hash.to_bytes(32, 'little', signed=False),
            random_bytes, res) != 0:
        raise ValueError(res.raw.rstrip(b'\00'))
    w = int.from_bytes(res.raw[32:64], 'little', signed=False)
    s = inv_mod_curve_size(w)
    return (int.from_bytes(res.raw[:32], 'little', signed=False), s)


def cpp_verify(msg_hash, r, s, stark_key) -> bool:
    w =inv_mod_curve_size(s)
    assert 1 <= stark_key < 2**N_ELEMENT_BITS_ECDSA, 'stark_key = %s' % stark_key
    assert 1 <= msg_hash < 2**N_ELEMENT_BITS_ECDSA, 'msg_hash = %s' % msg_hash
    assert 1 <= r < 2**N_ELEMENT_BITS_ECDSA, 'r = %s' % r
    assert 1 <= w < EC_ORDER, 'w = %s' % w
    return CPP_LIB_PATH.Verify(
        stark_key.to_bytes(32, 'little', signed=False),
        msg_hash.to_bytes(32, 'little', signed=False),
        r.to_bytes(32, 'little', signed=False),
        w.to_bytes(32, 'little', signed=False))
