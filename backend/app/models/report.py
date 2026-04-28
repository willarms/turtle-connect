from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text

from app.database import Base


class MeetingReport(Base):
    __tablename__ = "meeting_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    flag_password_request = Column(Boolean, default=False)
    flag_offensive_language = Column(Boolean, default=False)
    flag_confusing = Column(Boolean, default=False)
    additional_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
