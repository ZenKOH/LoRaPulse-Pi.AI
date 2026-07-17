# Architecture

LoRaPulse-Pi.AI is split into three layers.

## Node layer

Pico/RP2350-class nodes sample sensors, detect local events, reduce noisy readings into compact facts, and transmit small packets over LoRa or LoRaWAN.

## Gateway layer

A Raspberry Pi receives packets, validates checksums, applies airtime and privacy policies, stores events locally, renders summaries, and escalates large or urgent payloads over 4G/Wi-Fi/Ethernet.

## Policy layer

The policy layer decides whether to transmit, queue, aggregate, suppress, store locally, or use high-bandwidth backhaul.

```text
raw sensor data -> semantic compression -> privacy filter -> packet schema -> airtime budget -> route decision
```

The design keeps expensive or sensitive processing at the gateway and keeps low-power nodes simple.
