"""Pydantic schemas for request/response validation."""

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

USERNAME_RE = re.compile(r"^[a-z0-9_]{3,30}$")
URL_RE = re.compile(r"^https?://\S+$")


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.lower().strip()
        if not USERNAME_RE.match(v):
            raise ValueError("Username must be 3-30 chars: lowercase letters, numbers, underscores")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    bio: str
    avatar_url: str
    theme: str


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=500)
    theme: str | None = None

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v: str | None) -> str | None:
        if v is not None and v not in ("midnight", "sunset", "forest", "ocean", "mono"):
            raise ValueError("Unknown theme — pick midnight, sunset, forest, ocean or mono")
        return v


class LinkCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    url: str = Field(min_length=4, max_length=2000)
    icon: str = Field(default="link", max_length=50)
    sort_order: int = Field(default=0, ge=0)
    is_active: bool = True

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not URL_RE.match(v):
            raise ValueError("URL must start with http:// or https://")
        return v


class LinkUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    url: str | None = Field(default=None, min_length=4, max_length=2000)
    icon: str | None = Field(default=None, max_length=50)
    sort_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not URL_RE.match(v):
            raise ValueError("URL must start with http:// or https://")
        return v


class LinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    icon: str
    sort_order: int
    is_active: bool
    click_count: int
    created_at: datetime


class PageLink(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    icon: str


class PublicPage(BaseModel):
    username: str
    display_name: str
    bio: str
    avatar_url: str
    theme: str
    links: list[PageLink]


class DailyClick(BaseModel):
    date: str
    count: int


class AnalyticsOut(BaseModel):
    total_clicks: int
    total_links: int
    daily: list[DailyClick]
    top_links: list[LinkOut]
