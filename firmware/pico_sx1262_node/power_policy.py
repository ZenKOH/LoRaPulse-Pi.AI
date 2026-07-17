# MicroPython power policy stub.

DEFAULT_SLEEP_SECONDS = 300
CRITICAL_RETRY_SECONDS = 30


def next_sleep_seconds(priority):
    return CRITICAL_RETRY_SECONDS if priority >= 5 else DEFAULT_SLEEP_SECONDS
