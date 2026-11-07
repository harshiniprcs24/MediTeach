# MediTeach – Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Mobile App (Expo)                        │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐  │
│  │  Auth    │  │  Home    │  │  Chatbot  │  │  Profile  │  │
│  │  Screens │  │  + Scan  │  │  (AI)     │  │  Settings │  │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  └─────┬─────┘  │
│       └─────────────┴──────────────┴───────────────┘        │
│                     Service Layer (api.js)                   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS / REST
┌──────────────────────────▼──────────────────────────────────┐
│                  FastAPI Backend                              │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │  Auth    │  │ Prescription │  │  AI Services          │  │
│  │  Router  │  │  Router      │  │  ┌────────────────┐   │  │
│  └──────────┘  └──────┬───────┘  │  │ LLM (OpenAI)   │   │  │
│  ┌──────────┐         │          │  │ OCR (Vision)   │   │  │
│  │  Remind. │  ┌──────▼───────┐  │  │ STT (Whisper)  │   │  │
│  │  Router  │  │  OCR Service │  │  │ TTS (gTTS)     │   │  │
│  └──────────┘  └──────────────┘  │  │ Translate      │   │  │
│  ┌──────────┐                    │  └────────────────┘   │  │
│  │Assessment│                    └───────────────────────┘  │
│  │  Router  │                                               │
│  └──────────┘                                               │
│                     SQLAlchemy (Async)                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │  Database               │
              │  SQLite (dev)           │
              │  PostgreSQL (prod)      │
              └─────────────────────────┘
```

## Component Breakdown

### Frontend (React Native / Expo)

| Layer | Description |
|---|---|
| `app/` | File-based routing via Expo Router |
| `src/services/` | Thin API clients (fetch wrappers) |
| `src/context/` | AuthContext – global auth state |
| `src/hooks/` | `useAuth`, `useLanguage` |
| `src/localization/` | i18next with 4 language JSON files |
| `src/components/` | Reusable UI – Button, Input, Header, MedicineCard |

### Backend (FastAPI)

| Layer | Description |
|---|---|
| `api/v1/` | Route handlers (thin controllers) |
| `services/` | Business logic, AI orchestration |
| `models/` | SQLAlchemy ORM models |
| `schemas/` | Pydantic request/response validation |
| `core/` | JWT auth, bcrypt, app config |
| `database/` | Async engine, session management |
| `utils/` | File upload handler, input validators |
| `ai_models/` | Custom model weights directory |

## Data Flow – Prescription Upload

```
User → Camera/Gallery
  → frontend/prescription/upload.jsx
  → prescriptionService.uploadPrescription()
  → POST /api/v1/prescriptions/upload (multipart)
  → file_handler.save_upload_file()
  → OCRService.extract_text()          ← Google Vision / Tesseract
  → MedicineService.parse_prescription_text()  ← LLM (GPT-4o-mini)
  → Prescription saved to DB
  → PrescriptionOut returned to app
  → app/prescription/[id].jsx displays result
```

## Data Flow – AI Chatbot

```
User types / speaks
  → chatbot.jsx
  → chatbotService.sendMessage()
  → POST /api/v1/chatbot/chat
  → LLMService.chat()  ← OpenAI ChatCompletion
  → reply displayed in chat bubble
```

## Authentication Flow

```
Register/Login → JWT access_token (1h) + refresh_token (30d)
  → stored in AsyncStorage
  → api.js injects "Authorization: Bearer <token>" on every request
  → 401 response → tokens cleared → redirect to login
```

## Security Considerations

- Passwords hashed with bcrypt (cost factor 12)
- JWT signed with HS256 (configurable to RS256 for production)
- File uploads validated for content-type and size before processing
- All DB queries use parameterized statements via SQLAlchemy ORM
- User data is scoped by `user_id` in every query
- CORS restricted to configured origins
