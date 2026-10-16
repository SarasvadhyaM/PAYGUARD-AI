from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class AnalyzeMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=600)

    @field_validator("message")
    @classmethod
    def clean_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Message cannot be empty.")
        return cleaned[:600]


class AnalyzeMessageResponse(BaseModel):
    risk_category: str
    warning_signs: List[str]
    evidence_from_message: List[str]
    explanation: str
    recommended_actions: List[str]
    educational_tip: str
    limitations: str
    ai_status: str = "analysis complete"


class PaymentCheckRequest(BaseModel):
    intended_amount: str = Field(..., min_length=1)
    entered_amount: str = Field(..., min_length=1)
    recipient_name: str = Field(..., min_length=1)


class PaymentCheckResponse(BaseModel):
    status: str
    message: str
    warnings: List[str] = []
    is_safe_to_continue: bool = True


class SafetyQuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=400)


class SafetyQuestionResponse(BaseModel):
    answer: str
    suggested_action: str
    follow_up: str
    ai_status: str = "analysis complete"


class LearningScenario(BaseModel):
    id: int
    title: str
    scenario: str
    choices: List[str]
    correct_answer: str
    explanation: str
    risk_level: str
