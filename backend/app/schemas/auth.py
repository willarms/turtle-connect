from typing import Optional

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool = False


class GoogleAuthorizeResponse(BaseModel):
    authorize_url: str


class GoogleCallbackRequest(BaseModel):
    code: str
    code_verifier: str
    redirect_uri: Optional[str] = None
