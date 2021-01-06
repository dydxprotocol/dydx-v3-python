# ------------ Signature Types ------------
SIGNATURE_TYPE_NO_PREPEND = 0
SIGNATURE_TYPE_DECIMAL = 1
SIGNATURE_TYPE_HEXADECIMAL = 2

# ------------ Market Statistic Day Types ------------
MARKET_STATISTIC_DAY_ONE = '1'
MARKET_STATISTIC_DAY_SEVEN = '7'
MARKET_STATISTIC_DAY_THIRTY = '30'

# ------------ Order Types ------------
ORDER_TYPE_LIMIT = 'LIMIT'
ORDER_TYPE_STOP = 'STOP'
ORDER_TYPE_TRAILING_STOP = 'TRAILING_STOP'
ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'

# ------------ Order Side ------------
ORDER_SIDE_BUY = 'BUY'
ORDER_SIDE_SELL = 'SELL'

# ------------ Time in Force Types ------------
TIME_IN_FORCE_GTT = 'GTT'
TIME_IN_FORCE_FOK = 'FOK'
TIME_IN_FORCE_IOC = 'IOC'

# ------------ Position Status Types ------------
POSITION_STATUS_OPEN = 'OPEN'
POSITION_STATUS_CLOSED = 'CLOSED'
POSITION_STATUS_LIQUIDATED = 'LIQUIDATED'

# ------------ Order Status Types ------------
ORDER_STATUS_PENDING = 'PENDING'
ORDER_STATUS_OPEN = 'OPEN'
ORDER_STATUS_FILLED = 'FILLED'
ORDER_STATUS_CANCELED = 'CANCELED'
ORDER_STATUS_UNTRIGGERED = 'UNTRIGGERED'

# ------------ Transfer Status Types ------------
TRANSFER_STATUS_PENDING = 'PENDING'
TRANSFER_STATUS_CONFIRMED = 'CONFIRMED'
TRANSFER_STATUS_QUEUED = 'QUEUED'
TRANSFER_STATUS_CANCELED = 'CANCELED'
TRANSFER_STATUS_UNCONFIRMED = 'UNCONFIRMED'

# ------------ Account Action Types ------------
ACCOUNT_ACTION_DEPOSIT = 'DEPOSIT'
ACCOUNT_ACTION_WITHDRAWAL = 'WITHDRAWAL'

# ------------ Markets ------------
MARKET_BTC_USD = 'BTC-USD'
MARKET_ETH_USD = 'ETH-USD'
MARKET_LINK_USD = 'LINK-USD'

# ------------ Assets ------------
ASSET_USDC = 'USDC'
ASSET_BTC = 'BTC'
ASSET_ETH = 'ETH'
ASSET_LINK = 'LINK'
COLLATERAL_ASSET = ASSET_USDC

# ------------ Synthetic Assets by Market ------------
SYNTHETIC_ASSET_MAP = {
    MARKET_BTC_USD: ASSET_BTC,
    MARKET_ETH_USD: ASSET_ETH,
    MARKET_LINK_USD: ASSET_LINK,
}

# ------------ Asset IDs ------------
ASSET_ID_MAP = {
    ASSET_USDC: int(
        '0x24d6ea88d53b68601dcf03b3f204cbe829d3689194f823bd6a7f74292c22334',
        16,
    ),
    ASSET_BTC: 0,
    ASSET_ETH: 1,
    ASSET_LINK: 2,
}
COLLATERAL_ASSET_ID = ASSET_ID_MAP[COLLATERAL_ASSET]

# ------------ Asset Resolution (Quantum Size) ------------
#
# The asset resolution is the number of quantums (Starkware units) that fit
# within one "human-readable" unit of the asset. For example, if the asset
# resolution for BTC is 1e10, then the smallest unit representable within
# Starkware is 1e-10 BTC, i.e. 1/100th of a satoshi.
#
# For the collateral asset (USDC), the chosen resolution corresponds to the
# base units of the ERC-20 token. For the other, synthetic, assets, the
# resolutions are chosen such that prices relative to USDC are close to one.
ASSET_RESOLUTION = {
    ASSET_USDC: '1e6',
    ASSET_BTC: '1e10',
    ASSET_ETH: '1e8',
    ASSET_LINK: '1e7',
}
