import re
from typing import Dict, List, Tuple


def _normalize_number(value: str) -> float:
    cleaned = value.replace(",", "").replace("₹", "").replace("Rs", "").replace("INR", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return float("nan")


def get_rule_based_warning_signs(message: str) -> Tuple[List[str], List[str], str, List[str]]:
    text = message.lower()
    warning_signs: List[str] = []
    evidence: List[str] = []
    risk_category = "Low Apparent Concern"
    recommended_actions = [
        "Pause and verify the message through the official source or app you trust.",
        "Do not click unknown links or share OTP, PIN, or password details.",
        "If you are unsure, contact the sender or your bank using an official number."
    ]

    patterns = {
        "otp_request": [
            "otp", "one-time password", "pin", "security code", "verification code"
        ],
        "urgency": [
            "urgent", "immediately", "now", "within 10 minutes", "last chance"
        ],
        "prize": ["won", "lucky draw", "congratulations", "cashback reward", "free prize", "gift voucher"],
        "cashback": ["cashback", "refund", "reimbursement", "bonus", "extra money"],
        "unknown_app": ["upi app", "new app", "payment app", "install this app", "download link"],
        "unverified_link": ["click here", "bit.ly", "tinyurl", "shorturl", "open this link", "tap link"],
        "qr_instruction": ["scan qr", "scan this qr code", "qr code to pay", "pay via qr"],
        "suspension": ["suspended", "blocked", "account frozen", "service suspended", "security alert"]
    }

    if any(token in text for token in patterns["otp_request"]):
        warning_signs.append("Requests OTP, PIN, or verification code")
        evidence.append("Message asks for an OTP, PIN, or verification code.")
    if any(token in text for token in patterns["urgency"]):
        warning_signs.append("Creates urgency or pressure")
        evidence.append("Message creates urgency and pushes immediate action.")
    if any(token in text for token in patterns["prize"]):
        warning_signs.append("Claims a prize or reward")
        evidence.append("Message claims a prize, reward, or lucky draw.")
    if any(token in text for token in patterns["cashback"]):
        warning_signs.append("Promises unrealistic cashback or refund")
        evidence.append("Message promises unrealistic cashback or refund benefits.")
    if any(token in text for token in patterns["unknown_app"]):
        warning_signs.append("Pushes an unknown or unofficial app")
        evidence.append("Message asks the user to install or use an unknown payment app.")
    if any(token in text for token in patterns["unverified_link"]):
        warning_signs.append("Uses an unverified link")
        evidence.append("Message tells the user to click or open an unverified link.")
    if any(token in text for token in patterns["qr_instruction"]):
        warning_signs.append("Requests a QR payment without verification")
        evidence.append("Message instructs scanning a QR code to complete a payment.")
    if any(token in text for token in patterns["suspension"]):
        warning_signs.append("Threatens account suspension")
        evidence.append("Message threatens account locking or suspension.")

    if not warning_signs:
        risk_category = "Low Apparent Concern"
        explanation = "This message does not show obvious scam indicators based on the rule checks. A low score here is not a guarantee of safety."
        evidence = []
    elif len(warning_signs) == 1:
        risk_category = "Needs Verification"
        explanation = "The message contains one suspicious pattern that should be checked before acting. Use official communication channels to confirm legitimacy."
        recommended_actions.extend([
            "Look for official contact details from the company or bank itself.",
            "Confirm the sender by calling the verified number on the bank or app website."
        ])
    else:
        risk_category = "High Concern"
        explanation = "Multiple scam indicators appear together, such as urgency, reward claims, or payment instructions. Do not pay or share credentials until verified."
        recommended_actions.extend([
            "Do not complete any payment or share OTP, PIN, or password.",
            "Report the message to your bank or local cybercrime helpdesk if needed."
        ])

    if "otp" in text and any(term in text for term in ["suspended", "blocked", "urgent", "immediately"]):
        risk_category = "High Concern"
        warning_signs = list(dict.fromkeys(warning_signs + ["Threatens account suspension and asks for OTP"]))
        evidence.append("The message combines a suspension threat with a request for OTP or verification information.")

    return warning_signs, evidence, risk_category, recommended_actions


def validate_payment(intended_amount_raw: str, entered_amount_raw: str, recipient_name: str) -> Dict[str, object]:
    errors = []
    warnings = []
    intended = _normalize_number(intended_amount_raw)
    entered = _normalize_number(entered_amount_raw)

    if not intended_amount_raw or not intended_amount_raw.strip():
        errors.append("Intended amount is required.")
    if not entered_amount_raw or not entered_amount_raw.strip():
        errors.append("Entered amount is required.")
    if not recipient_name or not recipient_name.strip():
        errors.append("Recipient name is required.")

    if not (str(intended_amount_raw).strip() and re.search(r"\d", intended_amount_raw)):
        errors.append("Enter a valid intended amount.")
    if not (str(entered_amount_raw).strip() and re.search(r"\d", entered_amount_raw)):
        errors.append("Enter a valid entered amount.")

    if not errors:
        if intended < 0 or entered < 0:
            errors.append("Amounts cannot be negative.")
        if not (isinstance(intended, float) and not (isnan := str(intended) == 'nan')):
            errors.append("Intended amount is invalid.")
        if not (isinstance(entered, float) and not (str(entered) == 'nan')):
            errors.append("Entered amount is invalid.")

    if "nan" in str(intended) or "nan" in str(entered):
        errors.append("The amount value is invalid.")

    if not errors:
        if intended != entered:
            warnings.append(f"You intended to pay ₹{int(intended):,} but entered ₹{int(entered):,}. Please verify the amount before proceeding.")
            if intended > 0 and entered > 0:
                if entered / intended >= 10 and intended != 0:
                    warnings.append("Extra-zero or decimal mismatch detected. Double-check the entered amount before paying.")
        if recipient_name.strip() == "":
            errors.append("Recipient is missing. Please review the recipient before continuing.")

    return {
        "errors": errors,
        "warnings": warnings,
        "is_safe_to_continue": not errors,
    }


def validate_safety_question(question: str) -> str:
    lowered = question.lower()
    if any(token in lowered for token in ["pin", "otp", "password"]):
        return "Never share a PIN, OTP, or password. Use official channels such as your bank’s app, website, or customer care number."
    if any(token in lowered for token in ["qr code", "payment link", "refund", "cashback"]):
        return "Pause and verify the request through the official app or bank source before taking any action."
    return "Pause, verify the request through an official and trusted source, and avoid sharing credentials or clicking unknown links."
