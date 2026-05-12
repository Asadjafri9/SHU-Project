# StandupBot — Product Requirements Document (PRD)

**Project:** StandupBot
**Event:** Iterate '26 Hackathon
**Document version:** 1.0
**Status:** Ready to build

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Target User](#3-target-user)
4. [Solution Overview](#4-solution-overview)
5. [Competitive Differentiation](#5-competitive-differentiation)
6. [Goals & Non-Goals](#6-goals--non-goals)
7. [Tech Stack](#7-tech-stack)
8. [System Architecture](#8-system-architecture)
9. [Database Schema](#9-database-schema)
10. [API Specification](#10-api-specification)
11. [URL / Page Map](#11-url--page-map)
12. [Phase-by-Phase User Flow](#12-phase-by-phase-user-flow)
13. [AI Prompt Specification](#13-ai-prompt-specification)
14. [Edge Cases & Error Handling](#14-edge-cases--error-handling)
15. [UI / Visual Design Notes](#15-ui--visual-design-notes)
16. [Build Plan & Time Budget](#16-build-plan--time-budget)
17. [Demo Script](#17-demo-script)
18. [Judging Criteria Alignment](#18-judging-criteria-alignment)
19. [Judge Q&A Preparation](#19-judge-qa-preparation)
20. [Post-Hackathon Roadmap](#20-post-hackathon-roadmap)
21. [Appendix: File Structure](#21-appendix-file-structure)

---

## 1. Executive Summary

**One-liner:** Each team member answers 3 questions daily from their personal link → AI reads ALL submissions together → generates one smart team brief that flags blockers, cross-person dependencies, new joiners, and missing members.

**Why now:** University students run group projects (FYP, hackathons, society work, course assignments) entirely over WhatsApp. Existing standup tools like Geekbot and Standuply assume a paid corporate Slack workspace. Students are an underserved segment with a real recurring pain.

**Core insight:** The product's defensible value is *cross-person reasoning*. A judge cannot replicate it in ChatGPT because ChatGPT cannot independently receive private submissions from four different people and synthesize them.

---

## 2. Problem Statement

Student project teams of 4 to 6 members coordinate asynchronously over WhatsApp with no structure. The consequences are predictable and repeat every semester:

- Members go silent for days, and nobody notices until a deadline is close.
- Blockers stay hidden because there is no structured place to raise them.
- Two members duplicate work because neither knows what the other did.
- Everyone assumes someone else is handling the missing piece.
- The team leader cannot see status without manually pinging each person.

The pain peaks 48 hours before deadline, when discovery of blockers becomes a crisis rather than a routine adjustment.

---

## 3. Target User

**Primary user:** A university student team leader managing a 4 to 6 person group project with a fixed deadline.

**Secondary users:** The other 3 to 5 members of that team, who each interact with the app once per day for under 90 seconds.

**User context:**
- They already use Google for university email, so OAuth is frictionless.
- They use WhatsApp as the team's primary communication channel.
- They have laptops and phones with reliable internet during work hours.
- They will not pay for a tool, but they will adopt one that is free, fast, and removes a real pain.

---

## 4. Solution Overview

A web app, **StandupBot**, where:

1. A leader creates a project and adds members by email or by generating role-tagged invite links.
2. Each member signs in with Google and accepts their invite.
3. Each day, every active member opens the app and answers three questions in about 90 seconds: what they did, what they will do, and any blockers.
4. The leader clicks **Generate Brief**. The backend collects all submissions and sends them in one structured prompt to an LLM via OpenRouter.
5. The AI returns a single team brief that:
   - Names who is blocked and who can unblock them.
   - Flags cross-person dependencies.
   - Welcomes any member submitting for the first time.
   - Flags members who did not submit today.
   - Assigns an overall risk level: Low, Medium, or High.
6. All active members view the brief on a shared page.

---

## 5. Competitive Differentiation

| Alternative | Why it fails for this user |
|-------------|---------------------------|
| WhatsApp group | Stream of unstructured messages. Nobody synthesizes blockers across people. |
| ChatGPT (manual) | One person must collect every member's update and paste them in. Defeats the point. |
| Geekbot / Standuply | Requires paid Slack workspace. Students don't have one. |
| Notion / Trello | Capture tools, not synthesis tools. Don't reason across people. |
| Google Docs daily log | No prompting, no notifications, no synthesis, no accountability. |

The structural defensibility is multi-user private input plus cross-person AI reasoning. That cannot be done in a single chat tab.

---

## 6. Goals & Non-Goals

### Goals (MVP)

- A leader can create a project in under 60 seconds.
- A member can submit a standup in under 90 seconds.
- The AI brief generation completes in under 15 seconds and streams visibly to the screen.
- The product runs on a single laptop in front of judges with no setup beyond opening the URL.
- The AI brief demonstrably finds a cross-person blocker, welcomes a new joiner, and flags a missing member in the demo.

### Non-Goals (explicitly out of scope)

- Email or WhatsApp notifications.
- Full past-briefs archive UI (today only for MVP).
- Profile settings or account management beyond login.
- Project archival, deletion, or transfer of leadership.
- Mobile-native apps.
- Deadline reminder cron jobs.
- Payment, billing, or team-size enforcement.

---

## 7. Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Frontend | HTML, CSS, vanilla JavaScript | Zero build step, fastest to ship in a hackathon. |
| Backend | FastAPI (Python) | Async-friendly, easy OAuth, auto-generated docs at `/docs`. |
| Database | SQLite | File-based, zero setup, sufficient for demo and early users. |
| AI provider | OpenRouter API | One API key, swappable models. Use `openai/gpt-3.5-turbo` for speed or `mistralai/mistral-7b-instruct` for cost. |
| Auth | Google OAuth 2.0 | Students already have Google accounts. Removes password handling. |
| Hosting | Local for demo. Optional deploy: Vercel (frontend) + Render or Railway (backend). | Local-only is acceptable if the demo is on the team's laptop. |

---

## 8. System Architecture

```
[Browser]
    │
    │  HTML / CSS / JS  (served as static files)
    ▼
[FastAPI app]
    │
    ├── /auth/*       → Google OAuth handlers, session cookies
    ├── /api/*        → JSON endpoints for projects, members, standups, briefs
    ├── /static/*     → Frontend assets
    │
    ├──→ [SQLite file: standupbot.db]
    │
    └──→ [OpenRouter API]   (called only during brief generation)
```

Sessions are stored as signed cookies containing the user ID. There is no separate session store. Authorization is enforced per-route by reading the cookie and checking the user's role on the requested project.

---

## 9. Database Schema

### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PRIMARY KEY | Auto-increment. |
| email | TEXT UNIQUE | From Google. |
| name | TEXT | From Google. |
| avatar_url | TEXT | From Google. |
| created_at | DATETIME | Default now. |

### `projects`
| Column | Type | Notes |
|--------|------|-------|
| id | TEXT PRIMARY KEY | 6-character random slug, e.g. `abc123`. |
| name | TEXT | Project name. |
| description | TEXT | One-line, used in AI system prompt. |
| deadline | DATE | Final project deadline. |
| standup_closes_at | TIME | Default `21:00`. |
| leader_id | INTEGER | Foreign key → `users.id`. |
| created_at | DATETIME | Default now. |

### `project_members`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PRIMARY KEY | Auto-increment. |
| project_id | TEXT | Foreign key → `projects.id`. |
| user_id | INTEGER | Foreign key → `users.id`. NULL until invited user signs up. |
| email | TEXT | Used for email-based invite when user doesn't exist yet. |
| role | TEXT | Free text, e.g. "Backend API integration". |
| status | TEXT | One of `invited`, `active`, `declined`, `removed`. |
| invite_token | TEXT UNIQUE | For link-based invites. NULL otherwise. |
| invite_type | TEXT | One of `email`, `link`. |
| joined_at | DATETIME | Set when status becomes `active`. |
| is_first_standup | BOOLEAN | Default `true`, flipped to `false` after first submission. |
| created_at | DATETIME | Default now. |

### `standups`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PRIMARY KEY | Auto-increment. |
| project_id | TEXT | Foreign key → `projects.id`. |
| member_id | INTEGER | Foreign key → `project_members.id`. |
| date | DATE | Submission date. |
| did | TEXT | "What did you do today?" |
| will_do | TEXT | "What will you do tomorrow?" |
| blocker | TEXT | Free text, or NULL if "none". |
| submitted_at | DATETIME | Default now. |

A uniqueness constraint on `(project_id, member_id, date)` enforces one submission per member per day; the edit flow updates the existing row.

### `briefs`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PRIMARY KEY | Auto-increment. |
| project_id | TEXT | Foreign key → `projects.id`. |
| date | DATE | Brief date. |
| content | TEXT | AI-generated markdown. |
| generated_at | DATETIME | Default now. |
| submissions_count | INTEGER | Number of submissions included. |
| total_active_members | INTEGER | Active member count at generation time. |

---

## 10. API Specification

All `/api/*` routes require a valid session cookie unless noted. All responses are JSON.

### Auth

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/auth/google` | Redirect to Google OAuth consent screen. |
| GET | `/auth/google/callback` | Exchange code, upsert user, set session cookie, redirect to `/dashboard` or original invite URL. |
| POST | `/auth/logout` | Clear session cookie. |

### Dashboard

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/me` | Returns current user `{id, name, email, avatar_url}`. |
| GET | `/api/projects` | Returns all projects where the user is an active member, plus role and today's submission status. |

### Projects

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/projects` | Create a project. Body: `{name, description, deadline, standup_closes_at}`. Returns the project. |
| GET | `/api/projects/{id}` | Project detail + member list. Caller must be an active member. |
| GET | `/api/projects/{id}/brief/today` | Today's brief if it exists, else 404. |
| POST | `/api/projects/{id}/brief` | Generate today's brief. Leader only. Streams AI output. |

### Members

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/projects/{id}/members` | Add member by email + role. Leader only. |
| GET | `/api/projects/{id}/invite-links` | List invite links. Leader only. |
| POST | `/api/projects/{id}/invite-links` | Create invite link with role pre-assigned. Leader only. |
| GET | `/api/join/{token}` | Public. Returns invite preview `{project_name, role, is_used}`. |
| POST | `/api/join/{token}` | Accept invite. Requires login. |
| DELETE | `/api/projects/{id}/members/{member_id}` | Soft-remove (status → `removed`). Leader only. |

### Standups

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/projects/{id}/standup/today` | Current user's standup for today, if any. |
| POST | `/api/projects/{id}/standup` | Submit or update today's standup. Body: `{did, will_do, blocker}`. |
| GET | `/api/projects/{id}/standups/status` | Submission tracker for today (leader view). |

---

## 11. URL / Page Map

| URL | Audience | Purpose |
|-----|----------|---------|
| `/` | Public | Landing page with "Sign in with Google" and "I have an invite link". |
| `/login` | Public | OAuth entry point. |
| `/auth/google/callback` | System | OAuth callback (backend only). |
| `/dashboard` | Logged-in users | All projects the user is in. |
| `/projects/new` | Logged-in users | Create project form. |
| `/projects/{id}` | Active members | Project home. Leader sees Generate Brief. |
| `/projects/{id}/standup` | Active members | Daily 3-question form. |
| `/projects/{id}/brief` | Active members | Today's AI brief, color-coded. |
| `/projects/{id}/brief/{date}` | Active members | Past brief (nice-to-have, post-MVP). |
| `/projects/{id}/members` | Leader | Member list + add-by-email. |
| `/projects/{id}/invite-links` | Leader | Generate and manage role-tagged invite links. |
| `/join/{token}` | Anyone with link | Accept or decline invite. |

---

## 12. Phase-by-Phase User Flow

### Phase 0 — Landing & Auth

The user arrives at `/`. The page shows the tagline "Async standups for student teams. No meetings. 90 seconds a day." and two primary actions: Sign in with Google, and I have an invite link.

On Sign in with Google, the browser is redirected to Google's OAuth consent screen. After consent, Google redirects back to `/auth/google/callback` with an authorization code. The backend exchanges the code for an access token, fetches the user's profile, and performs an upsert into the `users` table keyed by email. A signed session cookie containing the user ID is set, and the user is redirected to `/dashboard`. If the user originally arrived via an invite link, they are redirected back to that link after auth.

### Phase 1 — Dashboard

`/dashboard` lists every project where the user has `status = "active"`. Each project card shows the project name, description, the user's role, a badge indicating whether they are the leader or a member, today's status badge (Standup due, Submitted, Brief ready, or Pending invite), and the deadline with days remaining.

A `+ New project` button in the top right takes the user to the create-project flow. Pending invites the user has not yet acted on appear in a separate section above the active projects.

### Phase 2 — Create Project (Leader)

`/projects/new` shows a form with four fields: project name, one-line description, deadline (date picker), and standup-closes-at time (defaulting to 21:00).

On submit, the backend generates a 6-character random slug, inserts the project, inserts the leader into `project_members` with `status = "active"`, `role = "Project Leader"`, and `is_first_standup = false`. The user is redirected to `/projects/{id}/members`.

### Phase 3 — Adding Members

The leader has two methods.

**Method A — Add by email.** The leader enters an email and a role string. The backend checks if a user with that email already exists. If yes, a `project_members` row is created with `user_id` filled, `status = "invited"`, and `invite_type = "email"`. If no, the same row is created with `user_id = NULL` and `email` filled. The next time that email signs in with Google, the backend scans for any `project_members` rows with matching email and NULL user_id and links them automatically.

The invited person sees the project on their dashboard with Join and Decline buttons. They are not visible to the AI until they become active.

**Method B — Invite link with pre-assigned role.** The leader opens `/projects/{id}/invite-links`, types a role name, and clicks Generate Link. The backend creates a `project_members` row with a unique `invite_token`, `invite_type = "link"`, `status = "invited"`. The leader copies the URL `/join/{token}` and sends it through any channel (typically WhatsApp).

When a recipient opens the link, they are sent through Google OAuth if not logged in, then shown an accept/decline page. On accept, the row is updated: `user_id` filled, `status = "active"`, `joined_at = now()`, `is_first_standup = true`. The token is marked used. If a second person tries the same token, they see "This invite link has already been used."

Only members with `status = "active"` are included in standup tracking and AI briefs. Invited, declined, and removed members are invisible to the AI.

### Phase 4 — Daily Standup Submission

`/projects/{id}/standup` shows the member's name, the project name, their role, and today's date pre-filled. Three text areas follow:

1. What did you do today?
2. What will you do tomorrow?
3. Any blockers? (type "none" if not)

On submit, the backend writes to `standups` with today's date. If the member's `is_first_standup` flag is `true`, the backend records it for the AI prompt and then flips the flag to `false` after submission. The success state shows "Submitted. X of Y members have submitted today."

If the member submits twice before the brief is generated, they see their previous answers with an Edit button that updates the same row. If they open the form after the brief has been generated, they see "Today's standup is closed. The brief is already out." with a link to view it. They can still submit for tomorrow.

### Phase 5 — Brief Generation (Leader)

`/projects/{id}` shows the leader a submission tracker: each active member with a green check if submitted or a gray clock if not, plus the time remaining until standup closes. A `Generate Brief` button is enabled as soon as there is at least one submission.

When clicked, the backend assembles the prompt (see Section 13), calls the OpenRouter API with streaming enabled, and pipes the streamed tokens to the browser via Server-Sent Events or chunked HTTP. The brief is rendered live on the screen as it generates, then saved to the `briefs` table on completion. The whole call should complete in under 15 seconds.

If the leader clicks Generate Brief with zero submissions, the request is rejected with an error.

### Phase 6 — Viewing the Brief

`/projects/{id}/brief` is accessible to all active members regardless of whether they submitted. The page shows the submission stats (e.g., "3 of 4 submitted"), the full AI brief rendered from markdown, and color-coded sections:

- Blockers in red.
- Completed work in green.
- New-member welcome in blue.
- Missing members in amber.

The brief is read-only. A "Past briefs" stub may be shown but is not required for MVP.

### Phase 7 — New Member Joining Mid-Project

When a new member accepts an invite to a project that has been running for days, three things happen. First, they immediately see all past briefs from the dashboard so they can catch up on context. Second, their `is_first_standup` flag is `true`, so on their first submission the backend adds `[FIRST STANDUP TODAY — welcome them]` next to their name in the AI system prompt. Third, the AI brief includes a dedicated welcome line. After their first submission, the flag is flipped to `false` so the welcome does not repeat.

This phase is the single most demo-worthy moment of the product: the AI noticing and warmly acknowledging the new joiner is something a generic chat tool cannot do.

---

## 13. AI Prompt Specification

Use the OpenRouter API with the model `openai/gpt-3.5-turbo` for the demo (fastest and most predictable streaming) or `mistralai/mistral-7b-instruct` for cost optimization in production.

### System prompt template

```python
system_prompt = f"""
You are a team standup assistant for a student project.

Project: {project.name}
Description: {project.description}
Deadline: {project.deadline} ({days_remaining} days away)

Active team members and their roles:
{member_list_with_roles_and_flags}

Your job:
1. Summarize what the team accomplished today.
2. Identify blockers and — critically — name the person who can unblock each one.
3. Flag cross-person dependencies (person A is waiting on person B).
4. Highlight any deadline risk given the progress reported.
5. Welcome any member submitting for the first time today with a warm one-line mention.
6. Flag any member who did not submit and note that the team is missing their update.
7. State the overall risk level: Low, Medium, or High.

Be direct and specific. Use names. Do not just summarize each person separately — find connections across the team. Format the output in markdown with clear sections.
"""
```

### Member list formatting rules

Each active member is listed as:

```
- {name}: {role}{flags}
```

Where `{flags}` is one of:
- `` (empty) for a normal active member who submitted.
- ` (LEADER)` for the project leader.
- ` [FIRST STANDUP TODAY — welcome them]` if `is_first_standup` was true before this submission.
- ` [DID NOT SUBMIT]` if no standup exists for them today.

Multiple flags can combine, e.g. `(LEADER) [DID NOT SUBMIT]`.

### User prompt template

```python
user_prompt = f"""
{standup_submissions_formatted}

Generate the team brief now.
"""
```

Each submission is formatted as:

```
{name} ({role}){first_standup_marker}:
- Did: {did}
- Will do: {will_do}
- Blocker: {blocker or "None"}
```

Members who did not submit are written as a single line:

```
{name} ({role}): DID NOT SUBMIT TODAY
```

### Example expected output

```
Team Brief — Monday 11 May
FYP — E-commerce Platform | 14 days remaining | Risk: MEDIUM

Welcome Sara! Sara joins the team today and has already hit the ground
running — repo set up and navbar started.

Blocker — action needed:
Ahmed is blocked on his payment API testing because he needs DB
credentials from Zain. Zain has no blockers tomorrow — this should
be the first thing Zain does in the morning.

Progress today:
- Ahmed: Stripe SDK set up, basic charge flow working.
- Sara: Repo set up, wireframes reviewed, navbar started (first day).
- Zain: Database schema complete, pushed to repo.

Tomorrow:
- Ahmed: Auth flow (after receiving credentials from Zain).
- Sara: Product listing page.
- Zain: Seed data scripts and share credentials with Ahmed immediately.

Missing:
- Fatima did not submit today. Her research deliverable is due in
  4 days — the team does not know her current status.

Risk: MEDIUM — One active blocker between Ahmed and Zain.
Fatima's absence from standup is a concern with 14 days left.
```

---

## 14. Edge Cases & Error Handling

| Situation | Behaviour |
|-----------|-----------|
| Member submits twice on the same day | The form pre-fills with their previous answers and shows an Edit button. Allowed until the brief is generated. After the brief is generated, the form is locked. |
| Member opens standup form after the brief is generated | Show "Today's standup is closed. The brief is already out." with a link to `/projects/{id}/brief`. The member may still submit for the next day. |
| Invite link clicked by a second person | Show "This invite link has already been used." The token is single-use. |
| User invited by email but no `users` row exists yet | On their first Google login, the backend scans `project_members` for rows with matching email and NULL `user_id` and links them. |
| Leader clicks Generate Brief with zero submissions | Reject the request. Show "No submissions yet — wait until at least one member submits." |
| Member declines an invite | `status` is set to `declined`. The leader is shown a small inline note next to that row. The declined member never appears in the AI brief. |
| New member joins mid-project | Sees all past briefs immediately on accepting. On first submission, the AI welcomes them. The flag flips after that submission. |
| Member removed by leader | `status` is set to `removed`. The member is excluded from all future standup tracking, AI briefs, and submission counts. Their past submissions remain in the database for audit but are not sent to future AI calls. |
| Project deadline passes | The project is treated as archived. The standup form is locked and shows "This project's deadline has passed." Past briefs remain viewable. |
| OpenRouter API call fails | Show "Brief generation failed. Try again." Do not save a partial brief. Log the error for the team. |
| User tries to access another project they are not in | Return 403 Forbidden. The frontend shows "You don't have access to this project." |

---

## 15. UI / Visual Design Notes

The product should look clean and modern without being over-designed. The hackathon judges are evaluating clarity, not visual ambition.

**Color system:**
- Primary text: near-black on white background.
- Accent: a single brand color (suggested: indigo `#4F46E5`) for buttons and links.
- Status colors used consistently across the app and inside the brief:
  - Blocker: red `#DC2626` background tint `#FEE2E2`.
  - Completed work: green `#16A34A` background tint `#DCFCE7`.
  - New member welcome: blue `#2563EB` background tint `#DBEAFE`.
  - Missing member: amber `#D97706` background tint `#FEF3C7`.

**Typography:** A single sans-serif system stack. One font size for body, one for headings.

**Components needed:**
- Button (primary, secondary, danger).
- Card (used for project cards and member cards).
- Badge (used for role, status, risk level).
- Text input and textarea with consistent padding and focus state.
- Toast for success and error messages.

**Empty states matter for the demo:**
- Dashboard with no projects: clear call-to-action to create one.
- Project with no submissions yet: friendly prompt telling the leader to wait.
- Brief page before generation: a calm placeholder, not an error.

---

## 16. Build Plan & Time Budget

The hackathon window is 9:00 AM to 4:30 PM, with submission and demo occurring inside that window. Allocate time as follows.

**9:00 to 9:30 — Setup.** Repository created, FastAPI scaffold running, SQLite initialized, Google OAuth credentials issued and tested locally. Static frontend folder served by FastAPI.

**9:30 to 10:30 — Auth and user model.** Google OAuth flow complete end-to-end. `/api/me` returns the logged-in user. Dashboard renders the user's name and avatar.

**10:30 to 11:30 — Projects and members.** Create-project form working. `project_members` table populated. Add-by-email flow functional. Invite-link generation and the accept/decline page working.

**11:30 to 12:30 — Standup form.** Members can submit the three-question form. Submission tracker on the project page shows green checks and gray clocks correctly.

**12:30 to 13:30 — AI brief generation.** OpenRouter integration. Prompt assembly correct. Streaming output rendering on the page. Brief saved to the database.

**13:30 to 14:30 — Polish and color-coding.** Brief page renders the markdown with the four status colors. Dashboard status badges work. Error and empty states wired up.

**14:30 to 15:30 — Demo data and rehearsal.** Seed a project with three submitted members, one missing member, and one of the submitters marked as first-standup. Rehearse the demo path twice end-to-end.

**15:30 to 16:00 — Submission.** Write the submission text, list tools used (FastAPI, SQLite, OpenRouter, Google OAuth), record a backup screen recording in case live demo fails, and submit.

**16:00 to 16:30 — Buffer.** Time to fix one or two last bugs. Do not start anything new.

---

## 17. Demo Script

Total demo time is short — likely 3 to 5 minutes depending on judge count. Follow this exact path.

1. **Open at the dashboard.** Show the leader's account, already logged in. Three projects visible. "Each user can be in multiple projects. Today I'm the leader of this FYP project."
2. **Open the project page.** Show the submission tracker. Three green checks, one gray clock. "Three members submitted, one didn't."
3. **Open one member's submission in a second tab.** Show that Ahmed wrote a blocker mentioning Zain's DB credentials. "These are private — each member only sees their own form."
4. **Switch back to the project page.** Hover over Sara's badge. "Sara is new — she joined this morning."
5. **Click Generate Brief.** As the AI streams output, narrate: "Watch — the AI is reading all four updates at once. It's going to find the Ahmed-Zain blocker, welcome Sara, and flag Fatima."
6. **Wait for the brief to finish.** Point at each color-coded section in order: blue for Sara's welcome, red for the blocker, amber for Fatima.
7. **Close with the differentiator.** "No chat app can do this. You'd need one person to manually collect four people's private updates and prompt an LLM yourself. We just do it."

If live demo is risky, have a 60-second screen recording of this exact path ready as backup, but always attempt live first — judges reward live demos per Section 9 of the rules.

---

## 18. Judging Criteria Alignment

The official rubric weights are: Problem clarity 20%, MVP execution 25%, Product thinking and usability 20%, Impact and startup potential 20%, Pitch and communication 15%.

**Problem clarity (20%).** The problem is named precisely: student group projects fail because async coordination on WhatsApp hides blockers until deadline. Every judge has lived this.

**MVP execution (25%).** The build is realistically completable in the event window because of deliberate scope cuts: no notifications, no past-briefs UI, no settings page, SQLite instead of a real DB, vanilla JS instead of a framework.

**Product thinking and usability (20%).** One clear user (team leader), one painful problem (hidden blockers), one main feature (AI cross-person synthesis), one demo path (create → submit → generate → view). The new-joiner welcome is a thoughtful product touch judges remember.

**Impact and startup potential (20%).** Every university has thousands of group projects per semester. The free-to-paid path (free for 5 members, paid for departments managing dozens of FYP groups) is credible without being over-promised.

**Pitch and communication (15%).** The judge Q&A is pre-prepared. The differentiator line ("ChatGPT cannot receive private input from four people independently") is sharp and quotable.

---

## 19. Judge Q&A Preparation

**"Why won't students just use a WhatsApp group?"**
WhatsApp is a stream, not a brief. Nobody reads 40 messages and synthesizes blockers across people. The AI connects Ahmed's blocker to the exact person who can fix it. That cross-person reasoning does not happen in any chat app.

**"Can't they just paste everything into ChatGPT?"**
One person would have to collect all updates manually, paste them, and write the prompt every single day. StandupBot does it automatically, across multiple people who submit independently, with project context baked in.

**"Why Google login instead of a simple link?"**
One user is in multiple projects. A simple link cannot give you a unified dashboard. Google login also removes password handling, and students already have university Google accounts.

**"What's the business model?"**
Free for teams up to five members. Paid for larger teams and professor dashboards managing many FYP groups. But that's not what we're building today — today we're building the one feature that makes student group projects ten times less chaotic.

**"What stops the leader from just asking each member in person?"**
Nothing — and that's exactly what fails. Asking each person manually does not scale beyond two members, breaks down across time zones and class schedules, and never produces a written synthesis the team can refer back to.

**"What happens if the AI is wrong about a dependency?"**
The brief is a draft for humans to read, not an authority. Members can immediately see what each person actually submitted, so any AI mistake is obvious within 5 seconds.

---

## 20. Post-Hackathon Roadmap

**Immediate next (week 1 to 4):**
- WhatsApp bot integration: members submit by replying to a WhatsApp message instead of opening a link.
- Past-briefs archive UI with date navigation.
- Email reminder at standup-close time for members who haven't submitted.

**Mid-term (month 2 to 6):**
- GitHub integration: auto-pull commits into the "Did" field as a draft.
- Notion and Trello sync: pull task updates as context for the AI.
- Multi-language support for non-English teams.

**Long term (6+ months):**
- Paid tier for university departments managing dozens of FYP groups at once with a supervisor dashboard.
- Cohort analytics: which teams are at risk based on standup patterns.
- Mobile app for one-tap submission.

---

## 21. Appendix: File Structure

A suggested layout for the codebase:

```
standupbot/
├── backend/
│   ├── main.py                 # FastAPI app entry
│   ├── db.py                   # SQLite connection + schema init
│   ├── auth.py                 # Google OAuth routes + session
│   ├── routes/
│   │   ├── projects.py
│   │   ├── members.py
│   │   ├── standups.py
│   │   └── briefs.py
│   ├── ai.py                   # OpenRouter prompt + streaming
│   ├── models.py               # Pydantic models
│   └── requirements.txt
├── frontend/
│   ├── index.html              # Landing
│   ├── dashboard.html
│   ├── project.html
│   ├── standup.html
│   ├── brief.html
│   ├── members.html
│   ├── invite-links.html
│   ├── join.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── api.js              # fetch helpers
│       ├── dashboard.js
│       ├── project.js
│       ├── standup.js
│       └── brief.js            # SSE streaming render
├── standupbot.db               # SQLite file (created at runtime)
├── .env                        # GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, OPENROUTER_API_KEY, SESSION_SECRET
└── README.md
```

The `.env` file must never be committed. The `README.md` should contain setup instructions: how to create Google OAuth credentials, where to get an OpenRouter API key, and how to run the FastAPI server.

---

**End of PRD.**
