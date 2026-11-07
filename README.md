# MediTeach 🏥

> AI-powered prescription management and health assistant for rural India — supporting English, Tamil, Hindi & Telugu.

## What It Does

- 📷 **Scan prescriptions** using the camera — AI extracts medicines, dosages, and instructions
- 🤖 **AI Health Chatbot** — ask questions about medications in your language
- 🔔 **Medicine Reminders** — never miss a dose
- 📋 **Symptom Assessment** — AI-generated urgency guidance
- 🌐 **4 languages** — English, Tamil, Hindi, Telugu (text + voice)

## Repository Structure

```
MediTeach/
├── frontend/      # React Native + Expo mobile app
├── backend/       # FastAPI Python REST API
└── docs/          # Architecture, API docs, project overview
```

## Quick Start

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add your API keys
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npx expo start
```

## Documentation

| Doc | Link |
|---|---|
| Project Overview | [docs/project_overview.md](docs/project_overview.md) |
| Architecture | [docs/architecture.md](docs/architecture.md) |
| API Reference | [docs/api_documentation.md](docs/api_documentation.md) |
| Backend README | [backend/README.md](backend/README.md) |
| Frontend README | [frontend/README.md](frontend/README.md) |

## Tech Stack

| Layer | Technology |
|---|---|
| Mobile | React Native, Expo Router, i18next |
| Backend | FastAPI, SQLAlchemy 2 (async), Pydantic v2 |
| Auth | JWT + bcrypt |
| AI | OpenAI GPT-4o-mini, Whisper, gTTS |
| OCR | Google Cloud Vision / Tesseract |
| Translation | Google Translate (deep-translator) |
| DB | SQLite (dev) / PostgreSQL (prod) |

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "feat: add my feature"`
4. Push and open a Pull Request

## License

MIT License – see [LICENSE](LICENSE) for details.
