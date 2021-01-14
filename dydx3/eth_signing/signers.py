import eth_account


class Signer(object):

    def sign(self, message_hash, opt_signer_address):
        '''
        Sign a message hash with an Ethereum key.

        :param message_hash: required
        :type message_hash: HexBytes

        :param opt_signer_address: optional
        :type opt_signer_address: str

        :returns: str
        '''
        raise NotImplementedError()


class SignWithWeb3(Signer):

    def __init__(self, web3):
        self.web3 = web3

    def sign(self, message_hash, opt_signer_address):
        signer_address = opt_signer_address or self.web3.eth.defaultAccount
        if not signer_address:
            raise ValueError(
                'Must set ethereum_address or web3.eth.defaultAccount',
            )
        return self.web3.eth.sign(signer_address, message_hash).hex()


class SignWithKey(Signer):

    def __init__(self, private_key):
        self.address = eth_account.Account.from_key(private_key).address
        self._private_key = private_key

    def sign(self, message_hash, opt_signer_address):
        if (
            opt_signer_address is not None and
            opt_signer_address != self.address
        ):
            raise ValueError(
                'ethereum_address was set but does not match the Ethereum ' +
                'key (eth_private_key / web3_account)',
            )
        return eth_account.Account.sign_message(
            eth_account.messages.encode_defunct(hexstr=message_hash.hex()),
            self._private_key,
        ).signature.hex()
