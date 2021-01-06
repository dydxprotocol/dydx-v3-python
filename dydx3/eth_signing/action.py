from dydx3.helpers.request_helpers import json_stringify

ONBOARDING_STATIC_STRING = 'DYDX-ONBOARDING'


def generate_onboarding_action():
    return ONBOARDING_STATIC_STRING


def generate_api_key_action(
    request_path,
    method,
    data={},
):
    return (json_stringify(data) if data else '') + request_path + method
