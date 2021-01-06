import re
import os
import time

from web3 import Web3

from dydx3 import Client
from dydx3 import constants
from dydx3 import epoch_seconds_to_iso
from dydx3 import generate_private_key_hex_unsafe
from dydx3 import private_key_to_public_hex

from tests.constants import DEFAULT_HOST


class TestIntegration():

    def test_integration(self):
        # Create an Ethereum account.
        web3 = Web3(None)
        web3_account = web3.eth.account.create()
        ethereum_address = web3_account.address

        # Generate STARK keys.
        api_private_key = generate_private_key_hex_unsafe()
        stark_private_key = generate_private_key_hex_unsafe()

        # Create client.
        client = Client(
            host=os.environ.get('V3_API_HOST', DEFAULT_HOST),
            api_private_key=api_private_key,
            stark_private_key=stark_private_key,
            web3_account=web3_account,
        )

        # Onboard user.
        client.onboarding.create_user(
            ethereum_address=ethereum_address,
        )

        # Get the user.
        get_user_result = client.private.get_user()
        assert get_user_result == {
            'user': {
                'ethereumAddress': ethereum_address.lower(),
                'isRegistered': False,
                'email': None,
                'username': None,
                'userData': {},
                'makerFeeRate': '0.05',
                'takerFeeRate': '0.04',
                'makerVolume30D': '0',
                'takerVolume30D': '0',
                'fees30D': '0',
            },
        }

        # Get the registration signature.
        get_registration_result = client.private.get_registration()
        assert re.match(
            '[0-9a-f]{128}$',
            get_registration_result['signature'],
        ) is not None, (
            'Invalid registration result: {}'.format(get_registration_result)
        )

        # Set the user's username.
        username = 'integration_user_{}'.format(int(time.time()))
        client.private.update_user(username=username)

        # Create a second account under the same user.
        #
        # NOTE: Support for multiple accounts under the same user is limited.
        # The frontend does not currently support mutiple accounts per user.
        stark_private_key_2 = generate_private_key_hex_unsafe()
        stark_public_key_2 = private_key_to_public_hex(stark_private_key_2)
        client.private.create_account(
            stark_public_key=stark_public_key_2,
        )

        # Get the primary account.
        get_account_result = client.private.get_account(
            ethereum_address=ethereum_address,
        )
        account = get_account_result['account']
        assert account['starkKey'] == client.stark_public_key

        # Get all accounts.
        get_all_accounts_result = client.private.get_accounts()
        get_all_accounts_public_keys = [
            a['starkKey'] for a in get_all_accounts_result['accounts']
        ]
        assert client.stark_public_key in get_all_accounts_public_keys
        assert stark_public_key_2 in get_all_accounts_public_keys

        # Get postiions.
        get_positions_result = client.private.get_positions(market='BTC-USD')
        assert get_positions_result == {'positions': []}

        # Create a test deposit.
        client.private.create_test_deposit(
            from_address=ethereum_address,
            credit_amount='200',
        )

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
        one_minute_from_now_iso = epoch_seconds_to_iso(time.time() + 60)
        client.private.create_withdrawal(
            position_id=account['positionId'],
            amount='1',
            asset=constants.ASSET_USDC,
            to_address=ethereum_address,
            expiration=one_minute_from_now_iso,
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
        api_private_key_2 = generate_private_key_hex_unsafe()
        api_public_key_2 = private_key_to_public_hex(api_private_key_2)
        client.api_keys.register_api_key(
            ethereum_address=ethereum_address,
            api_public_key=api_public_key_2,
        )

        # Get all API keys.
        api_keys_result = client.api_keys.get_api_keys(
            ethereum_address=ethereum_address,
        )
        api_keys_public_keys = [
            a['apiKey'] for a in api_keys_result['apiKeys']
        ]
        assert client.api_public_key in api_keys_public_keys
        assert api_public_key_2 in api_keys_public_keys

        # Delete an API key.
        client.api_keys.delete_api_key(
            ethereum_address=ethereum_address,
            api_public_key=api_public_key_2,
        )

        # Get all API keys after the deletion.
        api_keys_result_after = client.api_keys.get_api_keys(
            ethereum_address=ethereum_address,
        )
        assert len(api_keys_result_after['apiKeys']) == 1

        # TODO: Uncomment when the fast withdrawal endpoint works.
        #
        # # Initiate a fast withdrawal of USDC.
        # one_minute_from_now_iso = epoch_seconds_to_iso(time.time() + 60)
        # client.private.create_fast_withdrawal(
        #     credit_asset='USDC',
        #     credit_amount='100',
        #     debit_amount='100',
        #     to_address=ethereum_address,
        #     lp_position_id='foo', # TODO
        #     expiration=one_minute_from_now_iso,
        #     signature='mock-signature',
        # )

        # # Initiate a fast withdrawal, converting USDC -> USDT.
        # client.private.create_fast_withdrawal(
        #     credit_asset='USDT',
        #     credit_amount='85',
        #     debit_amount='100',
        #     to_address=ethereum_address,
        #     lp_position_id='foo', # TODO
        #     expiration=one_minute_from_now_iso,
        #     signature='mock-signature',
        # )
