import os
import json
import re
from typing import Any, Dict, List, Optional

from groq import Groq
from dotenv import load_dotenv

# These imports are used when saving real groups into the DB.
# They should work inside your real backend project.
try:
    from app.models.group import Group, GroupMembership
except Exception:
    Group = None
    GroupMembership = None

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def safe_parse_json(content: str) -> Dict[str, Any]:
    """
    Safely parse JSON from LLM output.
    Handles markdown code fences and minor formatting issues.
    """
    content = content.strip()
    content = content.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"LLM returned invalid JSON:\n{content}")


def summarize_personality(raw_personality: Any) -> Dict[str, Any]:
    """
    Converts raw personality data into a cleaner summary for the LLM.
    Works with:
    - dict quiz answers
    - string labels
    - None
    """
    if raw_personality is None:
        return {
            "style": "unknown",
            "sociability": "unknown",
            "energy_level": "unknown",
            "group_preference": "unknown",
        }

    if isinstance(raw_personality, str):
        return {
            "style": raw_personality,
            "sociability": "unknown",
            "energy_level": "unknown",
            "group_preference": "unknown",
        }

    if isinstance(raw_personality, dict):
        return {
            "style": raw_personality.get("style", "unknown"),
            "sociability": raw_personality.get("sociability", "unknown"),
            "energy_level": raw_personality.get("energy_level", "unknown"),
            "group_preference": raw_personality.get("group_preference", "unknown"),
        }

    return {
        "style": str(raw_personality),
        "sociability": "unknown",
        "energy_level": "unknown",
        "group_preference": "unknown",
    }


def build_grouping_payload(users: List[Any]) -> Dict[str, Any]:
    """
    Build a clean payload for the LLM from user/profile data.

    Supports:
    1. Plain dictionaries
    2. SQLAlchemy-like objects with attributes
    """
    cleaned_users = []

    for user in users:
        if isinstance(user, dict):
            user_id = user.get("id")
            name = user.get("name", f"User {user_id}")
            profile = user.get("profile", {}) or {}
            interests = profile.get("interests", []) or []
            raw_personality = profile.get("personality")
        else:
            user_id = getattr(user, "id", None)
            name = getattr(user, "name", f"User {user_id}")
            profile = getattr(user, "profile", None)
            interests = getattr(profile, "interests", []) if profile else []
            raw_personality = getattr(profile, "personality", None) if profile else None

        if user_id is None:
            raise ValueError("Every user must have an id.")

        cleaned_users.append(
            {
                "user_id": user_id,
                "name": name,
                "interests": interests,
                "personality_traits": summarize_personality(raw_personality),
            }
        )

    return {
        "users": cleaned_users,
        "constraints": {
            "min_group_size": 3,
            "max_group_size": 5,
            "target_group_size": 4,
            "grouping_goal": "maximize shared interests and social compatibility while keeping groups balanced",
        },
    }


