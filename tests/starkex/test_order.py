from dydx3.constants import MARKET_ETH_USD
from dydx3.constants import ORDER_SIDE_BUY
from dydx3.helpers.request_helpers import iso_to_epoch_seconds
from dydx3.starkex.order import SignableOrder

# Test data where the public key y-coordinate is odd.
MOCK_PUBLIC_KEY = (
    '3b865a18323b8d147a12c556bfb1d502516c325b1477a23ba6c77af31f020fd'
)
MOCK_PRIVATE_KEY = (
    '58c7d5a90b1776bde86ebac077e053ed85b0f7164f53b080304a531947f46e3'
)
MOCK_SIGNATURE = (
    '059487ea7c537f34516f4dc7c54ad30ab0096823269ba18aea0e64e13fb03462' +
    '03be73ed4dafbf99baeeaee6dce315cd834b5e3257d4e74371d14cf8f2189a59'
)

# Test data where the public key y-coordinate is even.
MOCK_PUBLIC_KEY_EVEN_Y = (
    '5c749cd4c44bdc730bc90af9bfbdede9deb2c1c96c05806ce1bc1cb4fed64f7'
)
MOCK_SIGNATURE_EVEN_Y = (
    '030644ef5b2de9e93f13df5a4cf8284e7256223366b5da29bf2002ed40825171' +
    '03961ec47c34c49e97095c546895cc22afa6e563474615729720fd8b768c5b87'
)

# Mock order params.
ORDER_PARAMS = {
    "market": MARKET_ETH_USD,
    "side": ORDER_SIDE_BUY,
    "position_id": 12345,
    "human_size": '145.0005',
    "human_price": '350.00067',
    "limit_fee": '0.125',
    "client_id": (
        'This is an ID that the client came up with ' +
        'to describe this order'
    ),
    "expiration_epoch_seconds": iso_to_epoch_seconds(
        '2020-09-17T04:15:55.028Z',
    ),
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

    def test_starkware_amounts(self):
        order = SignableOrder(**ORDER_PARAMS)
        starkware_order = order.to_starkware()
        assert starkware_order.quantums_amount_synthetic == 14500050000
        assert starkware_order.quantums_amount_collateral == 50750272151
        assert starkware_order.quantums_amount_fee == 6343784019

    def test_convert_order_fee_edge_case(self):
        order = SignableOrder(
            **dict(
                ORDER_PARAMS,
                limit_fee='0.000001999999999999999999999999999999999999999999',
            ),
        )
        starkware_order = order.to_starkware()
        assert starkware_order.quantums_amount_fee == 50751
