from typing import List, Optional

from pydantic import BaseModel, EmailStr


class ProfileOut(BaseModel):
    interests: List[str] = []
    personality_scores: dict = {}
    guardian_enabled: bool = False
    onboarding_complete: bool = False

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    profile: Optional[ProfileOut] = None

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    interests: Optional[List[str]] = None
    personality_scores: Optional[dict] = None
    guardian_enabled: Optional[bool] = None
    onboarding_complete: Optional[bool] = None
    name: Optional[str] = None
