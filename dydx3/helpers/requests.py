import json

import requests

from dydx3.errors import DydxApiError
from dydx3.helpers.request_helpers import remove_nones

# TODO: Use a separate session per client instance.
session = requests.session()
session.headers.update({
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'dydx/python',
})


def request(uri, method, headers=None, data_values={}):
    response = send_request(
        uri,
        method,
        headers,
        data=json.dumps(
            remove_nones(data_values)
        )
    )
    if not str(response.status_code).startswith('2'):
        raise DydxApiError(response)
    return response.json() if response.content else '{}'


def send_request(uri, method, headers=None, **kwargs):
    return getattr(session, method)(uri, headers=headers, **kwargs)
