from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database.base import Base, UUIDMixin, TimestampMixin


class Assessment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "assessments"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    symptoms = Column(JSON, nullable=False)            # List of symptom keys
    severity = Column(Integer, nullable=False)         # 1=mild, 2=moderate, 3=severe
    duration_days = Column(Integer, nullable=False)
    urgency = Column(String(20), nullable=True)        # low | medium | high
    summary = Column(Text, nullable=True)
    possible_conditions = Column(JSON, nullable=True)  # List of condition names
    recommendations = Column(JSON, nullable=True)      # List of recommendation strings
    language = Column(String(10), default="en")

    user = relationship("User", back_populates="assessments")

    def __repr__(self):
        return f"<Assessment id={self.id} urgency={self.urgency}>"
