"""
Google OAuth 2.0 helpers for SSO login and Google Meet link creation.

Login uses scopes: openid email profile
Meet link creation uses: calendar.events (incremental auth, requested separately)
"""
import json
import secrets
import urllib.parse

import httpx

from app.config import settings

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_CALENDAR_ENDPOINT = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
GOOGLE_MEET_API = "https://meet.googleapis.com/v2"


def build_authorize_url(scopes: list[str], state: str, code_challenge: str) -> str:
    """Build the Google OAuth 2.0 consent URL using PKCE."""
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{GOOGLE_AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"


async def exchange_code_for_tokens(code: str, code_verifier: str) -> dict:
    """Exchange authorization code for access/refresh tokens."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GOOGLE_TOKEN_ENDPOINT,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
                "code_verifier": code_verifier,
            },
        )
        resp.raise_for_status()
        return resp.json()


async def get_google_user_info(access_token: str) -> dict:
    """Fetch Google user profile using an access token."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            GOOGLE_USERINFO_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "google_id": data.get("sub"),
            "email": data.get("email"),
            "name": data.get("name", data.get("email", "User")),
        }


async def refresh_access_token(refresh_token: str) -> str:
    """Use a stored refresh token to get a fresh access token."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GOOGLE_TOKEN_ENDPOINT,
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


async def fetch_meet_activities(access_token: str, meet_url: str, since_iso: str) -> list[dict]:
    """
    Query the Meet REST API for completed conference records in a given space
    since a given ISO datetime. Returns a list of dicts:
      {"conference_id": str, "participant_google_ids": list[str], "duration_minutes": int, "ended_at": str}
    Returns an empty list on any error so callers can fail silently.
    """
    # Extract space code from URL: https://meet.google.com/abc-defg-hij -> abc-defg-hij
    space_code = meet_url.rstrip("/").split("/")[-1]
    space_name = f"spaces/{space_code}"
    headers = {"Authorization": f"Bearer {access_token}"}

    results = []
    try:
        async with httpx.AsyncClient() as client:
            # List conference records for this space since the cutoff
            resp = await client.get(
                f"{GOOGLE_MEET_API}/conferenceRecords",
                params={"filter": f'space.name="{space_name}" AND start_time>="{since_iso}"'},
                headers=headers,
            )
            print(f"[meet-sync] conferenceRecords status={resp.status_code} url={meet_url}")
            if resp.status_code != 200:
                print(f"[meet-sync] error body: {resp.text}")
                return []
            records = resp.json().get("conferenceRecords", [])
            print(f"[meet-sync] found {len(records)} record(s)")

            for record in records:
                record_name = record["name"]
                end_time = record.get("endTime")
                if not end_time:
                    continue  # meeting still in progress

                # Fetch participants for this record
                p_resp = await client.get(
                    f"{GOOGLE_MEET_API}/{record_name}/participants",
                    headers=headers,
                )
                if p_resp.status_code != 200:
                    continue
                participants = p_resp.json().get("participants", [])

                participant_google_ids = []
                total_duration = 0

                for p in participants:
                    signed_in = p.get("signedinUser", {})
                    # user resource name: "users/112233445566" — extract the ID
                    user_resource = signed_in.get("user", "")
                    google_id = user_resource.split("/")[-1] if user_resource else None
                    if google_id:
                        participant_google_ids.append(google_id)

                    # Sum up session durations for this participant
                    s_resp = await client.get(
                        f"{GOOGLE_MEET_API}/{p['name']}/participantSessions",
                        headers=headers,
                    )
                    if s_resp.status_code != 200:
                        continue
                    for session in s_resp.json().get("participantSessions", []):
                        start = session.get("startTime")
                        end = session.get("endTime")
                        if start and end:
                            from datetime import datetime as _dt
                            fmt = "%Y-%m-%dT%H:%M:%SZ"
                            try:
                                mins = int(
                                    (_dt.strptime(end, fmt) - _dt.strptime(start, fmt)).total_seconds() / 60
                                )
                                total_duration = max(total_duration, mins)
                            except ValueError:
                                pass

                results.append({
                    "conference_id": record_name,
                    "participant_google_ids": participant_google_ids,
                    "duration_minutes": max(total_duration, 1),
                    "ended_at": end_time,
                })
    except Exception as exc:
        print(f"[meet-sync] fetch_meet_activities failed: {exc}")

    return results


async def create_meet_link(access_token: str, group_name: str) -> dict:
    """
    Create a Google Calendar event with a Meet conference.
    Returns {"meet_url": str, "event_id": str}.
    """
    event_body = {
        "summary": f"Turtle Connect — {group_name}",
        "description": "Group video call via Turtle Connect",
        "start": {"dateTime": "2099-01-01T10:00:00Z", "timeZone": "UTC"},
        "end": {"dateTime": "2099-01-01T11:00:00Z", "timeZone": "UTC"},
        "conferenceData": {
            "createRequest": {
                "requestId": secrets.token_hex(8),
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GOOGLE_CALENDAR_ENDPOINT,
            params={"conferenceDataVersion": 1},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            content=json.dumps(event_body),
        )
        resp.raise_for_status()
        data = resp.json()
        return {"meet_url": data.get("hangoutLink", ""), "event_id": data.get("id", "")}
