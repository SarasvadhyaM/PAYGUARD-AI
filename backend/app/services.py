import json
from typing import Any, Dict, List

from app.config import settings
from app.llm_client import LLMOutputMalformedError, LLMUnavailableError, call_model_for_message
from app.rule_engine import get_rule_based_warning_signs, validate_payment, validate_safety_question


required_fields = [
    "risk_category",
    "warning_signs",
    "evidence_from_message",
    "explanation",
    "recommended_actions",
    "educational_tip",
    "limitations",
]


def _merge_llm_and_rule_output(rule_data: Dict[str, Any], llm_data: Dict[str, Any]) -> Dict[str, Any]:
    merged = {
        "risk_category": llm_data.get("risk_category") or rule_data["risk_category"],
        "warning_signs": list(dict.fromkeys((llm_data.get("warning_signs") or []) + (rule_data["warning_signs"] or []))),
        "evidence_from_message": list(dict.fromkeys((llm_data.get("evidence_from_message") or []) + (rule_data["evidence"] or []))),
        "explanation": llm_data.get("explanation") or rule_data["explanation"],
        "recommended_actions": list(dict.fromkeys((llm_data.get("recommended_actions") or []) + (rule_data["recommended_actions"] or []))),
        "educational_tip": llm_data.get("educational_tip") or "Pause, understand the request, and verify through official channels before paying.",
        "limitations": llm_data.get("limitations") or "This is an advisory tool, not a fraud guarantee. AI analysis unavailable if no model is configured.",
    }
    if not llm_data.get("warning_signs"):
        merged["warning_signs"] = rule_data["warning_signs"]
    if not merged["evidence_from_message"]:
        merged["evidence_from_message"] = rule_data["evidence"]
    if not merged["recommended_actions"]:
        merged["recommended_actions"] = rule_data["recommended_actions"]
    return merged


def analyze_message_service(message: str) -> Dict[str, Any]:
    cleaned = message.strip()[: settings.allowed_message_length]
    if not cleaned:
        raise ValueError("Message cannot be empty.")

    warning_signs, evidence, risk_category, recommended_actions = get_rule_based_warning_signs(cleaned)
    rule_data = {
        "warning_signs": warning_signs,
        "evidence": evidence,
        "risk_category": risk_category,
        "explanation": "Based on rule-based checks, this message may need further review. A missing keyword does not guarantee safety.",
        "recommended_actions": recommended_actions,
    }

    try:
        llm_data = call_model_for_message(cleaned)
        for field in required_fields:
            if field not in llm_data:
                raise LLMOutputMalformedError(f"Missing required field in AI output: {field}")
        merged = _merge_llm_and_rule_output(rule_data, llm_data)
        merged["ai_status"] = "AI analysis complete"
        return merged
    except (LLMUnavailableError, LLMOutputMalformedError, Exception):
        fallback = {
            "risk_category": risk_category,
            "warning_signs": warning_signs,
            "evidence_from_message": evidence,
            "explanation": "AI analysis unavailable. Rule-based checks were used instead. A keyword alone is not proof of fraud, and a missing keyword does not make a message safe.",
            "recommended_actions": recommended_actions,
            "educational_tip": "Pause. Understand. Verify. Pay safely.",
            "limitations": "AI analysis unavailable. This advisory tool uses rule-based checks and cannot guarantee fraud detection.",
            "ai_status": "AI analysis unavailable",
        }
        return fallback


def check_payment_service(intended_amount: str, entered_amount: str, recipient_name: str) -> Dict[str, Any]:
    validation = validate_payment(intended_amount, entered_amount, recipient_name)
    errors = validation["errors"]
    warnings = validation["warnings"]
    if errors:
        return {
            "status": "review required",
            "message": "Please fix the highlighted issues before continuing.",
            "warnings": errors,
            "is_safe_to_continue": False,
        }

    if warnings:
        return {
            "status": "verify amount",
            "message": warnings[0],
            "warnings": warnings,
            "is_safe_to_continue": False,
        }

    return {
        "status": "safe to proceed",
        "message": "The amount and recipient look consistent. Please review the recipient and confirm before proceeding.",
        "warnings": [],
        "is_safe_to_continue": True,
    }


def ask_safety_service(question: str) -> Dict[str, Any]:
    answer = validate_safety_question(question)
    return {
        "answer": answer,
        "suggested_action": "Stop, verify through an official bank or brand channel, and do not share credentials.",
        "follow_up": "If you are still unsure, call the official customer care number from the bank app or website.",
        "ai_status": "AI analysis unavailable",
    }


def get_learning_scenarios() -> List[Dict[str, Any]]:
    return [
        {
            "id": 1,
            "title": "Fake cashback alert",
            "scenario": "You receive a message: 'Congratulations! You have won a ₹2,000 cashback. Click this link and pay a small fee to claim your reward.'",
            "choices": ["Ignore it and verify with the official app", "Click the link to claim it", "Pay the fee to speed up the reward", "Share the OTP to confirm identity"],
            "correct_answer": "Ignore it and verify with the official app",
            "explanation": "Fake cashback offers often try to trick people into paying or sharing information. Verify through the actual company or bank app.",
            "risk_level": "High Concern",
        },
        {
            "id": 2,
            "title": "OTP request",
            "scenario": "A stranger says: 'Your account is at risk. Send the OTP you received to verify your identity immediately.'",
            "choices": ["Send the OTP to the caller", "Ask for a proper official reference and call the bank", "Reply with the OTP to prove it is yours", "Ignore the message and share nothing"],
            "correct_answer": "Ask for a proper official reference and call the bank",
            "explanation": "Legitimate banks never ask for OTPs or passwords. Always verify through official bank contact channels.",
            "risk_level": "High Concern",
        },
        {
            "id": 3,
            "title": "Suspicious QR code",
            "scenario": "A shopkeeper asks you to scan a QR code because a payment 'needs to be completed immediately' but the payment amount is unclear.",
            "choices": ["Scan it and pay immediately", "Ask for the invoice and verify the recipient", "Share the QR code with family", "Scan it because it is from a local shop"],
            "correct_answer": "Ask for the invoice and verify the recipient",
            "explanation": "A QR code is not safe by itself. Always verify the recipient and the payment details before scanning or paying.",
            "risk_level": "Needs Verification",
        },
        {
            "id": 4,
            "title": "Fake screenshot",
            "scenario": "You see a screenshot showing a large refund to your account, and the message says you can 'withdraw' it by paying a small processing fee.",
            "choices": ["Pay the fee to get the refund", "Report the screenshot as suspicious and ignore it", "Share your app login to check the refund", "Accept the refund and move faster"],
            "correct_answer": "Report the screenshot as suspicious and ignore it",
            "explanation": "Screenshots can be faked. Never pay a fee to unlock a refund or share login details for a suspicious claim.",
            "risk_level": "High Concern",
        },
        {
            "id": 5,
            "title": "Extra zeros",
            "scenario": "You intended to pay ₹500, but the app shows ₹5,000 for the transfer. The message says 'Just proceed, the amount is correct.'",
            "choices": ["Proceed because the app says it is correct", "Check the amount again and confirm before paying", "Send a smaller amount to test it", "Pay only a few rupees"],
            "correct_answer": "Check the amount again and confirm before paying",
            "explanation": "Extra-zero mistakes are common and dangerous. Always verify the amount and recipient before finalising a payment.",
            "risk_level": "High Concern",
        },
    ]
