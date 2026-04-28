import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

print("GROQ KEY:", os.getenv("GROQ_API_KEY"))  # ADD THIS

from app.database import SessionLocal
from app.models.user import User
from app.services.matching import get_suggested_groups

db = SessionLocal()
user = db.query(User).filter(User.email == "test@turtle.app").first()

print("User:", user.name)
print("Interests:", user.profile.interests)
print("Personality:", user.profile.personality_scores)
print()

groups = get_suggested_groups(db, user.profile, limit=6)

print("AI Suggested Groups:")
for i, g in enumerate(groups, 1):
    print(f"  {i}. {g.name} — {g.topics}")

db.close()