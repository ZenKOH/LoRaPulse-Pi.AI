from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .packet_schema import TelemetryPacket


@dataclass
class StoredEvent:
    id: int
    node_id: str
    message_type: int
    timestamp: str
    payload: dict[str, Any]
    route_action: str


class EventStore:
    def __init__(self, path: str | Path = "lorapulse.db") -> None:
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT NOT NULL,
                message_type INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                payload TEXT NOT NULL,
                route_action TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def add_packet(self, packet: TelemetryPacket, route_action: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO events (node_id, message_type, timestamp, payload, route_action) VALUES (?, ?, ?, ?, ?)",
            (packet.node_id, int(packet.message_type), packet.timestamp, json.dumps(packet.payload, sort_keys=True), route_action),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def list_events(self, limit: int = 100) -> list[StoredEvent]:
        rows = self.conn.execute(
            "SELECT id, node_id, message_type, timestamp, payload, route_action FROM events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [StoredEvent(row[0], row[1], row[2], row[3], json.loads(row[4]), row[5]) for row in rows]

    def close(self) -> None:
        self.conn.close()