def generate_groups(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send grouping payload to the LLM and return structured group assignments.
    """
    prompt = f"""
You are an AI social matching system for a senior community app.

Your job:
- Create balanced groups using each person's interests and personality traits.
- Put every user in EXACTLY ONE group.
- Do not leave any user out.
- Do not duplicate any user.
- Prefer groups of 3 to 5 users.
- Group people by shared interests and compatible personalities.
- Avoid solo groups unless absolutely unavoidable.

Return ONLY valid JSON. No markdown. No backticks. No explanation outside JSON.

Required output format:
{{
  "groups": [
    {{
      "group_name": "Short descriptive name",
      "description": "One sentence describing the group",
      "topics": ["topic1", "topic2"],
      "member_user_ids": [1, 2, 3],
      "reason": "Why these users fit together"
    }}
  ]
}}

Input payload:
{json.dumps(payload, indent=2)}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    content = response.choices[0].message.content
    print("\nRAW MODEL OUTPUT:\n")
    print(content)

    return safe_parse_json(content)


def validate_and_save_groups(
    db,
    result: Dict[str, Any],
    input_user_ids: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Validate LLM output and save it to the DB if a DB session is provided.

    If db is None:
    - performs validation only
    - returns what WOULD be saved
    """
    if "groups" not in result or not isinstance(result["groups"], list):
        raise ValueError("Result must contain a 'groups' list.")

    seen_user_ids = set()
    all_output_user_ids = []

    for idx, group in enumerate(result["groups"]):
        if not isinstance(group, dict):
            raise ValueError(f"Group at index {idx} is not a dictionary.")

        required_fields = ["group_name", "description", "topics", "member_user_ids", "reason"]
        for field in required_fields:
            if field not in group:
                raise ValueError(f"Missing field '{field}' in group at index {idx}.")

        if not isinstance(group["member_user_ids"], list) or len(group["member_user_ids"]) == 0:
            raise ValueError(f"Group '{group['group_name']}' must have at least one member.")

        for uid in group["member_user_ids"]:
            seen_user_ids.add(uid)
            all_output_user_ids.append(uid)

    if input_user_ids is not None:
        input_set = set(input_user_ids)
        output_set = set(all_output_user_ids)

        missing = input_set - output_set
        extra = output_set - input_set

        if missing:
            raise ValueError(f"These users were not assigned to any group: {sorted(missing)}")
        if extra:
            raise ValueError(f"These users were returned by the LLM but were not in the input: {sorted(extra)}")

    if db is None:
        return {
            "status": "validated_only",
            "groups_to_create": result["groups"],
            "message": "Validation passed. No DB session provided, so nothing was saved.",
        }

    if Group is None or GroupMembership is None:
        raise ValueError("Group and GroupMembership models could not be imported.")

    created_groups = []

    try:
        for group_data in result["groups"]:
            new_group = Group(
                name=group_data["group_name"],
                description=group_data["description"],
                topics=group_data["topics"],
            )
            db.add(new_group)
            db.flush()

            for user_id in group_data["member_user_ids"]:
                membership = GroupMembership(
                    user_id=user_id,
                    group_id=new_group.id,
                    favorite=False,
                )
                db.add(membership)

            created_groups.append(
                {
                    "group_id": new_group.id,
                    "group_name": group_data["group_name"],
                    "member_user_ids": group_data["member_user_ids"],
                }
            )

        db.commit()

        return {
            "status": "saved",
            "created_groups": created_groups,
        }

    except Exception:
        db.rollback()
        raise


def build_test_users() -> List[Dict[str, Any]]:
    """
    Fake users to test without needing your real database.
    """
    return [
        {
            "id": 1,
            "name": "Mary",
            "profile": {
                "interests": ["gardening", "books", "walking"],
                "personality": {
                    "style": "gentle",
                    "sociability": "medium",
                    "energy_level": "low",
                    "group_preference": "small",
                },
            },
        },
        {
            "id": 2,
            "name": "John",
            "profile": {
                "interests": ["history", "reading", "chess"],
                "personality": {
                    "style": "thoughtful",
                    "sociability": "medium",
                    "energy_level": "low",
                    "group_preference": "small",
                },
            },
        },
        {
            "id": 3,
            "name": "Linda",
            "profile": {
                "interests": ["music", "singing", "art"],
                "personality": {
                    "style": "creative",
                    "sociability": "high",
                    "energy_level": "medium",
                    "group_preference": "medium",
                },
            },
        },
        {
            "id": 4,
            "name": "Robert",
            "profile": {
                "interests": ["walking", "fitness", "health"],
                "personality": {
                    "style": "active",
                    "sociability": "medium",
                    "energy_level": "high",
                    "group_preference": "medium",
                },
            },
        },
        {
            "id": 5,
            "name": "Evelyn",
            "profile": {
                "interests": ["books", "poetry", "writing"],
                "personality": {
                    "style": "reflective",
                    "sociability": "low",
                    "energy_level": "low",
                    "group_preference": "small",
                },
            },
        },
        {
            "id": 6,
            "name": "Frank",
            "profile": {
                "interests": ["gardening", "nature", "birds"],
                "personality": {
                    "style": "calm",
                    "sociability": "medium",
                    "energy_level": "low",
                    "group_preference": "small",
                },
            },
        },
        {
            "id": 7,
            "name": "Susan",
            "profile": {
                "interests": ["movies", "storytelling", "music"],
                "personality": {
                    "style": "social",
                    "sociability": "high",
                    "energy_level": "medium",
                    "group_preference": "medium",
                },
            },
        },
        {
            "id": 8,
            "name": "Walter",
            "profile": {
                "interests": ["history", "travel", "culture"],
                "personality": {
                    "style": "curious",
                    "sociability": "medium",
                    "energy_level": "medium",
                    "group_preference": "medium",
                },
            },
        },
        {
            "id": 9,
            "name": "Patricia",
            "profile": {
                "interests": ["art", "crafts", "gardening"],
                "personality": {
                    "style": "creative",
                    "sociability": "medium",
                    "energy_level": "medium",
                    "group_preference": "small",
                },
            },
        },
        {
            "id": 10,
            "name": "James",
            "profile": {
                "interests": ["chess", "reading", "puzzles"],
                "personality": {
                    "style": "analytical",
                    "sociability": "low",
                    "energy_level": "low",
                    "group_preference": "small",
                },
            },
        },
    ]


def run_local_test():
    users = build_test_users()

    payload = build_grouping_payload(users)
    print("\nGROUPING PAYLOAD:\n")
    print(json.dumps(payload, indent=2))

    result = generate_groups(payload)
    print("\nPARSED GROUP RESULT:\n")
    print(json.dumps(result, indent=2))

    validated = validate_and_save_groups(
        db=None,
        result=result,
        input_user_ids=[u["id"] for u in users],
    )

    print("\nVALIDATION / DRY RUN RESULT:\n")
    print(json.dumps(validated, indent=2))


if __name__ == "__main__":
    run_local_test()