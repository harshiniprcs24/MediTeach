from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

from app.database.connection import get_db
from app.core.security import get_current_user_id
from app.models.reminder import Reminder

router = APIRouter()


class ReminderCreate(BaseModel):
    medicineName: str
    time: str
    frequency: str = "daily"
    notes: Optional[str] = None


class ReminderUpdate(BaseModel):
    medicineName: Optional[str] = None
    time: Optional[str] = None
    frequency: Optional[str] = None
    notes: Optional[str] = None


class ReminderToggle(BaseModel):
    enabled: bool


class ReminderOut(BaseModel):
    id: str
    medicineName: str
    time: str
    frequency: str
    notes: Optional[str]
    enabled: bool

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_map(cls, r: Reminder):
        return cls(
            id=r.id,
            medicineName=r.medicine_name,
            time=r.time,
            frequency=r.frequency,
            notes=r.notes,
            enabled=r.enabled,
        )


@router.get("", response_model=List[ReminderOut])
async def get_reminders(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(select(Reminder).where(Reminder.user_id == user_id))
    reminders = result.scalars().all()
    return [ReminderOut.from_orm_map(r) for r in reminders]


@router.get("/today", response_model=List[ReminderOut])
async def get_today_reminders(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Return enabled reminders for today."""
    result = await db.execute(
        select(Reminder).where(Reminder.user_id == user_id, Reminder.enabled == True)
    )
    reminders = result.scalars().all()
    return [ReminderOut.from_orm_map(r) for r in reminders]


@router.post("", response_model=ReminderOut, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    payload: ReminderCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    reminder = Reminder(
        user_id=user_id,
        medicine_name=payload.medicineName,
        time=payload.time,
        frequency=payload.frequency,
        notes=payload.notes,
    )
    db.add(reminder)
    await db.flush()
    await db.refresh(reminder)
    return ReminderOut.from_orm_map(reminder)


@router.put("/{reminder_id}", response_model=ReminderOut)
async def update_reminder(
    reminder_id: str,
    payload: ReminderUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id)
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    if payload.medicineName is not None:
        reminder.medicine_name = payload.medicineName
    if payload.time is not None:
        reminder.time = payload.time
    if payload.frequency is not None:
        reminder.frequency = payload.frequency
    if payload.notes is not None:
        reminder.notes = payload.notes

    await db.flush()
    await db.refresh(reminder)
    return ReminderOut.from_orm_map(reminder)


@router.patch("/{reminder_id}", response_model=ReminderOut)
async def toggle_reminder(
    reminder_id: str,
    payload: ReminderToggle,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id)
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    reminder.enabled = payload.enabled
    await db.flush()
    await db.refresh(reminder)
    return ReminderOut.from_orm_map(reminder)


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id)
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    await db.delete(reminder)
