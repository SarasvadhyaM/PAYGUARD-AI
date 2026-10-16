# PayGuard AI

PayGuard AI is a functional prototype for safer digital payments. It helps users pause, understand, and verify suspicious payment messages before they act.

Tagline: Pause. Understand. Verify. Pay Safely.

## Overview

This prototype combines:
- React + Vite for the user interface
- Python + FastAPI for the API layer
- Deterministic rule-based scam detection as the primary safety layer
- Optional AI analysis using a configurable open-weight model provider when available
- Beginner-friendly safety guidance, payment checks, and an offline learning quiz

## Goals

- Help elderly, first-time, rural, and low-digital-literacy users spot suspicious payment requests
- Prevent mistakes such as OCR-like extra-zero transfers and missing recipients
- Encourage verification through official bank or app channels
- Offer a safe, accessible UI without requiring real payment actions

## Project Structure

```text
codetrio/
├── README.md
├── .env.example
├── .gitignore
├── LICENSES/
│   ├── code-license.txt
│   └── model-license.txt
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── llm_client.py
│   │   ├── main.py
│   │   ├── rule_engine.py
│   │   ├── schemas.py
│   │   └── services.py
│   ├── requirements.txt
│   └── tests/
│       └── test_api.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── styles.css
│   │   └── ...
│   └── dist/
```

## Installation

### 1) Backend

```bash
cd D:\codetrio
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

### 2) Frontend

```bash
cd D:\codetrio\frontend
npm install
```

### 3) Environment variables

Copy the sample environment file:

```bash
copy .env.example .env
```

Then configure values as needed:

```env
DEBUG=false
ALLOWED_MESSAGE_LENGTH=600
LLM_PROVIDER=none
LLM_MODEL=gpt-oss:20b
LLM_API_BASE=http://localhost:11434
LLM_API_KEY=
LLM_API_KEY_HEADER=Authorization
VITE_API_BASE_URL=http://localhost:8000
```

## Model Configuration

The application is intentionally configurable by provider and model name.

Examples:
- Ollama: set `LLM_PROVIDER=ollama`, `LLM_API_BASE=http://localhost:11434`, `LLM_MODEL=llama3.2:latest`
- Remote hosted model: set `LLM_PROVIDER=openai-like`, `LLM_API_BASE=https://your-endpoint`, `LLM_API_KEY=...`, `LLM_MODEL=model-name`

Important:
- The backend never stores PINs, OTPs, or passwords.
- The app treats incoming message text as untrusted data.
- If no model is configured, the app uses the deterministic rule-based fallback and clearly marks the result as `AI analysis unavailable`.
- No credentials are committed to the repository.

## Running the App

### Backend

```bash
cd D:\codetrio
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd D:\codetrio\frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

The frontend expects the API at `http://localhost:8000` unless `VITE_API_BASE_URL` is changed.

## API Overview

### GET /api/health
Returns service health status.

### POST /api/analyze-message
Input:
```json
{
  "message": "URGENT: Your account is suspended. Send OTP now."
}
```

Output fields:
- `risk_category`
- `warning_signs`
- `evidence_from_message`
- `explanation`
- `recommended_actions`
- `educational_tip`
- `limitations`
- `ai_status`

### POST /api/check-payment
Input:
```json
{
  "intended_amount": "500",
  "entered_amount": "5000",
  "recipient_name": "Asha Sharma"
}
```

Validates empty inputs, negatives, invalid values, mismatches, and missing recipients.

### POST /api/ask-safety
Input:
```json
{
  "question": "I received a message asking for an OTP. What should I do?"
}
```

Returns a beginner-friendly answer and points users to official bank channels.

### GET /api/learning-scenarios
Returns five offline learning scenarios with choices, the correct answer, explanation, and score tracking.

## Architecture Notes

The project keeps business logic separate from route handling:
- `app.main` defines the FastAPI routes and CORS setup
- `app.services` contains business logic
- `app.rule_engine` contains deterministic checks and validation
- `app.llm_client` handles model calls and malformed-output protection
- `app.schemas` includes Pydantic validation

This separation makes the app easier to test and safer to extend.

## Safety and Privacy Notes

- Synthetic data only
- No real payment processing occurs
- No storage of PINs, OTPs, or passwords
- The API does not log full messages
- The app is advisory-only and does not claim fraud-detection guarantees
- Users are redirected to official app or bank channels whenever a risk is present

## Known Limitations

- Rule-based checks are heuristic and not a guarantee of fraud or safety
- AI output is optional and only used when a provider is configured
- Voice input depends on browser support
- The app is a prototype meant for learning and demonstration
- Real open-weight inference was not successfully tested in this environment because no model endpoint was configured and run

## Tests

The required behavior is covered by backend tests in `backend/tests/test_api.py`.

Run:

```bash
cd D:\codetrio
.\.venv\Scripts\python.exe -m pytest backend/tests/test_api.py -q
```

Verified results at the time of writing:
- 8 passed

Frontend production build:

```bash
cd D:\codetrio\frontend
npm run build
```

Verified result:
- Vite build succeeded

## Demo Script

1. Open the frontend app in a browser.
2. Go to the Scam Analyzer page.
3. Load an example suspicious message or paste your own.
4. Review the warning signs and recommended actions.
5. Switch to Payment Checker and compare different intended vs entered amounts.
6. Try the Safety Assistant with a question about OTPs or QR codes.
7. Open Learn Safety and complete the quiz to test understanding.
8. Explain that the tool is advisory and asks users to verify via official channels.

## GitHub Publishing Steps

```bash
git init
git add .
git commit -m "Initial PayGuard AI prototype"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

## Licenses

- Code license: `LICENSES/code-license.txt`
- Model license: `LICENSES/model-license.txt`

## Honest Statement on Real Open-Weight Inference

Real open-weight inference was not successfully tested in this environment. The app is built to use configurable open-weight model providers, but no actual provider or model endpoint was configured and run during this prototype cycle. The rule-based logic was fully exercised and verified, while AI output remains a graceful fallback rather than a claimed real-model result.
