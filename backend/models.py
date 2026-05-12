from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    avatar_url: Optional[str] = None


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    standup_closes_at: Optional[str] = "21:00"


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    standup_closes_at: str = "21:00"
    leader_id: int
    role: Optional[str] = None
    status: Optional[str] = None
    today_status: Optional[str] = None


class MemberInvite(BaseModel):
    email: str
    role: str = "Member"


class InviteLinkCreate(BaseModel):
    role: str


class StandupSubmit(BaseModel):
    did: str
    will_do: str
    blocker: Optional[str] = None