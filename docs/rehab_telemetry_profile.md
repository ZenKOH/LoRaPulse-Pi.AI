# Rehabilitation telemetry profile

The rehabilitation profile is designed for operational telemetry, not clinical records.

Allowed by default:

- session counts;
- device uptime;
- battery status;
- safety flag counts;
- device fault codes;
- gateway connectivity status;
- anonymised utilisation summaries.

Blocked by default:

- patient names;
- home addresses;
- medical record numbers;
- diagnosis notes;
- free-text clinical notes;
- therapist observations that identify a person.

A rural clinic can use this profile to monitor equipment utilisation, device status and safety flags without sending identifiable patient content over LoRa.
