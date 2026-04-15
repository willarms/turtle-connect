import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def safe_parse_json(content: str):
    content = content.strip()
    content = content.replace("```json", "").replace("```", "")

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise


def generate_groups(users):
    prompt = f"""
You are a social matching system.

Group users into 2–4 balanced groups.

Rules:
- Each user appears once
- Return ONLY valid JSON
- No markdown, no backticks

Format:
{{
  "groups": [
    {{
      "name": "Group name",
      "members": ["u1", "u2"],
      "reason": "why"
    }}
  ]
}}

Users:
{json.dumps(users)}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    content = response.choices[0].message.content

    return safe_parse_json(content)