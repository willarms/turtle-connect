"""
Safety / scam detection service — uses Groq to analyze messages for suspicious patterns.
"""
import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_message(content: str, sender_name: str = "Unknown", group_name: str = "Unknown") -> dict:
    """
    Uses Groq to analyze a message for scam/safety concerns.
    Returns {"flagged": bool, "reason": str or None, "severity": str}
    """
    prompt = f"""
You are a safety monitoring system for a senior social app.

Analyze this message for scams, fraud, manipulation, credential requests, or suspicious behavior.

Message from {sender_name} in group "{group_name}":
"{content}"

Return ONLY valid JSON. No markdown. No backticks.

Format:
{{
  "flagged": false,
  "severity": "none",
  "reason": null
}}

Rules:
- "flagged" must be true or false
- "severity" must be one of: "none", "low", "medium", "high"
- "reason" must be a short 1-sentence explanation or null if not flagged
- Flag: credential requests, password requests, money requests, gift cards, wire transfers, urgency/pressure, moving off platform, impersonation
- Do NOT flag normal friendly conversation
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        content_raw = response.choices[0].message.content.strip()
        content_raw = content_raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(content_raw)

        flagged = result.get("flagged", False)
        reason = result.get("reason", None)
        severity = result.get("severity", "none")

        if flagged:
            print(f"🚨 SAFETY FLAG: [{severity}] {reason} | Message: '{content[:60]}...'")

        return {"flagged": flagged, "reason": reason, "severity": severity}

    except Exception as e:
        print(f"Safety check failed: {e}")
        return {"flagged": False, "reason": None, "severity": "none"}