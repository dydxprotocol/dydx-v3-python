import json
import os
from web3 import Web3

from dydx3.constants import ASSET_RESOLUTION
from dydx3.constants import COLLATERAL_ASSET
from dydx3.constants import COLLATERAL_ASSET_ID_BY_NETWORK_ID
from dydx3.constants import DEFAULT_GAS_AMOUNT
from dydx3.constants import DEFAULT_GAS_MULTIPLIER
from dydx3.constants import DEFAULT_GAS_PRICE
from dydx3.constants import DEFAULT_GAS_PRICE_ADDITION
from dydx3.constants import MAX_SOLIDITY_UINT
from dydx3.constants import STARKWARE_PERPETUALS_CONTRACT
from dydx3.constants import TOKEN_CONTRACTS
from dydx3.errors import TransactionReverted

ERC20_ABI = 'abi/erc20.json'
STARKWARE_PERPETUALS_ABI = 'abi/starkware-perpetuals.json'
COLLATERAL_ASSET_RESOLUTION = float(ASSET_RESOLUTION[COLLATERAL_ASSET])


class Eth(object):

    def __init__(
        self,
        web3,
        network_id,
        eth_private_key,
        default_address,
        stark_public_key,
        send_options,
    ):
        self.web3 = web3
        self.network_id = network_id
        self.eth_private_key = eth_private_key
        self.default_address = default_address
        self.stark_public_key = stark_public_key
        self.send_options = send_options

        self.cached_contracts = {}
        self._next_nonce_for_address = {}

    # -----------------------------------------------------------
    # Helper Functions
    # -----------------------------------------------------------

    def create_contract(
        self,
        address,
        file_path,
    ):
        dydx_folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..',
        )
        return self.web3.eth.contract(
            address=address,
            abi=json.load(open(os.path.join(dydx_folder, file_path), 'r')),
        )

    def get_contract(
        self,
        address,
        file_path,
    ):
        if address not in self.cached_contracts:
            self.cached_contracts[address] = self.create_contract(
                address,
                file_path,
            )
        return self.cached_contracts[address]

    def get_exchange_contract(
        self,
        contract_address=None,
    ):
        if contract_address is None:
            contract_address = STARKWARE_PERPETUALS_CONTRACT.get(
                self.network_id,
            )
        if contract_address is None:
            raise ValueError(
                'Perpetuals exchange contract on network {}'.format(
                    self.network_id,
                )
            )
        contract_address = Web3.toChecksumAddress(contract_address)
        return self.get_contract(contract_address, STARKWARE_PERPETUALS_ABI)

    def get_token_contract(
        self,
        asset,
        token_address,
    ):
        if token_address is None:
            token_address = TOKEN_CONTRACTS.get(asset, {}).get(self.network_id)
        if token_address is None:
            raise ValueError(
                'Token address unknown for asset {} on network {}'.format(
                    asset,
                    self.network_id,
                )
            )
        token_address = Web3.toChecksumAddress(token_address)
        return self.get_contract(token_address, ERC20_ABI)

    def send_eth_transaction(
        self,
        method=None,
        options=None,
    ):
        options = dict(self.send_options, **(options or {}))

        if 'from' not in options:
            options['from'] = self.default_address
        if options.get('from') is None:
            raise ValueError(
                "options['from'] is not set, and no default address is set",
            )
        auto_detect_nonce = 'nonce' not in options
        if auto_detect_nonce:
            options['nonce'] = self.get_next_nonce(options['from'])
        if 'gasPrice' not in options:
            try:
                options['gasPrice'] = (
                    self.web3.eth.gasPrice + DEFAULT_GAS_PRICE_ADDITION
                )
            except Exception:
                options['gasPrice'] = DEFAULT_GAS_PRICE
        if 'value' not in options:
            options['value'] = 0
        gas_multiplier = options.pop('gasMultiplier', DEFAULT_GAS_MULTIPLIER)
        if 'gas' not in options:
            try:
                options['gas'] = int(
                    method.estimateGas(options) * gas_multiplier
                )
            except Exception:
                options['gas'] = DEFAULT_GAS_AMOUNT

        signed = self.sign_tx(method, options)
        try:
            tx_hash = self.web3.eth.sendRawTransaction(signed.rawTransaction)
        except ValueError as error:
            while (
                auto_detect_nonce and
                (
                    'nonce too low' in str(error) or
                    'replacement transaction underpriced' in str(error)
                )
            ):
                try:
                    options['nonce'] += 1
                    signed = self.sign_tx(method, options)
                    tx_hash = self.web3.eth.sendRawTransaction(
                        signed.rawTransaction,
                    )
                except ValueError as inner_error:
                    error = inner_error
                else:
                    break  # Break on success...
            else:
                raise error  # ...and raise error otherwise.

        # Update next nonce for the account.
        self._next_nonce_for_address[options['from']] = options['nonce'] + 1

        return tx_hash.hex()

    def get_next_nonce(
        self,
        ethereum_address,
    ):
        if self._next_nonce_for_address.get(ethereum_address) is None:
            self._next_nonce_for_address[ethereum_address] = (
                self.web3.eth.getTransactionCount(ethereum_address)
            )
        return self._next_nonce_for_address[ethereum_address]

    def sign_tx(
        self,
        method,
        options,
    ):
        if method is None:
            tx = options
        else:
            tx = method.buildTransaction(options)
        return self.web3.eth.account.sign_transaction(
            tx,
            self.eth_private_key,
        )

    def wait_for_tx(
        self,
        tx_hash,
    ):
        '''
        Wait for a tx to be mined and return the receipt. Raise on revert.

        :param tx_hash: required
        :type tx_hash: number

        :returns: transactionReceipt

        :raises: TransactionReverted
        '''
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        if tx_receipt['status'] == 0:
            raise TransactionReverted(tx_receipt)

    # -----------------------------------------------------------
    # Transactions
    # -----------------------------------------------------------

    def register_user(
        self,
        registration_signature,
        stark_public_key=None,
        ethereum_address=None,
        send_options=None,
    ):
        '''
        Register a STARK key, using a signature provided by dYdX.

        :param registration_signature: required
        :type registration_signature: string

        :param stark_public_key: optional
        :type stark_public_key: string

        :param ethereum_address: optional
        :type ethereum_address: string

        :param send_options: optional
        :type send_options: dict

        :returns: transactionHash

        :raises: ValueError
        '''
        stark_public_key = stark_public_key or self.stark_public_key
        if stark_public_key is None:
            raise ValueError('No stark_public_key was provided')

        ethereum_address = ethereum_address or self.default_address
        if ethereum_address is None:
            raise ValueError(
                'ethereum_address was not provided, '
                'and no default address is set',
            )

        contract = self.get_exchange_contract()
        return self.send_eth_transaction(
            method=contract.functions.registerUser(
                ethereum_address,
                int(stark_public_key, 16),
                registration_signature,
            ),
            options=send_options,
        )

    def deposit_to_exchange(
        self,
        position_id,
        human_amount,
        stark_public_key=None,
        send_options=None,
    ):
        '''
        Deposit collateral to the L2 perpetuals exchange.

        :param position_id: required
        :type position_id: int or string

        :param human_amount: required
        :type human_amount: number or string

        :param stark_public_key: optional
        :type stark_public_key: string

        :param send_options: optional
        :type send_options: dict

        :returns: transactionHash

        :raises: ValueError
        '''
        stark_public_key = stark_public_key or self.stark_public_key
        if stark_public_key is None:
            raise ValueError('No stark_public_key was provided')

        contract = self.get_exchange_contract()
        return self.send_eth_transaction(
            method=contract.functions.deposit(
                int(stark_public_key, 16),
                COLLATERAL_ASSET_ID_BY_NETWORK_ID[self.network_id],
                int(position_id),
                int(float(human_amount) * COLLATERAL_ASSET_RESOLUTION),
            ),
            options=send_options,
        )

    def withdraw(
        self,
        stark_public_key=None,
        send_options=None,
    ):
        '''
        Withdraw from exchange.

        :param stark_public_key: optional
        :type stark_public_key: string

        :param send_options: optional
        :type send_options: dict

        :returns: transactionHash

        :raises: ValueError
        '''
        stark_public_key = stark_public_key or self.stark_public_key
        if stark_public_key is None:
            raise ValueError('No stark_public_key was provided')

        contract = self.get_exchange_contract()
        return self.send_eth_transaction(
            method=contract.functions.withdraw(
                int(stark_public_key, 16),
                COLLATERAL_ASSET_ID_BY_NETWORK_ID[self.network_id],
            ),
            options=send_options,
        )

    def withdraw_to(
        self,
        recipient,
        stark_public_key=None,
        send_options=None,
    ):
        '''
        Withdraw from exchange to address.

        :param recipient: required
        :type recipient: string

        :param stark_public_key: optional
        :type stark_public_key: string

        :param send_options: optional
        :type send_options: dict

        :returns: transactionHash

        :raises: ValueError
        '''
        stark_public_key = stark_public_key or self.stark_public_key
        if stark_public_key is None:
            raise ValueError('No stark_public_key was provided')

        contract = self.get_exchange_contract()
        return self.send_eth_transaction(
            method=contract.functions.withdrawTo(
                int(stark_public_key, 16),
                COLLATERAL_ASSET_ID_BY_NETWORK_ID[self.network_id],
                recipient,
            ),
            options=send_options,
        )

    def transfer_eth(
        self,
        to_address=None,  # Require keyword args to avoid confusing the amount.
        human_amount=None,
        send_options=None,
    ):
        '''
        Send Ethereum.

        :param to_address: required
        :type to_address: number

        :param human_amount: required
        :type human_amount: number or string

        :param send_options: optional
        :type send_options: dict

        :returns: transactionHash

        :raises: ValueError
        '''
        if to_address is None:
            raise ValueError('to_address is required')

        if human_amount is None:
            raise ValueError('human_amount is required')

        return self.send_eth_transaction(
            options=dict(
                send_options,
                to=to_address,
                value=Web3.toWei(human_amount, 'ether'),
            ),
        )

    def transfer_token(
        self,
        to_address=None,  # Require keyword args to avoid confusing the amount.
        human_amount=None,
        asset=COLLATERAL_ASSET,
        token_address=None,
        send_options=None,
    ):
        '''
        Send Ethereum.

        :param to_address: required
        :type to_address: number

        :param human_amount: required
        :type human_amount: number of string

        :param asset: optional
        :type asset: string

        :param token_address: optional
        :type asset: string

        :param send_options: optional
        :type send_options: dict

        :returns: transactionHash

        :raises: ValueError
        '''
        if to_address is None:
            raise ValueError('to_address is required')

        if human_amount is None:
            raise ValueError('human_amount is required')

        if asset not in ASSET_RESOLUTION:
            raise ValueError('Unknown asset {}'.format(asset))
        asset_resolution = ASSET_RESOLUTION[asset]

        contract = self.get_token_contract(asset, token_address)
        return self.send_eth_transaction(
            method=contract.functions.transfer(
                to_address,
                int(float(human_amount) * float(asset_resolution)),
            ),
            options=send_options,
        )

    def set_token_max_allowance(
        self,
        spender,
        asset=COLLATERAL_ASSET,
        token_address=None,
        send_options=None,
    ):
        '''
        Set max allowance for some spender for some asset or token_address.

        :param spender: required
        :type spender: string

        :param asset: optional
        :type asset: string

        :param token_address: optional
        :type asset: string

        :param send_options: optional
        :type send_options: dict

        :returns: transactionHash

        :raises: ValueError
        '''
        contract = self.get_token_contract(asset, token_address)
        return self.send_eth_transaction(
            method=contract.functions.approve(
                spender,
                MAX_SOLIDITY_UINT,
            ),
            options=send_options,
        )

    # -----------------------------------------------------------
    # Getters
    # -----------------------------------------------------------

    def get_eth_balance(
        self,
        owner=None,
    ):
        '''
        Get the owner's ether balance as a human readable amount.

        :param owner: optional
        :type owner: string

        :returns: string

        :raises: ValueError
        '''
        owner = owner or self.default_address
        if owner is None:
            raise ValueError(
                'owner was not provided, and no default address is set',
            )

        wei_balance = self.web3.eth.getBalance(owner)
        return Web3.fromWei(wei_balance, 'ether')

    def get_token_balance(
        self,
        owner=None,
        asset=COLLATERAL_ASSET,
        token_address=None,
    ):
        '''
        Get the owner's balance for some asset or token address.

        :param owner: optional
        :type owner: string

        :param asset: optional
        :type asset: string

        :param token_address: optional
        :type asset: string

        :returns: int
        '''
        owner = owner or self.default_address
        if owner is None:
            raise ValueError(
                'owner was not provided, and no default address is set',
            )

        contract = self.get_token_contract(asset, token_address)
        return contract.functions.balanceOf(owner).call()

    def get_token_allowance(
        self,
        spender,
        owner=None,
        asset=COLLATERAL_ASSET,
        token_address=None,
    ):
        '''
        Get allowance for some spender for some asset or token address.

        :param spender: required
        :type spender: string

        :param owner: optional
        :type owner: string

        :param asset: optional
        :type asset: string

        :param token_address: optional
        :type token_address: string

        :returns: int

        :raises: ValueError
        '''
        owner = owner or self.default_address
        if owner is None:
            raise ValueError(
                'owner was not provided, and no default address is set',
            )

        contract = self.get_token_contract(asset, token_address)
        return contract.functions.allowance(owner, spender).call()
