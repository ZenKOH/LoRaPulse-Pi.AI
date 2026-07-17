from lorapulse.ai_summary import summarize_events
from lorapulse.storage import StoredEvent


def test_summary_mentions_nodes_and_faults():
    text = summarize_events([
        StoredEvent(1, "node-a", 5, "2026-01-01T00:00:00Z", {"sess": 1, "fault": 0, "bat": 80}, "send_lora"),
        StoredEvent(2, "node-b", 6, "2026-01-01T00:01:00Z", {"fault": 1, "bat": 15}, "send_lora"),
    ])
    assert "2 telemetry events" in text
    assert "node-a" in text and "node-b" in text
    assert "Low battery" in text
