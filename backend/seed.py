"""
Seed script — populates the database with test users and sample groups.
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
        "name": "Photography Circle",
        "description": "Share your favorite shots and tips for capturing life's beautiful moments.",
        "topics": ["Photography"],
    },
    {
        "name": "Bird Watchers Club",
        "description": "Spot, identify, and celebrate our feathered friends together.",
        "topics": ["Bird Watching", "Outdoors", "Nature"],
    },
    {
        "name": "Music Lovers",
        "description": "Share your favorite songs, artists, and musical memories.",
        "topics": ["Music"],
    },
    {
        "name": "Pet Lovers",
        "description": "Celebrate our furry, feathered, and scaly companions.",
        "topics": ["Pets"],
    },
    {
        "name": "Walking Club",
        "description": "Stay active and enjoy the outdoors with fellow walkers.",
        "topics": ["Walking", "Outdoors", "Fitness"],
    },
    {
        "name": "Chess & Card Games Club",
        "description": "Weekly virtual game nights with chess, card games, and friendly competition.",
        "topics": ["Chess", "Card Games"],
    },
    {
        "name": "Painting & Art Circle",
        "description": "Share your artwork, get inspired, and explore creative techniques together.",
        "topics": ["Painting", "Art", "Crafts"],
    },
]

USERS = [
    {
        "email": "test@turtle.app",
        "name": "Margaret Thompson",
        "password": "password123",
        "interests": ["Gardening", "Crocheting", "Knitting", "Movies", "Reading", "Baking"],
        "personality": {
            "q1": "Focus on doing the right thing and fixing what's wrong",
            "q2": "Listen more than I speak",
            "q3": "Volunteering in the community",
            "q4": "Share my values openly",
            "q5": "Shared values and integrity",
        },
        "groups": ["Garden Enthusiasts", "Yarn Crafters Circle", "Book Club Friends", "Cooking & Baking Circle"],
    },
    {
        "email": "dorothy.harris@turtle.app",
        "name": "Dorothy Harris",
        "password": "password123",
        "interests": ["Gardening", "Bird Watching", "Walking", "Photography"],
        "personality": {
            "q1": "Step back and analyze it objectively",
            "q2": "Ask thoughtful questions",
            "q3": "Learning something new",
            "q4": "Ask lots of questions to understand them",
            "q5": "Learning and intellectual growth",
        },
        "groups": ["Garden Enthusiasts", "Bird Watchers Club", "Walking Club", "Photography Circle"],
    },
    {
        "email": "helen.martinez@turtle.app",
        "name": "Helen Martinez",
        "password": "password123",
        "interests": ["Knitting", "Crocheting", "Painting", "Music"],
        "personality": {
            "q1": "Reflect on my feelings and the deeper meaning",
            "q2": "Share stories and personal experiences",
            "q3": "Reading, journaling, or creating something",
            "q4": "Look for a deep personal connection",
            "q5": "Meaningful, authentic interactions",
        },
        "groups": ["Yarn Crafters Circle", "Painting & Art Circle", "Music Lovers"],
    },
    {
        "email": "robert.chen@turtle.app",
        "name": "Robert Chen",
        "password": "password123",
        "interests": ["Chess", "Card Games", "Reading", "Fishing"],
        "personality": {
            "q1": "Look for the most efficient solution to succeed",
            "q2": "Get straight to the point",
            "q3": "Working on a personal project or goal",
            "q4": "Keep it professional and efficient",
            "q5": "Getting things done together",
        },
        "groups": ["Chess & Card Games Club", "Book Club Friends", "Fishing Friends"],
    },
    {
        "email": "barbara.wilson@turtle.app",
        "name": "Barbara Wilson",
        "password": "password123",
        "interests": ["Cooking", "Baking", "Movies", "Music"],
        "personality": {
            "q1": "Look for the positive opportunities it presents",
            "q2": "Keep things light and positive",
            "q3": "Trying something fun and spontaneous",
            "q4": "Bring energy and enthusiasm",
            "q5": "Fun and shared enjoyment",
        },
        "groups": ["Cooking & Baking Circle", "Classic Movie Buffs", "Music Lovers"],
    },
    {
        "email": "james.oconnor@turtle.app",
        "name": "James O'Connor",
        "password": "password123",
        "interests": ["Fishing", "Walking", "Bird Watching", "Photography"],
        "personality": {
            "q1": "Think about how to help others through it",
            "q2": "Make sure everyone feels included",
            "q3": "Volunteering in the community",
            "q4": "Focus on finding common ground",
            "q5": "Warmth and care for one another",
        },
        "groups": ["Fishing Friends", "Walking Club", "Bird Watchers Club", "Photography Circle"],
    },
    {
        "email": "patricia.lee@turtle.app",
        "name": "Patricia Lee",
        "password": "password123",
        "interests": ["Painting", "Reading", "Movies", "Pets"],
        "personality": {
            "q1": "Reflect on my feelings and the deeper meaning",
            "q2": "Listen more than I speak",
            "q3": "Reading, journaling, or creating something",
            "q4": "Look for a deep personal connection",
            "q5": "Meaningful, authentic interactions",
        },
        "groups": ["Painting & Art Circle", "Book Club Friends", "Classic Movie Buffs", "Pet Lovers"],
    },
    {
        "email": "frank.nguyen@turtle.app",
        "name": "Frank Nguyen",
        "password": "password123",
        "interests": ["Chess", "Card Games", "Fishing", "Walking"],
        "personality": {
            "q1": "Consider all possible risks and outcomes",
            "q2": "Plan ahead before speaking",
            "q3": "Organizing and planning",
            "q4": "Hold back until I know them better",
            "q5": "Safety and reliability",
        },
        "groups": ["Chess & Card Games Club", "Fishing Friends", "Walking Club"],
    },
    {
        "email": "susan.baker@turtle.app",
        "name": "Susan Baker",
        "password": "password123",
        "interests": ["Music", "Pets", "Cooking", "Gardening"],
        "personality": {
            "q1": "Think about how to help others through it",
            "q2": "Make sure everyone feels included",
            "q3": "Spending time with close friends or family",
            "q4": "Focus on finding common ground",
            "q5": "Warmth and care for one another",
        },
        "groups": ["Music Lovers", "Pet Lovers", "Cooking & Baking Circle", "Garden Enthusiasts"],
    },
    {
        "email": "walter.scott@turtle.app",
        "name": "Walter Scott",
        "password": "password123",
        "interests": ["Movies", "Music", "Reading", "Bird Watching"],
        "personality": {
            "q1": "Take charge and confront it directly",
            "q2": "Take the lead",
            "q3": "Taking on a challenge",
            "q4": "Take initiative in the conversation",
            "q5": "Clear leadership and direction",
        },
        "groups": ["Classic Movie Buffs", "Music Lovers", "Book Club Friends", "Bird Watchers Club"],
    },
    {
        "email": "carol.adams@turtle.app",
        "name": "Carol Adams",
        "password": "password123",
        "interests": ["Knitting", "Painting", "Pets", "Baking"],
        "personality": {
            "q1": "Focus on doing the right thing and fixing what's wrong",
            "q2": "Make sure everyone feels included",
            "q3": "Spending time with close friends or family",
            "q4": "Share my values openly",
            "q5": "Shared values and integrity",
        },
        "groups": ["Yarn Crafters Circle", "Painting & Art Circle", "Pet Lovers", "Cooking & Baking Circle"],
    },
    {
        "email": "nancy.patel@turtle.app",
        "name": "Nancy Patel",
        "password": "password123",
        "interests": ["Photography", "Painting", "Walking", "Pets"],
        "personality": {
            "q1": "Look for the positive opportunities it presents",
            "q2": "Share stories and personal experiences",
            "q3": "Trying something fun and spontaneous",
            "q4": "Bring energy and enthusiasm",
            "q5": "Fun and shared enjoyment",
        },
        "groups": ["Photography Circle", "Painting & Art Circle", "Walking Club", "Pet Lovers"],
    },
    {
        "email": "george.murphy@turtle.app",
        "name": "George Murphy",
        "password": "password123",
        "interests": ["Chess", "Card Games", "Reading", "Movies"],
        "personality": {
            "q1": "Consider all possible risks and outcomes",
            "q2": "Plan ahead before speaking",
            "q3": "Working on a personal project or goal",
            "q4": "Ask lots of questions to understand them",
            "q5": "Learning and intellectual growth",
        },
        "groups": ["Chess & Card Games Club", "Book Club Friends", "Classic Movie Buffs"],
    },
]


def seed():
    db = SessionLocal()
    try:
        if db.query(Group).count() > 0:
            print("Database already seeded. Skipping.")
            return

        # Create groups
        group_map = {}
        for g in GROUPS:
            group = Group(name=g["name"], description=g["description"])
            group.topics = g["topics"]
            db.add(group)
            db.flush()
            group_map[g["name"]] = group

        # Create users
        for u in USERS:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if existing:
                continue

            user = User(
                email=u["email"],
                name=u["name"],
                password_hash=hash_password(u["password"]),
            )
            db.add(user)
            db.flush()

            profile = Profile(
                user_id=user.id,
                guardian_enabled=False,
                onboarding_complete=True,
            )
            profile.interests = u["interests"]
            profile.personality_scores = u["personality"]
            db.add(profile)
            db.flush()

            for i, group_name in enumerate(u["groups"]):
                group = group_map.get(group_name)
                if group:
                    membership = GroupMembership(
                        user_id=user.id,
                        group_id=group.id,
                        is_favorite=(i < 2),
                    )
                    db.add(membership)

        db.commit()
        print("Seeded successfully!")
        print(f"  Created {len(GROUPS)} groups")
        print(f"  Created {len(USERS)} users")
    finally:
        db.close()


if __name__ == "__main__":
    seed()