from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .airtime_budget import AirTimeBudget, estimate_lora_airtime_seconds
from .packet_schema import MessageType, TelemetryPacket, compress_observation
from .privacy_filters import PrivacyFilter


class RouteAction(str, Enum):
    SEND_LORA = "send_lora"
    QUEUE = "queue"
    ESCALATE_4G = "escalate_4g"
    DROP_DUPLICATE = "drop_duplicate"
    STORE_LOCAL = "store_local"
    BLOCKED_PRIVACY = "blocked_privacy"


@dataclass(frozen=True)
class Event:
    node_id: str
    kind: str
    priority: int
    battery: int
    payload: dict[str, Any]
    size_hint_bytes: int | None = None

    @property
    def fingerprint(self) -> str:
        body = json.dumps({"node": self.node_id, "kind": self.kind, "payload": self.payload}, sort_keys=True)
        return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class RouteDecision:
    action: RouteAction
    reason: str
    packet: TelemetryPacket | None = None
    airtime_seconds: float = 0.0


MESSAGE_MAP = {
    "heartbeat": MessageType.HEARTBEAT,
    "sensor_summary": MessageType.SENSOR_SUMMARY,
    "alert": MessageType.ALERT,
    "location": MessageType.LOCATION_BEACON,
    "location_beacon": MessageType.LOCATION_BEACON,
    "session_summary": MessageType.SESSION_SUMMARY,
    "device_fault": MessageType.DEVICE_FAULT,
    "fault": MessageType.DEVICE_FAULT,
}


class EventRouter:
    def __init__(self, budget: AirTimeBudget, max_lora_payload_bytes: int | None = None, duplicate_cache_size: int = 512, privacy_filter: PrivacyFilter | None = None) -> None:
        self.budget = budget
        self.max_lora_payload_bytes = max_lora_payload_bytes or budget.region.max_payload_bytes
        self.duplicate_cache_size = duplicate_cache_size
        self.privacy_filter = privacy_filter or PrivacyFilter()
        self._recent: list[str] = []

    def route(self, event: Event, spreading_factor: int = 9) -> RouteDecision:
        sensitive = self.privacy_filter.find_sensitive(event.payload)
        if sensitive:
            return RouteDecision(RouteAction.BLOCKED_PRIVACY, f"blocked sensitive fields: {', '.join(sensitive)}")
        if event.fingerprint in self._recent:
            return RouteDecision(RouteAction.DROP_DUPLICATE, "duplicate event suppressed")
        self._remember(event.fingerprint)

        msg_type = MESSAGE_MAP.get(event.kind, MessageType.SENSOR_SUMMARY)
        compact_payload = compress_observation(event.payload) or event.payload
        packet = TelemetryPacket(event.node_id, msg_type, event.battery, compact_payload).with_checksum()
        encoded_size = len(json.dumps(compact_payload, separators=(",", ":")).encode("utf-8")) if event.size_hint_bytes is None else event.size_hint_bytes

        if encoded_size > self.max_lora_payload_bytes and event.priority < 5:
            return RouteDecision(RouteAction.ESCALATE_4G, "payload too large for LoRa; use high-bandwidth backhaul", packet)

        airtime = estimate_lora_airtime_seconds(min(encoded_size, 255), spreading_factor=spreading_factor)
        if event.priority >= 5:
            self.budget.record_uplink(event.node_id, min(airtime, self.budget.remaining_seconds(event.node_id)))
            return RouteDecision(RouteAction.SEND_LORA, "critical priority event sent immediately", packet, airtime)
        if self.budget.can_send(event.node_id, airtime):
            self.budget.record_uplink(event.node_id, airtime)
            return RouteDecision(RouteAction.SEND_LORA, "within airtime budget", packet, airtime)
        if event.priority >= 3:
            return RouteDecision(RouteAction.QUEUE, "airtime budget exhausted; queued for retry", packet, airtime)
        return RouteDecision(RouteAction.STORE_LOCAL, "low priority event stored locally", packet, airtime)

    def _remember(self, fingerprint: str) -> None:
        self._recent.append(fingerprint)
        if len(self._recent) > self.duplicate_cache_size:
            del self._recent[: len(self._recent) - self.duplicate_cache_size]
