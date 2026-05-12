import os
import json
from datetime import date
import httpx
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-3.5-turbo"


def _build_system_prompt(project: dict, days_remaining: int, member_list: str) -> str:
    return f"""You are a team standup assistant for a student project.

Project: {project['name']}
Description: {project.get('description', '') or 'N/A'}
Deadline: {project.get('deadline', 'N/A')} ({days_remaining} days away)

Active team members and their roles:
{member_list}

Your job:
1. Summarize what the team accomplished today.
2. Identify blockers and — critically — name the person who can unblock each one.
3. Flag cross-person dependencies (person A is waiting on person B).
4. Highlight any deadline risk given the progress reported.
5. Welcome any member submitting for the first time today with a warm one-line mention.
6. Flag any member who did not submit and note that the team is missing their update.
7. State the overall risk level: Low, Medium, or High.

Be direct and specific. Use names. Do not just summarize each person separately — find connections across the team. Format the output in markdown with clear sections."""


def _build_user_prompt(submissions: list, missing_members: list) -> str:
    parts = []
    for s in submissions:
        first_marker = " (FIRST STANDUP TODAY)" if s["is_first_standup"] else ""
        leader_marker = " (LEADER)" if s["role"] == "Project Leader" else ""
        parts.append(
            f"{s['name']} ({s['role']}){leader_marker}{first_marker}:\n"
            f"- Did: {s['did']}\n"
            f"- Will do: {s['will_do']}\n"
            f"- Blocker: {s['blocker'] or 'None'}"
        )

    for m in missing_members:
        leader_marker = " (LEADER)" if m["role"] == "Project Leader" else ""
        parts.append(f"{m['name']} ({m['role']}){leader_marker}: DID NOT SUBMIT TODAY")

    return "\n\n".join(parts) + "\n\nGenerate the team brief now."


async def generate_brief_stream(project: dict, submissions: list, active_members: list, db):
    deadline = project.get("deadline")
    if deadline:
        days_remaining = (date.fromisoformat(deadline) - date.today()).days
    else:
        days_remaining = -1

    submitted_ids = {s["member_id"] for s in submissions}
    missing = [dict(m) for m in active_members if m["id"] not in submitted_ids]

    member_lines = []
    for m in active_members:
        flags = ""
        if m["role"] == "Project Leader":
            flags += " (LEADER)"
        if m["id"] not in submitted_ids:
            flags += " [DID NOT SUBMIT]"
        member_lines.append(f"- {m['name']}: {m['role']}{flags}")

    member_list = "\n".join(member_lines)

    system_prompt = _build_system_prompt(project, days_remaining, member_list)
    user_prompt = _build_user_prompt(submissions, missing)

    full_content = ""

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream(
            "POST",
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": True,
            },
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            full_content += content
                            yield f"data: {json.dumps({'content': content})}\n\n"
                    except json.JSONDecodeError:
                        continue

    cursor = db.execute(
        "INSERT INTO briefs (project_id, date, content, submissions_count, total_active_members) VALUES (?, ?, ?, ?, ?)",
        (project["id"], date.today(), full_content, len(submissions), len(active_members)),
    )
    db.commit()

    yield "data: [DONE]\n\n"