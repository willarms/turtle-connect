import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# -----------------------------
# SAMPLE USERS (TEST DATA)
# -----------------------------
def get_test_users():
    return [
        {"id": "u1", "interests": ["reading", "history"], "personality": "caregiver"},
        {"id": "u2", "interests": ["books", "writing"], "personality": "social"},
        {"id": "u3", "interests": ["sports", "fitness"], "personality": "independent"},
        {"id": "u4", "interests": ["music", "guitar"], "personality": "creative"},
        {"id": "u5", "interests": ["gaming", "tech"], "personality": "analytical"},
        {"id": "u6", "interests": ["art", "design"], "personality": "creative"},
        {"id": "u7", "interests": ["movies", "storytelling"], "personality": "social"},
        {"id": "u8", "interests": ["running", "health"], "personality": "independent"},
        {"id": "u9", "interests": ["science", "math"], "personality": "analytical"},
        {"id": "u10", "interests": ["travel", "culture"], "personality": "adventurous"},
    ]


# -----------------------------
# CORE LLM FUNCTION
# -----------------------------
def group_users_with_llm(users):
    prompt = f"""
You are a social matching system.

Group users into 2–4 balanced groups based on:
- shared interests
- personality compatibility

Rules:
- Each user appears in EXACTLY ONE group
- Groups should be socially compatible
- Try to balance group sizes
- Return ONLY valid JSON

Return format:
{{
  "groups": [
    {{
      "name": "Group name",
      "members": ["u1", "u2"],
      "reason": "why these users fit"
    }}
  ]
}}

Users:
{json.dumps(users, indent=2)}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    content = response.choices[0].message.content
    print("\n🧠 RAW MODEL OUTPUT:\n", content)

    # -----------------------------
    # SAFE JSON PARSING
    # -----------------------------
    try:
        parsed = json.loads(content)
        print("\n✅ PARSED GROUPS:\n", json.dumps(parsed, indent=2))
        return parsed

    except json.JSONDecodeError:
        print("\n❌ JSON PARSE FAILED — trying cleanup...")

        # fallback cleanup (common LLM issue)
        cleaned = content.strip()
        cleaned = cleaned.replace("```json", "").replace("```", "")

        try:
            parsed = json.loads(cleaned)
            print("\n✅ PARSED AFTER CLEANUP:\n", json.dumps(parsed, indent=2))
            return parsed
        except:
            print("\n❌ FAILED COMPLETELY — model did not return valid JSON")
            return None


# -----------------------------
# RUN TEST
# -----------------------------
if __name__ == "__main__":
    users = get_test_users()
    result = group_users_with_llm(users)