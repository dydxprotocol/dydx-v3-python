"""Constants related to creating hashes of Starkware objects."""

ORDER_PREFIX = 3
ORDER_PADDING_BITS = 17
WITHDRAWAL_PADDING_BITS = 49
WITHDRAWAL_PREFIX = 6

ORDER_FIELD_BIT_LENGTHS = {
    "asset_id_synthetic": 128,
    "asset_id_collateral": 250,
    "asset_id_fee": 250,
    "quantums_amount": 64,
    "nonce": 32,
    "position_id": 64,
    "expiration_epoch_seconds": 32,
}

WITHDRAWAL_FIELD_BIT_LENGTHS = {
    "asset_id": 250,
    "position_id": 64,
    "nonce": 32,
    "quantums_amount": 64,
    "expiration_epoch_seconds": 32,
}

ORACLE_PRICE_FIELD_BIT_LENGTHS = {
    "asset_name": 128,
    "oracle_name": 40,
    "price": 120,
    "timestamp_epoch_seconds": 32,
}
