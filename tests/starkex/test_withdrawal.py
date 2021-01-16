from dydx3.helpers.request_helpers import iso_to_epoch_seconds
from dydx3.starkex.withdrawal import SignableWithdrawal

MOCK_PUBLIC_KEY = (
    '3b865a18323b8d147a12c556bfb1d502516c325b1477a23ba6c77af31f020fd'
)
MOCK_PRIVATE_KEY = (
    '58c7d5a90b1776bde86ebac077e053ed85b0f7164f53b080304a531947f46e3'
)
MOCK_SIGNATURE = (
    '0214a0ab2f3c065c5848ad9dbac6cc98509b66e76a8f563d5c8ffda01b0fa2e0' +
    '07242b1c65d039fe645d122ecea7c3e58c8fda5814e0c152dbdeef4af706ad06'
)

# Mock withdrawal params.
WITHDRAWAL_PARAMS = {
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
