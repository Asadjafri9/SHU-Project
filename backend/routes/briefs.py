import os
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from db import get_db
from auth import require_user
from ai import generate_brief_stream

router = APIRouter(prefix="/api/projects/{project_id}", tags=["briefs"])


@router.get("/brief/today")
def get_today_brief(project_id: str, user=Depends(require_user)):
    db = next(get_db())
    member = db.execute(
        "SELECT * FROM project_members WHERE project_id = ? AND user_id = ? AND status = 'active'",
        (project_id, user["id"]),
    ).fetchone()
    if not member:
        raise HTTPException(403, "Not a member of this project")

    brief = db.execute(
        "SELECT * FROM briefs WHERE project_id = ? AND date = ?",
        (project_id, date.today()),
    ).fetchone()
    if not brief:
        raise HTTPException(404, "No brief generated yet for today")
    return dict(brief)


@router.post("/brief")
def generate_brief(project_id: str, user=Depends(require_user)):
    db = next(get_db())
    leader = db.execute(
        "SELECT * FROM project_members WHERE project_id = ? AND user_id = ? AND role = 'Project Leader'",
        (project_id, user["id"]),
    ).fetchone()
    if not leader:
        raise HTTPException(403, "Only the leader can generate a brief")

    submissions = db.execute(
        """
        SELECT s.*, u.name, pm.role, pm.is_first_standup
        FROM standups s
        JOIN project_members pm ON s.member_id = pm.id
        LEFT JOIN users u ON pm.user_id = u.id
        WHERE s.project_id = ? AND s.date = ?
    """,
        (project_id, date.today()),
    ).fetchall()

    if not submissions:
        raise HTTPException(400, "No submissions yet — wait until at least one member submits.")

    active_members = db.execute(
        """
        SELECT pm.*, u.name FROM project_members pm
        LEFT JOIN users u ON pm.user_id = u.id
        WHERE pm.project_id = ? AND pm.status = 'active'
    """,
        (project_id,),
    ).fetchall()

    project = db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()

    return StreamingResponse(
        generate_brief_stream(dict(project), submissions, active_members, db),
        media_type="text/event-stream",
    )