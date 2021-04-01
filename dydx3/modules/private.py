import hmac
import hashlib
import base64

from dydx3.constants import COLLATERAL_ASSET
from dydx3.constants import COLLATERAL_TOKEN_DECIMALS
from dydx3.constants import FACT_REGISTRY_CONTRACT
from dydx3.constants import TIME_IN_FORCE_GTT
from dydx3.constants import TOKEN_CONTRACTS
from dydx3.helpers.db import get_account_id
from dydx3.helpers.request_helpers import epoch_seconds_to_iso
from dydx3.helpers.request_helpers import generate_now_iso
from dydx3.helpers.request_helpers import generate_query_path
from dydx3.helpers.request_helpers import random_client_id
from dydx3.helpers.request_helpers import iso_to_epoch_seconds
from dydx3.helpers.request_helpers import json_stringify
from dydx3.helpers.request_helpers import remove_nones
from dydx3.helpers.requests import request
from dydx3.starkex.helpers import get_transfer_erc20_fact
from dydx3.starkex.helpers import nonce_from_client_id
from dydx3.starkex.order import SignableOrder
from dydx3.starkex.withdrawal import SignableWithdrawal
from dydx3.starkex.conditional_transfer import SignableConditionalTransfer


class Private(object):

    def __init__(
        self,
        host,
        network_id,
        stark_private_key,
        default_address,
        api_key_credentials,
    ):
        self.host = host
        self.network_id = network_id
        self.stark_private_key = stark_private_key
        self.default_address = default_address
        self.api_key_credentials = api_key_credentials

    # ============ Request Helpers ============

    def _private_request(
        self,
        method,
        endpoint,
        data={},
    ):
        now_iso_string = generate_now_iso()
        request_path = '/'.join(['/v3', endpoint])
        signature = self.sign(
            request_path=request_path,
            method=method.upper(),
            iso_timestamp=now_iso_string,
            data=remove_nones(data),
        )
        headers = {
            'DYDX-SIGNATURE': signature,
            'DYDX-API-KEY': self.api_key_credentials['key'],
            'DYDX-TIMESTAMP': now_iso_string,
            'DYDX-PASSPHRASE': self.api_key_credentials['passphrase'],
        }
        return request(
            self.host + request_path,
            method,
            headers,
            data,
        )

    def _get(self, endpoint, params):
        return self._private_request(
            'get',
            generate_query_path(endpoint, params),
        )

    def _post(self, endpoint, data):
        return self._private_request(
            'post',
            endpoint,
            data
        )

    def _put(self, endpoint, data):
        return self._private_request(
            'put',
            endpoint,
            data
        )

    def _delete(self, endpoint, params):
        return self._private_request(
            'delete',
            generate_query_path(endpoint, params),
        )

    # ============ Requests ============

    def get_api_keys(
        self,
    ):
        '''
        Get API keys.

        :returns: Object containing an array of apiKeys

        :raises: DydxAPIError
        '''
        return self._get(
            'api-keys',
            {},
        )

    def get_registration(self):
        '''
        Get signature for registration

        :returns: str

        :raises: DydxAPIError
        '''

        return self._get('registration', {})

    def get_user(self):
        '''
        Get user information

        :returns: User

        :raises: DydxAPIError
        '''
        return self._get('users', {})

    def update_user(
        self,
        user_data={},
        email=None,
        username=None,
    ):
        '''
        Update user information

        :param user_data: optional
        :type user_data: dict

        :param email: optional
        :type email: str

        :param username: optional
        :type username: str

        :returns: User

        :raises: DydxAPIError
        '''
        return self._put(
            'users',
            {
                'email': email,
                'username': username,
                'userData': json_stringify(user_data),
            },
        )

    def create_account(
        self,
        stark_public_key,
        stark_public_key_y_coordinate,
    ):
        '''
        Make an account

        :param stark_public_key: required
        :type stark_public_key: str

        :param stark_public_key_y_coordinate: required
        :type stark_public_key_y_coordinate: str

        :returns: Account

        :raises: DydxAPIError
        '''
        return self._post(
            'accounts',
            {
                'starkKey': stark_public_key,
                'starkKeyYCoordinate': stark_public_key_y_coordinate,
            }
        )

    def get_account(
        self,
        ethereum_address=None,
    ):
        '''
        Get an account

        :param ethereum_address: optional
        :type ethereum_address: str

        :returns: Account

        :raises: DydxAPIError
        '''
        address = ethereum_address or self.default_address
        if address is None:
            raise ValueError('ethereum_address was not set')
        return self._get(
            '/'.join(['accounts', get_account_id(address)]),
            {},
        )

    def get_accounts(
        self,
    ):
        '''
        Get accounts

        :returns: Arrat of accounts for a user

        :raises: DydxAPIError
        '''
        return self._get(
            'accounts',
            {},
        )

    def get_positions(
        self,
        market=None,
        status=None,
        limit=None,
        created_before_or_at=None,
    ):
        '''
        Get positions

        :param market: optional
        :type market: str in list [
            "BTC-USD",
            "ETH-USD",
            "LINK-USD",
            ...
        ]

        :param status: optional
        :type status: str in list [
            "OPEN",
            "CLOSED",
            "LIQUIDATED",
        ]

        :param limit: optional
        :type limit: str

        :param created_before_or_at: optional
        :type created_before_or_at: ISO str

        :returns: Array of positions

        :raises: DydxAPIError
        '''
        return self._get(
            'positions',
            {
                'market': market,
                'limit': limit,
                'status': status,
                'createdBeforeOrAt': created_before_or_at,
            },
        )

    def get_orders(
        self,
        market=None,
        status=None,
        side=None,
        order_type=None,
        limit=None,
        created_before_or_at=None,
    ):
        '''
        Get orders

        :param market: optional
        :type market: str in list [
            "BTC-USD",
            "ETH-USD",
            "LINK-USD",
            ...
        ]

        :param status: optional
        :type status: str in list [
            "PENDING",
            "OPEN",
            "FILLED",
            "CANCELED",
            "UNTRIGGERED",
        ]

        :param side: optional
        :type side: str in list [
            "BUY",
            "SELL",
        ]

        :param order_type: optional
        :type order_type: str in list [
            "LIMIT",
            "STOP",
            "TRAILING_STOP",
            "TAKE_PROFIT",
        ]

        :param limit: optional
        :type limit: str

        :param created_before_or_at: optional
        :type created_before_or_at: ISO str

        :returns: Array of orders

        :raises: DydxAPIError
        '''
        return self._get(
            'orders',
            {
                'market': market,
                'status': status,
                'side': side,
                'type': order_type,
                'limit': limit,
                'createdBeforeOrAt': created_before_or_at,
            },
        )

    def get_order_by_id(
        self,
        order_id,
    ):
        '''
        Get order by its id

        :param order_id: required
        :type order_id: str

        :returns: Order

        :raises: DydxAPIError
        '''
        return self._get(
            '/'.join(['orders', order_id]),
            {},
        )

    def get_order_by_client_id(
        self,
        client_id,
    ):
        '''
        Get order by its client_id

        :param client_id: required
        :type client_id: str

        :returns: Order

        :raises: DydxAPIError
        '''
        return self._get(
            '/'.join(['orders/client', client_id]),
            {},
        )

    def create_order(
        self,
        position_id,
        market,
        side,
        order_type,
        post_only,
        size,
        price,
        limit_fee,
        time_in_force=None,
        cancel_id=None,
        trigger_price=None,
        trailing_percent=None,
        client_id=None,
        expiration=None,
        expiration_epoch_seconds=None,
        signature=None,
    ):
        '''
        Post an order

        :param position_id: required
        :type position_id: str or int

        :param market: required
        :type market: str in list [
            "BTC-USD",
            "ETH-USD",
            "LINK-USD",
            ...
        ]

        :param side: required
        :type side: str in list[
            "BUY",
            "SELL",
        ],

        :param order_type: required
        :type order_type: str in list [
            "LIMIT",
            "STOP",
            "TRAILING_STOP",
            "TAKE_PROFIT",
        ]

        :param post_only: required
        :type post_only: bool

        :param size: required
        :type size: str

        :param price: required
        :type price: str

        :param limit_fee: required
        :type limit_fee: str

        :param time_in_force: optional
        :type time_in_force: str in list [
            "GTT",
            "FOK",
            "IOC",
        ]

        :param cancel_id: optional
        :type cancel_id: str

        :param trigger_price: optional
        :type trigger_price: Decimal

        :param trailing_percent: optional
        :type trailing_percent: Decimal

        :param client_id: optional
        :type client_id: str

        :param expiration: optional
        :type expiration: ISO str

        :param expiration_epoch_seconds: optional
        :type expiration_epoch_seconds: int

        :param signature: optional
        type signature: str

        :returns: Order

        :raises: DydxAPIError
        '''
        client_id = client_id or random_client_id()
        if bool(expiration) == bool(expiration_epoch_seconds):
            raise ValueError(
                'Exactly one of expiration and expiration_epoch_seconds must '
                'be specified',
            )
        expiration = expiration or epoch_seconds_to_iso(
            expiration_epoch_seconds,
        )
        expiration_epoch_seconds = (
            expiration_epoch_seconds or iso_to_epoch_seconds(expiration)
        )

        order_signature = signature
        if not order_signature:
            if not self.stark_private_key:
                raise Exception(
                    'No signature provided and client was not ' +
                    'initialized with stark_private_key'
                )
            order_to_sign = SignableOrder(
                network_id=self.network_id,
                position_id=position_id,
                client_id=client_id,
                market=market,
                side=side,
                human_size=size,
                human_price=price,
                limit_fee=limit_fee,
                expiration_epoch_seconds=expiration_epoch_seconds,
            )
            order_signature = order_to_sign.sign(self.stark_private_key)

        order = {
            'market': market,
            'side': side,
            'type': order_type,
            'timeInForce': time_in_force or TIME_IN_FORCE_GTT,
            'size': size,
            'price': price,
            'limitFee': limit_fee,
            'expiration': expiration,
            'cancelId': cancel_id,
            'triggerPrice': trigger_price,
            'trailingPercent': trailing_percent,
            'postOnly': post_only,
            'clientId': client_id,
            'signature': order_signature,
        }

        return self._post(
            'orders',
            order,
        )

    def cancel_order(
        self,
        order_id,
    ):
        '''
        Cancel an order

        :param order_id: required
        :type order_id: str

        :returns: Order

        :raises: DydxAPIError
        '''
        return self._delete(
            '/'.join(['orders', order_id]),
            {},
        )

    def cancel_all_orders(
        self,
        market=None,
    ):
        '''
        Cancel all orders

        :param market: optional
        :type market: str in list [
            "BTC-USD",
            "ETH-USD",
            "LINK-USD",
            ...
        ]

        :returns: Array of orders

        :raises: DydxAPIError
        '''
        params = {'market': market} if market else {}
        return self._delete(
            'orders',
            params,
        )

    def get_fills(
        self,
        market=None,
        order_id=None,
        limit=None,
        created_before_or_at=None,
    ):
        '''
        Get fills

        :param market: optional
        :type market: str in list [
            "BTC-USD",
            "ETH-USD",
            "LINK-USD",
            ...
        ]

        :param order_id: optional
        :type order_id: str

        :param limit: optional
        :type limit: str

        :param created_before_or_at: optional
        :type created_before_or_at: ISO str

        :returns: Array of fills

        :raises: DydxAPIError
        '''
        return self._get(
            'fills',
            {
                'market': market,
                'orderId': order_id,
                'limit': limit,
                'createdBeforeOrAt': created_before_or_at,
            }
        )

    def get_transfers(
        self,
        transfer_type=None,
        limit=None,
        created_before_or_at=None,
    ):
        '''
        Get transfers

        :param transfer_type: optional
        :type transfer_type: str in list [
            "DEPOSIT",
            "WITHDRAWAL",
            "FAST_WITHDRAWAL",
        ]

        :param limit: optional
        :type limit: str

        :param created_before_or_at: optional
        :type created_before_or_at: ISO str

        :returns: Array of transfers

        :raises: DydxAPIError
        '''
        return self._get(
            'transfers',
            {
                'type': transfer_type,
                'limit': limit,
                'createdBeforeOrAt': created_before_or_at,
            },
        )

    def create_withdrawal(
        self,
        position_id,
        amount,
        asset,
        to_address,
        client_id=None,
        expiration=None,
        expiration_epoch_seconds=None,
        signature=None,
    ):
        '''
        Post a withdrawal

        :param position_id: required
        :type position_id: int or str

        :param amount: required
        :type amount: str

        :param asset: required
        :type asset: str in list [
            "ETH",
            "LINK",
            "BTC",
            "USDC",
            "USDT",
            "USD",
            ...
        ]

        :param client_id: optional
        :type client_id: str

        :param expiration: optional
        :type expiration: ISO str

        :param expiration_epoch_seconds: optional
        :type expiration_epoch_seconds: int

        :param signature: optional
        :type signature: str

        :returns: Transfer

        :raises: DydxAPIError
        '''
        client_id = client_id or random_client_id()
        if bool(expiration) == bool(expiration_epoch_seconds):
            raise ValueError(
                'Exactly one of expiration and expiration_epoch_seconds must '
                'be specified',
            )
        expiration = expiration or epoch_seconds_to_iso(
            expiration_epoch_seconds,
        )
        expiration_epoch_seconds = (
            expiration_epoch_seconds or iso_to_epoch_seconds(expiration)
        )

        if not signature:
            if not self.stark_private_key:
                raise Exception(
                    'No signature provided and client was not' +
                    'initialized with stark_private_key'
                )
            withdrawal_to_sign = SignableWithdrawal(
                network_id=self.network_id,
                position_id=position_id,
                client_id=client_id,
                human_amount=amount,
                expiration_epoch_seconds=expiration_epoch_seconds,
            )
            signature = withdrawal_to_sign.sign(self.stark_private_key)

        params = {
            'amount': amount,
            'asset': asset,
            'expiration': expiration,
            'clientId': client_id,
            'signature': signature,
        }
        return self._post('withdrawals', params)

    def create_fast_withdrawal(
        self,
        position_id,
        credit_asset,
        credit_amount,
        debit_amount,
        to_address,
        lp_position_id,
        lp_stark_public_key,
        client_id=None,
        expiration=None,
        expiration_epoch_seconds=None,
        signature=None,
    ):
        '''
        Post a fast withdrawal

        :param credit_asset: required
        :type credit_asset: str in list [
            "USDC",
            "USDT",
        ]

        :param position_id: required
        :type position_id: str or int

        :param credit_amount: required
        :type credit_amount: str or int

        :param debit_amount: required
        :type debit_amount: str or int

        :param to_address: required
        :type to_address: str

        :param lp_position_id: required
        :type lp_position_id: str or int

        :param lp_stark_public_key: required
        :type lp_stark_public_key: str

        :param client_id: optional
        :type client_id: str

        :param expiration: optional
        :type expiration: ISO str

        :param expiration_epoch_seconds: optional
        :type expiration_epoch_seconds: int

        :param signature: optional
        :type signature: str

        :returns: Transfer

        :raises: DydxAPIError
        '''
        client_id = client_id or random_client_id()
        if bool(expiration) == bool(expiration_epoch_seconds):
            raise ValueError(
                'Exactly one of expiration and expiration_epoch_seconds must '
                'be specified',
            )
        expiration = expiration or epoch_seconds_to_iso(
            expiration_epoch_seconds,
        )
        expiration_epoch_seconds = (
            expiration_epoch_seconds or iso_to_epoch_seconds(expiration)
        )

        if not signature:
            if not self.stark_private_key:
                raise Exception(
                    'No signature provided and client was not' +
                    'initialized with stark_private_key'
                )
            fact = get_transfer_erc20_fact(
                recipient=to_address,
                token_decimals=COLLATERAL_TOKEN_DECIMALS,
                human_amount=credit_amount,
                token_address=(
                    TOKEN_CONTRACTS[COLLATERAL_ASSET][self.network_id]
                ),
                salt=nonce_from_client_id(client_id),
            )
            transfer_to_sign = SignableConditionalTransfer(
                network_id=self.network_id,
                sender_position_id=position_id,
                receiver_position_id=lp_position_id,
                receiver_public_key=lp_stark_public_key,
                fact_registry_address=FACT_REGISTRY_CONTRACT[self.network_id],
                fact=fact,
                human_amount=debit_amount,
                client_id=client_id,
                expiration_epoch_seconds=expiration_epoch_seconds,
            )
            signature = transfer_to_sign.sign(self.stark_private_key)

        params = {
            'creditAsset': credit_asset,
            'creditAmount': credit_amount,
            'debitAmount': debit_amount,
            # TODO: Signature verification should work regardless of case.
            'toAddress': to_address.lower(),
            'lpPositionId': lp_position_id,
            'expiration': expiration,
            'clientId': client_id,
            'signature': signature,
        }
        return self._post('fast-withdrawals', params)

    def get_funding_payments(
        self,
        market=None,
        limit=None,
        effective_before_or_at=None,
    ):
        '''
        Get funding payments

        :param market: optional
        :type market: str in list [
            "BTC-USD",
            "ETH-USD",
            "LINK-USD",
            ...
        ]

        :param limit: optional
        :type limit: str

        :param effective_before_or_at: optional
        :type effective_before_or_at: ISO str

        :returns: Array of funding payments

        :raises: DydxAPIError
        '''
        return self._get(
            'funding',
            {
                'market': market,
                'limit': limit,
                'effectiveBeforeOrAt': effective_before_or_at,
            },
        )

    def get_historical_pnl(
        self,
        account,
        created_before_or_at=None,
        created_on_or_after=None,
    ):
        '''
        Get historical pnl ticks

        :param account: required
        :type account: str

        :param created_before_or_at: optional
        :type created_before_or_at: ISO str

        :param created_on_or_after: optional
        :type created_on_or_after: ISO str

        :returns: Array of historical pnl ticks

        :raises: DydxAPIError
        '''
        return self._get(
            'historical-pnl',
            {
                'account': account,
                'createdBeforeOrAt': created_before_or_at,
                'createdOnOrAfter': created_on_or_after,
            },
        )

    # ============ Signing ============

    def sign(
        self,
        request_path,
        method,
        iso_timestamp,
        data,
    ):
        message_string = (
            iso_timestamp +
            method +
            request_path +
            (json_stringify(data) if data else '')
        )

        hashed = hmac.new(
            base64.urlsafe_b64decode(
                (self.api_key_credentials['secret']).encode('utf-8'),
            ),
            msg=message_string.encode('utf-8'),
            digestmod=hashlib.sha256,
        )
        return base64.urlsafe_b64encode(hashed.digest()).decode()
