# Regional radio safety

LoRa commonly uses unlicensed ISM bands, but those bands still have rules. Frequency, transmit power, antenna gain and duty cycle vary by region and by network operator.

LoRaPulse includes conservative profiles for planning:

| Profile | Default frequency | Daily uplink planning budget | Notes |
| --- | --- | --- | --- |
| EU868 | 868.1 MHz | 30 s/node/day | Conservative TTN-style fair-use planning |
| US915 | 915.0 MHz | 60 s/node/day | Planning profile only; verify FCC/network requirements |
| AU915 | 915.0 MHz | 60 s/node/day | Planning profile only; verify ACMA/network requirements |
| AS923 | 923.2 MHz | 30 s/node/day | Country-specific parameters vary |

These profiles are not legal advice. Treat them as guardrails for development and simulation, not as certification evidence.
