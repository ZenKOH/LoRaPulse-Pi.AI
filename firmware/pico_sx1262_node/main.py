# MicroPython Pico + SX1262 example node.
# Driver-agnostic stub: replace radio_send with your SX1262 board driver call.

from packet_encoder import encode_packet
from sensors import read_operational_sample
from power_policy import next_sleep_seconds

NODE_ID = "pico-sx1262-01"


def radio_send(payload):
    print("TX", payload)


def loop_once():
    sample = read_operational_sample()
    payload = encode_packet(NODE_ID, "sensor_summary", sample.get("battery", 100), sample)
    radio_send(payload)
    return next_sleep_seconds(priority=1)


if __name__ == "__main__":
    loop_once()
