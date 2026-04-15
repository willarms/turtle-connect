import os
import json
import re
from typing import Any, Dict, List, Optional

from groq import Groq
from dotenv import load_dotenv

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


def build_safety_payload(
    text: str,
    source_type: str = "message",
    conversation_id: Optional[str] = None,
    user_id: Optional[Any] = None,
    group_id: Optional[Any] = None,
    user_display_name: Optional[str] = None,
    extra_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a clean payload for the LLM.

    source_type examples:
    - "message"
    - "call_transcript"
    - "chat_snippet"
    """
    if not text or not text.strip():
        raise ValueError("Safety payload requires non-empty text.")

    payload = {
        "source_type": source_type,
        "conversation_id": conversation_id,
        "user_id": user_id,
        "group_id": group_id,
        "user_display_name": user_display_name,
        "text": text.strip(),
        "safety_rules": [
            "Flag credential requests such as passwords, PINs, verification codes, or banking logins.",
            "Flag financial solicitation or requests to move, send, wire, gift, or withdraw money.",
            "Flag attempts to move communication off-platform for suspicious reasons.",
            "Flag pressure, urgency, secrecy, intimidation, or manipulation.",
            "Flag impersonation, fake technical support, fake emergencies, or romance scam patterns.",
            "Do not flag normal friendly conversation just because money, family, or help is mentioned casually.",
            "Be conservative and brief. Only flag when there is a meaningful reason.",
        ],
        "output_preferences": {
            "keep_brief": True,
            "guardian_friendly_summary": True,
            "do_not_include_full_transcript": True,
        },
        "extra_context": extra_context or {},
    }

    return payload


def analyze_safety(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send the safety payload to the LLM and return structured safety analysis.
    """
    prompt = f"""
You are a safety monitoring system for a senior social app.

Your job:
- Review the provided text snippet.
- Detect potential scam, fraud, coercion, credential theft, financial exploitation, impersonation, or suspicious manipulation.
- Also detect if the text appears normal and harmless.
- Be brief and impartial.
- Do NOT overreact.
- Do NOT include legal advice.
- Do NOT include the full transcript in the output.

Return ONLY valid JSON. No markdown. No backticks. No extra commentary.

Required output format:
{{
  "is_flagged": true,
  "severity": "low",
  "alert_type": "credential_request",
  "reason": "Short factual explanation",
  "guardian_summary": "Short guardian-facing summary",
  "recommended_action": "monitor"
}}

Rules for fields:
- "is_flagged" must be true or false
- "severity" must be one of: "none", "low", "medium", "high"
- "alert_type" must be one of:
  "none",
  "credential_request",
  "financial_solicitation",
  "off_platform_pressure",
  "impersonation",
  "manipulation_or_coercion",
  "romance_scam_pattern",
  "technical_support_scam",
  "other_suspicious_behavior"
- "reason" should be 1 short sentence
- "guardian_summary" should be 1 short sentence suitable for a dashboard
- "recommended_action" must be one of:
  "none",
  "monitor",
  "review",
  "notify_guardian",
  "urgent_review"

If the text is harmless, return:
{{
  "is_flagged": false,
  "severity": "none",
  "alert_type": "none",
  "reason": "No meaningful safety concern detected.",
  "guardian_summary": "No alert.",
  "recommended_action": "none"
}}

Input payload:
{json.dumps(payload, indent=2)}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    content = response.choices[0].message.content

    print("\nRAW SAFETY MODEL OUTPUT:\n")
    print(content)

    return safe_parse_json(content)


def validate_safety_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the LLM safety output.
    Returns the cleaned result if valid.
    """
    required_fields = [
        "is_flagged",
        "severity",
        "alert_type",
        "reason",
        "guardian_summary",
        "recommended_action",
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing required field in safety result: {field}")

    if not isinstance(result["is_flagged"], bool):
        raise ValueError("'is_flagged' must be a boolean.")

    valid_severities = {"none", "low", "medium", "high"}
    if result["severity"] not in valid_severities:
        raise ValueError(f"Invalid severity: {result['severity']}")

    valid_alert_types = {
        "none",
        "credential_request",
        "financial_solicitation",
        "off_platform_pressure",
        "impersonation",
        "manipulation_or_coercion",
        "romance_scam_pattern",
        "technical_support_scam",
        "other_suspicious_behavior",
    }
    if result["alert_type"] not in valid_alert_types:
        raise ValueError(f"Invalid alert_type: {result['alert_type']}")

    valid_actions = {"none", "monitor", "review", "notify_guardian", "urgent_review"}
    if result["recommended_action"] not in valid_actions:
        raise ValueError(f"Invalid recommended_action: {result['recommended_action']}")

    if not isinstance(result["reason"], str) or not result["reason"].strip():
        raise ValueError("'reason' must be a non-empty string.")

    if not isinstance(result["guardian_summary"], str) or not result["guardian_summary"].strip():
        raise ValueError("'guardian_summary' must be a non-empty string.")

    # consistency checks
    if result["is_flagged"] is False:
        if result["severity"] != "none":
            raise ValueError("If is_flagged is false, severity must be 'none'.")
        if result["alert_type"] != "none":
            raise ValueError("If is_flagged is false, alert_type must be 'none'.")
        if result["recommended_action"] != "none":
            raise ValueError("If is_flagged is false, recommended_action must be 'none'.")

    if result["is_flagged"] is True and result["severity"] == "none":
        raise ValueError("Flagged results cannot have severity 'none'.")

    return result


def analyze_and_validate_safety(
    text: str,
    source_type: str = "message",
    conversation_id: Optional[str] = None,
    user_id: Optional[Any] = None,
    group_id: Optional[Any] = None,
    user_display_name: Optional[str] = None,
    extra_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience wrapper:
    build payload -> call LLM -> validate result
    """
    payload = build_safety_payload(
        text=text,
        source_type=source_type,
        conversation_id=conversation_id,
        user_id=user_id,
        group_id=group_id,
        user_display_name=user_display_name,
        extra_context=extra_context,
    )

    result = analyze_safety(payload)
    validated = validate_safety_result(result)
    return validated


def build_test_safety_cases() -> List[Dict[str, Any]]:
    """
    Test snippets for local development without needing the real database.
    """
    return [
        {
            "label": "harmless_chat",
            "source_type": "message",
            "text": "Hi Henry, I loved hearing about your favorite books today. Would you like to join our gardening chat tomorrow afternoon?",
        },
        {
            "label": "credential_request",
            "source_type": "message",
            "text": "This is support. I need your password and the 6-digit code sent to your phone so I can fix your account.",
        },
        {
            "label": "financial_solicitation",
            "source_type": "call_transcript",
            "text": "I am stuck overseas and need help immediately. Can you wire me $2,000 today and keep this between us for now?",
        },
        {
            "label": "off_platform_pressure",
            "source_type": "message",
            "text": "Don't use Turtle chat anymore. Message me on WhatsApp instead and don't mention this group to anyone.",
        },
        {
            "label": "possible_romance_scam",
            "source_type": "message",
            "text": "I feel such a deep connection with you already. I know we just met, but can you buy me a gift card so I can pay my phone bill?",
        },
        {
            "label": "borderline_but_safe",
            "source_type": "call_transcript",
            "text": "My daughter usually helps me with banking because websites confuse me sometimes, but I am doing okay today.",
        },
    ]


def run_local_safety_test() -> None:
    """
    Run several local test cases and print results.
    """
    test_cases = build_test_safety_cases()

    for case in test_cases:
        print("\n" + "=" * 70)
        print(f"TEST CASE: {case['label']}")
        print("=" * 70)

        try:
            result = analyze_and_validate_safety(
                text=case["text"],
                source_type=case["source_type"],
                conversation_id=f"test_{case['label']}",
                user_id="henry_01",
                group_id="group_books_01",
                user_display_name="Henry",
            )

            print("\nVALIDATED SAFETY RESULT:\n")
            print(json.dumps(result, indent=2))

        except Exception as e:
            print(f"\nERROR in test case '{case['label']}': {e}")


if __name__ == "__main__":
    run_local_safety_test()