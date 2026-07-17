from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class RegionProfile:
    name: str
    uplink_limit_seconds_per_day: float
    downlink_limit_per_day: int
    default_frequency_mhz: float
    max_payload_bytes: int
    notes: str


REGION_PROFILES: dict[str, RegionProfile] = {
    "EU868": RegionProfile("EU868", 30.0, 10, 868.1, 51, "Conservative TTN-style fair access default; verify ETSI/local rules."),
    "US915": RegionProfile("US915", 60.0, 10, 915.0, 51, "Planning profile only; verify FCC and network-server limits."),
    "AU915": RegionProfile("AU915", 60.0, 10, 915.0, 51, "Planning profile only; verify ACMA and network-server limits."),
    "AS923": RegionProfile("AS923", 30.0, 10, 923.2, 51, "Country-specific parameters vary; verify local AS923 plan."),
}


def get_region_profile(name: str) -> RegionProfile:
    key = name.upper()
    if key not in REGION_PROFILES:
        raise KeyError(f"unknown region profile: {name}")
    return REGION_PROFILES[key]


def estimate_lora_airtime_seconds(
    payload_bytes: int,
    spreading_factor: int = 9,
    bandwidth: int = 125_000,
    coding_rate: int = 1,
    preamble_symbols: int = 8,
    explicit_header: bool = True,
    crc_enabled: bool = True,
) -> float:
    """Approximate LoRa time-on-air in seconds for planning and tests."""
    if payload_bytes < 0:
        raise ValueError("payload_bytes must be non-negative")
    if spreading_factor not in range(7, 13):
        raise ValueError("spreading_factor must be from 7 to 12")
    if bandwidth <= 0:
        raise ValueError("bandwidth must be positive")
    sf = spreading_factor
    low_data_rate_optimization = 1 if (sf >= 11 and bandwidth == 125_000) else 0
    header_disabled = 0 if explicit_header else 1
    crc = 1 if crc_enabled else 0
    symbol_time = (2**sf) / bandwidth
    preamble_time = (preamble_symbols + 4.25) * symbol_time
    numerator = 8 * payload_bytes - 4 * sf + 28 + 16 * crc - 20 * header_disabled
    denominator = 4 * (sf - 2 * low_data_rate_optimization)
    payload_symbols = 8 + max(math.ceil(numerator / denominator) * (coding_rate + 4), 0)
    return round(preamble_time + payload_symbols * symbol_time, 4)


@dataclass
class AirTimeBudget:
    region: RegionProfile
    used_seconds_by_node: dict[str, float] = field(default_factory=dict)
    downlinks_by_node: dict[str, int] = field(default_factory=dict)
    budget_date: date = field(default_factory=date.today)

    def reset_if_new_day(self) -> None:
        today = date.today()
        if self.budget_date != today:
            self.used_seconds_by_node.clear()
            self.downlinks_by_node.clear()
            self.budget_date = today

    def remaining_seconds(self, node_id: str) -> float:
        self.reset_if_new_day()
        return max(0.0, self.region.uplink_limit_seconds_per_day - self.used_seconds_by_node.get(node_id, 0.0))

    def can_send(self, node_id: str, airtime_seconds: float) -> bool:
        return airtime_seconds <= self.remaining_seconds(node_id)

    def record_uplink(self, node_id: str, airtime_seconds: float) -> None:
        self.reset_if_new_day()
        self.used_seconds_by_node[node_id] = self.used_seconds_by_node.get(node_id, 0.0) + airtime_seconds

    def can_downlink(self, node_id: str) -> bool:
        self.reset_if_new_day()
        return self.downlinks_by_node.get(node_id, 0) < self.region.downlink_limit_per_day

    def record_downlink(self, node_id: str) -> None:
        if not self.can_downlink(node_id):
            raise RuntimeError("downlink limit exceeded")
        self.downlinks_by_node[node_id] = self.downlinks_by_node.get(node_id, 0) + 1
