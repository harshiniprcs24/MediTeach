# MediTeach Backend

FastAPI backend for MediTeach – AI-powered prescription management and health assistant.

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI + Uvicorn |
| Database | SQLAlchemy 2 (async) – SQLite dev / PostgreSQL prod |
| Auth | JWT (python-jose) + bcrypt |
| OCR | Google Cloud Vision / Tesseract |
| LLM | OpenAI GPT-4o-mini |
| Speech | OpenAI Whisper (STT) + gTTS (TTS) |
| Translation | deep-translator (Google Translate) |

## Quick Start

```bash
cd backend

# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Run development server
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

## Project Structure

```
app/
  main.py          # FastAPI app entry point
  api/v1/          # Route handlers
  core/            # Config, security (JWT/bcrypt)
  database/        # SQLAlchemy engine, session, base models
  models/          # ORM models
  schemas/         # Pydantic request/response schemas
  services/        # Business logic layer
  ai_models/       # Custom model weights (gitignored)
  utils/           # File handler, validators
tests/             # pytest test suite
uploads/           # User-uploaded prescription images
migrations/        # Alembic migration scripts
```

## Running Tests

```bash
pytest tests/ -v
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/forgot-password` | Password reset |
| POST | `/api/v1/auth/refresh` | Refresh token |
| POST | `/api/v1/prescriptions/upload` | Upload & OCR prescription |
| GET | `/api/v1/prescriptions` | List prescriptions |
| GET | `/api/v1/prescriptions/{id}` | Get prescription detail |
| DELETE | `/api/v1/prescriptions/{id}` | Delete prescription |
| GET | `/api/v1/medicines/search` | Search medicines |
| POST | `/api/v1/chatbot/chat` | AI chat |
| POST | `/api/v1/chatbot/voice` | Voice chat |
| POST | `/api/v1/assessment/submit` | Submit symptoms |
| GET | `/api/v1/assessment/{id}` | Get assessment result |
| GET | `/api/v1/reminders` | List reminders |
| POST | `/api/v1/reminders` | Create reminder |
| PATCH | `/api/v1/reminders/{id}` | Toggle reminder |
| DELETE | `/api/v1/reminders/{id}` | Delete reminder |
| GET | `/api/v1/profile/me` | Get profile |
| PATCH | `/api/v1/profile/me` | Update profile |
