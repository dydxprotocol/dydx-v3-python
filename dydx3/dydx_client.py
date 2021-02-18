from web3 import Web3

from dydx3.eth_signing import SignWithWeb3
from dydx3.eth_signing import SignWithKey
from dydx3.modules.api_keys import ApiKeys
from dydx3.modules.eth import Eth
from dydx3.modules.private import Private
from dydx3.modules.public import Public
from dydx3.modules.onboarding import Onboarding
from dydx3.starkex.helpers import private_key_to_public_key_pair_hex


class Client(object):

    def __init__(
        self,
        host,
        api_timeout=3000,  # TODO: Actually use this.
        default_ethereum_address=None,
        eth_private_key=None,
        eth_send_options=None,
        network_id=None,
        stark_private_key=None,
        stark_public_key=None,
        stark_public_key_y_coordinate=None,
        web3=None,
        web3_account=None,
        web3_provider=None,
        api_key_credentials=None,
    ):
        # Remove trailing '/' if present, from host.
        if host.endswith('/'):
            host = host[:-1]

        self.host = host
        self.api_timeout = api_timeout
        self.eth_send_options = eth_send_options or {}
        self.stark_private_key = stark_private_key
        self.api_key_credentials = api_key_credentials
        self.stark_public_key_y_coordinate = stark_public_key_y_coordinate

        self.web3 = None
        self.eth_signer = None
        self.default_address = None
        self.network_id = None

        if web3 is not None or web3_provider is not None:
            if isinstance(web3_provider, str):
                web3_provider = Web3.HTTPProvider(web3_provider)
            self.web3 = web3 or Web3(web3_provider)
            self.eth_signer = SignWithWeb3(self.web3)
            self.default_address = self.web3.eth.defaultAccount or None
            self.network_id = self.web3.net.version

        if eth_private_key is not None or web3_account is not None:
            # May override web3 or web3_provider configuration.
            key = eth_private_key or web3_account.key
            self.eth_signer = SignWithKey(key)
            self.default_address = self.eth_signer.address

        self.default_address = default_ethereum_address or self.default_address
        self.network_id = int(network_id or self.network_id or 1)

        # Initialize the public module. Other modules are initialized on
        # demand, if the necessary configuration options were provided.
        self._public = Public(host)
        self._private = None
        self._api_keys = None
        self._eth = None
        self._onboarding = None

        # Derive the public keys.
        if stark_private_key is not None:
            self.stark_public_key, self.stark_public_key_y_coordinate = (
                private_key_to_public_key_pair_hex(stark_private_key)
            )
            if (
                stark_public_key is not None and
                stark_public_key != self.stark_public_key
            ):
                raise ValueError('STARK public/private key mismatch')
            if (
                stark_public_key_y_coordinate is not None and
                stark_public_key_y_coordinate !=
                    self.stark_public_key_y_coordinate
            ):
                raise ValueError('STARK public/private key mismatch (y)')
        else:
            self.stark_public_key = stark_public_key
            self.stark_public_key_y_coordinate = stark_public_key_y_coordinate

        # Generate default API key credentials if needed and possible.
        if self.eth_signer and not self.api_key_credentials:
            # This may involve a web3 call, so recover on failure.
            try:
                self.api_key_credentials = (
                    self.onboarding.recover_default_api_key_credentials(
                        ethereum_address=self.eth_signer.address,
                    )
                )
            except Exception as e:
                print(
                    'Warning: Failed to derive default API key credentials:',
                    e,
                )

    @property
    def public(self):
        '''
        Get the public module, used for interacting with public endpoints.
        '''
        return self._public

    @property
    def private(self):
        '''
        Get the private module, used for interacting with endpoints that
        require API-key auth.
        '''
        if not self._private:
            if self.api_key_credentials:
                self._private = Private(
                    host=self.host,
                    network_id=self.network_id,
                    stark_private_key=self.stark_private_key,
                    default_address=self.default_address,
                    api_key_credentials=self.api_key_credentials,
                )
            else:
                raise Exception(
                    'Private endpoints not supported ' +
                    'since api_key_credentials were not specified',
                )
        return self._private

    @property
    def api_keys(self):
        '''
        Get the api_keys module, used for managing API keys. Requires
        Ethereum key auth.
        '''
        if not self._api_keys:
            if self.eth_signer:
                self._api_keys = ApiKeys(
                    host=self.host,
                    eth_signer=self.eth_signer,
                    network_id=self.network_id,
                    default_address=self.default_address,
                )
            else:
                raise Exception(
                    'API keys module is not supported since no Ethereum ' +
                    'signing method (web3, web3_account, web3_provider) was ' +
                    'provided',
                )
        return self._api_keys

    @property
    def onboarding(self):
        '''
        Get the onboarding module, used to create a new user. Requires
        Ethereum key auth.
        '''
        if not self._onboarding:
            if self.eth_signer:
                self._onboarding = Onboarding(
                    host=self.host,
                    eth_signer=self.eth_signer,
                    network_id=self.network_id,
                    default_address=self.default_address,
                    stark_public_key=self.stark_public_key,
                    stark_public_key_y_coordinate=(
                        self.stark_public_key_y_coordinate
                    ),
                )
            else:
                raise Exception(
                    'Onboarding is not supported since no Ethereum ' +
                    'signing method (web3, web3_account, web3_provider) was ' +
                    'provided',
                )
        return self._onboarding

    @property
    def eth(self):
        '''
        Get the eth module, used for interacting with Ethereum smart contracts.
        '''
        if not self._eth:
            eth_private_key = getattr(self.eth_signer, '_private_key', None)
            if self.web3 and eth_private_key:
                self._eth = Eth(
                    web3=self.web3,
                    network_id=self.network_id,
                    eth_private_key=eth_private_key,
                    default_address=self.default_address,
                    stark_public_key=self.stark_public_key,
                    send_options=self.eth_send_options,
                )
            else:
                raise Exception(
                    'Eth module is not supported since neither web3 ' +
                    'nor web3_provider was provided OR since neither ' +
                    'eth_private_key nor web3_account was provided',
                )
        return self._eth
