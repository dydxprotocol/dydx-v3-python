'''Integration test.
This test can be very slow due to on-chain calls.
Run with `pytest -s` to enable print statements.
'''

import re
import os
import time

from web3 import Web3

from dydx3 import Client
from dydx3 import DydxApiError
from dydx3 import constants
from dydx3 import epoch_seconds_to_iso
from dydx3 import generate_private_key_hex_unsafe
from dydx3 import private_key_to_public_key_pair_hex

from tests.constants import DEFAULT_HOST
from tests.constants import DEFAULT_NETWORK_ID
from tests.constants import SEVEN_DAYS_S

from integration_tests.util import wait_for_condition

HOST = os.environ.get('V3_API_HOST', DEFAULT_HOST)
NETWORK_ID = os.environ.get('NETWORK_ID', DEFAULT_NETWORK_ID)
LP_POSITION_ID = os.environ.get('LP_POSITION_ID', '2')
LP_PUBLIC_KEY = os.environ.get(
    'LP_PUBLIC_KEY',
    '04a9ecd28a67407c3cff8937f329ca24fd631b1d9ca2b9f2df47c7ebf72bf0b0',
)


class TestIntegration():

    def test_integration_without_funds(self):
        # Create an Ethereum account and STARK keys for the new user.
        web3_account = Web3(None).eth.account.create()
        ethereum_address = web3_account.address
        stark_private_key = generate_private_key_hex_unsafe()

        # Create client for the new user.
        client = Client(
            host=HOST,
            network_id=NETWORK_ID,
            stark_private_key=stark_private_key,
            web3_account=web3_account,
        )

        # Onboard the user.
        client.onboarding.create_user()

        # Register a new API key.
        client.api_keys.create_api_key()

        # Get the primary account.
        get_account_result = client.private.get_account(
            ethereum_address=ethereum_address,
        )
        account = get_account_result['account']
        assert int(account['starkKey'], 16) == int(client.stark_public_key, 16)

        # Initiate a regular (slow) withdrawal.
        #
        # Expect signature validation to pass, although the collateralization
        # check will fail.
        expected_error = (
            'Withdrawal would put account under collateralization minumum'
        )
        expiration_epoch_seconds = time.time() + SEVEN_DAYS_S + 60
        try:
            client.private.create_withdrawal(
                position_id=account['positionId'],
                amount='1',
                asset=constants.ASSET_USDC,
                to_address=ethereum_address,
                expiration_epoch_seconds=expiration_epoch_seconds,
            )
        except DydxApiError as e:
            if expected_error not in str(e):
                raise

        # Post an order.
        #
        # Expect signature validation to pass, although the collateralization
        # check will fail.
        one_minute_from_now_iso = epoch_seconds_to_iso(time.time() + 60)
        try:
            client.private.create_order(
                position_id=account['positionId'],
                market=constants.MARKET_BTC_USD,
                side=constants.ORDER_SIDE_BUY,
                order_type=constants.ORDER_TYPE_LIMIT,
                post_only=False,
                size='10',
                price='1000',
                limit_fee='0.1',
                expiration=one_minute_from_now_iso,
            )
        except DydxApiError as e:
            if expected_error not in str(e):
                raise

    def test_integration(self):
        source_private_key = os.environ.get('TEST_SOURCE_PRIVATE_KEY')
        if source_private_key is None:
            raise ValueError('TEST_SOURCE_PRIVATE_KEY must be set')

        web3_provider = os.environ.get('TEST_WEB3_PROVIDER_URL')
        if web3_provider is None:
            raise ValueError('TEST_WEB3_PROVIDER_URL must be set')

        # Create client that will be used to fund the new user.
        source_client = Client(
            host='',
            eth_private_key=source_private_key,
            web3_provider=web3_provider,
        )

        # Create an Ethereum account and STARK keys for the new user.
        web3_account = Web3(None).eth.account.create()
        ethereum_address = web3_account.address
        eth_private_key = web3_account.key
        stark_private_key = generate_private_key_hex_unsafe()

        # Fund the new user with ETH and USDC.
        fund_eth_hash = source_client.eth.transfer_eth(
            to_address=ethereum_address,
            human_amount=0.001,
        )
        fund_usdc_hash = source_client.eth.transfer_token(
            to_address=ethereum_address,
            human_amount=2,
        )
        print('Waiting for funds...')
        source_client.eth.wait_for_tx(fund_eth_hash)
        source_client.eth.wait_for_tx(fund_usdc_hash)
        print('...done.')

        # Create client for the new user.
        client = Client(
            host=HOST,
            network_id=NETWORK_ID,
            stark_private_key=stark_private_key,
            eth_private_key=eth_private_key,
            web3_provider=web3_provider,
        )

        # Onboard the user.
        res = client.onboarding.create_user()
        api_key_credentials = res['apiKey']

        print('eth_private_key', eth_private_key)
        print('stark_private_key', stark_private_key)
        print('client.api_key_credentials', client.api_key_credentials)

        # Get the user.
        get_user_result = client.private.get_user()
        assert get_user_result['user'] == {
            'ethereumAddress': ethereum_address.lower(),
            'isRegistered': False,
            'email': None,
            'username': None,
            'userData': {},
            'makerFeeRate': '0.0005',
            'takerFeeRate': '0.0015',
            'makerVolume30D': '0',
            'takerVolume30D': '0',
            'fees30D': '0',
        }

        # Get the registration signature.
        registration_result = client.private.get_registration()
        signature = registration_result['signature']
        assert re.match('0x[0-9a-f]{130}$', signature) is not None, (
            'Invalid registration result: {}'.format(registration_result)
        )

        # Register the user on-chain.
        registration_tx_hash = client.eth.register_user(signature)
        print('Waiting for registration...')
        client.eth.wait_for_tx(registration_tx_hash)
        print('...done.')

        # Set the user's username.
        username = 'integration_user_{}'.format(int(time.time()))
        client.private.update_user(username=username)

        # Create a second account under the same user.
        #
        # NOTE: Support for multiple accounts under the same user is limited.
        # The frontend does not currently support mutiple accounts per user.
        stark_private_key_2 = generate_private_key_hex_unsafe()
        stark_public_key_2, stark_public_key_y_coordinate_2 = (
            private_key_to_public_key_pair_hex(stark_private_key_2)
        )

        client.private.create_account(
            stark_public_key=stark_public_key_2,
            stark_public_key_y_coordinate=stark_public_key_y_coordinate_2,
        )

        # Get the primary account.
        get_account_result = client.private.get_account(
            ethereum_address=ethereum_address,
        )
        account = get_account_result['account']
        assert int(account['starkKey'], 16) == int(client.stark_public_key, 16)

        # Get all accounts.
        get_all_accounts_result = client.private.get_accounts()
        get_all_accounts_public_keys = [
            a['starkKey'] for a in get_all_accounts_result['accounts']
        ]
        assert int(client.stark_public_key, 16) in [
            int(k, 16) for k in get_all_accounts_public_keys
        ]

        # TODO: Fix.
        # assert int(stark_public_key_2, 16) in [
        #     int(k, 16) for k in get_all_accounts_public_keys
        # ]

        # Get positions.
        get_positions_result = client.private.get_positions(market='BTC-USD')
        assert get_positions_result == {'positions': []}

        # Set allowance on the Starkware perpetual contract, for the deposit.
        approve_tx_hash = client.eth.set_token_max_allowance(
            client.eth.get_exchange_contract().address,
        )
        print('Waiting for allowance...')
        client.eth.wait_for_tx(approve_tx_hash)
        print('...done.')

        # Send an on-chain deposit.
        deposit_tx_hash = client.eth.deposit_to_exchange(
            account['positionId'],
            3,
        )
        print('Waiting for deposit...')
        client.eth.wait_for_tx(deposit_tx_hash)
        print('...done.')

        # Wait for the deposit to be processed.
        print('Waiting for deposit to be processed on dYdX...')
        wait_for_condition(
            lambda: len(client.private.get_transfers()['transfers']) > 0,
            True,
            60,
        )
        print('...transfer was recorded, waiting for confirmation...')
        wait_for_condition(
            lambda: client.private.get_account()['account']['quoteBalance'],
            '2',
            180,
        )
        print('...done.')

        # Post an order.
        one_minute_from_now_iso = epoch_seconds_to_iso(time.time() + 60)
        create_order_result = client.private.create_order(
            position_id=account['positionId'],
            market=constants.MARKET_BTC_USD,
            side=constants.ORDER_SIDE_BUY,
            order_type=constants.ORDER_TYPE_LIMIT,
            post_only=False,
            size='10',
            price='1000',
            limit_fee='0.1',
            expiration=one_minute_from_now_iso,
        )

        # Get the order.
        order_id = create_order_result['order']['id']
        get_order_result = client.private.get_order_by_id(order_id)
        assert get_order_result['order']['market'] == constants.MARKET_BTC_USD

        # Cancel the order.
        client.private.cancel_order(order_id)

        # Cancel all orders.
        client.private.cancel_all_orders()

        # Get open orders.
        get_orders_result = client.private.get_orders(
            market=constants.MARKET_BTC_USD,
            status=constants.POSITION_STATUS_OPEN,
        )
        assert get_orders_result == {'orders': []}

        # Get fills.
        client.private.get_fills(
            market=constants.MARKET_BTC_USD,
        )

        # Initiate a regular (slow) withdrawal.
        expiration_epoch_seconds = time.time() + SEVEN_DAYS_S + 60
        client.private.create_withdrawal(
            position_id=account['positionId'],
            amount='1',
            asset=constants.ASSET_USDC,
            to_address=ethereum_address,
            expiration_epoch_seconds=expiration_epoch_seconds,
        )

        # Get deposits.
        deposits_result = client.private.get_transfers(
            transfer_type=constants.ACCOUNT_ACTION_DEPOSIT,
        )
        assert len(deposits_result['transfers']) == 1

        # Get withdrawals.
        withdrawals_result = client.private.get_transfers(
            transfer_type=constants.ACCOUNT_ACTION_WITHDRAWAL,
        )
        assert len(withdrawals_result['transfers']) == 1

        # Get funding payments.
        client.private.get_funding_payments(
            market=constants.MARKET_BTC_USD,
        )

        # Register a new API key.
        create_api_key_result = client.api_keys.create_api_key()
        new_api_key_credentials = create_api_key_result['apiKey']

        # Get all API keys.
        get_api_keys_result = client.private.get_api_keys()
        api_keys_public_keys = [
            a['key'] for a in get_api_keys_result['apiKeys']
        ]
        assert api_key_credentials['key'] in api_keys_public_keys

        # Delete an API key.
        client.api_keys.delete_api_key(
            api_key=new_api_key_credentials['key'],
            ethereum_address=ethereum_address,
        )

        # Get all API keys after the deletion.
        get_api_keys_result_after = client.private.get_api_keys()
        assert len(get_api_keys_result_after['apiKeys']) == 1

        # Initiate a fast withdrawal of USDC.
        expiration_epoch_seconds = time.time() + SEVEN_DAYS_S + 60
        client.private.create_fast_withdrawal(
            position_id=account['positionId'],
            credit_asset='USDC',
            credit_amount='1',
            debit_amount='2',
            to_address=ethereum_address,
            lp_position_id=LP_POSITION_ID,
            lp_stark_public_key=LP_PUBLIC_KEY,
            client_id='mock-client-id',
            expiration_epoch_seconds=expiration_epoch_seconds,
        )

        # Send an on-chain withdraw.
        withdraw_tx_hash = client.eth.withdraw()
        print('Waiting for withdraw...')
        client.eth.wait_for_tx(withdraw_tx_hash)
        print('...done.')

        # Wait for the withdraw to be processed.
        print('Waiting for withdraw to be processed on dYdX...')
        wait_for_condition(
            lambda: len(client.private.get_transfers()['transfers']) > 0,
            True,
            60,
        )
        print('...transfer was recorded, waiting for confirmation...')
        wait_for_condition(
            lambda: client.private.get_account()['account']['quoteBalance'],
            '2',
            180,
        )
        print('...done.')

        # Send an on-chain withdraw_to.
        withdraw_to_tx_hash = client.eth.withdraw_to(
            recipient=ethereum_address,
        )
        print('Waiting for withdraw_to...')
        client.eth.wait_for_tx(withdraw_to_tx_hash)
        print('...done.')

        # Wait for the withdraw_to to be processed.
        print('Waiting for withdraw_to to be processed on dYdX...')
        wait_for_condition(
            lambda: len(client.private.get_transfers()['transfers']) > 0,
            True,
            60,
        )
        print('...transfer was recorded, waiting for confirmation...')
        wait_for_condition(
            lambda: client.private.get_account()['account']['quoteBalance'],
            '2',
            180,
        )
        print('...done.')
