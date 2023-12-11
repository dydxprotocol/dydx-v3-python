from dydx3.constants import NETWORK_ID_SEPOLIA
from dydx3.helpers.request_helpers import iso_to_epoch_seconds
from dydx3.starkex.transfer import SignableTransfer

MOCK_PUBLIC_KEY = (
    '3b865a18323b8d147a12c556bfb1d502516c325b1477a23ba6c77af31f020fd'
)
MOCK_PRIVATE_KEY = (
    '58c7d5a90b1776bde86ebac077e053ed85b0f7164f53b080304a531947f46e3'
)
MOCK_SIGNATURE = (
    '02b4d393ea955be0f53029e2f8a10d31671eb9d3ada015d973c903417264688a' +
    '02ffb6b7f29870208f1f860b125de95b5444142a867be9dcd80128999518ddd3'
)

# Mock transfer params.
TRANSFER_PARAMS = {
    'sender_position_id': 12345,
    'receiver_position_id': 67890,
    'receiver_public_key': (
        '05135ef87716b0faecec3ba672d145a6daad0aa46437c365d490022115aba674'
    ),
    'human_amount': '49.478023',
    'expiration_epoch_seconds': iso_to_epoch_seconds(
        '2020-09-17T04:15:55.028Z',
    ),
    'client_id': (
        'This is an ID that the client came up with to describe this transfer'
    ),
}


class TestTransfer():

    def test_sign_transfer(self):
        transfer = SignableTransfer(
            **TRANSFER_PARAMS, network_id=NETWORK_ID_SEPOLIA)
        signature = transfer.sign(MOCK_PRIVATE_KEY)
        assert signature == MOCK_SIGNATURE

    def test_sign_transfer_different_client_id(self):
        alternative_transfer_params = {**TRANSFER_PARAMS}
        alternative_transfer_params['client_id'] += '!'

        transfer = SignableTransfer(
            **alternative_transfer_params,
            network_id=NETWORK_ID_SEPOLIA
        )
        signature = transfer.sign(MOCK_PRIVATE_KEY)
        assert signature != MOCK_SIGNATURE

    def test_sign_transfer_different_receiver_position_id(self):
        alternative_transfer_params = {**TRANSFER_PARAMS}
        alternative_transfer_params['receiver_position_id'] += 1

        transfer = SignableTransfer(
            **alternative_transfer_params,
            network_id=NETWORK_ID_SEPOLIA
        )
        signature = transfer.sign(MOCK_PRIVATE_KEY)
        assert signature != MOCK_SIGNATURE

    def test_verify_signature(self):
        transfer = SignableTransfer(
            **TRANSFER_PARAMS, network_id=NETWORK_ID_SEPOLIA)
        assert transfer.verify_signature(MOCK_SIGNATURE, MOCK_PUBLIC_KEY)

    def test_starkware_representation(self):
        transfer = SignableTransfer(
            **TRANSFER_PARAMS, network_id=NETWORK_ID_SEPOLIA)
        starkware_transfer = transfer.to_starkware()
        assert starkware_transfer.quantums_amount == 49478023

        # Order expiration should be rounded up and should have a buffer added.
        assert starkware_transfer.expiration_epoch_hours == 444533
