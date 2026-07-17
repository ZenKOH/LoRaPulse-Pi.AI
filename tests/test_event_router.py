from lorapulse.airtime_budget import AirTimeBudget, get_region_profile
from lorapulse.event_router import Event, EventRouter, RouteAction


def test_router_sends_compact_event_within_budget():
    router = EventRouter(AirTimeBudget(get_region_profile("EU868")))
    decision = router.route(Event("rehab-01", "session_summary", 3, 80, {"temperature": [24, 24.1], "session_events": ["start", "complete"], "faults": []}))
    assert decision.action == RouteAction.SEND_LORA
    assert decision.packet is not None


def test_router_blocks_private_payload():
    router = EventRouter(AirTimeBudget(get_region_profile("EU868")))
    decision = router.route(Event("rehab-01", "session_summary", 3, 80, {"patient_name": "Jane Doe", "sessions": 1}))
    assert decision.action == RouteAction.BLOCKED_PRIVACY


def test_router_suppresses_duplicate():
    router = EventRouter(AirTimeBudget(get_region_profile("EU868")))
    event = Event("node-1", "heartbeat", 1, 90, {"battery": 90})
    first = router.route(event)
    second = router.route(event)
    assert first.action == RouteAction.SEND_LORA
    assert second.action == RouteAction.DROP_DUPLICATE


def test_large_noncritical_payload_escalates():
    router = EventRouter(AirTimeBudget(get_region_profile("EU868")), max_lora_payload_bytes=40)
    decision = router.route(Event("node-1", "sensor_summary", 1, 90, {"blob": "x" * 200}, size_hint_bytes=200))
    assert decision.action == RouteAction.ESCALATE_4G
