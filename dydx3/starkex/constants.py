"""Constants related to creating hashes of Starkware objects."""

ONE_HOUR_IN_SECONDS = 60 * 60
ORDER_SIGNATURE_EXPIRATION_BUFFER_HOURS = 24 * 7  # Seven days.

CONDITIONAL_TRANSFER_PADDING_BITS = 81
CONDITIONAL_TRANSFER_PREFIX = 5
ORDER_PREFIX = 3
ORDER_PADDING_BITS = 17
WITHDRAWAL_PADDING_BITS = 49
WITHDRAWAL_PREFIX = 6

# Note: Fees are not supported for conditional transfers.
CONDITIONAL_TRANSFER_FEE_ASSET_ID = 0
CONDITIONAL_TRANSFER_MAX_AMOUNT_FEE = 0

CONDITIONAL_TRANSFER_FIELD_BIT_LENGTHS = {
    "asset_id": 250,
    "receiver_public_key": 251,
    "position_id": 64,
    "condition": 251,
    "quantums_amount": 64,
    "nonce": 32,
    "expiration_epoch_hours": 32,
}

ORDER_FIELD_BIT_LENGTHS = {
    "asset_id_synthetic": 128,
    "asset_id_collateral": 250,
    "asset_id_fee": 250,
    "quantums_amount": 64,
    "nonce": 32,
    "position_id": 64,
    "expiration_epoch_hours": 32,
}

WITHDRAWAL_FIELD_BIT_LENGTHS = {
    "asset_id": 250,
    "position_id": 64,
    "nonce": 32,
    "quantums_amount": 64,
    "expiration_epoch_hours": 32,
}

ORACLE_PRICE_FIELD_BIT_LENGTHS = {
    "asset_name": 128,
    "oracle_name": 40,
    "price": 120,
    "timestamp_epoch_seconds": 32,
}
