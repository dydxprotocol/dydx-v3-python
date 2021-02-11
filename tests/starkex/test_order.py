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
    '00cecbe513ecdbf782cd02b2a5efb03e58d5f63d15f2b840e9bc0029af04e8dd' +
    '0090b822b16f50b2120e4ea9852b340f7936ff6069d02acca02f2ed03029ace5'
)

# Test data where the public key y-coordinate is even.
MOCK_PUBLIC_KEY_EVEN_Y = (
    '5c749cd4c44bdc730bc90af9bfbdede9deb2c1c96c05806ce1bc1cb4fed64f7'
)
MOCK_SIGNATURE_EVEN_Y = (
    '00fc0756522d78bef51f70e3981dc4d1e82273f59cdac6bc31c5776baabae6ec' +
    '0158963bfd45d88a99fb2d6d72c9bbcf90b24c3c0ef2394ad8d05f9d3983443a'
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

    def test_starkware_representation(self):
        order = SignableOrder(**ORDER_PARAMS)
        starkware_order = order.to_starkware()
        assert starkware_order.quantums_amount_synthetic == 145000500000
        assert starkware_order.quantums_amount_collateral == 50750272151
        assert starkware_order.quantums_amount_fee == 6343784019

        # Order expiration should be rounded up and should have a buffer added.
        assert starkware_order.expiration_epoch_hours == 444701

    def test_convert_order_fee_edge_case(self):
        order = SignableOrder(
            **dict(
                ORDER_PARAMS,
                limit_fee='0.000001999999999999999999999999999999999999999999',
            ),
        )
        starkware_order = order.to_starkware()
        assert starkware_order.quantums_amount_fee == 50751
