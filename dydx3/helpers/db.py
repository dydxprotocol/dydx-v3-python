import uuid

NAMESPACE = uuid.UUID('0f9da948-a6fb-4c45-9edc-4685c3f3317d')


def get_user_id(address):
    return str(uuid.uuid5(NAMESPACE, address))


def get_account_id(
    address,
    accountNumber=0,
):
    return str(
        uuid.uuid5(
            NAMESPACE,
            get_user_id(address.lower()) + str(accountNumber),
        ),
    )
