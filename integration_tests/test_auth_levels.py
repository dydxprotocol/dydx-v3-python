import os
import time

from web3 import Web3

from dydx3 import Client
from dydx3 import DydxApiError
from dydx3 import SignableWithdrawal
from dydx3 import constants
from dydx3 import epoch_seconds_to_iso
from dydx3 import generate_private_key_hex_unsafe
from dydx3 import iso_to_epoch_seconds
from dydx3 import private_key_to_public_hex
from dydx3.helpers.request_helpers import random_client_id

from tests.constants import DEFAULT_HOST

API_HOST = os.environ.get('V3_API_HOST', DEFAULT_HOST)


class TestAuthLevels():

    def test_public(self):
        client = Client(
            host=API_HOST,
        )
        client.public.get_markets()

    def test_private_with_private_keys(self):
        # Generate STARK keys and Ethhereum account.
        api_private_key = generate_private_key_hex_unsafe()
        stark_private_key = generate_private_key_hex_unsafe()
        eth_account = Web3(None).eth.account.create()

        # Get public keys.
        api_public_key = private_key_to_public_hex(api_private_key)
        stark_public_key = private_key_to_public_hex(stark_private_key)

        # Onboard the user.
        Client(
            host=API_HOST,
            eth_private_key=eth_account.key,
        ).onboarding.create_user(
            api_public_key=api_public_key,
            stark_public_key=stark_public_key,
        )

        # Create a second client WITHOUT eth_private_key.
        client = Client(
            host=API_HOST,
            api_private_key=api_private_key,
            stark_private_key=stark_private_key,
        )

        # Create a test deposit.
        client.private.create_test_deposit(
            from_address=eth_account.address,
            credit_amount='1',
        )

        # Get the primary account.
        get_account_result = client.private.get_account(
            ethereum_address=eth_account.address,
        )
        account = get_account_result['account']

        # Initiate a withdrawal.
        client.private.create_withdrawal(
            position_id=account['positionId'],
            amount='1',
            asset=constants.ASSET_USDC,
            to_address=eth_account.address,
            expiration=epoch_seconds_to_iso(time.time() + 60),
        )

    def test_private_without_stark_private_key(self):
        # Generate STARK keys and Ethhereum account.
        api_private_key = generate_private_key_hex_unsafe()
        stark_private_key = generate_private_key_hex_unsafe()
        eth_account = Web3(None).eth.account.create()

        # Get public keys.
        api_public_key = private_key_to_public_hex(api_private_key)
        stark_public_key = private_key_to_public_hex(stark_private_key)

        # Onboard the user.
        Client(
            host=API_HOST,
            eth_private_key=eth_account.key,
        ).onboarding.create_user(
            api_public_key=api_public_key,
            stark_public_key=stark_public_key,
        )

        # Create a second client WITHOUT eth_private_key or stark_private_key.
        client = Client(
            host=API_HOST,
            api_private_key=api_private_key,
        )

        # Create a test deposit.
        client.private.create_test_deposit(
            from_address=eth_account.address,
            credit_amount='200',
        )

        # Get the primary account.
        get_account_result = client.private.get_account(
            ethereum_address=eth_account.address,
        )
        account = get_account_result['account']

        # Sign a withdrawal.
        client_id = random_client_id()
        expiration = epoch_seconds_to_iso(time.time() + 60)
        signable_withdrawal = SignableWithdrawal(
            position_id=account['positionId'],
            client_id=client_id,
            human_amount='1',
            expiration_epoch_seconds=iso_to_epoch_seconds(expiration),
        )
        signature = signable_withdrawal.sign(stark_private_key)

        # Initiate a withdrawal.
        client.private.create_withdrawal(
            position_id=account['positionId'],
            amount='1',
            asset=constants.ASSET_USDC,
            to_address=eth_account.address,
            expiration=expiration,
            client_id=client_id,
            signature=signature,
        )

    def test_onboard_with_private_keys(self):
        # Generate keys.
        api_private_key = generate_private_key_hex_unsafe()
        stark_private_key = generate_private_key_hex_unsafe()
        eth_private_key = Web3(None).eth.account.create().key

        # Create client WITH private keys.
        client = Client(
            host=API_HOST,
            api_private_key=api_private_key,
            stark_private_key=stark_private_key,
            eth_private_key=eth_private_key,
        )

        # Onboard the user.
        client.onboarding.create_user()

        # Register and then revoke a second API key.
        api_private_key_2 = generate_private_key_hex_unsafe()
        api_public_key_2 = private_key_to_public_hex(api_private_key_2)
        client.api_keys.register_api_key(api_public_key_2)
        client.api_keys.get_api_keys()
        client.api_keys.delete_api_key(api_public_key_2)

    def test_onboard_with_web3_provider(self):
        # Generate private keys.
        api_private_key = generate_private_key_hex_unsafe()
        stark_private_key = generate_private_key_hex_unsafe()

        # Get public keys.
        api_public_key = private_key_to_public_hex(api_private_key)
        stark_public_key = private_key_to_public_hex(stark_private_key)

        # Get account address from local Ethereum node.
        ethereum_address = Web3().eth.accounts[0]

        # Create client WITHOUT any private keys.
        client = Client(
            host=API_HOST,
            web3_provider=Web3.HTTPProvider('http://localhost:8545'),
        )

        # Onboard the user.
        try:
            client.onboarding.create_user(
                ethereum_address=ethereum_address,
                stark_public_key=stark_public_key,
                api_public_key=api_public_key,
            )

        # If the Ethereum address was already onboarded, ignore the error.
        except DydxApiError:
            pass

        # Register and then revoke a second API key.
        api_private_key_2 = generate_private_key_hex_unsafe()
        api_public_key_2 = private_key_to_public_hex(api_private_key_2)
        client.api_keys.register_api_key(
            api_public_key=api_public_key_2,
            ethereum_address=ethereum_address,
        )
        client.api_keys.get_api_keys(
            ethereum_address=ethereum_address,
        )
        client.api_keys.delete_api_key(
            api_public_key=api_public_key_2,
            ethereum_address=ethereum_address,
        )

    def test_onboard_with_web3_default_account(self):
        # Generate private keys.
        api_private_key = generate_private_key_hex_unsafe()
        stark_private_key = generate_private_key_hex_unsafe()

        # Get public keys.
        api_public_key = private_key_to_public_hex(api_private_key)
        stark_public_key = private_key_to_public_hex(stark_private_key)

        # Connect to local Ethereum node.
        web3 = Web3()
        web3.eth.defaultAccount = web3.eth.accounts[1]

        # Create client WITHOUT any private keys.
        client = Client(
            host=API_HOST,
            web3=web3,
        )

        # Onboard the user.
        try:
            client.onboarding.create_user(
                stark_public_key=stark_public_key,
                api_public_key=api_public_key,
            )

        # If the Ethereum address was already onboarded, ignore the error.
        except DydxApiError:
            pass

        # Register and then revoke a second API key.
        api_private_key_2 = generate_private_key_hex_unsafe()
        api_public_key_2 = private_key_to_public_hex(api_private_key_2)
        client.api_keys.register_api_key(api_public_key_2)
        client.api_keys.get_api_keys()
        client.api_keys.delete_api_key(api_public_key_2)
