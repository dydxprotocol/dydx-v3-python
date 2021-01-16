from dydx3.eth_signing import SignOnboardingAction
from dydx3.helpers.requests import request


class Onboarding(object):

    def __init__(
        self,
        host,
        eth_signer,
        network_id,
        default_address,
        stark_public_key,
        api_public_key,
    ):
        self.host = host
        self.default_address = default_address
        self.stark_public_key = stark_public_key
        self.api_public_key = api_public_key

        self.signer = SignOnboardingAction(eth_signer, network_id)

    # ============ Request Helpers ============

    def _post(
        self,
        endpoint,
        data,
        opt_ethereum_address,
    ):
        ethereum_address = opt_ethereum_address or self.default_address

        signature = self.signer.sign(ethereum_address)

        request_path = '/'.join(['/v3', endpoint])
        return request(
            self.host + request_path,
            'post',
            {
                'DYDX-SIGNATURE': signature,
                'DYDX-ETHEREUM-ADDRESS': ethereum_address,
            },
            data,
        )

    # ============ Requests ============

    def create_user(
        self,
        stark_public_key=None,
        api_public_key=None,
        ethereum_address=None,
    ):
        '''
        Onboard a user with an Ethereum address, STARK key, and API key.

        By default, onboards using the STARK and/or API public keys
        corresponding to private keys that the client was initialized with.

        :param stark_public_key: optional
        :type stark_public_key: str

        :param api_public_key: optional
        :type api_public_key: str

        :param ethereum_address: optional
        :type ethereum_address: str

        :returns: { apiKey, user, account }

        :raises: DydxAPIError
        '''
        stark_key = stark_public_key or self.stark_public_key
        if stark_key is None:
            raise ValueError('No STARK private or public key provided')
        api_key = api_public_key or self.api_public_key
        if api_key is None:
            raise ValueError('No API private or public key provided')
        return self._post(
            'onboarding',
            {
                'starkKey': stark_key,
                'apiKey': api_key,
            },
            ethereum_address,
        )
