from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.schemas import AnalyzeMessageRequest, PaymentCheckRequest, SafetyQuestionRequest
from app.services import analyze_message_service, ask_safety_service, check_payment_service, get_learning_scenarios

app = FastAPI(title="PayGuard AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "PayGuard AI"}


@app.post("/api/analyze-message")
def analyze_message(payload: AnalyzeMessageRequest):
    try:
        return analyze_message_service(payload.message)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Unable to analyze message right now.") from exc


@app.post("/api/check-payment")
def check_payment(payload: PaymentCheckRequest):
    try:
        return check_payment_service(payload.intended_amount, payload.entered_amount, payload.recipient_name)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.errors()) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/ask-safety")
def ask_safety(payload: SafetyQuestionRequest):
    try:
        return ask_safety_service(payload.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/learning-scenarios")
def learning_scenarios():
    return get_learning_scenarios()
