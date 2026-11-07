from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database.base import Base, UUIDMixin, TimestampMixin


class Prescription(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "prescriptions"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    doctor = Column(String(255), nullable=True)
    file_path = Column(String(512), nullable=True)
    raw_text = Column(Text, nullable=True)
    medicines = Column(JSON, nullable=True)       # List of parsed medicine dicts
    instructions = Column(Text, nullable=True)
    language = Column(String(10), default="en")

    user = relationship("User", back_populates="prescriptions")

    def __repr__(self):
        return f"<Prescription id={self.id} user_id={self.user_id}>"
