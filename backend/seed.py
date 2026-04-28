"""
Seed script — populates the database with demo users, groups, chat messages,
activity logs, a scheduled meeting, and a guardian link for professor testing.

Usage:
    python seed.py           # seed if empty
    python seed.py --reset   # wipe everything and re-seed
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.models import Group, GroupMembership, User, Profile
from app.models.activity import Activity
from app.models.message import Message
from app.models.report import MeetingReport
from app.models.user import GuardianLink
from app.services.auth import hash_password

Base.metadata.create_all(bind=engine)

GROUPS = [
    {
        "name": "Garden Enthusiasts",
        "description": "Connect with fellow gardeners to share tips, seeds, and stories from our gardens.",
        "topics": ["Gardening", "Plants", "Outdoors"],
    },
    {
        "name": "Yarn Crafters Circle",
        "description": "A cozy group for knitters, crocheters, and all fiber artists to share patterns and projects.",
        "topics": ["Knitting", "Crocheting", "Crafts"],
    },
    {
        "name": "Classic Movie Buffs",
        "description": "Discuss your favorite films from the golden age of cinema and share recommendations.",
        "topics": ["Movies", "Entertainment"],
    },
    {
        "name": "Fishing Friends",
        "description": "Share fishing stories, techniques, and the ones that didn't get away!",
        "topics": ["Fishing", "Outdoors"],
    },
    {
        "name": "Book Club Friends",
        "description": "Monthly discussions of great reads, from mysteries to memoirs.",
        "topics": ["Reading", "Books"],
    },
    {
        "name": "Cooking & Baking Circle",
        "description": "Share recipes, cooking tips, and enjoy virtual cooking sessions together.",
        "topics": ["Cooking", "Baking"],
    },
    {
        "name": "Photography Walkers",
        "description": "Combine a love of walking and photography to capture the beauty around us.",
        "topics": ["Photography", "Walking", "Outdoors"],
    },
    {
        "name": "Card & Board Game Club",
        "description": "Weekly virtual game nights with card games, chess, and friendly competition.",
        "topics": ["Card Games", "Chess"],
    },
]

USERS = [
    {
        "email": "margaret@turtle.app",
        "name": "Margaret Thompson",
        "password": "password123",
        "interests": ["Gardening", "Knitting", "Movies", "Reading"],
        "guardian": True,
    },
    {
        "email": "henry@turtle.app",
        "name": "Henry Kowalski",
        "password": "password123",
        "interests": ["Fishing", "Card Games", "Cooking"],
        "guardian": False,
    },
    {
        "email": "dorothy@turtle.app",
        "name": "Dorothy Nguyen",
        "password": "password123",
        "interests": ["Books", "Photography", "Gardening", "Baking"],
        "guardian": False,
    },
]

# group index → list of user indices who are members
MEMBERSHIPS = {
    0: [0, 2],        # Garden Enthusiasts: Margaret, Dorothy
    1: [0],           # Yarn Crafters: Margaret
    2: [0, 1],        # Classic Movie Buffs: Margaret, Henry
    3: [1],           # Fishing Friends: Henry
    4: [0, 2],        # Book Club: Margaret, Dorothy
    5: [1, 2],        # Cooking & Baking: Henry, Dorothy
    6: [2],           # Photography Walkers: Dorothy
    7: [1],           # Card & Board Game: Henry
}

# Chat messages: (group_index, user_index, content, minutes_ago)
MESSAGES = [
    # Garden Enthusiasts
    (0, 2, "Good morning everyone! My tomatoes are finally coming in.", 120),
    (0, 0, "Dorothy, that's wonderful! I had a great harvest last week too.", 115),
    (0, 2, "Margaret, any tips for keeping the deer away this season?", 110),
    (0, 0, "I've been using coffee grounds around the beds — seems to help!", 105),
    (0, 2, "Oh I'll have to try that. Looking forward to our next chat 🌱", 100),

    # Book Club Friends
    (4, 0, "Has everyone finished the first three chapters of our book?", 200),
    (4, 2, "Just finished last night — what a story so far!", 195),
    (4, 0, "The part about the lighthouse really surprised me.", 190),
    (4, 2, "Same! Can't wait to discuss. See you at our next meeting!", 185),
]


def reset_db(db):
    """Delete all seeded data in safe dependency order."""
    db.query(MeetingReport).delete()
    db.query(Message).delete()
    db.query(Activity).delete()
    db.query(GuardianLink).delete()
    db.query(GroupMembership).delete()
    db.query(Profile).delete()
    db.query(User).delete()
    db.query(Group).delete()
    db.commit()
    print("Database cleared.")


def seed():
    db = SessionLocal()
    try:
        do_reset = "--reset" in sys.argv

        if do_reset:
            reset_db(db)
        elif db.query(Group).count() > 0:
            print("Database already seeded. Use --reset to wipe and re-seed.")
            return

        # --- Groups ---
        groups = []
        for i, g in enumerate(GROUPS):
            group = Group(name=g["name"], description=g["description"])
            group.topics = g["topics"]
            # Schedule a meeting 3 days from now on the first group
            if i == 0:
                group.next_meeting_at = datetime.utcnow() + timedelta(days=3)
            db.add(group)
            groups.append(group)
        db.flush()

        # --- Users & Profiles ---
        users = []
        for u in USERS:
            user = User(
                email=u["email"],
                name=u["name"],
                password_hash=hash_password(u["password"]),
            )
            db.add(user)
            db.flush()

            profile = Profile(
                user_id=user.id,
                guardian_enabled=u["guardian"],
                onboarding_complete=True,
            )
            profile.interests = u["interests"]
            db.add(profile)
            users.append(user)
        db.flush()

        # --- Guardian link for Margaret ---
        db.add(GuardianLink(
            senior_id=users[0].id,
            guardian_email="fdougher@nd.edu",
            accepted=True,
        ))

        # --- Memberships ---
        for group_idx, user_indices in MEMBERSHIPS.items():
            for i, user_idx in enumerate(user_indices):
                db.add(GroupMembership(
                    user_id=users[user_idx].id,
                    group_id=groups[group_idx].id,
                    is_favorite=(i == 0 and user_idx == 0),
                ))
        db.flush()

        # --- Chat messages ---
        for group_idx, user_idx, content, minutes_ago in MESSAGES:
            db.add(Message(
                group_id=groups[group_idx].id,
                sender_id=users[user_idx].id,
                content=content,
                created_at=datetime.utcnow() - timedelta(minutes=minutes_ago),
            ))

        # --- Activity logs (past calls) ---
        call_log = [
            (0, 0, 45, 7),   # Margaret, Garden group, 45 min, 7 days ago
            (0, 0, 30, 14),  # Margaret, Garden group, 30 min, 14 days ago
            (2, 0, 60, 5),   # Margaret, Movie group, 60 min, 5 days ago
            (2, 1, 60, 5),   # Henry, Movie group, 60 min, 5 days ago
            (4, 2, 45, 3),   # Dorothy, Book Club, 45 min, 3 days ago
            (5, 1, 30, 10),  # Henry, Cooking group, 30 min, 10 days ago
        ]
        for group_idx, user_idx, duration, days_ago in call_log:
            db.add(Activity(
                user_id=users[user_idx].id,
                group_id=groups[group_idx].id,
                activity_type="call",
                duration_minutes=duration,
                created_at=datetime.utcnow() - timedelta(days=days_ago),
            ))

        # --- Sample meeting report ---
        db.add(MeetingReport(
            user_id=users[0].id,
            group_id=groups[2].id,
            flag_password_request=False,
            flag_offensive_language=False,
            flag_confusing=True,
            additional_notes="Someone mentioned sending money but I think it was a misunderstanding.",
            created_at=datetime.utcnow() - timedelta(days=5),
        ))

        db.commit()

        print("\n✅ Seeded successfully!\n")
        print("Test accounts:")
        for u in USERS:
            print(f"  {u['email']} / {u['password']}  ({u['name']})")
        print(f"\n{len(GROUPS)} groups created, memberships and chat history populated.")
        print("Guardian dashboard: log in as margaret@turtle.app and visit /guardian\n")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
