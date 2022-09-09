'''Example for connecting to private WebSockets with an existing account.

Usage: python -m examples.websockets
'''

import asyncio
import json
import websockets

from dydx3 import Client
from dydx3.helpers.request_helpers import generate_now_iso
from dydx3.constants import API_HOST_GOERLI
from dydx3.constants import NETWORK_ID_GOERLI
from dydx3.constants import WS_HOST_GOERLI
from web3 import Web3

# Ganache test address.
ETHEREUM_ADDRESS = '0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b'

# Ganache node.
WEB_PROVIDER_URL = 'http://localhost:8545'

client = Client(
    network_id=NETWORK_ID_GOERLI,
    host=API_HOST_GOERLI,
    default_ethereum_address=ETHEREUM_ADDRESS,
    web3=Web3(Web3.HTTPProvider(WEB_PROVIDER_URL)),
)

now_iso_string = generate_now_iso()
signature = client.private.sign(
    request_path='/ws/accounts',
    method='GET',
    iso_timestamp=now_iso_string,
    data={},
)
req = {
    'type': 'subscribe',
    'channel': 'v3_accounts',
    'accountNumber': '0',
    'apiKey': client.api_key_credentials['key'],
    'passphrase': client.api_key_credentials['passphrase'],
    'timestamp': now_iso_string,
    'signature': signature,
}


async def main():
    # Note: This doesn't work with Python 3.9.
    async with websockets.connect(WS_HOST_GOERLI) as websocket:

        await websocket.send(json.dumps(req))
        print(f'> {req}')

        while True:
            res = await websocket.recv()
            print(f'< {res}')

asyncio.get_event_loop().run_until_complete(main())
