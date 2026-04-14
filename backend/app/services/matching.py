"""
Group matching service — stub for now.
Will call Claude API to match users to groups based on interests + personality.
"""
from typing import List

from sqlalchemy.orm import Session

from app.models.group import Group
from app.models.user import Profile


def get_suggested_groups(db: Session, profile: Profile, limit: int = 6) -> List[Group]:
    """
    Stub: returns groups whose topics overlap with user interests.
    Will be replaced with Claude-powered matching.
    """
    if not profile or not profile.interests:
        return db.query(Group).limit(limit).all()

    user_interests = set(i.lower() for i in profile.interests)
    all_groups = db.query(Group).all()

    scored = []
    for group in all_groups:
        group_topics = set(t.lower() for t in group.topics)
        overlap = len(user_interests & group_topics)
        if overlap > 0:
            scored.append((overlap, group))

    scored.sort(key=lambda x: x[0], reverse=True)
    matched = [g for _, g in scored[:limit]]

    # Pad with any groups if not enough matches
    if len(matched) < limit:
        matched_ids = {g.id for g in matched}
        extras = [g for g in all_groups if g.id not in matched_ids]
        matched += extras[: limit - len(matched)]

    return matched
