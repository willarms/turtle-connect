from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.group import Group, GroupMembership
from app.models.user import User
from app.schemas.group import GroupCreate, GroupOut
from app.services.matching import get_suggested_groups

router = APIRouter(prefix="/api/groups", tags=["groups"])


def _serialize_group(group: Group, user_id: int) -> dict:
    membership = next((m for m in group.memberships if m.user_id == user_id), None)
    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "topics": group.topics,
        "member_count": group.member_count,
        "created_at": group.created_at,
        "is_favorite": membership.is_favorite if membership else False,
        "is_member": membership is not None,
    }


@router.get("", response_model=List[GroupOut])
def list_all_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    groups = db.query(Group).all()
    return [_serialize_group(g, current_user.id) for g in groups]


@router.get("/my", response_model=List[GroupOut])
def list_my_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memberships = (
        db.query(GroupMembership)
        .filter(GroupMembership.user_id == current_user.id)
        .all()
    )
    return [_serialize_group(m.group, current_user.id) for m in memberships]


@router.get("/suggested", response_model=List[GroupOut])
def list_suggested_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    suggested = get_suggested_groups(db, current_user.profile)
    return [_serialize_group(g, current_user.id) for g in suggested]


@router.get("/{group_id}", response_model=GroupOut)
def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return _serialize_group(group, current_user.id)


@router.post("", response_model=GroupOut, status_code=201)
def create_group(
    body: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = Group(name=body.name, description=body.description)
    group.topics = body.topics or []
    db.add(group)
    db.flush()

    membership = GroupMembership(user_id=current_user.id, group_id=group.id)
    db.add(membership)
    db.commit()
    db.refresh(group)
    return _serialize_group(group, current_user.id)


@router.post("/{group_id}/join", response_model=GroupOut)
def join_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    existing = (
        db.query(GroupMembership)
        .filter_by(user_id=current_user.id, group_id=group_id)
        .first()
    )
    if not existing:
        db.add(GroupMembership(user_id=current_user.id, group_id=group_id))
        db.commit()
        db.refresh(group)

    return _serialize_group(group, current_user.id)


@router.post("/{group_id}/favorite", response_model=GroupOut)
def toggle_favorite(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = (
        db.query(GroupMembership)
        .filter_by(user_id=current_user.id, group_id=group_id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=400, detail="You are not a member of this group")

    membership.is_favorite = not membership.is_favorite
    db.commit()
    db.refresh(membership.group)
    return _serialize_group(membership.group, current_user.id)
