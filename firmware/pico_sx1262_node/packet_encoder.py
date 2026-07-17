# MicroPython-friendly compact packet encoder stub.
# Replace the print-based demo flow with the board-specific SX1262 send call.

import json


def encode_packet(node_id, kind, battery, payload):
    return json.dumps({
        "node": node_id,
        "kind": kind,
        "battery": battery,
        "payload": payload,
    }, separators=(",", ":"))
