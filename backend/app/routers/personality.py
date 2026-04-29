from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import Profile, User
from app.services.big5 import score_big5, summarize_personality, interpret_big5
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/personality", tags=["personality"])


@router.post("/big5")
def submit_big5(
    answers: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scores = score_big5(answers)

    profile = current_user.profile
    if profile is None:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        db.flush()  

    profile.personality_scores = {
        "model": "big5",
        "scores": scores,
        "interpretation": interpret_big5(scores),
        "summary": summarize_personality(scores)
    }

    profile.onboarding_complete = True

    db.commit()
    db.refresh(current_user)

    return profile.personality_scores