from dydx3.starkex.api_request import SignableApiRequest

MOCK_PUBLIC_KEY = (
    '3b865a18323b8d147a12c556bfb1d502516c325b1477a23ba6c77af31f020fd'
)
MOCK_PRIVATE_KEY = (
    '58c7d5a90b1776bde86ebac077e053ed85b0f7164f53b080304a531947f46e3'
)
MOCK_SIGNATURE = (
    '05191fb93fc14a948a4185ccd4b78a3ef423426da2362f0bb9adb91977be1a9a' +
    '050d8fbaa17b429a70df6d4c938058e848b96496a00c8878f8e7a7f88037240b'
)


class TestApiRequest():

    def test_sign_api_request(self):
        api_request = SignableApiRequest(
            iso_timestamp='2020-10-19T20:31:20.000Z',
            method='GET',
            body='',
            request_path='/v3/users',
        )
        signature = api_request.sign(MOCK_PRIVATE_KEY)
        assert signature == MOCK_SIGNATURE
