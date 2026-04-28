from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.activity import Activity
from app.models.group import Group, GroupMembership
from app.models.message import Message
from app.models.report import MeetingReport
from app.models.user import User
from app.schemas.group import GroupCreate, GroupOut
from app.services.matching import get_suggested_groups
from app.services.google_oauth import create_meet_link, refresh_access_token

from app.services.email import send_email, build_group_report_html
from app.config import settings

class LogCallRequest(BaseModel):
    duration_minutes: int


class MeetingReportRequest(BaseModel):
    flag_password_request: bool = False
    flag_offensive_language: bool = False
    flag_confusing: bool = False
    additional_notes: str = ""

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
        "google_meet_url": group.google_meet_url,
        "members": [{"id": m.user_id, "name": m.user.name} for m in group.memberships],
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


@router.post("/{group_id}/meet-link")
async def create_group_meet_link(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a Google Meet link for the group."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    membership = (
        db.query(GroupMembership)
        .filter_by(user_id=current_user.id, group_id=group_id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="You must be a member to create a Meet link")

    # No calendar refresh token — need OAuth
    if not current_user.google_refresh_token:
        return {"needs_calendar_auth": True}

    try:
        access_token = await refresh_access_token(current_user.google_refresh_token)
    except Exception:
        return {"needs_calendar_auth": True}

    # Link already exists — verify Meet scope and update host, then return
    if group.google_meet_url:
        import httpx as _httpx
        space_code = group.google_meet_url.rstrip("/").split("/")[-1]
        async with _httpx.AsyncClient() as client:
            test = await client.get(
                "https://meet.googleapis.com/v2/conferenceRecords",
                params={"filter": f'space.name="spaces/{space_code}"', "pageSize": "1"},
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if test.status_code == 403:
            return {"needs_calendar_auth": True}
        group.meet_host_user_id = current_user.id
        db.commit()
        return _serialize_group(group, current_user.id)

    try:
        result = await create_meet_link(access_token, group.name)
    except Exception as exc:
        import httpx as _httpx
        if isinstance(exc, _httpx.HTTPStatusError) and exc.response.status_code in (401, 403):
            return {"needs_calendar_auth": True}
        raise HTTPException(status_code=502, detail=f"Google Calendar API error: {exc}")

    group.google_meet_url = result["meet_url"]
    group.meet_event_id = result["event_id"]
    group.meet_host_user_id = current_user.id
    db.commit()
    db.refresh(group)
    return _serialize_group(group, current_user.id)


@router.post("/{group_id}/log-call")
def log_call(
    group_id: int,
    body: LogCallRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = db.query(GroupMembership).filter_by(user_id=current_user.id, group_id=group_id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="You must be a member of this group")

    db.add(Activity(
        user_id=current_user.id,
        group_id=group_id,
        activity_type="call",
        duration_minutes=body.duration_minutes,
    ))
    db.commit()
    return {"ok": True}


@router.post("/{group_id}/report")
def submit_meeting_report(
    group_id: int,
    body: MeetingReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = db.query(GroupMembership).filter_by(user_id=current_user.id, group_id=group_id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="You must be a member of this group")

    report = MeetingReport(
        user_id=current_user.id,
        group_id=group_id,
        flag_password_request=body.flag_password_request,
        flag_offensive_language=body.flag_offensive_language,
        flag_confusing=body.flag_confusing,
        additional_notes=body.additional_notes.strip() or None,
    )
    db.add(report)
    db.commit()
    return {"ok": True}


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

@router.post("/{group_id}/leave", response_model=GroupOut)
def leave_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    membership = (
        db.query(GroupMembership)
        .filter_by(user_id=current_user.id, group_id=group_id)
        .first()
    )

    if membership:
        db.delete(membership)
        db.commit()

    # IMPORTANT: return updated group (same pattern as join)
    return _serialize_group(group, current_user.id)

@router.post("/{group_id}/report")
async def report_group(
    group_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Save structured report to DB (post-meeting modal flags)
    flag_password = bool(payload.get("flag_password_request", False))
    flag_language = bool(payload.get("flag_offensive_language", False))
    flag_confusing = bool(payload.get("flag_confusing", False))
    notes = (payload.get("additional_notes") or payload.get("details") or "").strip() or None

    db.add(MeetingReport(
        user_id=current_user.id,
        group_id=group_id,
        flag_password_request=flag_password,
        flag_offensive_language=flag_language,
        flag_confusing=flag_confusing,
        additional_notes=notes,
    ))
    db.commit()

    # Send admin email if any flags are raised or a reason was given
    any_flagged = flag_password or flag_language or flag_confusing or notes or payload.get("reason")
    if any_flagged:
        try:
            html = build_group_report_html({
                "group_name": group.name,
                "reason": payload.get("reason"),
                "details": notes,
            })
            await send_email(
                to="fdougher@nd.edu",
                subject="Group Safety Report",
                html=html,
            )
        except Exception:
            # Email delivery failure is non-critical — report is already saved to DB
            pass

    return {"success": True}


@router.get("/{group_id}/messages")
def get_messages(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    msgs = (
        db.query(Message)
        .filter(Message.group_id == group_id)
        .order_by(Message.created_at.asc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": m.id,
            "group_id": m.group_id,
            "sender_id": m.sender_id,
            "sender_name": m.sender.name if m.sender else "Unknown",
            "content": m.content,
            "created_at": m.created_at.isoformat(),
        }
        for m in msgs
    ]