import json

import requests

from dydx3.errors import DydxApiError
from dydx3.helpers.request_helpers import remove_nones

requests.get

class _RequestManager:

    _session = None
    api_timeout = None

    def _set_session(self):
        self._session = requests.session()
        self._session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'dydx/python',
        })

    def request(self, uri, method, headers=None, data_values={}):
        response = self.send_request(
            uri,
            method,
            headers,
            data=json.dumps(
                remove_nones(data_values)
            ),
            timeout=self.api_timeout
        )
        if not str(response.status_code).startswith('2'):
            raise DydxApiError(response)
        if response.content:
            return response.json()
        return '{}'

    def send_request(self, uri, method, headers=None, **kwargs):
        if not _RequestManager._session:
            self._set_session()
        return getattr(self._session, method)(uri, headers=headers, **kwargs)
