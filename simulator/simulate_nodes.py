from __future__ import annotations

from collections import Counter

from lorapulse.airtime_budget import AirTimeBudget, get_region_profile
from lorapulse.event_router import Event, EventRouter


def simulate(nodes: int = 4, events: int = 40, region: str = "EU868") -> dict[str, object]:
    budget = AirTimeBudget(get_region_profile(region))
    router = EventRouter(budget)
    actions: Counter[str] = Counter()
    airtime = 0.0
    for idx in range(events):
        node = f"node-{idx % nodes:02d}"
        event = Event(
            node_id=node,
            kind="session_summary" if idx % 5 == 0 else "sensor_summary",
            priority=3 if idx % 7 == 0 else 1,
            battery=max(5, 100 - idx),
            payload={
                "temperature": [24.0 + idx * 0.01, 24.2 + idx * 0.01, 24.5 + idx * 0.01],
                "session_events": ["start", "complete"] if idx % 5 == 0 else [],
                "faults": ["low_battery"] if idx % 33 == 0 and idx > 0 else [],
                "rssi": -95 - (idx % 20),
            },
        )
        decision = router.route(event)
        actions[decision.action.value] += 1
        airtime += decision.airtime_seconds
    return {
        "nodes": nodes,
        "events": events,
        "region": region,
        "actions": dict(actions),
        "estimated_airtime_seconds": round(airtime, 4),
        "remaining_by_node": {f"node-{i:02d}": round(budget.remaining_seconds(f"node-{i:02d}"), 4) for i in range(nodes)},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(simulate(), indent=2))
