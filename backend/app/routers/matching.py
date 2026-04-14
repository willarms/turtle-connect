from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.group import GroupOut
from app.services.matching import get_suggested_groups

router = APIRouter(prefix="/api/match", tags=["matching"])


@router.post("", response_model=List[GroupOut])
def run_matching(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run AI matching and return suggested groups for the current user."""
    suggested = get_suggested_groups(db, current_user.profile)
    return [
        {
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "topics": g.topics,
            "member_count": g.member_count,
            "created_at": g.created_at,
            "is_favorite": False,
            "is_member": False,
        }
        for g in suggested
    ]
