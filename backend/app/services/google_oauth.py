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
