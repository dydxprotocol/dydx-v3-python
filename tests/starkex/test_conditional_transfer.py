from dydx3.constants import NETWORK_ID_ROPSTEN
from dydx3.helpers.request_helpers import iso_to_epoch_seconds
from dydx3.starkex.conditional_transfer import SignableConditionalTransfer

MOCK_PUBLIC_KEY = (
    '3b865a18323b8d147a12c556bfb1d502516c325b1477a23ba6c77af31f020fd'
)
MOCK_PRIVATE_KEY = (
    '58c7d5a90b1776bde86ebac077e053ed85b0f7164f53b080304a531947f46e3'
)
MOCK_SIGNATURE = (
    '04814c5d3501863134108802cab5d12df4b959654332103b837252549d24e9a6' +
    '06bc01225e9f1690b08b63de2a3b179fb2927d4564b3440bbb0da4c37caf597e'
)

# Mock conditional transfer params.
CONDITIONAL_TRANSFER_PARAMS = {
    "network_id": NETWORK_ID_ROPSTEN,
    'sender_position_id': 12345,
    'receiver_position_id': 67890,
    'receiver_public_key': (
        '05135ef87716b0faecec3ba672d145a6daad0aa46437c365d490022115aba674'
    ),
    'fact_registry_address': '0x12aa12aa12aa12aa12aa12aa12aa12aa12aa12aa',
    'fact': bytes.fromhex(
        '12ff12ff12ff12ff12ff12ff12ff12ff12ff12ff12ff12ff12ff12ff12ff12ff'
    ),
    'human_amount': '49.478023',
    'expiration_epoch_seconds': iso_to_epoch_seconds(
        '2020-09-17T04:15:55.028Z',
    ),
    'client_id': (
        'This is an ID that the client came up with to describe this transfer'
    ),
}


class TestConditionalTransfer():

    def test_sign_conditional_transfer(self):
        transfer = SignableConditionalTransfer(**CONDITIONAL_TRANSFER_PARAMS)
        signature = transfer.sign(MOCK_PRIVATE_KEY)
        assert signature == MOCK_SIGNATURE

    def test_verify_signature(self):
        transfer = SignableConditionalTransfer(**CONDITIONAL_TRANSFER_PARAMS)
        assert transfer.verify_signature(MOCK_SIGNATURE, MOCK_PUBLIC_KEY)

    def test_starkware_representation(self):
        transfer = SignableConditionalTransfer(**CONDITIONAL_TRANSFER_PARAMS)
        starkware_transfer = transfer.to_starkware()
        assert starkware_transfer.quantums_amount == 49478023

        # Order expiration should be rounded up and should have a buffer added.
        assert starkware_transfer.expiration_epoch_hours == 444533
