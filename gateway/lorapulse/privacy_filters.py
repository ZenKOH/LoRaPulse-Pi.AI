from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

DEFAULT_BLOCKED_KEYS = {
    "patient_name", "name", "email", "phone", "address", "home_address",
    "nric", "ssn", "medical_record_number", "mrn", "diagnosis_notes",
    "therapy_notes", "free_text", "clinician_notes",
}
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")


@dataclass
class PrivacyFilter:
    blocked_keys: set[str] = field(default_factory=lambda: set(DEFAULT_BLOCKED_KEYS))
    block_free_text: bool = True

    def find_sensitive(self, payload: dict[str, Any]) -> list[str]:
        hits: list[str] = []
        self._walk(payload, "", hits)
        return sorted(set(hits))

    def sanitize(self, payload: dict[str, Any]) -> dict[str, Any]:
        clean: dict[str, Any] = {}
        for key, value in payload.items():
            if key.lower() in self.blocked_keys:
                continue
            if isinstance(value, dict):
                clean[key] = self.sanitize(value)
            elif isinstance(value, str):
                if self._looks_sensitive_text(value):
                    continue
                clean[key] = value[:80] if self.block_free_text else value
            else:
                clean[key] = value
        return clean

    def _walk(self, value: Any, path: str, hits: list[str]) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                current = f"{path}.{key}" if path else key
                if key.lower() in self.blocked_keys:
                    hits.append(current)
                self._walk(item, current, hits)
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                self._walk(item, f"{path}[{idx}]", hits)
        elif isinstance(value, str) and self._looks_sensitive_text(value):
            hits.append(path or "text")

    @staticmethod
    def _looks_sensitive_text(text: str) -> bool:
        if EMAIL_RE.search(text) or PHONE_RE.search(text):
            return True
        lowered = text.lower()
        risky_terms = ["patient", "diagnosis", "medication", "home address", "medical record"]
        return any(term in lowered for term in risky_terms)
