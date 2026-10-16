import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app
from app.services import get_learning_scenarios

client = TestClient(app)


def test_payment_mismatch_warning():
    response = client.post(
        "/api/check-payment",
        json={"intended_amount": "500", "entered_amount": "5000", "recipient_name": "Asha Sharma"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "verify amount"
    assert any("₹500" in message and "₹5,000" in message for message in body["warnings"])


def test_payment_match_has_no_warning():
    response = client.post(
        "/api/check-payment",
        json={"intended_amount": "500", "entered_amount": "500", "recipient_name": "Asha Sharma"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "safe to proceed"
    assert body["warnings"] == []


def test_negative_amount_validation_error():
    response = client.post(
        "/api/check-payment",
        json={"intended_amount": "-500", "entered_amount": "500", "recipient_name": "Asha Sharma"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_safe_to_continue"] is False
    assert any("negative" in warning.lower() for warning in body["warnings"])


def test_otp_plus_suspension_message_warns():
    response = client.post(
        "/api/analyze-message",
        json={
            "message": "URGENT: Your account is suspended. Send the OTP now to reactivate your account before midnight."
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["risk_category"] == "High Concern"
    assert any("OTP" in warning or "OTP, PIN" in warning for warning in body["warning_signs"])
    assert any("suspension" in item.lower() or "account" in item.lower() for item in body["evidence_from_message"])


def test_ordinary_bill_reminder_not_auto_flagged():
    response = client.post(
        "/api/analyze-message",
        json={"message": "Your electricity bill is due today. Please use the official app to pay the bill before 6 PM."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["risk_category"] == "Low Apparent Concern"
    assert body["warning_signs"] == []


def test_unavailable_model_returns_explicit_fallback():
    response = client.post(
        "/api/analyze-message",
        json={"message": "Your account needs activity update. Share the OTP to restore access."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ai_status"] == "AI analysis unavailable"
    assert "AI analysis unavailable" in body["limitations"]


def test_malformed_ai_response_is_caught(monkeypatch):
    from app import services

    def fake_call(*args, **kwargs):
        return {"warning_signs": ["fake"]}

    monkeypatch.setattr(services, "call_model_for_message", fake_call)
    response = client.post("/api/analyze-message", json={"message": "Check this message for scam signs."})
    assert response.status_code == 200
    body = response.json()
    assert body["ai_status"] == "AI analysis unavailable"


def test_quiz_scenarios_are_valid():
    scenarios = get_learning_scenarios()
    assert len(scenarios) == 5
    for item in scenarios:
        assert item["correct_answer"] in item["choices"]
        assert item["explanation"]
