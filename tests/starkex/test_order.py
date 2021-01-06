from dydx3.constants import MARKET_ETH_USD
from dydx3.constants import ORDER_SIDE_BUY
from dydx3.starkex.order import SignableOrder

# Test data where the public key y-coordinate is odd.
MOCK_PUBLIC_KEY = (
    '3b865a18323b8d147a12c556bfb1d502516c325b1477a23ba6c77af31f020fd'
)
MOCK_PRIVATE_KEY = (
    '58c7d5a90b1776bde86ebac077e053ed85b0f7164f53b080304a531947f46e3'
)
MOCK_SIGNATURE = (
    '073b286b35acfdee9d3c5e7b07fc1392d53a0fae2f960c9cf4e66b5cac0b8de5' +
    '04c26bdadd93668d82668e3e3dd4e603093f4bfefb4e3570249024d074dbf182'
)

# Test data where the public key y-coordinate is even.
MOCK_PUBLIC_KEY_EVEN_Y = (
    '5c749cd4c44bdc730bc90af9bfbdede9deb2c1c96c05806ce1bc1cb4fed64f7'
)
MOCK_SIGNATURE_EVEN_Y = (
    '032ec9c1a22f939a16bf729402a376fda3420d24a8f93b886b1f1664f10ec4de' +
    '0532951bcb4f733ebb17e44d3fc368f4bd441dc74a2757f79531708165730333'
)

# Mock order params.
ORDER_PARAMS = {
    "market": MARKET_ETH_USD,
    "side": ORDER_SIDE_BUY,
    "position_id": 12345,
    "human_size": '145.0005',
    "human_price": '350.00067',
    "human_limit_fee": '0.032985',
    "client_id": (
        'This is an ID that the client came up with ' +
        'to describe this order'
    ),
    "expiration_epoch_seconds": 1600316155,
}


class TestOrder():

    def test_sign_order(self):
        order = SignableOrder(**ORDER_PARAMS)
        signature = order.sign(MOCK_PRIVATE_KEY)
        assert signature == MOCK_SIGNATURE

    def test_verify_signature_odd_y(self):
        order = SignableOrder(**ORDER_PARAMS)
        assert order.verify_signature(MOCK_SIGNATURE, MOCK_PUBLIC_KEY)

    def test_verify_signature_even_y(self):
        order = SignableOrder(**ORDER_PARAMS)
        assert order.verify_signature(
            MOCK_SIGNATURE_EVEN_Y,
            MOCK_PUBLIC_KEY_EVEN_Y,
        )
