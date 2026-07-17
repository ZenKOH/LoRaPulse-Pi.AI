from lorapulse.privacy_filters import PrivacyFilter


def test_privacy_filter_finds_sensitive_fields():
    filt = PrivacyFilter()
    hits = filt.find_sensitive({"email": "person@example.com", "payload": {"therapy_notes": "patient did well"}})
    assert "email" in hits
    assert "payload.therapy_notes" in hits


def test_privacy_filter_sanitizes_payload():
    filt = PrivacyFilter()
    clean = filt.sanitize({"sessions": 4, "patient_name": "Jane", "note": "ok"})
    assert clean == {"sessions": 4, "note": "ok"}
