from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from db import get_db
from auth import require_user
from models import StandupSubmit

router = APIRouter(prefix="/api/projects/{project_id}", tags=["standups"])


@router.get("/standup/today")
def get_today_standup(project_id: str, user=Depends(require_user)):
    db = next(get_db())
    member = db.execute(
        "SELECT * FROM project_members WHERE project_id = ? AND user_id = ? AND status = 'active'",
        (project_id, user["id"]),
    ).fetchone()
    if not member:
        raise HTTPException(403, "Not a member of this project")

    standup = db.execute(
        "SELECT * FROM standups WHERE project_id = ? AND member_id = ? AND date = ?",
        (project_id, member["id"], date.today()),
    ).fetchone()

    brief_exists = db.execute(
        "SELECT id FROM briefs WHERE project_id = ? AND date = ?",
        (project_id, date.today()),
    ).fetchone()

    if brief_exists and not standup:
        return {"standup_closed": True, "message": "Today's standup is closed. The brief is already out."}

    if not standup:
        return {"submitted": False, "member_id": member["id"], "is_first_standup": bool(member["is_first_standup"])}

    return {
        "submitted": True,
        "standup": dict(standup),
        "is_first_standup": bool(member["is_first_standup"]),
    }


@router.post("/standup")
def submit_standup(project_id: str, data: StandupSubmit, user=Depends(require_user)):
    db = next(get_db())
    member = db.execute(
        "SELECT * FROM project_members WHERE project_id = ? AND user_id = ? AND status = 'active'",
        (project_id, user["id"]),
    ).fetchone()
    if not member:
        raise HTTPException(403, "Not a member of this project")

    brief_exists = db.execute(
        "SELECT id FROM briefs WHERE project_id = ? AND date = ?",
        (project_id, date.today()),
    ).fetchone()
    if brief_exists:
        raise HTTPException(400, "Today's standup is closed. The brief has already been generated.")

    existing = db.execute(
        "SELECT * FROM standups WHERE project_id = ? AND member_id = ? AND date = ?",
        (project_id, member["id"], date.today()),
    ).fetchone()

    if existing:
        db.execute(
            "UPDATE standups SET did = ?, will_do = ?, blocker = ? WHERE id = ?",
            (data.did, data.will_do, data.blocker, existing["id"]),
        )
    else:
        db.execute(
            "INSERT INTO standups (project_id, member_id, date, did, will_do, blocker) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, member["id"], date.today(), data.did, data.will_do, data.blocker),
        )
        if member["is_first_standup"]:
            db.execute(
                "UPDATE project_members SET is_first_standup = 0 WHERE id = ?",
                (member["id"],),
            )

    db.commit()

    total = db.execute(
        "SELECT COUNT(*) as c FROM project_members WHERE project_id = ? AND status = 'active'",
        (project_id,),
    ).fetchone()["c"]
    submitted = db.execute(
        "SELECT COUNT(*) as c FROM standups WHERE project_id = ? AND date = ?",
        (project_id, date.today()),
    ).fetchone()["c"]

    return {"ok": True, "submitted_count": submitted, "total_active_members": total}


@router.get("/standups/status")
def standup_status(project_id: str, user=Depends(require_user)):
    db = next(get_db())
    member = db.execute(
        "SELECT * FROM project_members WHERE project_id = ? AND user_id = ? AND status = 'active'",
        (project_id, user["id"]),
    ).fetchone()
    if not member:
        raise HTTPException(403, "Not a member of this project")

    members = db.execute(
        """
        SELECT pm.id, u.name, pm.role,
            CASE WHEN s.id IS NOT NULL THEN 1 ELSE 0 END AS submitted
        FROM project_members pm
        LEFT JOIN users u ON pm.user_id = u.id
        LEFT JOIN standups s ON s.member_id = pm.id AND s.project_id = ? AND s.date = ?
        WHERE pm.project_id = ? AND pm.status = 'active'
    """,
        (project_id, date.today(), project_id),
    ).fetchall()

    return [{"name": m["name"], "role": m["role"], "submitted": bool(m["submitted"])} for m in members]