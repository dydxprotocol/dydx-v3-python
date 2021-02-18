from dydx3.helpers.request_helpers import iso_to_epoch_seconds
from dydx3.starkex.withdrawal import SignableWithdrawal

MOCK_PUBLIC_KEY = (
    '3b865a18323b8d147a12c556bfb1d502516c325b1477a23ba6c77af31f020fd'
)
MOCK_PRIVATE_KEY = (
    '58c7d5a90b1776bde86ebac077e053ed85b0f7164f53b080304a531947f46e3'
)
MOCK_SIGNATURE = (
    '05e48c33f8205a5359c95f1bd7385c1c1f587e338a514298c07634c0b6c952ba' +
    '0687d6980502a5d7fa84ef6fdc00104db22c43c7fb83e88ca84f19faa9ee3de1'
)

# Mock withdrawal params.
WITHDRAWAL_PARAMS = {
    "network_id": 3,
    "position_id": 12345,
    "human_amount": '49.478023',
    "client_id": (
        'This is an ID that the client came up with ' +
        'to describe this withdrawal'
    ),
    "expiration_epoch_seconds": iso_to_epoch_seconds(
        '2020-09-17T04:15:55.028Z',
    ),
}


class TestWithdrawal():

    def test_sign_withdrawal(self):
        withdrawal = SignableWithdrawal(**WITHDRAWAL_PARAMS)
        signature = withdrawal.sign(MOCK_PRIVATE_KEY)
        assert signature == MOCK_SIGNATURE

    def test_verify_signature(self):
        withdrawal = SignableWithdrawal(**WITHDRAWAL_PARAMS)
        assert withdrawal.verify_signature(MOCK_SIGNATURE, MOCK_PUBLIC_KEY)

    def test_starkware_representation(self):
        withdrawal = SignableWithdrawal(**WITHDRAWAL_PARAMS)
        starkware_withdrawal = withdrawal.to_starkware()
        assert starkware_withdrawal.quantums_amount == 49478023

        # Order expiration should be rounded up and should have a buffer added.
        assert starkware_withdrawal.expiration_epoch_hours == 444533
