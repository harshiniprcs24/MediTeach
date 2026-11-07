from sqlalchemy import Column, String, Text, JSON

from app.database.base import Base, UUIDMixin, TimestampMixin


class Medicine(Base, UUIDMixin, TimestampMixin):
    """Global medicine reference database."""
    __tablename__ = "medicines"

    name = Column(String(255), nullable=False, index=True)
    generic_name = Column(String(255), nullable=True)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    side_effects = Column(Text, nullable=True)
    dosage_info = Column(Text, nullable=True)
    contraindications = Column(Text, nullable=True)
    translations = Column(JSON, nullable=True)  # {"ta": "...", "hi": "...", "te": "..."}

    def __repr__(self):
        return f"<Medicine id={self.id} name={self.name}>"
