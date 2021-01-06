from collections import namedtuple

from dydx3.constants import COLLATERAL_ASSET
from dydx3.constants import COLLATERAL_ASSET_ID
from dydx3.starkex.constants import WITHDRAWAL_FIELD_BIT_LENGTHS
from dydx3.starkex.constants import WITHDRAWAL_PADDING_BITS
from dydx3.starkex.constants import WITHDRAWAL_PREFIX
from dydx3.starkex.helpers import nonce_from_client_id
from dydx3.starkex.helpers import to_quantums_exact
from dydx3.starkex.signable import Signable
from dydx3.starkex.starkex_resources.signature import pedersen_hash

StarkwareWithdrawal = namedtuple(
    'StarkwareWithdrawal',
    [
        'quantums_amount',
        'position_id',
        'nonce',
        'expiration_epoch_seconds',
    ],
)


class SignableWithdrawal(Signable):

    def __init__(
        self,
        position_id,
        human_amount,
        client_id,
        expiration_epoch_seconds,
    ):
        quantums_amount = to_quantums_exact(human_amount, COLLATERAL_ASSET)
        message = StarkwareWithdrawal(
            quantums_amount=quantums_amount,
            position_id=int(position_id),
            nonce=nonce_from_client_id(client_id),
            expiration_epoch_seconds=expiration_epoch_seconds,
        )
        super(SignableWithdrawal, self).__init__(message)

    def to_starkware(self):
        return self._message

    def _calculate_hash(self):
        """Calculate the hash of the Starkware order."""

        # TODO: Check values are in bounds

        packed = WITHDRAWAL_PREFIX
        packed <<= WITHDRAWAL_FIELD_BIT_LENGTHS['position_id']
        packed += self._message.position_id
        packed <<= WITHDRAWAL_FIELD_BIT_LENGTHS['nonce']
        packed += self._message.nonce
        packed <<= WITHDRAWAL_FIELD_BIT_LENGTHS['quantums_amount']
        packed += self._message.quantums_amount
        packed <<= WITHDRAWAL_FIELD_BIT_LENGTHS['expiration_epoch_seconds']
        packed += self._message.expiration_epoch_seconds
        packed <<= WITHDRAWAL_PADDING_BITS

        return pedersen_hash(COLLATERAL_ASSET_ID, packed)
