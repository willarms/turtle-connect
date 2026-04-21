from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.group import GroupMembership
from app.models.user import User


def build_dashboard_data(db: Session, senior: User) -> dict:
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    activities = db.query(Activity).filter(
        Activity.user_id == senior.id, Activity.created_at >= week_ago
    ).all()

    calls = [a for a in activities if a.activity_type == "call"]
    messages = [a for a in activities if a.activity_type == "message"]
    avg_duration = sum(c.duration_minutes for c in calls) / len(calls) if calls else 0
    active_groups = db.query(GroupMembership).filter_by(user_id=senior.id).count()

    daily = defaultdict(lambda: {"calls": 0, "messages": 0})
    for a in activities:
        day = a.created_at.strftime("%a")
        if a.activity_type == "call":
            daily[day]["calls"] += 1
        else:
            daily[day]["messages"] += 1

    group_time = defaultdict(int)
    for a in activities:
        group_time[a.group_id] += a.duration_minutes or 1
    total_time = sum(group_time.values()) or 1
    group_participation = []
    for gid, t in group_time.items():
        m = db.query(GroupMembership).filter_by(user_id=senior.id, group_id=gid).first()
        name = m.group.name if m else f"Group {gid}"
        group_participation.append({"name": name, "percentage": round(t / total_time * 100)})

    recent = db.query(Activity).filter_by(user_id=senior.id).order_by(
        Activity.created_at.desc()
    ).limit(5).all()
    recent_activity = []
    for a in recent:
        m = db.query(GroupMembership).filter_by(user_id=senior.id, group_id=a.group_id).first()
        recent_activity.append({
            "group": m.group.name if m else f"Group {a.group_id}",
            "type": a.activity_type,
            "duration_minutes": a.duration_minutes,
            "created_at": a.created_at.isoformat(),
        })

    return {
        "senior_name": senior.name,
        "total_calls": len(calls),
        "total_messages": len(messages),
        "avg_duration_minutes": round(avg_duration),
        "active_groups": active_groups,
        "weekly_activity": [{"day": d, **c} for d, c in sorted(daily.items())],
        "group_participation": group_participation,
        "recent_activity": recent_activity,
    }
