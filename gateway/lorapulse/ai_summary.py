from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable

from .storage import StoredEvent


def summarize_events(events: Iterable[StoredEvent]) -> str:
    events = list(events)
    if not events:
        return "No telemetry events were recorded."
    by_node: dict[str, list[StoredEvent]] = defaultdict(list)
    actions: Counter[str] = Counter()
    faults = alerts = sessions = 0
    low_battery_nodes: set[str] = set()
    for event in events:
        by_node[event.node_id].append(event)
        actions[event.route_action] += 1
        payload = event.payload
        faults += int(payload.get("fault", payload.get("faults", 0)) or 0)
        alerts += 1 if event.message_type == 3 else 0
        sessions += int(payload.get("sess", payload.get("sessions", 0)) or 0)
        battery = payload.get("bat", payload.get("battery"))
        if isinstance(battery, int) and battery < 20:
            low_battery_nodes.add(event.node_id)
    top_nodes = ", ".join(f"{node} ({len(items)})" for node, items in sorted(by_node.items()))
    summary = [
        f"Recorded {len(events)} telemetry events across {len(by_node)} node(s): {top_nodes}.",
        "Routing decisions: " + ", ".join(f"{k}={v}" for k, v in sorted(actions.items())) + ".",
    ]
    if sessions:
        summary.append(f"Session activity was observed in {sessions} completed or summarised session event(s).")
    if faults or alerts:
        summary.append(f"Attention required: {faults} fault marker(s) and {alerts} alert packet(s) were recorded.")
    else:
        summary.append("No fault or alert packets were recorded in this window.")
    if low_battery_nodes:
        summary.append("Low battery warning for: " + ", ".join(sorted(low_battery_nodes)) + ".")
    return " ".join(summary)
