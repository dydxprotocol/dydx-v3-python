from dydx3.helpers.request_helpers import generate_now_iso
from dydx3.helpers.request_helpers import generate_query_path
from dydx3.helpers.request_helpers import json_stringify
from dydx3.eth_signing import SignEthPrivateAction
from dydx3.helpers.requests import request


class EthPrivate(object):
    """Module for adding/deleting API keys and recovery."""

    def __init__(
        self,
        host,
        eth_signer,
        network_id,
        default_address,
    ):
        self.host = host
        self.default_address = default_address

        self.signer = SignEthPrivateAction(eth_signer, network_id)

    # ============ Request Helpers ============

    def _request(
        self,
        method,
        endpoint,
        opt_ethereum_address,
        data={}
    ):
        ethereum_address = opt_ethereum_address or self.default_address

        request_path = '/'.join(['/v3', endpoint])
        timestamp = generate_now_iso()
        signature = self.signer.sign(
            ethereum_address,
            method=method.upper(),
            request_path=request_path,
            body=json_stringify(data) if data else '{}',
            timestamp=timestamp,
        )

        return request(
            self.host + request_path,
            method,
            {
                'DYDX-SIGNATURE': signature,
                'DYDX-TIMESTAMP': timestamp,
                'DYDX-ETHEREUM-ADDRESS': ethereum_address,
            },
            data,
        )

    def _post(
        self,
        endpoint,
        opt_ethereum_address,
    ):
        return self._request(
            'post',
            endpoint,
            opt_ethereum_address,
        )

    def _delete(
        self,
        endpoint,
        opt_ethereum_address,
        params={},
    ):
        url = generate_query_path(endpoint, params)
        return self._request(
            'delete',
            url,
            opt_ethereum_address,
        )

    def _get(
        self,
        endpoint,
        opt_ethereum_address,
        params={},
    ):
        url = generate_query_path(endpoint, params)
        return self._request(
            'get',
            url,
            opt_ethereum_address,
        )

# ============ Requests ============

    def create_api_key(
        self,
        ethereum_address=None,
    ):
        '''
        Register an API key.

        :param ethereum_address: optional
        :type ethereum_address: str

        :returns: Object containing an apiKey

        :raises: DydxAPIError
        '''
        return self._post(
            'api-keys',
            ethereum_address,
        )

    def delete_api_key(
        self,
        api_key,
        ethereum_address=None,
    ):
        '''
        Delete an API key.

        :param api_key: required
        :type api_key: str

        :param ethereum_address: optional
        :type ethereum_address: str

        :returns: None

        :raises: DydxAPIError
        '''
        return self._delete(
            'api-keys',
            ethereum_address,
            {
                'apiKey': api_key,
            },
        )

    def recovery(
        self,
        ethereum_address=None
    ):
        '''
        This is for if you can't recover your starkKey or apiKey and need an
        additional way to get your starkKey and balance on our exchange,
        both of which are needed to call the L1 solidity function needed to
        recover your funds.

        :param ethereum_address: optional
        :type ethereum_address: str

        :returns: {
            starkKey: str,
            positionId: str,
            equity: str,
            freeCollateral: str,
            quoteBalance: str,
            positions: array of open positions
        }

        :raises: DydxAPIError
        '''
        return self._get(
            'recovery',
            ethereum_address,
        )
