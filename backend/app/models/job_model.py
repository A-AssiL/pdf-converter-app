from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from backend.app.db.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, index=True)
    status = Column(String(50), nullable=False)
    input_path = Column(String(1024), nullable=False)
    output_path = Column(String(1024), nullable=True)
    error_message = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    file_id = Column(String(36), ForeignKey("files.id"), nullable=False)

    file = relationship("FileRecord", back_populates="jobs")
