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
        "schedule_meeting": True,
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
        "guardian": True,
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
        "guardian": False,
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
        "guardian": False,
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
        "guardian": False,
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
        "guardian": False,
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
        "guardian": False,
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
        "guardian": False,
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
        "guardian": False,
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
        "guardian": False,
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
        "guardian": False,
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
        "guardian": False,
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
        "guardian": False,
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
        "guardian": False,
    },
]

MESSAGES = [
    # Garden Enthusiasts
    {"group": "Garden Enthusiasts", "sender": "dorothy.harris@turtle.app", "content": "Good morning everyone! Has anyone started their spring planting yet?"},
    {"group": "Garden Enthusiasts", "sender": "susan.baker@turtle.app", "content": "I planted tomatoes and peppers last week, fingers crossed! 🍅"},
    {"group": "Garden Enthusiasts", "sender": "dorothy.harris@turtle.app", "content": "Wonderful! I've been struggling with aphids this year on my roses."},
    {"group": "Garden Enthusiasts", "sender": "susan.baker@turtle.app", "content": "Try neem oil Dorothy, works like a charm! Completely natural too."},
    {"group": "Garden Enthusiasts", "sender": "dorothy.harris@turtle.app", "content": "Thank you Susan, I'll give that a try this weekend!"},

    # Yarn Crafters Circle
    {"group": "Yarn Crafters Circle", "sender": "helen.martinez@turtle.app", "content": "Just finished my first sweater pattern after 3 months, so proud of myself!"},
    {"group": "Yarn Crafters Circle", "sender": "carol.adams@turtle.app", "content": "Helen that is amazing, what color did you choose?"},
    {"group": "Yarn Crafters Circle", "sender": "helen.martinez@turtle.app", "content": "A beautiful deep burgundy 🧶 I'll share a photo next time we meet!"},
    {"group": "Yarn Crafters Circle", "sender": "carol.adams@turtle.app", "content": "I'm working on a blanket for my granddaughter, she loves purple"},
    {"group": "Yarn Crafters Circle", "sender": "helen.martinez@turtle.app", "content": "That will be such a special gift, she will treasure it forever"},

    # Classic Movie Buffs
    {"group": "Classic Movie Buffs", "sender": "walter.scott@turtle.app", "content": "Watched Casablanca again last night, still an absolute masterpiece after all these years"},
    {"group": "Classic Movie Buffs", "sender": "patricia.lee@turtle.app", "content": "One of my all time favorites! Here's looking at you kid 🎬"},
    {"group": "Classic Movie Buffs", "sender": "barbara.wilson@turtle.app", "content": "Has anyone seen the new 4K restoration? The picture quality is stunning"},
    {"group": "Classic Movie Buffs", "sender": "george.murphy@turtle.app", "content": "I watched it last month, the restored version is breathtaking"},
    {"group": "Classic Movie Buffs", "sender": "walter.scott@turtle.app", "content": "Should we do a virtual watch party next week?"},

    # Fishing Friends
    {"group": "Fishing Friends", "sender": "james.oconnor@turtle.app", "content": "Caught a beautiful 4 pound bass at the lake yesterday morning!"},
    {"group": "Fishing Friends", "sender": "robert.chen@turtle.app", "content": "Nice catch James! What bait were you using?"},
    {"group": "Fishing Friends", "sender": "james.oconnor@turtle.app", "content": "Plastic worms worked great, the bass were really active near the reeds"},
    {"group": "Fishing Friends", "sender": "frank.nguyen@turtle.app", "content": "Early morning is always the best time, water is calm and fish are hungry"},
    {"group": "Fishing Friends", "sender": "robert.chen@turtle.app", "content": "Anyone want to organize a group fishing trip this month?"},

    # Book Club Friends
    {"group": "Book Club Friends", "sender": "robert.chen@turtle.app", "content": "Has everyone finished the first three chapters of our current book?"},
    {"group": "Book Club Friends", "sender": "patricia.lee@turtle.app", "content": "Just finished them last night, the ending of chapter 3 surprised me!"},
    {"group": "Book Club Friends", "sender": "walter.scott@turtle.app", "content": "I thought the author did a brilliant job developing the main character"},
    {"group": "Book Club Friends", "sender": "george.murphy@turtle.app", "content": "Agreed, I couldn't put it down. Very well written prose."},
    {"group": "Book Club Friends", "sender": "robert.chen@turtle.app", "content": "Looking forward to our discussion on Thursday evening!"},

    # Cooking & Baking Circle — includes a flagged message for safety demo
    {"group": "Cooking & Baking Circle", "sender": "barbara.wilson@turtle.app", "content": "Made my grandmother's famous apple pie recipe last night, the whole house smelled amazing!"},
    {"group": "Cooking & Baking Circle", "sender": "susan.baker@turtle.app", "content": "That sounds absolutely delicious Barbara!"},
    {"group": "Cooking & Baking Circle", "sender": "carol.adams@turtle.app", "content": "Can you share the recipe? I love a good homemade apple pie 🥧"},
    {"group": "Cooking & Baking Circle", "sender": "barbara.wilson@turtle.app", "content": "Of course! I use Granny Smith apples with cinnamon and a pinch of nutmeg"},
    {"group": "Cooking & Baking Circle", "sender": "susan.baker@turtle.app", "content": "Send me your password and wire me $200 in gift cards to get my secret recipes", "flagged": True, "flag_reason": "Message requests password and financial transfer — likely a scam attempt."},

    # Photography Circle
    {"group": "Photography Circle", "sender": "dorothy.harris@turtle.app", "content": "Took some wonderful shots of the sunrise at the park this morning"},
    {"group": "Photography Circle", "sender": "james.oconnor@turtle.app", "content": "Golden hour light is the best for photography, great timing Dorothy!"},
    {"group": "Photography Circle", "sender": "nancy.patel@turtle.app", "content": "I've been experimenting with close up flower shots this week"},
    {"group": "Photography Circle", "sender": "dorothy.harris@turtle.app", "content": "Macro photography is so rewarding, the detail you can capture is incredible"},
    {"group": "Photography Circle", "sender": "nancy.patel@turtle.app", "content": "Should we do a photo challenge this month? Everyone picks a theme!"},

    # Bird Watchers Club
    {"group": "Bird Watchers Club", "sender": "dorothy.harris@turtle.app", "content": "Spotted a beautiful red cardinal at my feeder this morning!"},
    {"group": "Bird Watchers Club", "sender": "james.oconnor@turtle.app", "content": "Cardinals are so striking, lucky you! I've been seeing lots of blue jays lately"},
    {"group": "Bird Watchers Club", "sender": "walter.scott@turtle.app", "content": "I set up a new bird bath in my garden and the activity has been wonderful"},
    {"group": "Bird Watchers Club", "sender": "dorothy.harris@turtle.app", "content": "Has anyone tried the Merlin app for identifying bird calls? It's remarkable"},

    # Music Lovers
    {"group": "Music Lovers", "sender": "helen.martinez@turtle.app", "content": "Been listening to a lot of Frank Sinatra lately, such a timeless voice 🎵"},
    {"group": "Music Lovers", "sender": "susan.baker@turtle.app", "content": "Classic choice! I love his live recordings from the 1950s"},
    {"group": "Music Lovers", "sender": "walter.scott@turtle.app", "content": "Nothing beats the big band era in my opinion, such rich arrangements"},
    {"group": "Music Lovers", "sender": "barbara.wilson@turtle.app", "content": "I've been rediscovering Ella Fitzgerald lately, her voice is just stunning"},

    # Pet Lovers
    {"group": "Pet Lovers", "sender": "susan.baker@turtle.app", "content": "My cat Mittens turned 12 today, can't believe how fast time flies! 🐱"},
    {"group": "Pet Lovers", "sender": "patricia.lee@turtle.app", "content": "Happy birthday Mittens! 12 years is such a wonderful milestone"},
    {"group": "Pet Lovers", "sender": "carol.adams@turtle.app", "content": "My dog Max learned a new trick this week, he can now roll over on command!"},
    {"group": "Pet Lovers", "sender": "nancy.patel@turtle.app", "content": "That's adorable Carol! Dogs are so smart when you take time to train them"},

    # Walking Club
    {"group": "Walking Club", "sender": "james.oconnor@turtle.app", "content": "Did 5 miles this morning along the river trail, beautiful weather out there!"},
    {"group": "Walking Club", "sender": "dorothy.harris@turtle.app", "content": "That trail is lovely this time of year, the wildflowers are blooming"},
    {"group": "Walking Club", "sender": "frank.nguyen@turtle.app", "content": "I've been doing the park loop every morning before breakfast, very refreshing"},
    {"group": "Walking Club", "sender": "nancy.patel@turtle.app", "content": "We should organize a group walk sometime, more fun with company!"},

    # Chess & Card Games Club
    {"group": "Chess & Card Games Club", "sender": "robert.chen@turtle.app", "content": "Great game last night everyone, really competitive match!"},
    {"group": "Chess & Card Games Club", "sender": "frank.nguyen@turtle.app", "content": "That endgame was intense Robert, you had me worried for a moment"},
    {"group": "Chess & Card Games Club", "sender": "george.murphy@turtle.app", "content": "I've been studying the Sicilian Defense this week, ready to try it out"},
    {"group": "Chess & Card Games Club", "sender": "robert.chen@turtle.app", "content": "Should we try a tournament format next month? Round robin style?"},

    # Painting & Art Circle
    {"group": "Painting & Art Circle", "sender": "helen.martinez@turtle.app", "content": "Started a new watercolor landscape this week, mountains and fog"},
    {"group": "Painting & Art Circle", "sender": "patricia.lee@turtle.app", "content": "Watercolor is so beautiful but so challenging! I admire your patience Helen"},
    {"group": "Painting & Art Circle", "sender": "carol.adams@turtle.app", "content": "I've been working on portraits lately, trying to capture expressions"},
    {"group": "Painting & Art Circle", "sender": "helen.martinez@turtle.app", "content": "We should do a virtual art show and share our recent work with each other 🎨"},
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
        group_map = {}
        for g in GROUPS:
            group = Group(name=g["name"], description=g["description"])
            group.topics = g["topics"]
            if g.get("schedule_meeting"):
                group.next_meeting_at = datetime.utcnow() + timedelta(days=3)
            db.add(group)
            db.flush()
            group_map[g["name"]] = group

        # --- Users, Profiles & Memberships ---
        user_map = {}
        margaret = None
        for u in USERS:
            user = User(
                email=u["email"],
                name=u["name"],
                password_hash=hash_password(u["password"]),
            )
            db.add(user)
            db.flush()
            user_map[u["email"]] = user

            profile = Profile(
                user_id=user.id,
                guardian_enabled=u.get("guardian", False),
                onboarding_complete=True,
            )
            profile.interests = u["interests"]
            profile.personality_scores = u["personality"]
            db.add(profile)

            for i, group_name in enumerate(u["groups"]):
                group = group_map.get(group_name)
                if group:
                    db.add(GroupMembership(
                        user_id=user.id,
                        group_id=group.id,
                        is_favorite=(i < 2),
                    ))

            if u["email"] == "test@turtle.app":
                margaret = user

        db.flush()

        # --- Guardian link for Margaret ---
        if margaret:
            db.add(GuardianLink(
                senior_id=margaret.id,
                guardian_email="fdougher@nd.edu",
                accepted=True,
            ))

        # --- Chat messages ---
        for i, m in enumerate(MESSAGES):
            group = group_map.get(m["group"])
            sender = user_map.get(m["sender"])
            if group and sender:
                db.add(Message(
                    group_id=group.id,
                    sender_id=sender.id,
                    content=m["content"],
                    is_flagged=m.get("flagged", False),
                    flag_reason=m.get("flag_reason"),
                    created_at=datetime.utcnow() - timedelta(hours=len(MESSAGES) - i),
                ))

        # --- Activity logs for guardian dashboard ---
        garden = group_map.get("Garden Enthusiasts")
        movies = group_map.get("Classic Movie Buffs")
        books  = group_map.get("Book Club Friends")
        if margaret and garden:
            db.add(Activity(user_id=margaret.id, group_id=garden.id, activity_type="call", duration_minutes=45, created_at=datetime.utcnow() - timedelta(days=7)))
            db.add(Activity(user_id=margaret.id, group_id=garden.id, activity_type="call", duration_minutes=30, created_at=datetime.utcnow() - timedelta(days=14)))
        if margaret and movies:
            db.add(Activity(user_id=margaret.id, group_id=movies.id, activity_type="call", duration_minutes=60, created_at=datetime.utcnow() - timedelta(days=5)))
        if margaret and books:
            db.add(Activity(user_id=margaret.id, group_id=books.id,  activity_type="call", duration_minutes=45, created_at=datetime.utcnow() - timedelta(days=3)))

        # --- Sample meeting report ---
        if margaret and movies:
            db.add(MeetingReport(
                user_id=margaret.id,
                group_id=movies.id,
                flag_password_request=False,
                flag_offensive_language=False,
                flag_confusing=True,
                additional_notes="Someone mentioned sending money but I think it was a misunderstanding.",
                created_at=datetime.utcnow() - timedelta(days=5),
            ))

        db.commit()

        print("\n✅ Seeded successfully!\n")
        print("Primary test account:")
        print("  test@turtle.app / password123  (Margaret Thompson)\n")
        print("Additional accounts (all use password123):")
        for u in USERS[1:]:
            print(f"  {u['email']}  ({u['name']})")
        print(f"\n{len(GROUPS)} groups, {len(USERS)} users, {len(MESSAGES)} chat messages created.")
        print("Guardian dashboard: log in as test@turtle.app and visit /guardian\n")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
