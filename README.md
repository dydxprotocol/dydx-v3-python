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

The `Client` object can be created with different levels of authentication depending on which features are needed. For more complete examples, see the [examples](./examples/) directory, as well as [the integration tests](./integration_tests/).

### Public endpoints

No authentication information is required to access public endpoints.

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
```

### Private endpoints

One of the following is required:
* `api_key_credentials`
* `eth_private_key`
* `web3`
* `web3_account`
* `web3_provider`

```python
#
# Access private API endpoints, without providing a STARK private key.
#
private_client = Client(
    host='http://localhost:8080',
    api_key_credentials={ 'key': '...', ... },
)
private_client.private.get_orders()
private_client.private.create_order(
    # No STARK key, so signatures are required for orders and withdrawals.
    signature='...',
    # ...
)

#
# Access private API endpoints, with a STARK private key.
#
private_client_with_key = Client(
    host='http://localhost:8080',
    api_key_credentials={ 'key': '...', ... },
    stark_private_key='...',
)
private_client.private.create_order(
    # Order will be signed using the provided STARK private key.
    # ...
)
```

### Onboarding and API key management endpoints

One of the following is required:
* `eth_private_key`
* `web3`
* `web3_account`
* `web3_provider`

```python
#
# Onboard a new user or manage API keys, without providing private keys.
#
web3_client = Client(
    host='http://localhost:8080',
    web3_provider=Web3.HTTPProvider('http://localhost:8545'),
)
web3_client.onboarding.create_user(
    stark_public_key='...',
    ethereum_address='...',
)
web3_client.api_keys.create_api_key(
    ethereum_address='...',
)

#
# Onboard a new user or manage API keys, with private keys.
#
web3_client_with_keys = Client(
    host='http://localhost:8080',
    stark_private_key='...',
    eth_private_key='...',
)
web3_client_with_keys.onboarding.create_user()
web3_client_with_keys.api_keys.create_api_key()
```

### Using the C++ Library for STARK Signing

By default, STARK curve operations such as signing and verification will use the Python native implementation. These operations occur whenever placing an order or requesting a withdrawal. To use the C++ implementation, initialize the client object with `crypto_c_exports_path`:

```python
client = Client(
    crypto_c_exports_path='./libcrypto_c_exports.so',
    ...
)
```

The path should point to a C++ shared library file, built from Starkware's `crypto-cpp` library ([CMake target](https://github.com/starkware-libs/crypto-cpp/blob/601de408bee9f897315b8a5cb0c88e2450a91282/src/starkware/crypto/ffi/CMakeLists.txt#L3)) for the particular platform (e.g. Linux, etc.) that you are running your trading program on.
