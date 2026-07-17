# RP2350/Perpetuo-style LoRaWAN node placeholder.
# Integrate with the board vendor's LoRaWAN firmware or MicroPython stack.

PROFILE = {
    "region": "EU868",
    "default_frequency_mhz": 868.1,
    "otaa": True,
    "confirmed_uplinks": False,
}


def main():
    print("LoRaWAN profile", PROFILE)


if __name__ == "__main__":
    main()
