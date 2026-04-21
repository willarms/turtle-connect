from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import GuardianLink, Profile, User
from app.schemas.user import GuardianEmailUpdate, ProfileUpdate, UserOut

router = APIRouter(prefix="/api/users", tags=["users"])


def _build_user_out(user: User) -> dict:
    profile = user.profile
    profile_data = None
    if profile:
        link = user.guardian_links[0] if user.guardian_links else None
        profile_data = {
            "interests": profile.interests,
            "personality_scores": profile.personality_scores,
            "guardian_enabled": profile.guardian_enabled,
            "onboarding_complete": profile.onboarding_complete,
            "guardian_email": link.guardian_email if link else None,
        }
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "profile": profile_data,
    }


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return _build_user_out(current_user)


@router.put("/me/profile", response_model=UserOut)
def update_profile(
    body: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = current_user.profile
    if profile is None:
        profile = Profile(user_id=current_user.id)
        db.add(profile)

    if body.interests is not None:
        profile.interests = body.interests
    if body.personality_scores is not None:
        profile.personality_scores = body.personality_scores
    if body.guardian_enabled is not None:
        profile.guardian_enabled = body.guardian_enabled
    if body.onboarding_complete is not None:
        profile.onboarding_complete = body.onboarding_complete
    if body.name is not None:
        current_user.name = body.name

    db.commit()
    db.refresh(current_user)
    return _build_user_out(current_user)


@router.put("/me/guardian-email", response_model=UserOut)
def update_guardian_email(
    body: GuardianEmailUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    link = current_user.guardian_links[0] if current_user.guardian_links else None
    if link:
        link.guardian_email = str(body.guardian_email)
    else:
        db.add(GuardianLink(senior_id=current_user.id, guardian_email=str(body.guardian_email)))
    db.commit()
    db.refresh(current_user)
    return _build_user_out(current_user)
