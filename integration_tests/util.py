import time


class TimedOutWaitingForCondition(Exception):

    def __init__(self, last_value, expected_value):
        self.last_value = last_value
        self.expected_value = expected_value


def wait_for_condition(fn, expected_value, timeout_s, interval_s=1):
    start = time.time()
    result = fn()
    while result != expected_value:
        if time.time() - start > timeout_s:
            raise TimedOutWaitingForCondition(result, expected_value)
        time.sleep(interval_s)
        if time.time() - start > timeout_s:
            raise TimedOutWaitingForCondition(result, expected_value)
        result = fn()
    return result
