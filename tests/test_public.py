import os

from dydx3 import Client
from dydx3.constants import MARKET_BTC_USD
from dydx3.constants import MARKET_STATISTIC_DAY_ONE

from tests.constants import DEFAULT_HOST

ADDRESS_1 = '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C0'
API_HOST = os.environ.get('V3_API_HOST', DEFAULT_HOST)


class TestPublic():

    def test_check_if_user_exists(self):
        public = Client(API_HOST).public
        json = public.check_if_user_exists(ADDRESS_1)
        assert json == {'exists': False}

    def test_check_if_username_exists(self):
        public = Client(API_HOST).public
        json = public.check_if_username_exists('foo')
        assert json == {'exists': False}

    def test_get_markets(self):
        public = Client(API_HOST).public
        json = public.get_markets()
        assert json != {}

    def test_get_orderbook(self):
        public = Client(API_HOST).public
        json = public.get_orderbook(MARKET_BTC_USD)
        assert json != {}

    def test_get_stats(self):
        public = Client(API_HOST).public
        json = public.get_stats(
            MARKET_BTC_USD,
            MARKET_STATISTIC_DAY_ONE,
        )
        assert json != {}

    def test_get_trades(self):
        public = Client(API_HOST).public
        json = public.get_trades(MARKET_BTC_USD)
        assert json != {}

    def test_get_historical_funding(self):
        public = Client(API_HOST).public
        json = public.get_historical_funding(MARKET_BTC_USD)
        assert json != {}

    def test_get_candles(self):
        public = Client(API_HOST).public
        json = public.get_candles(MARKET_BTC_USD)
        assert json != {}

    def test_get_fast_withdrawal(self):
        public = Client(API_HOST).public
        json = public.get_fast_withdrawal()
        assert json != {}

    def test_verify_email(self):
        try:
            public = Client(API_HOST).public
            public.verify_email('token')
        except Exception as e:
            # No userId gotten with token: token so no verification
            # has occurred
            assert e.status_code == 400

    def test_public_retroactive_mining(self):
        public = Client(API_HOST).public
        json = public.get_public_retroactive_mining_rewards(ADDRESS_1)
        assert json != {}
