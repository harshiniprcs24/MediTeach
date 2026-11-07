from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database.base import Base, UUIDMixin, TimestampMixin


class Reminder(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "reminders"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    medicine_name = Column(String(255), nullable=False)
    time = Column(String(20), nullable=False)          # e.g. "08:00 AM"
    frequency = Column(String(50), default="daily")    # daily | twice_daily | weekly
    notes = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="reminders")

    def __repr__(self):
        return f"<Reminder id={self.id} medicine={self.medicine_name}>"
