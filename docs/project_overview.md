# MediTeach – Project Overview

## Problem Statement

Patients in rural and semi-urban India face major barriers to understanding their medical prescriptions:
- Handwritten prescriptions are difficult to read
- Medical terminology is complex and intimidating
- Limited English literacy among patients
- No easy way to track medication schedules

## Solution

MediTeach is an AI-powered mobile application that bridges the gap between patients and their prescriptions by providing:

1. **OCR Prescription Scanning** – photograph or upload a prescription; AI extracts medicine names, dosages, and instructions
2. **Multilingual Support** – English, Tamil, Hindi, Telugu with voice input/output
3. **AI Health Chatbot** – ask questions about medications, side effects, and general health in your native language
4. **Medicine Reminders** – set daily reminders with push notifications
5. **Symptom Assessment** – describe symptoms and receive AI-generated guidance with urgency classification
6. **Medicine Information** – search a curated drug database for details on any medicine

## Target Users

- Rural and semi-urban patients aged 30–70
- Caregivers managing medication for elderly family members
- Community health workers (ASHAs, ANMs)
- First-time smartphone users in regional language markets

## Key Features

| Feature | Technology |
|---|---|
| OCR | Google Cloud Vision / Tesseract |
| LLM Chatbot | OpenAI GPT-4o-mini |
| Speech-to-Text | OpenAI Whisper |
| Text-to-Speech | gTTS / OpenAI TTS |
| Translation | Google Translate (deep-translator) |
| Mobile App | React Native + Expo Router |
| Backend API | FastAPI + SQLAlchemy |
| Auth | JWT (HS256) + bcrypt |

## Languages Supported

| Code | Language |
|---|---|
| en | English |
| ta | Tamil (தமிழ்) |
| hi | Hindi (हिन्दी) |
| te | Telugu (తెలుగు) |

## Impact Goals

- Reduce medication errors due to misunderstood prescriptions
- Improve medication adherence through reminders
- Empower patients with accessible health education
- Support healthcare workers with AI-assisted tools
