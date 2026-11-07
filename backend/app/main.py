from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.api.v1 import auth, prescriptions, medicines, chatbot, assessment, reminders, profile
from app.database.connection import connect_db, disconnect_db

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="MediTeach API – AI-powered prescription management and health assistant",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Events
@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

# Routers
API_PREFIX = "/api/v1"
app.include_router(auth.router,          prefix=f"{API_PREFIX}/auth",          tags=["Auth"])
app.include_router(prescriptions.router, prefix=f"{API_PREFIX}/prescriptions",  tags=["Prescriptions"])
app.include_router(medicines.router,     prefix=f"{API_PREFIX}/medicines",      tags=["Medicines"])
app.include_router(chatbot.router,       prefix=f"{API_PREFIX}/chatbot",        tags=["Chatbot"])
app.include_router(assessment.router,    prefix=f"{API_PREFIX}/assessment",     tags=["Assessment"])
app.include_router(reminders.router,     prefix=f"{API_PREFIX}/reminders",      tags=["Reminders"])
app.include_router(profile.router,       prefix=f"{API_PREFIX}/profile",        tags=["Profile"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
