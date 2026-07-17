from __future__ import annotations

import json
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import IntEnum
from typing import Any


class PacketError(ValueError):
    """Raised when a telemetry packet is malformed or fails integrity checks."""


class MessageType(IntEnum):
    HEARTBEAT = 0x01
    SENSOR_SUMMARY = 0x02
    ALERT = 0x03
    LOCATION_BEACON = 0x04
    SESSION_SUMMARY = 0x05
    DEVICE_FAULT = 0x06


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canonical(obj: dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def checksum_for(obj: dict[str, Any]) -> str:
    return f"{zlib.crc32(_canonical(obj)) & 0xFFFFFFFF:08x}"


@dataclass(frozen=True)
class TelemetryPacket:
    node_id: str
    message_type: MessageType
    battery: int
    payload: dict[str, Any]
    timestamp: str = field(default_factory=utc_now_iso)
    schema_version: int = 1
    checksum: str | None = None

    def __post_init__(self) -> None:
        if not self.node_id or len(self.node_id) > 32:
            raise PacketError("node_id must be present and no longer than 32 characters")
        if not 0 <= int(self.battery) <= 100:
            raise PacketError("battery must be an integer percentage from 0 to 100")
        if not isinstance(self.payload, dict):
            raise PacketError("payload must be a dictionary")

    def body_without_checksum(self) -> dict[str, Any]:
        return {
            "v": self.schema_version,
            "node": self.node_id,
            "type": int(self.message_type),
            "battery": int(self.battery),
            "ts": self.timestamp,
            "payload": self.payload,
        }

    def with_checksum(self) -> "TelemetryPacket":
        body = self.body_without_checksum()
        return TelemetryPacket(self.node_id, self.message_type, int(self.battery), self.payload, self.timestamp, self.schema_version, checksum_for(body))

    def to_dict(self) -> dict[str, Any]:
        packet = self.with_checksum() if self.checksum is None else self
        body = packet.body_without_checksum()
        body["crc"] = packet.checksum
        return body

    def encode_json(self) -> bytes:
        return _canonical(self.to_dict())

    @classmethod
    def decode_json(cls, raw: bytes | str) -> "TelemetryPacket":
        try:
            data = json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw)
        except json.JSONDecodeError as exc:
            raise PacketError("packet is not valid JSON") from exc
        required = {"v", "node", "type", "battery", "ts", "payload", "crc"}
        missing = required - data.keys()
        if missing:
            raise PacketError(f"missing packet fields: {sorted(missing)}")
        supplied_crc = str(data.pop("crc"))
        if supplied_crc != checksum_for(data):
            raise PacketError("checksum mismatch")
        try:
            msg_type = MessageType(int(data["type"]))
        except (ValueError, TypeError) as exc:
            raise PacketError("unknown message type") from exc
        return cls(str(data["node"]), msg_type, int(data["battery"]), dict(data["payload"]), str(data["ts"]), int(data["v"]), supplied_crc)


def _trend(values: list[float]) -> str:
    if len(values) < 2:
        return "stable"
    delta = values[-1] - values[0]
    if delta > 0.5:
        return "rising"
    if delta < -0.5:
        return "falling"
    return "stable"


def compress_observation(raw: dict[str, Any]) -> dict[str, Any]:
    """Convert verbose sensor observations into compact semantic telemetry."""
    compact: dict[str, Any] = {}
    temperatures = raw.get("temperature") or raw.get("temperatures")
    if isinstance(temperatures, list) and temperatures:
        nums = [float(v) for v in temperatures if isinstance(v, (int, float))]
        if nums:
            compact["tmp"] = round(sum(nums) / len(nums), 1)
            compact["tr"] = _trend(nums)
    if "battery" in raw:
        compact["bat"] = max(0, min(100, int(raw["battery"])))
    if "rssi" in raw:
        compact["rssi"] = int(raw["rssi"])
    session_events = raw.get("session_events")
    if isinstance(session_events, list):
        compact["sess"] = 1 if "complete" in session_events else 0
    faults = raw.get("faults")
    if isinstance(faults, list):
        compact["fault"] = len(faults)
    if "lat" in raw and "lon" in raw:
        compact["lat"] = round(float(raw["lat"]), 5)
        compact["lon"] = round(float(raw["lon"]), 5)
    return compact
