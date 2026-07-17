from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class TelemetryProfile:
    name: str
    region: str
    node_type: str
    allowed_event_types: list[str]
    privacy_mode: str = "strict"
    max_payload_bytes: int | None = None
    defaults: dict[str, Any] | None = None


def load_profile(path: str | Path) -> TelemetryProfile:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return TelemetryProfile(
        name=str(data["name"]),
        region=str(data.get("region", "EU868")),
        node_type=str(data.get("node_type", "generic")),
        allowed_event_types=list(data.get("allowed_event_types", [])),
        privacy_mode=str(data.get("privacy_mode", "strict")),
        max_payload_bytes=data.get("max_payload_bytes"),
        defaults=dict(data.get("defaults", {})),
    )
