from lorapulse.packet_schema import MessageType, PacketError, TelemetryPacket, compress_observation


def test_packet_roundtrip_with_checksum():
    packet = TelemetryPacket("node-01", MessageType.HEARTBEAT, 91, {"bat": 91}).with_checksum()
    decoded = TelemetryPacket.decode_json(packet.encode_json())
    assert decoded.node_id == "node-01"
    assert decoded.message_type == MessageType.HEARTBEAT
    assert decoded.payload["bat"] == 91


def test_checksum_rejects_tampering():
    packet = TelemetryPacket("node-01", MessageType.HEARTBEAT, 91, {"bat": 91}).with_checksum()
    raw = packet.encode_json().decode("utf-8").replace('"bat":91', '"bat":10')
    try:
        TelemetryPacket.decode_json(raw)
    except PacketError as exc:
        assert "checksum" in str(exc)
    else:
        raise AssertionError("tampered packet should fail")


def test_compress_observation_creates_semantic_payload():
    compact = compress_observation({"temperature": [28.1, 28.2, 29.0], "battery": 62, "session_events": ["start", "complete"], "faults": []})
    assert compact["tr"] == "rising"
    assert compact["bat"] == 62
    assert compact["sess"] == 1
    assert compact["fault"] == 0
