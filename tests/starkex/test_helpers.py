from dydx3.starkex.helpers import generate_private_key_hex_unsafe
from dydx3.starkex.helpers import nonce_from_client_id
from dydx3.starkex.helpers import private_key_from_bytes
from dydx3.starkex.helpers import private_key_to_public_hex


class TestHelpers():

    def test_nonce_from_client_id(self):
        assert nonce_from_client_id('') == 2018687061
        assert nonce_from_client_id('1') == 3079101259
        assert nonce_from_client_id('a') == 2951628987
        assert nonce_from_client_id(
            'A really long client ID used to identify an order or withdrawal',
        ) == 2913863714
        assert nonce_from_client_id(
            'A really long client ID used to identify an order or withdrawal!',
        ) == 230317226

    def test_generate_private_key_hex_unsafe(self):
        assert (
            generate_private_key_hex_unsafe() !=
            generate_private_key_hex_unsafe()
        )

    def test_private_key_from_bytes(self):
        assert (
            private_key_from_bytes(b'0') ==
            '0x2242959533856f2a03f3c7d9431e28ef4fe5cb2a15038c37f1d76d35dc508b'
        )
        assert (
            private_key_from_bytes(b'a') ==
            '0x1d61128b46faa109512e0e00fe9adf5ff52047ed61718eeeb7c0525dfcd2f8e'
        )
        assert (
            private_key_from_bytes(
                b'really long input data for key generation with the '
                b'keyPairFromData() function'
            ) ==
            '0x7c4946831bde597b73f1d5721af9c67731eafeb75c1b8e92ac457a61819a29'
        )

    def test_private_key_to_public_hex(self):
        assert private_key_to_public_hex(
            '0x2242959533856f2a03f3c7d9431e28ef4fe5cb2a15038c37f1d76d35dc508b',
        ) == (
            '0x69a33d37101d7089b606f92e4b41553c237a474ad9d6f62eeb6708415f98f4d'
        )
