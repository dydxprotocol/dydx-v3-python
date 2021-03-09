from dydx3.starkex.starkex_resources.cpp_signature import (
  check_cpp_lib_path, cpp_hash, cpp_sign, cpp_verify
)
from dydx3.starkex.starkex_resources.python_signature import (
  py_sign, ECSignature, ECPoint, py_verify, py_pedersen_hash
)
from typing import Optional, Union

def sign(msg_hash: int, priv_key: int, seed: Optional[int] = None) -> ECSignature:
  if check_cpp_lib_path():
    return cpp_sign(msg_hash=msg_hash, priv_key=priv_key, seed=seed)

  return py_sign(msg_hash=msg_hash, priv_key=priv_key, seed=seed)

def verify(msg_hash: int, r: int, s: int, public_key: Union[int, ECPoint]) -> bool:
  if check_cpp_lib_path():
    return cpp_verify(msg_hash=msg_hash, r=r, s=s, stark_key=public_key)

  return py_verify(msg_hash=msg_hash, r=r, s=s, public_key=public_key)

def get_hash(*elements: int) -> int:
  if check_cpp_lib_path():
    return cpp_hash(*elements)

  return py_pedersen_hash(*elements)
