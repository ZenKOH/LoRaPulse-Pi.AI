# Payload design

LoRaPulse payloads should be small, deterministic, checksum-protected, privacy-safe, semantic rather than raw, and tolerant of packet loss.

## Good payload

```json
{"t":"summary","bat":78,"sess":9,"fault":0,"rssi":-104}
```

## Bad payload

```json
{"patient_name":"Jane Doe","therapy_notes":"...","raw_samples":[...]}
```

The default privacy filter blocks patient names, email addresses, phone numbers, home addresses, medical record numbers and free-text clinical notes.
