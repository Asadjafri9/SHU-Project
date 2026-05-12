import secrets
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from db import get_db
from auth import require_user
from models import MemberInvite, InviteLinkCreate

router = APIRouter(prefix="/api/projects/{project_id}", tags=["members"])


@router.post("/members")
def add_member_by_email(project_id: str, data: MemberInvite, user=Depends(require_user)):
    db = next(get_db())
    leader = db.execute(
        "SELECT * FROM project_members WHERE project_id = ? AND user_id = ? AND role = 'Project Leader'",
        (project_id, user["id"]),
    ).fetchone()
    if not leader:
        raise HTTPException(403, "Only the leader can add members")

    existing_user = db.execute("SELECT * FROM users WHERE email = ?", (data.email,)).fetchone()
    if existing_user:
        db.execute(
            "INSERT INTO project_members (project_id, user_id, email, role, status, invite_type) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, existing_user["id"], data.email, data.role, "invited", "email"),
        )
    else:
        db.execute(
            "INSERT INTO project_members (project_id, email, role, status, invite_type) VALUES (?, ?, ?, ?, ?)",
            (project_id, data.email, data.role, "invited", "email"),
        )
    db.commit()
    return {"ok": True}


@router.get("/invite-links")
def list_invite_links(project_id: str, user=Depends(require_user)):
    db = next(get_db())
    leader = db.execute(
        "SELECT * FROM project_members WHERE project_id = ? AND user_id = ? AND role = 'Project Leader'",
        (project_id, user["id"]),
    ).fetchone()
    if not leader:
        raise HTTPException(403, "Only the leader can manage invite links")

    links = db.execute(
        "SELECT * FROM project_members WHERE project_id = ? AND invite_type = 'link' AND status = 'invited'",
        (project_id,),
    ).fetchall()
    return [dict(l) for l in links]


@router.post("/invite-links")
def create_invite_link(project_id: str, data: InviteLinkCreate, user=Depends(require_user)):
    db = next(get_db())
    leader = db.execute(
        "SELECT * FROM project_members WHERE project_id = ? AND user_id = ? AND role = 'Project Leader'",
        (project_id, user["id"]),
    ).fetchone()
    if not leader:
        raise HTTPException(403, "Only the leader can create invite links")

    token = secrets.token_urlsafe(16)
    db.execute(
        "INSERT INTO project_members (project_id, role, status, invite_token, invite_type) VALUES (?, ?, ?, ?, ?)",
        (project_id, data.role, "invited", token, "link"),
    )
    db.commit()
    return {"invite_token": token, "invite_url": f"/join/{token}"}


@router.delete("/members/{member_id}")
def remove_member(project_id: str, member_id: int, user=Depends(require_user)):
    db = next(get_db())
    leader = db.execute(
        "SELECT * FROM project_members WHERE project_id = ? AND user_id = ? AND role = 'Project Leader'",
        (project_id, user["id"]),
    ).fetchone()
    if not leader:
        raise HTTPException(403, "Only the leader can remove members")

    db.execute(
        "UPDATE project_members SET status = 'removed' WHERE id = ? AND project_id = ?",
        (member_id, project_id),
    )
    db.commit()
    return {"ok": True}


@router.get("/join/{token}")
def preview_invite(token: str):
    db = next(get_db())
    invite = db.execute(
        "SELECT pm.*, p.name as project_name FROM project_members pm JOIN projects p ON pm.project_id = p.id WHERE pm.invite_token = ?",
        (token,),
    ).fetchone()
    if not invite:
        raise HTTPException(404, "Invite not found")
    if invite["status"] != "invited":
        raise HTTPException(410, "This invite link has already been used")
    return {"project_name": invite["project_name"], "role": invite["role"], "is_used": False}


@router.post("/join/{token}")
def accept_invite(token: str, user=Depends(require_user)):
    db = next(get_db())
    invite = db.execute(
        "SELECT * FROM project_members WHERE invite_token = ? AND status = 'invited'",
        (token,),
    ).fetchone()
    if not invite:
        raise HTTPException(404, "Invite not found or already used")

    db.execute(
        "UPDATE project_members SET user_id = ?, status = 'active', joined_at = ?, invite_token = NULL WHERE id = ?",
        (user["id"], datetime.utcnow().isoformat(), invite["id"]),
    )
    db.commit()
    return {"ok": True, "project_id": invite["project_id"]}