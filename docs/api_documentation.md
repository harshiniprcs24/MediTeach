# MediTeach API Documentation

Base URL: `http://localhost:8000/api/v1`

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

## Auth

### POST `/auth/register`
Register a new user.

**Request Body:**
```json
{
  "name": "Ravi Kumar",
  "email": "ravi@example.com",
  "phone": "9876543210",
  "password": "Secure1234",
  "preferred_language": "ta"
}
```

**Response 201:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "name": "Ravi Kumar",
    "email": "ravi@example.com",
    "phone": "9876543210",
    "preferred_language": "ta",
    "is_active": true
  }
}
```

---

### POST `/auth/login`
```json
{ "email": "ravi@example.com", "password": "Secure1234" }
```
**Response 200:** Same as register.

---

### POST `/auth/forgot-password`
```json
{ "email": "ravi@example.com" }
```
**Response 200:** `{ "message": "If that email exists, a reset link has been sent." }`

---

### POST `/auth/refresh`
```json
{ "refresh_token": "eyJ..." }
```
**Response 200:** New `access_token` + `refresh_token`.

---

### POST `/auth/logout`
Requires auth. **Response 204.**

---

## Prescriptions

### POST `/prescriptions/upload`
Upload a prescription image. Multipart form.

**Form fields:**
- `file` – image file (JPEG/PNG/WEBP/HEIC, max 10MB)
- `language` – query param (default `en`)

**Response 201:**
```json
{
  "id": "uuid",
  "title": "Dr. Sharma Clinic",
  "doctor": "Dr. Sharma",
  "raw_text": "Tab. Paracetamol 500mg...",
  "medicines": [
    {
      "name": "Paracetamol",
      "dosage": "500mg",
      "frequency": "Twice daily",
      "duration": "5 days",
      "instructions": "After meals"
    }
  ],
  "instructions": "Take rest. Drink plenty of fluids.",
  "language": "en",
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

### GET `/prescriptions`
Query params: `page`, `limit`, `sort` (e.g. `created_at:desc`)

**Response 200:**
```json
{
  "items": [...],
  "total": 12,
  "page": 1,
  "limit": 20
}
```

---

### GET `/prescriptions/{id}` → **Response 200:** Full prescription object.
### DELETE `/prescriptions/{id}` → **Response 204.**

---

## Medicines

### GET `/medicines/search?q=paracetamol&lang=en`
**Response 200:**
```json
{
  "results": [
    {
      "id": "uuid",
      "name": "Paracetamol",
      "generic_name": "Acetaminophen",
      "category": "Analgesic / Antipyretic",
      "description": "Used to treat pain and fever.",
      "side_effects": "Nausea, liver damage (overdose)",
      "dosage_info": "500mg–1000mg every 4–6 hours",
      "contraindications": "Liver disease, alcohol use"
    }
  ],
  "query": "paracetamol"
}
```

### GET `/medicines/{id}` → Single medicine object.
### GET `/medicines/info?name=aspirin` → Lookup by name.
### POST `/medicines/interactions` → `{ "medicine_ids": ["id1", "id2"] }`

---

## Chatbot

### POST `/chatbot/chat`
```json
{
  "message": "What are the side effects of Metformin?",
  "history": [
    { "role": "user", "content": "..." },
    { "role": "bot", "content": "..." }
  ]
}
```
**Response 200:** `{ "reply": "Metformin may cause nausea..." }`

---

### POST `/chatbot/voice`
```json
{
  "audio": "<base64 encoded audio>",
  "language": "ta"
}
```
**Response 200:**
```json
{
  "text": "மெட்ஃபார்மின் பக்க விளைவுகள் என்ன?",
  "reply": "மெட்ஃபார்மின் குமட்டல்...",
  "audioReply": "<base64 mp3>"
}
```

---

## Assessment

### POST `/assessment/submit`
```json
{
  "symptoms": ["fever", "headache", "body_ache"],
  "severity": 2,
  "duration": 3
}
```
**Response 201:**
```json
{
  "id": "uuid",
  "symptoms": ["fever", "headache", "body_ache"],
  "severity": 2,
  "duration_days": 3,
  "urgency": "medium",
  "summary": "Your symptoms suggest a possible viral infection...",
  "possible_conditions": ["Viral fever", "Dengue (monitor)", "Flu"],
  "recommendations": [
    "Drink at least 2–3 litres of water daily.",
    "Take paracetamol for fever as directed.",
    "See a doctor if fever exceeds 103°F or persists beyond 3 days."
  ],
  "created_at": "2024-01-15T10:00:00Z"
}
```

### GET `/assessment/{id}` → Full assessment object.
### GET `/assessment/history?limit=10` → List of past assessments.

---

## Reminders

### GET `/reminders` → All reminders for current user.
### GET `/reminders/today` → Enabled reminders for today.

### POST `/reminders`
```json
{
  "medicineName": "Metformin",
  "time": "08:00 AM",
  "frequency": "daily",
  "notes": "Take with breakfast"
}
```
**Response 201:** Reminder object.

### PUT `/reminders/{id}` → Update reminder fields.
### PATCH `/reminders/{id}` → `{ "enabled": false }` to toggle.
### DELETE `/reminders/{id}` → **Response 204.**

---

## Profile

### GET `/profile/me` → Current user profile.
### PATCH `/profile/me`
```json
{
  "name": "Ravi Kumar",
  "phone": "9876543210",
  "preferred_language": "hi"
}
```
**Response 200:** Updated user object.

### DELETE `/profile/me` → **Response 204.** Permanently deletes account.

---

## Error Responses

All errors follow this shape:
```json
{ "detail": "Human-readable error message" }
```

| Status | Meaning |
|---|---|
| 400 | Bad request / validation error |
| 401 | Unauthorized (missing or invalid token) |
| 403 | Forbidden (inactive account) |
| 404 | Resource not found |
| 409 | Conflict (duplicate email) |
| 413 | File too large |
| 422 | Pydantic validation error |
| 500 | Internal server error |
