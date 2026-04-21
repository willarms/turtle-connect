import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import Profile, User
from app.schemas.auth import (
    GoogleAuthorizeResponse,
    GoogleCallbackRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth import (
    create_access_token,
    get_user_by_email,
    hash_password,
    verify_password,
)
from app.services.google_oauth import (
    build_authorize_url,
    exchange_code_for_tokens,
    get_google_user_info,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if get_user_by_email(db, body.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=body.email, name=body.name, password_hash=hash_password(body.password))
    db.add(user)
    db.flush()

    profile = Profile(user_id=user.id)
    db.add(profile)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, body.email)
    if not user or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


# ---------------------------------------------------------------------------
# Google OAuth 2.0
# ---------------------------------------------------------------------------

LOGIN_SCOPES = ["openid", "email", "profile"]
CALENDAR_SCOPES = LOGIN_SCOPES + [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/meetings.space.readonly",
]


@router.get("/google/authorize-url-v2", response_model=GoogleAuthorizeResponse)
def google_authorize_url_v2(
    scope: str = Query("login"),
    state: str = Query(...),
    code_challenge: str = Query(...),
):
    """Build the Google consent URL with PKCE code_challenge supplied by frontend."""
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")

    scopes = CALENDAR_SCOPES if scope == "calendar" else LOGIN_SCOPES
    url = build_authorize_url(scopes, state, code_challenge)
    return GoogleAuthorizeResponse(authorize_url=url)


@router.post("/google/callback", response_model=TokenResponse)
async def google_callback(body: GoogleCallbackRequest, db: Session = Depends(get_db)):
    """
    Exchange the Google authorization code for tokens, then create or find the user.
    Returns a Turtle Connect JWT identical to email/password login.
    """
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")

    try:
        tokens = await exchange_code_for_tokens(body.code, body.code_verifier)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Google token exchange failed: {exc}")

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    try:
        user_info = await get_google_user_info(access_token)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not fetch Google user info: {exc}")

    google_id = user_info["google_id"]
    email = user_info["email"]
    name = user_info["name"]

    user = db.query(User).filter(User.google_id == google_id).first()
    if not user and email:
        user = get_user_by_email(db, email)

    if user:
        if not user.google_id:
            user.google_id = google_id
        if refresh_token:
            user.google_refresh_token = refresh_token
        db.commit()
        db.refresh(user)
    else:
        user = User(
            email=email,
            name=name,
            google_id=google_id,
            google_refresh_token=refresh_token,
            password_hash=None,
        )
        db.add(user)
        db.flush()
        profile = Profile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(user)

    jwt = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=jwt)
