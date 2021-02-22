from web3 import Web3

from dydx3.constants import NETWORK_ID_MAINNET
from dydx3.constants import SIGNATURE_TYPE_NO_PREPEND
from dydx3.eth_signing import util
from dydx3.eth_signing.sign_off_chain_action import SignOffChainAction

# On mainnet, include an extra onlySignOn parameter.
EIP712_ONBOARDING_ACTION_STRUCT_STRING = (
    'dYdX(' +
    'string action,' +
    'string onlySignOn' +
    ')'
)
EIP712_ONBOARDING_ACTION_STRUCT_STRING_TESTNET = (
    'dYdX(' +
    'string action' +
    ')'
)

ONLY_SIGN_ON_DOMAIN_MAINNET = 'https://trade.dydx.exchange'


class SignOnboardingAction(SignOffChainAction):

    def get_hash(
        self,
        action,
    ):
        # On mainnet, include an extra onlySignOn parameter.
        if self.network_id == NETWORK_ID_MAINNET:
            eip_712_struct_str = EIP712_ONBOARDING_ACTION_STRUCT_STRING
        else:
            eip_712_struct_str = EIP712_ONBOARDING_ACTION_STRUCT_STRING_TESTNET

        data = [
            [
                'bytes32',
                'bytes32',
            ],
            [
                util.hash_string(eip_712_struct_str),
                util.hash_string(action),
            ],
        ]

        # On mainnet, include an extra onlySignOn parameter.
        if self.network_id == NETWORK_ID_MAINNET:
            data[0].append('bytes32')
            data[1].append(util.hash_string(ONLY_SIGN_ON_DOMAIN_MAINNET))

        struct_hash = Web3.solidityKeccak(*data)
        return self.get_eip712_hash(struct_hash)

    def sign(
        self,
        signer_address,
        **message,
    ):
        '''Create an EIP 712 typed signature using a web3 provider.

        TODO: Implement in a general way.
        '''
        # On mainnet, include an extra onlySignOn parameter.
        if self.network_id == NETWORK_ID_MAINNET:
            eip_712_message = get_eip_712_message_mainnet(message['action'])
        else:
            eip_712_message = get_eip_712_message_testnet(
                message['action'],
                self.network_id,
            )

        raw_signature = self.signer.sign_typed_data(
            eip_712_message,
            signer_address,
        )
        typed_signature = util.create_typed_signature(
            raw_signature,
            SIGNATURE_TYPE_NO_PREPEND,
        )
        return typed_signature


# TODO: Implement in a general way.
def get_eip_712_message_mainnet(action):
    return {
        "types": {
            "EIP712Domain": [
                {
                    "name": "name",
                    "type": "string",
                },
                {
                    "name": "version",
                    "type": "string",
                },
                {
                    "name": "chainId",
                    "type": "uint256",
                }
            ],
            "dYdX": [
                {
                    "type": "string",
                    "name": "action",
                },
                {
                    "type": "string",
                    "name": "onlySignOn",
                }
            ]
        },
        "domain": {
            "name": "dYdX",
            "version": "1.0",
            "chainId": 1,
        },
        "primaryType": "dYdX",
        "message": {
            "action": action,
            "onlySignOn": "https://trade.dydx.exchange",
        }
    }


# TODO: Implement in a general way.
def get_eip_712_message_testnet(action, network_id):
    return {
        "types": {
            "EIP712Domain": [
                {
                    "name": "name",
                    "type": "string",
                },
                {
                    "name": "version",
                    "type": "string",
                },
                {
                    "name": "chainId",
                    "type": "uint256",
                }
            ],
            "dYdX": [
                {
                    "type": "string",
                    "name": "action",
                },
            ]
        },
        "domain": {
            "name": "dYdX",
            "version": "1.0",
            "chainId": network_id,
        },
        "primaryType": "dYdX",
        "message": {
            "action": action,
        }
    }
