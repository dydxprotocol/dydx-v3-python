from dydx3.helpers.request_helpers import generate_query_path
from dydx3.helpers.requests import request


class Public(object):

    def __init__(
        self,
        host,
    ):
        self.host = host

    # ============ Request Helpers ============

    def _get(self, request_path, params={}):
        return request(
            generate_query_path(self.host + request_path, params),
            'get',
        )

    def _put(self, endpoint, data):
        return request(
            self.host + '/v3/' + endpoint,
            'put',
            {},
            data,
        )

    # ============ Requests ============

    def check_if_user_exists(self, ethereum_address):
        '''
        Check if user exists

        :param host: required
        :type host: str

        :returns: Bool

        :raises: DydxAPIError
        '''
        uri = '/v3/users/exists'
        return self._get(
            uri,
            {'ethereumAddress': ethereum_address},
        )

    def check_if_username_exists(self, username):
        '''
        Check if username exists

        :param username: required
        :type username: str

        :returns: Bool

        :raises: DydxAPIError
        '''
        uri = '/v3/usernames'
        return self._get(uri, {'username': username})

    def get_markets(self, market=None):
        '''
        Get one or more markets

        :param market: optional
        :type market: str in list [
            "BTC-USD",
            "ETH-USD",
            "LINK-USD",
            ...
        ]

        :returns: Market array

        :raises: DydxAPIError
        '''
        uri = '/v3/markets'
        return self._get(uri, {'market': market})

    def get_orderbook(self, market):
        '''
        Get orderbook for a market

        :param market: required
        :type market: str in list [
            "BTC-USD",
            "ETH-USD",
            "LINK-USD",
            ...
        ]

        :returns: Object containing bid array and ask array of open orders
        for a market

        :raises: DydxAPIError
        '''
        uri = '/'.join(['/v3/orderbook', market])
        return self._get(uri)

    def get_stats(self, market=None, days=None):
        '''
        Get one or more day statistics for a market

        :param market: optional
        :type market: str in list [
            "BTC-USD",
            "ETH-USD",
            "LINK-USD",
            ...
        ]

        :param days: optional
        :type days: str in list [
            "1",
            "7",
            "30",
        ]

        :returns: Statistic information for a market, either for all time
        periods or just one.

        :raises: DydxAPIError
        '''
        uri = (
            '/'.join(['/v3/stats', market])
            if market is not None
            else '/v3/stats'
        )

        return self._get(uri, {'days': days})

    def get_trades(self, market, starting_before_or_at=None):
        '''
        Get trades for a market

        :param market: required
        :type market: str in list [
            "BTC-USD",
            "ETH-USD",
            "LINK-USD",
            ...
        ]

        :param starting_before_or_at: optional
        :type starting_before_or_at: str

        :returns: Trade array

        :raises: DydxAPIError
        '''
        uri = '/'.join(['/v3/trades', market])
        return self._get(
            uri,
            {'startingBeforeOrAt': starting_before_or_at},
        )

    def get_historical_funding(self, market, effective_before_or_at=None):
        '''
        Get historical funding for a market

        :param market: required
        :type market: str in list [
            "BTC-USD",
            "ETH-USD",
            "LINK-USD",
            ...
        ]

        :param effective_before_or_at: optional
        :type effective_before_or_at: str

        :returns: Array of historical funding for a specific market

        :raises: DydxAPIError
        '''
        uri = '/'.join(['/v3/historical-funding', market])
        return self._get(
            uri,
            {'effectiveBeforeOrAt': effective_before_or_at},
        )

    def get_fast_withdrawal(
        self,
        creditAsset=None,
        creditAmount=None,
        debitAmount=None,
    ):
        '''
        Get all fast withdrawal account information

        :param creditAsset: optional
        :type creditAsset: str

        :param creditAmount: optional
        :type creditAmount: str

        :param debitAmount: optional
        :type debitAmount: str

        :returns: All fast withdrawal accounts

        :raises: DydxAPIError
        '''
        uri = '/v3/fast-withdrawals'
        return self._get(
            uri,
            {
                'creditAsset': creditAsset,
                'creditAmount': creditAmount,
                'debitAmount': debitAmount,
            },
        )

    def get_candles(
        self,
        market,
        resolution=None,
        from_iso=None,
        to_iso=None,
        limit=None,
    ):
        '''
        Get Candles

        :param market: required
        :type market: str in list [
            "BTC-USD",
            "ETH-USD",
            "LINK-USD",
            ...
        ]

        :param resolution: optional
        :type resolution: str in list [
            "1DAY",
            "4HOURS"
            "1HOUR",
            "30MINS",
            "15MINS",
            "5MINS",
            "1MIN",
        ]

        :param from_iso: optional
        :type from_iso: str

        :param to_iso: optional
        :type to_iso: str

        :param limit: optional
        :type limit: str

        :returns: Array of candles

        :raises: DydxAPIError
        '''
        uri = '/'.join(['/v3/candles', market])
        return self._get(
            uri,
            {
                'resolution': resolution,
                'fromISO': from_iso,
                'toISO': to_iso,
                'limit': limit,
            },
        )

    def get_time(self):
        '''
        Get api server time as iso and as epoch in seconds with MS

        :returns: ISO string and Epoch number in seconds with MS of server time

        :raises: DydxAPIError
        '''
        uri = '/v3/time'
        return self._get(uri)

    def verify_email(
        self,
        token,
    ):
        '''
        Verify email with token

        :param token: required
        :type token: string

        :returns: empty object

        :raises: DydxAPIError
        '''
        return self._put(
            'emails/verify-email',
            {
                'token': token,
            }
        )

    def get_public_retroactive_mining_rewards(
        self,
        ethereum_address,
    ):
        '''
        Get public retroactive mining rewards

        :param ethereumAddress: required
        :type ethereumAddress: str

        :returns: PublicRetroactiveMiningRewards

        :raises: DydxAPIError
        '''
        return self._get(
            '/v3/rewards/public-retroactive-mining',
            {
                'ethereumAddress': ethereum_address,
            },
        )

    def get_config(self):
        '''
        Get global config variables for the exchange as a whole.
        This includes (but is not limited to) details on the exchange,
        including addresses, fees, transfers, and rate limits.

        :returns: GlobalConfigVariables

        :raises: DydxAPIError
        '''
        return self._get('/v3/config')

    def get_insurance_fund_balance(self):
        '''
        Get the balance of the dYdX insurance fund

        :returns: Balance of the dYdX insurance fund in USD

        :raises: DydxAPIError
        '''
        return self._get('/v3/insurance-fund/balance')

    def get_profile(
        self,
        publicId,
    ):
        '''
        Get Public Profile

        :param publicId: required
        :type publicId: str

        :returns: PublicProfile

        :raises: DydxAPIError
        '''
        uri = '/'.join(['/v3/profile', publicId])
        return self._get(uri)

    def get_historical_leaderboard_pnls(
        self,
        period,
        limit=None,
    ):
        '''
        Get Historical Leaderboard Pnls

        :param period: required
        :type period: str
        :type period: str in list [
            "LEAGUES",
            "DAILY",
            "DAILY_COMPETITION",
            ...
        ]

        :param limit: optional
        :type limit: str

        :returns: HistoricalLeaderboardPnl

        :raises: DydxAPIError
        '''
        uri = '/'.join(['/v3/accounts/historical-leaderboard-pnls', period])
        return self._get(
            uri,
            {
                'limit': limit,
            }
        )
