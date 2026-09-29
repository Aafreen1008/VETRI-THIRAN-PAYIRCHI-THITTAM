# PocketSmart AI

PocketSmart is a full-stack AI-assisted budget and recommendation planner inspired by the supplied project documentation.

## Features
- Landing page, registration and login
- JWT authentication with Argon2 password hashing
- SQLite persistence for users and recommendation history
- Dashboard with spending summary and quick planner cards
- AI-assisted Home, Party/Event and Jewelry planning
- Deterministic fallback recommendations when Gemini is not configured
- Recommendation detail and history pages
- Product/search links generated from safe search terms
- AI chat assistant for budgeting questions
- Responsive frontend with no Node.js build step
- FastAPI Swagger docs at `/docs`

## Requirements
- Python 3.11+
- A Gemini API key is optional. The app still runs without one using local fallback recommendations.

## Run

### Windows PowerShell
```powershell
cd PocketSmart
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# edit .env and optionally add GEMINI_API_KEY
python -m uvicorn app.main:app --reload
```

### macOS/Linux
```bash
cd PocketSmart
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and optionally add GEMINI_API_KEY
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

## Test
```bash
python -m pytest -q
```

Health check: http://127.0.0.1:8000/api/health
API docs: http://127.0.0.1:8000/docs

## Project structure
```text
PocketSmart/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── ai.py
│   ├── recommendations.py
│   └── main.py
├── static/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── planner.html
│   ├── history.html
│   ├── detail.html
│   ├── css/styles.css
│   └── js/app.js
├── data/
├── uploads/
├── tests/test_api.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
