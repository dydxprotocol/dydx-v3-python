<p align="center"><img src="https://s3.amazonaws.com/dydx-assets/dydx_logo_black.svg" width="256" /></p>

<div align="center">
  <a href="https://circleci.com/gh/dydxprotocol/workflows/dydx-v3-python/tree/master">
    <img src="https://img.shields.io/circleci/project/github/dydxprotocol/dydx-v3-python.svg?token=089b73e1b03736647446c0d80057bc8609790e2d" alt='CI' />
  </a>
  <a href='https://pypi.org/project/dydx-v3-python'>
    <img src='https://img.shields.io/pypi/v/dydx-v3-python.svg' alt='PyPI'/>
  </a>
  <a href='https://github.com/dydxprotocol/dydx-v3-python/blob/master/LICENSE'>
    <img src='https://img.shields.io/github/license/dydxprotocol/dydx-v3-python.svg' alt='License' />
  </a>
</div>
<br>

Python client for dYdX (v3 API).

The library is currently tested against Python versions 2.7, 3.4, 3.5, and 3.6

## Installation

The `dydx-v3-python` package is available on [PyPI](https://pypi.org/project/dydx-v3-python). Install with `pip`:

```bash
pip install dydx-v3-python
```

## Getting Started

The `Client` object can be created with different levels of authentication depending on which features are needed. For more example requests, see [test_integration.py](./integration_tests/test_integration.py).

```python
from dydx3 import Client
from web3 import Web3

#
# Access public API endpoints.
#
public_client = Client(
    host='http://localhost:8080',
)
public_client.public.get_markets()

#
# Access private API endpoints, without providing a STARK key.
#
private_client = Client(
    host='http://localhost:8080',
    api_private_key='...',
)
private_client.private.get_orders()
private_client.private.create_order(
    signature='...',  # No STARK key, so signature is required.
    # ...
)

#
# Access private API endpoints, with a STARK key.
#
private_client_with_key = Client(
    host='http://localhost:8080',
    api_private_key='...',
    stark_private_key='...',
)
private_client.private.create_order(
    # Order will be signed using the provided STARK key.
    # ...
)

#
# Onboard a new user or manage API keys, without providing private keys.
#
web3_client = Client(
    host='http://localhost:8080',
    web3_provider=Web3.HTTPProvider('http://localhost:8545'),
)
web3_client.onboarding.create_user(
    stark_public_key='...',
    api_public_key='...',
    ethereum_address='...',
)
web3_client.api_keys.register_api_key(
    api_public_key='...',  # Register a second API key.
    ethereum_address='...',
)

#
# Onboard a new user or manage API keys, with private keys.
#
web3_client_with_keys = Client(
    host='http://localhost:8080',
    api_private_key='...',
    stark_private_key='...',
    eth_private_key='...',
)
web3_client_with_keys.onboarding.create_user()
web3_client_with_keys.api_keys.register_api_key(
    api_public_key='...',  # Register a second API key.
)
```
