'''Example for placing, replacing, and canceling orders.

Usage: python -m examples.orders
'''

import time

from dydx3 import Client
from dydx3.constants import API_HOST_SEPOLIA
from dydx3.constants import MARKET_BTC_USD
from dydx3.constants import NETWORK_ID_SEPOLIA
from dydx3.constants import ORDER_SIDE_BUY
from dydx3.constants import ORDER_STATUS_OPEN
from dydx3.constants import ORDER_TYPE_LIMIT
from web3 import Web3

# Ganache test address.
ETHEREUM_ADDRESS = '0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b'

# Ganache node.
WEB_PROVIDER_URL = 'http://localhost:8545'

client = Client(
    network_id=NETWORK_ID_SEPOLIA,
    host=API_HOST_SEPOLIA,
    default_ethereum_address=ETHEREUM_ADDRESS,
    web3=Web3(Web3.HTTPProvider(WEB_PROVIDER_URL)),
)

# Set STARK key.
stark_private_key = client.onboarding.derive_stark_key()
client.stark_private_key = stark_private_key

# Get our position ID.
account_response = client.private.get_account()
position_id = account_response['account']['positionId']

# Post an bid at a price that is unlikely to match.
order_params = {
    'position_id': position_id,
    'market': MARKET_BTC_USD,
    'side': ORDER_SIDE_BUY,
    'order_type': ORDER_TYPE_LIMIT,
    'post_only': True,
    'size': '0.0777',
    'price': '20',
    'limit_fee': '0.0015',
    'expiration_epoch_seconds': time.time() + 5,
}
order_response = client.private.create_order(**order_params)
order_id = order_response['order']['id']

# Replace the order at a higher price, several times.
# Note that order replacement is done atomically in the matching engine.
for replace_price in range(21, 26):
    order_response = client.private.create_order(
        **dict(
            order_params,
            price=str(replace_price),
            cancel_id=order_id,
        ),
    )
    order_id = order_response['order']['id']

# Count open orders (there should be exactly one).
orders_response = client.private.get_orders(
    market=MARKET_BTC_USD,
    status=ORDER_STATUS_OPEN,
)
assert len(orders_response['orders']) == 1

# Cancel all orders.
client.private.cancel_all_orders()

# Count open orders (there should be none).
orders_response = client.private.get_orders(
    market=MARKET_BTC_USD,
    status=ORDER_STATUS_OPEN,
)
assert len(orders_response['orders']) == 0
