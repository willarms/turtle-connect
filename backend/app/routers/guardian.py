from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.activity import Activity
from app.models.group import Group, GroupMembership
from app.models.message import Message
from app.models.report import MeetingReport
from app.models.user import GuardianLink, User
from app.services.auth import get_user_by_id
from app.services.dashboard import build_dashboard_data
from app.services.email import build_report_html, send_email

router = APIRouter(prefix="/api/guardian", tags=["guardian"])


async def _sync_meet_activities(senior: User, db: Session, since: datetime) -> None:
    memberships = db.query(GroupMembership).filter_by(user_id=senior.id).all()
    since_iso = since.strftime("%Y-%m-%dT%H:%M:%SZ")

    for m in memberships:
        group: Group = m.group
        if not group.google_meet_url or not group.meet_host_user_id:
            continue

        print(f"[meet-sync] checking group {group.id} ({group.name}), meet_url={group.google_meet_url}, host_id={group.meet_host_user_id}")
        host = db.query(User).filter_by(id=group.meet_host_user_id).first() if group.meet_host_user_id else None
        if not host or not host.google_refresh_token:
            for membership in group.memberships:
                candidate = membership.user
                if candidate.google_refresh_token:
                    host = candidate
                    break
        if not host or not host.google_refresh_token:
            continue

        try:
            access_token = await refresh_access_token(host.google_refresh_token)
        except Exception:
            continue

        records = await fetch_meet_activities(access_token, group.google_meet_url, since_iso)

        for rec in records:
            existing = db.query(Activity).filter_by(meet_conference_id=rec["conference_id"]).first()
            if existing:
                continue

            senior_google_id = senior.google_id
            if senior_google_id and senior_google_id not in rec["participant_google_ids"]:
                continue

            ended_at = datetime.strptime(rec["ended_at"][:19], "%Y-%m-%dT%H:%M:%S")
            db.add(Activity(
                user_id=senior.id,
                group_id=group.id,
                activity_type="call",
                duration_minutes=rec["duration_minutes"],
                meet_conference_id=rec["conference_id"],
                created_at=ended_at,
            ))

    db.commit()


@router.get("/{senior_id}/dashboard")
async def get_dashboard(
    senior_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    senior = get_user_by_id(db, senior_id)
    if not senior:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    try:
        await _sync_meet_activities(senior, db, week_ago)
    except Exception as exc:
        print(f"[guardian] meet sync failed: {exc}")

    activities = (
        db.query(Activity)
        .filter(Activity.user_id == senior_id, Activity.created_at >= week_ago)
        .all()
    )

    calls = [a for a in activities if a.activity_type == "call"]
    messages = [a for a in activities if a.activity_type == "message"]

    avg_duration = (
        sum(c.duration_minutes for c in calls) / len(calls) if calls else 0
    )

    active_groups = len(
        db.query(GroupMembership).filter(GroupMembership.user_id == senior_id).all()
    )

    # Weekly breakdown by day
    daily = defaultdict(lambda: {"calls": 0, "messages": 0})
    for a in activities:
        day = a.created_at.strftime("%a")
        if a.activity_type == "call":
            daily[day]["calls"] += 1
        else:
            daily[day]["messages"] += 1

    weekly_activity = [
        {"day": day, **counts}
        for day, counts in sorted(daily.items())
    ]

    # Group participation (time per group)
    group_time = defaultdict(int)
    for a in activities:
        group_time[a.group_id] += a.duration_minutes or 1

    total_time = sum(group_time.values()) or 1
    group_participation = []
    for gid, t in group_time.items():
        membership = db.query(GroupMembership).filter_by(user_id=senior_id, group_id=gid).first()
        name = membership.group.name if membership else f"Group {gid}"
        group_participation.append({"name": name, "percentage": round(t / total_time * 100)})

    # Recent activity
    recent = (
        db.query(Activity)
        .filter(Activity.user_id == senior_id)
        .order_by(Activity.created_at.desc())
        .limit(5)
        .all()
    )
    recent_activity = []
    for a in recent:
        membership = db.query(GroupMembership).filter_by(user_id=senior_id, group_id=a.group_id).first()
        group_name = membership.group.name if membership else f"Group {a.group_id}"
        recent_activity.append({
            "group": group_name,
            "type": a.activity_type,
            "duration_minutes": a.duration_minutes,
            "created_at": a.created_at.isoformat(),
        })

    # Flagged messages alerts
    flagged_messages = (
        db.query(Message)
        .filter(Message.sender_id == senior_id, Message.is_flagged == True)
        .order_by(Message.created_at.desc())
        .limit(10)
        .all()
    )

    alerts = []
    for m in flagged_messages:
        group = db.query(Group).filter(Group.id == m.group_id).first()
        alerts.append({
            "type": "flagged_message",
            "message": m.content,
            "reason": m.flag_reason,
            "group": group.name if group else "Unknown",
            "created_at": m.created_at.isoformat(),
        })

    # Meeting report alerts
    meeting_reports = (
        db.query(MeetingReport)
        .filter(MeetingReport.user_id == senior_id)
        .filter(
            (MeetingReport.flag_password_request == True) |
            (MeetingReport.flag_offensive_language == True) |
            (MeetingReport.flag_confusing == True) |
            (MeetingReport.additional_notes != None)
        )
        .order_by(MeetingReport.created_at.desc())
        .limit(10)
        .all()
    )

    for r in meeting_reports:
        group = db.query(Group).filter(Group.id == r.group_id).first()
        flags = []
        if r.flag_password_request:
            flags.append("Someone asked for password/login info")
        if r.flag_offensive_language:
            flags.append("Offensive or upsetting language")
        if r.flag_confusing:
            flags.append("Something confusing happened")
        alerts.append({
            "type": "meeting_report",
            "message": r.additional_notes or "No additional notes",
            "reason": ", ".join(flags) if flags else "User submitted a report",
            "group": group.name if group else "Unknown",
            "created_at": r.created_at.isoformat(),
        })

    # Sort all alerts by date newest first
    alerts.sort(key=lambda x: x["created_at"], reverse=True)

    return {
        "senior_name": senior.name,
        "total_calls": len(calls),
        "total_messages": len(messages),
        "avg_duration_minutes": round(avg_duration),
        "active_groups": active_groups,
        "weekly_activity": weekly_activity,
        "group_participation": group_participation,
        "recent_activity": recent_activity,
        "alerts": alerts,
    }


@router.post("/{senior_id}/send-report")
async def send_report(
    senior_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    senior = get_user_by_id(db, senior_id)
    if not senior:
        raise HTTPException(status_code=404, detail="User not found")

    if not senior.profile or not senior.profile.guardian_enabled:
        raise HTTPException(status_code=400, detail="Guardian monitoring is not enabled for this user")

    link = db.query(GuardianLink).filter_by(senior_id=senior_id).first()
    if not link:
        raise HTTPException(status_code=400, detail="No guardian email address set. Please add one in Profile settings.")

    data = build_dashboard_data(db, senior)
    html = build_report_html(data)
    await send_email(
        to=link.guardian_email,
        subject=f"Activity Report — {senior.name}",
        html=html,
    )
    return {"ok": True, "sent_to": link.guardian_email}