import json
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    topics_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
    google_meet_url = Column(String, nullable=True)
    meet_event_id = Column(String, nullable=True)

    memberships = relationship("GroupMembership", back_populates="group")
    messages = relationship("Message", back_populates="group")
    activities = relationship("Activity", back_populates="group")

    @property
    def topics(self):
        return json.loads(self.topics_json or "[]")

    @topics.setter
    def topics(self, value):
        self.topics_json = json.dumps(value)

    @property
    def member_count(self):
        return len(self.memberships)


class GroupMembership(Base):
    __tablename__ = "group_memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_favorite = Column(Boolean, default=False)

    user = relationship("User", back_populates="memberships")
    group = relationship("Group", back_populates="memberships")
