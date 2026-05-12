import string
import random
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from db import get_db
from auth import require_user
from models import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _gen_slug(length=6):
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=length))


@router.post("", response_model=ProjectResponse)
def create_project(data: ProjectCreate, user=Depends(require_user)):
    db = next(get_db())
    slug = _gen_slug()
    cursor = db.execute(
        "INSERT INTO projects (id, name, description, deadline, standup_closes_at, leader_id) VALUES (?, ?, ?, ?, ?, ?)",
        (slug, data.name, data.description, data.deadline, data.standup_closes_at or "21:00", user["id"]),
    )
    db.execute(
        "INSERT INTO project_members (project_id, user_id, role, status, invite_type, joined_at, is_first_standup) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (slug, user["id"], "Project Leader", "active", "email", datetime.utcnow().isoformat(), 0),
    )
    db.commit()
    project = db.execute("SELECT * FROM projects WHERE id = ?", (slug,)).fetchone()
    return {**dict(project), "role": "Project Leader", "status": "active", "today_status": "standup_due"}


@router.get("")
def list_projects(user=Depends(require_user)):
    db = next(get_db())
    rows = db.execute(
        """
        SELECT p.*, pm.role, pm.status,
            CASE WHEN s.id IS NOT NULL THEN 'submitted'
                 WHEN b.id IS NOT NULL THEN 'brief_ready'
                 ELSE 'standup_due' END AS today_status
        FROM projects p
        JOIN project_members pm ON p.id = pm.project_id
        LEFT JOIN standups s ON s.project_id = p.id AND s.member_id = pm.id AND s.date = ?
        LEFT JOIN briefs b ON b.project_id = p.id AND b.date = ?
        WHERE pm.user_id = ? AND pm.status = 'active'
        ORDER BY p.created_at DESC
    """,
        (date.today(), date.today(), user["id"]),
    ).fetchall()
    return [dict(r) for r in rows]


@router.get("/{project_id}")
def get_project(project_id: str, user=Depends(require_user)):
    db = next(get_db())
    project = db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not project:
        raise HTTPException(404, "Project not found")
    member = db.execute(
        "SELECT * FROM project_members WHERE project_id = ? AND user_id = ? AND status = 'active'",
        (project_id, user["id"]),
    ).fetchone()
    if not member:
        raise HTTPException(403, "You don't have access to this project")
    members = db.execute(
        "SELECT pm.*, u.name, u.email, u.avatar_url FROM project_members pm LEFT JOIN users u ON pm.user_id = u.id WHERE pm.project_id = ? AND pm.status != 'removed'",
        (project_id,),
    ).fetchall()
    return {**dict(project), "members": [dict(m) for m in members], "current_member": dict(member)}