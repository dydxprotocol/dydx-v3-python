import decimal
import math

from collections import namedtuple

from dydx3.constants import COLLATERAL_ASSET
from dydx3.constants import COLLATERAL_ASSET_ID_BY_NETWORK_ID
from dydx3.constants import ORDER_SIDE_BUY
from dydx3.constants import SYNTHETIC_ASSET_ID_MAP
from dydx3.constants import SYNTHETIC_ASSET_MAP
from dydx3.starkex.constants import ONE_HOUR_IN_SECONDS
from dydx3.starkex.constants import ORDER_FIELD_BIT_LENGTHS
from dydx3.starkex.constants import ORDER_PADDING_BITS
from dydx3.starkex.constants import ORDER_PREFIX
from dydx3.starkex.constants import ORDER_SIGNATURE_EXPIRATION_BUFFER_HOURS
from dydx3.starkex.helpers import nonce_from_client_id
from dydx3.starkex.helpers import to_quantums_exact
from dydx3.starkex.helpers import to_quantums_round_down
from dydx3.starkex.helpers import to_quantums_round_up
from dydx3.starkex.signable import Signable
from dydx3.starkex.starkex_resources.proxy import get_hash

DECIMAL_CONTEXT_ROUND_DOWN = decimal.Context(rounding=decimal.ROUND_DOWN)
DECIMAL_CONTEXT_ROUND_UP = decimal.Context(rounding=decimal.ROUND_UP)

StarkwareOrder = namedtuple(
    'StarkwareOrder',
    [
        'order_type',
        'asset_id_synthetic',
        'asset_id_collateral',
        'asset_id_fee',
        'quantums_amount_synthetic',
        'quantums_amount_collateral',
        'quantums_amount_fee',
        'is_buying_synthetic',
        'position_id',
        'nonce',
        'expiration_epoch_hours',
    ],
)


class SignableOrder(Signable):

    def __init__(
        self,
        network_id,
        market,
        side,
        position_id,
        human_size,
        human_price,
        limit_fee,
        client_id,
        expiration_epoch_seconds,
    ):
        synthetic_asset = SYNTHETIC_ASSET_MAP[market]
        synthetic_asset_id = SYNTHETIC_ASSET_ID_MAP[synthetic_asset]
        collateral_asset_id = COLLATERAL_ASSET_ID_BY_NETWORK_ID[network_id]
        is_buying_synthetic = side == ORDER_SIDE_BUY
        quantums_amount_synthetic = to_quantums_exact(
            human_size,
            synthetic_asset,
        )

        # Note: By creating the decimals outside the context and then
        # multiplying within the context, we ensure rounding does not occur
        # until after the multiplication is computed with full precision.
        if is_buying_synthetic:
            human_cost = DECIMAL_CONTEXT_ROUND_UP.multiply(
                decimal.Decimal(human_size),
                decimal.Decimal(human_price)
            )
            quantums_amount_collateral = to_quantums_round_up(
                human_cost,
                COLLATERAL_ASSET,
            )
        else:
            human_cost = DECIMAL_CONTEXT_ROUND_DOWN.multiply(
                decimal.Decimal(human_size),
                decimal.Decimal(human_price)
            )
            quantums_amount_collateral = to_quantums_round_down(
                human_cost,
                COLLATERAL_ASSET,
            )

        # The limitFee is a fraction, e.g. 0.01 is a 1 % fee.
        # It is always paid in the collateral asset.
        # Constrain the limit fee to six decimals of precision.
        # The final fee amount must be rounded up.
        limit_fee_rounded = DECIMAL_CONTEXT_ROUND_DOWN.quantize(
            decimal.Decimal(limit_fee),
            decimal.Decimal('0.000001'),
        )
        quantums_amount_fee_decimal = DECIMAL_CONTEXT_ROUND_UP.multiply(
            limit_fee_rounded,
            quantums_amount_collateral,
        ).to_integral_value(context=DECIMAL_CONTEXT_ROUND_UP)

        # Orders may have a short time-to-live on the orderbook, but we need
        # to ensure their signatures are valid by the time they reach the
        # blockchain. Therefore, we enforce that the signed expiration includes
        # a buffer relative to the expiration timestamp sent to the dYdX API.
        expiration_epoch_hours = math.ceil(
            float(expiration_epoch_seconds) / ONE_HOUR_IN_SECONDS,
        ) + ORDER_SIGNATURE_EXPIRATION_BUFFER_HOURS

        message = StarkwareOrder(
            order_type='LIMIT_ORDER_WITH_FEES',
            asset_id_synthetic=synthetic_asset_id,
            asset_id_collateral=collateral_asset_id,
            asset_id_fee=collateral_asset_id,
            quantums_amount_synthetic=quantums_amount_synthetic,
            quantums_amount_collateral=quantums_amount_collateral,
            quantums_amount_fee=int(quantums_amount_fee_decimal),
            is_buying_synthetic=is_buying_synthetic,
            position_id=int(position_id),
            nonce=nonce_from_client_id(client_id),
            expiration_epoch_hours=expiration_epoch_hours,
        )
        super(SignableOrder, self).__init__(network_id, message)

    def to_starkware(self):
        return self._message

    def _calculate_hash(self):
        """Calculate the hash of the Starkware order."""

        # TODO: Check values are in bounds

        if self._message.is_buying_synthetic:
            asset_id_sell = self._message.asset_id_collateral
            asset_id_buy = self._message.asset_id_synthetic
            quantums_amount_sell = self._message.quantums_amount_collateral
            quantums_amount_buy = self._message.quantums_amount_synthetic
        else:
            asset_id_sell = self._message.asset_id_synthetic
            asset_id_buy = self._message.asset_id_collateral
            quantums_amount_sell = self._message.quantums_amount_synthetic
            quantums_amount_buy = self._message.quantums_amount_collateral

        part_1 = quantums_amount_sell
        part_1 <<= ORDER_FIELD_BIT_LENGTHS['quantums_amount']
        part_1 += quantums_amount_buy
        part_1 <<= ORDER_FIELD_BIT_LENGTHS['quantums_amount']
        part_1 += self._message.quantums_amount_fee
        part_1 <<= ORDER_FIELD_BIT_LENGTHS['nonce']
        part_1 += self._message.nonce

        part_2 = ORDER_PREFIX
        for _ in range(3):
            part_2 <<= ORDER_FIELD_BIT_LENGTHS['position_id']
            part_2 += self._message.position_id
        part_2 <<= ORDER_FIELD_BIT_LENGTHS['expiration_epoch_hours']
        part_2 += self._message.expiration_epoch_hours
        part_2 <<= ORDER_PADDING_BITS

        assets_hash = get_hash(
            get_hash(
                asset_id_sell,
                asset_id_buy,
            ),
            self._message.asset_id_fee,
        )
        return get_hash(
            get_hash(
                assets_hash,
                part_1,
            ),
            part_2,
        )
