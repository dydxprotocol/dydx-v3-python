from typing import Optional, Union

from dydx3.starkex.starkex_resources.cpp_signature import check_cpp_lib_path
from dydx3.starkex.starkex_resources.cpp_signature import cpp_hash
from dydx3.starkex.starkex_resources.cpp_signature import cpp_verify
from dydx3.starkex.starkex_resources.python_signature import ECPoint
from dydx3.starkex.starkex_resources.python_signature import ECSignature
from dydx3.starkex.starkex_resources.python_signature import py_pedersen_hash
from dydx3.starkex.starkex_resources.python_signature import py_sign
from dydx3.starkex.starkex_resources.python_signature import py_verify


def sign(
    msg_hash: int,
    priv_key: int,
    seed: Optional[int] = None,
) -> ECSignature:
    # Note: cpp_sign() is not optimized and is currently slower than py_sign().
    #       So always use py_sign() for now.
    return py_sign(msg_hash=msg_hash, priv_key=priv_key, seed=seed)


def verify(
    msg_hash: int,
    r: int,
    s: int,
    public_key: Union[int, ECPoint],
) -> bool:
    if check_cpp_lib_path():
        return cpp_verify(msg_hash=msg_hash, r=r, s=s, stark_key=public_key)

    return py_verify(msg_hash=msg_hash, r=r, s=s, public_key=public_key)


def get_hash(*elements: int) -> int:
    if check_cpp_lib_path():
        return cpp_hash(*elements)

    return py_pedersen_hash(*elements)
