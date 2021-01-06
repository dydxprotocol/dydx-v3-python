from dydx3.starkex.helpers import deserialize_signature
from dydx3.starkex.helpers import serialize_signature
from dydx3.starkex.starkex_resources.signature import sign
from dydx3.starkex.starkex_resources.signature import verify


class Signable(object):
    """Base class for an object signable with a STARK key."""

    def __init__(self, message):
        self._message = message
        self._hash = None

    @property
    def hash(self):
        """Get the hash of the object."""
        if self._hash is None:
            self._hash = self._calculate_hash()
        return self._hash

    def sign(self, private_key_hex):
        """Sign the hash of the object using the given private key."""
        r, s = sign(self.hash, int(private_key_hex, 16))
        return serialize_signature(r, s)

    def verify_signature(self, signature_hex, public_key_hex):
        """Return True if the signature is valid for the given public key."""
        r, s = deserialize_signature(signature_hex)
        return verify(self.hash, r, s, int(public_key_hex, 16))

    def _calculate_hash(self):
        raise NotImplementedError
