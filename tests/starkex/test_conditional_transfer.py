from dydx3.helpers.request_helpers import iso_to_epoch_seconds
from dydx3.starkex.conditional_transfer import SignableConditionalTransfer

MOCK_PUBLIC_KEY = (
    '3b865a18323b8d147a12c556bfb1d502516c325b1477a23ba6c77af31f020fd'
)
MOCK_PRIVATE_KEY = (
    '58c7d5a90b1776bde86ebac077e053ed85b0f7164f53b080304a531947f46e3'
)
MOCK_SIGNATURE = (
    '067e90143a21d8a6aca85207de5e124e9644f7adc18deb42c5cf1240766e57bb' +
    '04a39c4fdadf214d7282a59d37b21e0d3ea7fe1fc0d0ee25c22a3dd9d5cb8307'
)

# Mock conditional transfer params.
CONDITIONAL_TRANSFER_PARAMS = {
    'sender_position_id': 12345,
    'receiver_position_id': 67890,
    'receiver_public_key': (
        '05135ef87716b0faecec3ba672d145a6daad0aa46437c365d490022115aba674'
    ),
    'condition': b'mock-condition',
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
