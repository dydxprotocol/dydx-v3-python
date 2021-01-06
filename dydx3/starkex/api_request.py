from collections import namedtuple

from dydx3.starkex.helpers import message_to_hash
from dydx3.starkex.signable import Signable

StarkwareApiRequest = namedtuple(
    'StarkwareApiRequest',
    [
        'iso_timestamp',
        'method',
        'request_path',
        'body',
    ],
)


class SignableApiRequest(Signable):

    def __init__(
        self,
        iso_timestamp,
        method,
        request_path,
        body,
    ):
        message = StarkwareApiRequest(
            iso_timestamp=iso_timestamp,
            method=method,
            request_path=request_path,
            body=body,
        )
        super(SignableApiRequest, self).__init__(message)

    @property
    def message(self):
        return self.message

    def _calculate_hash(self):
        """Calculate the hash of the Starkware ApiRequest."""

        message_string = (
            self._message.iso_timestamp
            + self._message.method
            + self._message.request_path
            + self._message.body
        )
        return message_to_hash(message_string)
