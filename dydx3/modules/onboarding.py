from web3 import Web3

from dydx3.constants import OFF_CHAIN_ONBOARDING_ACTION
from dydx3.constants import OFF_CHAIN_KEY_DERIVATION_ACTION
from dydx3.eth_signing import SignOnboardingAction
from dydx3.helpers.requests import request


class Onboarding(object):

    def __init__(
        self,
        host,
        eth_signer,
        network_id,
        default_address,
        stark_public_key=None,
        stark_public_key_y_coordinate=None,
    ):
        self.host = host
        self.default_address = default_address
        self.stark_public_key = stark_public_key
        self.stark_public_key_y_coordinate = stark_public_key_y_coordinate

        self.signer = SignOnboardingAction(eth_signer, network_id)

    # ============ Request Helpers ============

    def _post(
        self,
        endpoint,
        data,
        opt_ethereum_address,
    ):
        ethereum_address = opt_ethereum_address or self.default_address

        signature = self.signer.sign(
            ethereum_address,
            action=OFF_CHAIN_ONBOARDING_ACTION,
        )

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
        stark_public_key_y_coordinate=None,
        ethereum_address=None,
    ):
        '''
        Onboard a user with an Ethereum address and STARK key.

        By default, onboards using the STARK and/or API public keys
        corresponding to private keys that the client was initialized with.

        :param stark_public_key: optional
        :type stark_public_key: str

        :param stark_public_key_y_coordinate: optional
        :type stark_public_key_y_coordinate: str

        :param ethereum_address: optional
        :type ethereum_address: str

        :returns: { apiKey, user, account }

        :raises: DydxAPIError
        '''
        stark_key = stark_public_key or self.stark_public_key
        stark_key_y = (
            stark_public_key_y_coordinate or self.stark_public_key_y_coordinate
        )
        if stark_key is None:
            raise ValueError(
                'STARK private key or public key is required'
            )
        if stark_key is None:
            raise ValueError(
                'STARK private key or public key y-coordinate is required'
            )
        return self._post(
            'onboarding',
            {
                'starkKey': stark_key,
                'starkKeyYCoordinate': stark_key_y,
            },
            ethereum_address,
        )

    # ============ Key Derivation ============

    def derive_stark_key(
        self,
        ethereum_address,
    ):
        '''
        Derive a STARK key pair deterministically from an Ethereum key.

        This is the function used by the dYdX frontend to derive a user's
        STARK key pair in a way that is recoverable. Programmatic traders may
        optionally derive their STARK key pair in the same way.

        :param ethereum_address: optional
        :type ethereum_address: str
        '''
        signature = self.signer.sign(
            ethereum_address or self.default_address,
            action=OFF_CHAIN_KEY_DERIVATION_ACTION,
        )
        signature_int = int(signature, 16)
        hashed_signature = Web3.solidityKeccak(['uint256'], [signature_int])
        private_key_int = int(hashed_signature.hex(), 16) >> 5
        return hex(private_key_int)
