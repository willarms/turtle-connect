from fastapi import APIRouter
from app.services.matching import generate_groups

router = APIRouter()

@router.post("/match-groups")
def match_groups(payload: dict):
    users = payload.get("users", [])
    return generate_groups(users)