# LoRaPulse-Pi.AI

**Adaptive LoRa + Raspberry Pi edge telemetry for off-grid sensors, field robots, clinics and remote infrastructure.**

LoRaPulse-Pi.AI is a software-first reference stack for low-bandwidth telemetry. It turns noisy edge events into compact, prioritised, regulation-aware packets that can travel over LoRa or LoRaWAN, while the Raspberry Pi gateway stores, filters, summarises and optionally escalates high-bandwidth events over 4G/Wi-Fi/Ethernet.

The project is inspired by Raspberry Pi's survey of LoRa radio devices for Raspberry Pi and Pico-class hardware. The article highlights LoRa's small-packet, long-range profile, region-specific radio rules, Pico/RP2350 LoRa nodes, Raspberry Pi LoRa Bonnets, GPS breakouts, 4G HATs and LoRaWAN concentrators. LoRaPulse focuses on the missing software layer: **what deserves scarce airtime**.

> **Core principle:** do not transmit raw noise. Transmit small, meaningful, privacy-safe operational facts.

## What is included

- Compact packet schema with checksum validation.
- Region profiles for EU868, US915, AU915 and AS923.
- Airtime estimator and daily airtime budget manager.
- Event router for LoRa send / queue / 4G escalation / duplicate suppression / local storage.
- Privacy filter for health and rehabilitation telemetry.
- SQLite gateway event store.
- Deterministic gateway summary engine.
- Simulator for software-only testing.
- MicroPython firmware stubs for Pico SX1262 and RP2350/Perpetuo-style nodes.
- Example deployment profiles for rehabilitation, robotics, environmental monitoring and disaster mesh.
- Pytest suite and GitHub Actions CI.

## Why it matters

LoRa is excellent for long-range, low-power messages, but it is not a general internet pipe. A responsible LoRa system must care about payload size, spreading factor, duty cycle, local regulations, downlink scarcity, duplicate suppression and privacy. LoRaPulse treats the radio channel as a scarce shared resource.

## Quick start

```bash
git clone https://github.com/ZenKOH/LoRaPulse-Pi.AI.git
cd LoRaPulse-Pi.AI
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest -q
```

Run a simulation:

```bash
lorapulse simulate --nodes 4 --events 40 --region EU868
```

Inspect an airtime estimate:

```bash
lorapulse airtime --payload-bytes 32 --spreading-factor 9 --bandwidth 125000
```

Route a sample rehabilitation event:

```bash
lorapulse route --profile examples/rehab_clinic_node.yaml --event '{"node_id":"rehab-03","kind":"session_summary","priority":3,"battery":78,"payload":{"sessions":9,"faults":0}}'
```

## Architecture

```text
Pico / RP2350 LoRa node
  ├── sensors
  ├── local event detector
  ├── privacy-safe payload encoder
  └── LoRa / LoRaWAN radio
          ↓
Raspberry Pi gateway
  ├── LoRa receiver adapter
  ├── packet validator
  ├── airtime budget manager
  ├── event router
  ├── SQLite local store
  ├── deterministic summary engine
  ├── optional dashboard
  └── optional 4G / Wi-Fi / Ethernet backhaul
          ↓
Cloud, local dashboard, CSV export, or TTN integration
```

## Message policy

| Event type | Default behaviour |
| --- | --- |
| Heartbeat | Send low-frequency tiny payload |
| Routine reading | Aggregate locally |
| Threshold warning | Send if airtime budget allows |
| Critical alert | Send immediately, with controlled repeat/backoff |
| Large payload | Cache locally and escalate by 4G/Wi-Fi |
| Duplicate event | Suppress or compress |
| Health-related free text | Block or sanitise by default |

## Safety and compliance

LoRa uses unlicensed ISM bands, but unlicensed does not mean unrestricted. Always check your jurisdiction's frequency, power, duty-cycle and antenna rules before transmitting. LoRaPulse includes conservative policy helpers, but it cannot provide legal compliance guarantees.

Health and rehabilitation profiles are designed for operational telemetry, not clinical records. Do not send patient-identifiable information unless you have implemented appropriate consent, security, encryption and local regulatory controls.

## Repository layout

```text
├── docs/                       # Architecture and deployment guides
├── firmware/                   # MicroPython node examples
├── gateway/lorapulse/          # Python package for gateway logic
├── examples/                   # YAML profiles
├── simulator/                  # Standalone simulation scripts
├── tests/                      # Pytest validation
└── .github/workflows/          # CI
```

## Roadmap

- V0.1: software simulator, packet schema, airtime budgeting, routing, storage and tests.
- V0.2: Pico SX1262 node firmware and Raspberry Pi receiver adapters.
- V0.3: browser dashboard, GPS support and 4G backhaul queue.
- V0.4: LoRaWAN / The Things Network payload decoder examples.
- V0.5: optional encrypted payloads and richer AI-assisted gateway summaries.

## Licence

MIT for software and documentation unless otherwise noted.
