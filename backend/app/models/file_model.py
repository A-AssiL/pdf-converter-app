"""SQLAlchemy model representing uploaded file metadata."""

from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship

from backend.app.db.database import Base

class FileRecord(Base):
    __tablename__ = "files"

    id = Column(String(36), primary_key=True, index=True)
    filename = Column(String(260), nullable=False)
    path = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    jobs = relationship("Job", back_populates="file")