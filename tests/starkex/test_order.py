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
    '01ac25fb542c7f58953cbbaec0bd774e480d6e22d7c7145f531986c32ce28e09' +
    '0038738abd1a7a960a45376c926fc7e41889d0f365c8749a80306e355dcf78ec'
)

# Test data where the public key y-coordinate is even.
MOCK_PUBLIC_KEY_EVEN_Y = (
    '5c749cd4c44bdc730bc90af9bfbdede9deb2c1c96c05806ce1bc1cb4fed64f7'
)
MOCK_SIGNATURE_EVEN_Y = (
    '05de75d37686126262e31560aca7e3e3782210d1ed5395b8c8704b1a51831a7a' +
    '01427d9b50773cd537e357c969aeb8dc24e23365418b641a11b5902d1140b8de'
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
