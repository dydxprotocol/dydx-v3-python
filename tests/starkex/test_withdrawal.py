from dydx3.starkex.withdrawal import SignableWithdrawal

MOCK_PUBLIC_KEY = (
    '3b865a18323b8d147a12c556bfb1d502516c325b1477a23ba6c77af31f020fd'
)
MOCK_PRIVATE_KEY = (
    '58c7d5a90b1776bde86ebac077e053ed85b0f7164f53b080304a531947f46e3'
)
MOCK_SIGNATURE = (
    '033cb5733344f13b8527711e651ade3dd3ed61d0c700085c2d6e13a31fb7e748' +
    '0088291b597390d15920576de379cf6d64a0f8ee08b2e61a5abf3b3fcfe563a0'
)

# Mock withdrawal params.
WITHDRAWAL_PARAMS = {
    "position_id": 12345,
    "human_amount": '49.478023',
    "client_id": (
        'This is an ID that the client came up with ' +
        'to describe this withdrawal'
    ),
    "expiration_epoch_seconds": 1600316155,
}


class TestWithdrawal():

    def test_sign_withdrawal(self):
        withdrawal = SignableWithdrawal(**WITHDRAWAL_PARAMS)
        signature = withdrawal.sign(MOCK_PRIVATE_KEY)
        assert signature == MOCK_SIGNATURE

    def test_verify_signature(self):
        withdrawal = SignableWithdrawal(**WITHDRAWAL_PARAMS)
        assert withdrawal.verify_signature(MOCK_SIGNATURE, MOCK_PUBLIC_KEY)
