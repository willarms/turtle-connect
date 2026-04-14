"""
Seed script — populates the database with a test user and sample groups.
Run from the backend directory: python seed.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.models import Group, GroupMembership, User, Profile
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

def seed():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Group).count() > 0:
            print("Database already seeded. Skipping.")
            return

        # Create groups
        for g in GROUPS:
            group = Group(name=g["name"], description=g["description"])
            group.topics = g["topics"]
            db.add(group)
        db.flush()

        # Create a test user
        existing = db.query(User).filter(User.email == "test@turtle.app").first()
        if not existing:
            user = User(
                email="test@turtle.app",
                name="Margaret Thompson",
                password_hash=hash_password("password123"),
            )
            db.add(user)
            db.flush()

            profile = Profile(
                user_id=user.id,
                guardian_enabled=True,
                onboarding_complete=True,
            )
            profile.interests = ["Gardening", "Knitting", "Movies", "Reading"]
            db.add(profile)
            db.flush()

            # Join first 4 groups
            groups = db.query(Group).limit(4).all()
            for i, group in enumerate(groups):
                membership = GroupMembership(
                    user_id=user.id,
                    group_id=group.id,
                    is_favorite=(i < 2),
                )
                db.add(membership)

        db.commit()
        print("Seeded successfully!")
        print("  Test user: test@turtle.app / password123")
        print(f"  Created {len(GROUPS)} groups")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
