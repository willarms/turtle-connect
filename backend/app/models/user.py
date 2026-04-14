import json
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    profile = relationship("Profile", back_populates="user", uselist=False)
    memberships = relationship("GroupMembership", back_populates="user")
    sent_messages = relationship("Message", back_populates="sender")
    activities = relationship("Activity", back_populates="user")
    guardian_links = relationship("GuardianLink", foreign_keys="GuardianLink.senior_id", back_populates="senior")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    interests_json = Column(Text, default="[]")
    personality_scores_json = Column(Text, default="{}")
    guardian_enabled = Column(Boolean, default=False)
    onboarding_complete = Column(Boolean, default=False)

    user = relationship("User", back_populates="profile")

    @property
    def interests(self):
        return json.loads(self.interests_json or "[]")

    @interests.setter
    def interests(self, value):
        self.interests_json = json.dumps(value)

    @property
    def personality_scores(self):
        return json.loads(self.personality_scores_json or "{}")

    @personality_scores.setter
    def personality_scores(self, value):
        self.personality_scores_json = json.dumps(value)


class GuardianLink(Base):
    __tablename__ = "guardian_links"

    id = Column(Integer, primary_key=True, index=True)
    senior_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    guardian_email = Column(String, nullable=False)
    accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    senior = relationship("User", foreign_keys=[senior_id], back_populates="guardian_links")
