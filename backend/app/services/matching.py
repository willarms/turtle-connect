"""
Group matching service — uses Groq AI to match users to groups based on interests + personality.
"""
import json
import os
from typing import List

from dotenv import load_dotenv
from groq import Groq
from sqlalchemy.orm import Session

from app.models.group import Group
from app.models.user import Profile

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_suggested_groups(db: Session, profile: Profile, limit: int = 6) -> List[Group]:
    """
    Uses Groq to rank and suggest the best groups for a user based on
    their interests and personality scores.
    """
    if not profile or not profile.interests:
        return db.query(Group).limit(limit).all()

    all_groups = db.query(Group).all()
    if not all_groups:
        return []

    # Build group list for the prompt
    groups_data = [
        {
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "topics": g.topics,
        }
        for g in all_groups
    ]

    # Build user profile for the prompt
    user_data = {
        "interests": profile.interests,
        "personality": profile.personality_scores,
    }

    prompt = f"""
You are a social group matching system for a senior community app.

Given a user's interests and personality, pick the {limit} best matching groups from the list below.

Return ONLY valid JSON. No markdown. No backticks. No explanation.

Required format:
{{
  "recommended_group_ids": [1, 2, 3, 4, 5, 6]
}}

Rules:
- Return exactly {limit} group IDs ordered from best match to worst
- Prioritize shared interests first, then personality compatibility
- Only return IDs from the provided group list

User profile:
{json.dumps(user_data, indent=2)}

Available groups:
{json.dumps(groups_data, indent=2)}
"""

    try:
        print("Calling Groq API...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        content = response.choices[0].message.content.strip()
        print(f"RAW GROQ OUTPUT: {content}")
        content = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)

        recommended_ids = result.get("recommended_group_ids", [])
        print(f"Recommended IDs: {recommended_ids}")

        # Map IDs back to group objects in order
        group_map = {g.id: g for g in all_groups}
        matched = [group_map[gid] for gid in recommended_ids if gid in group_map]

        # Pad with remaining groups if AI returned fewer than limit
        if len(matched) < limit:
            matched_ids = {g.id for g in matched}
            extras = [g for g in all_groups if g.id not in matched_ids]
            matched += extras[:limit - len(matched)]

        print(f"✅ GROQ MATCHED user {profile.user_id} → {[g.name for g in matched[:limit]]}")
        return matched[:limit]

    except Exception as e:
        print(f"Groq matching failed, falling back to topic overlap: {e}")
        # Fallback to simple topic overlap
        user_interests = set(i.lower() for i in profile.interests)
        scored = []
        for group in all_groups:
            group_topics = set(t.lower() for t in group.topics)
            overlap = len(user_interests & group_topics)
            if overlap > 0:
                scored.append((overlap, group))
        scored.sort(key=lambda x: x[0], reverse=True)
        matched = [g for _, g in scored[:limit]]
        if len(matched) < limit:
            matched_ids = {g.id for g in matched}
            extras = [g for g in all_groups if g.id not in matched_ids]
            matched += extras[:limit - len(matched)]
        return matched