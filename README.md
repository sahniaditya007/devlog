# DevLog — AI-Assisted Engineering Decision Log

A full-stack application for logging, tracking, and understanding architectural decisions across engineering projects. Built as an assessment submission for the Associate Software Engineer role at Better Software.

---

## Quick Start

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit as needed
flask db upgrade              # runs migrations
flask run                     # starts on :5000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                   # starts on :5173 (proxies API to :5000)
```

### Tests

```bash
cd backend
source venv/bin/activate
pytest --tb=short -v
```

---

## Architecture

```
devlog/
├── backend/
│   ├── app/
│   │   ├── __init__.py        # Flask app factory
│   │   ├── config.py          # Environment-based config
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── decision.py    # State machine lives here
│   │   │   └── decision_link.py
│   │   ├── schemas/           # Marshmallow validation + serialization
│   │   ├── services/          # Business logic layer
│   │   │   ├── ai_service.py  # OpenAI integration
│   │   │   └── decision_service.py
│   │   ├── routes/            # Thin HTTP handlers
│   │   └── utils/errors.py
│   ├── tests/                 # pytest test suite
│   └── wsgi.py
└── frontend/
    └── src/
        ├── api/               # Axios API clients
        ├── components/        # Reusable UI components
        ├── context/           # React context (auth)
        ├── pages/             # Route-level page components
        └── types/index.ts     # Shared TypeScript interfaces
```

### Layer Separation

The backend enforces strict layer separation:

```
HTTP Request → Route (thin) → Service (business logic) → Model (domain) → DB
                     ↑
               Schema validates input
```

Routes never contain business logic. Services never import Flask. Models never call services.

---

## Key Technical Decisions

### 1. Decision State Machine (enforced in model)

Decisions follow a one-way state machine:

```
proposed → accepted → deprecated
         ↘           ↘
           deprecated   superseded
```

The `Decision.transition_to()` method is the **single source of truth** for status changes. It raises `ValueError` for invalid transitions. This prevents invalid states from ever reaching the database, regardless of how the route or service is called.

**Tradeoff:** Slightly more coupling in the model, but correctness is guaranteed at the domain level rather than relying on callers to check.

### 2. Marshmallow for Validation + Serialization

All API inputs are validated through Marshmallow schemas before touching the database. Schemas also control serialization (what fields are exposed in responses).

**Why not Pydantic?** Marshmallow integrates naturally with Flask and SQLAlchemy. Pydantic v2 would require more boilerplate for ORM integration.

**Tradeoff:** Marshmallow's error messages are less ergonomic than Pydantic's, but the integration is simpler.

### 3. SQLite for Development, PostgreSQL-ready

`DATABASE_URL` defaults to SQLite for zero-setup local development. The same SQLAlchemy ORM code works with PostgreSQL in production — just change the env var.

**Tradeoff:** SQLite doesn't enforce foreign key constraints by default (enabled via `PRAGMA foreign_keys = ON` in the event listener). This is a known footgun.

### 4. JWT Authentication (Flask-JWT-Extended)

Stateless JWT tokens stored in `localStorage` on the frontend. The `@jwt_required()` decorator protects all non-public routes.

**Tradeoff:** `localStorage` is vulnerable to XSS. HttpOnly cookies would be more secure but require CSRF protection. For this assessment scope, JWT in localStorage is acceptable.

### 5. AI Integration with Graceful Degradation

`ai_service.py` calls OpenAI to generate a one-paragraph summary and suggest tags when a decision is created. If the API call fails (no key, rate limit, network error), the decision is still saved — AI fields are `null`. The service logs the error for observability.

**Tradeoff:** AI enrichment is async-in-spirit but currently synchronous (blocks the request). For production, this should be a background task (Celery, RQ).

### 6. Decision Links (bidirectional graph)

`DecisionLink` stores directed relationships (`supersedes`, `relates_to`, `blocked_by`). The API returns both outgoing and incoming links for a decision, with a `direction` field, so the frontend can render the full graph without a second query.

### 7. React + Vite + TailwindCSS

Vite for fast HMR, TailwindCSS for utility-first styling, React Router for client-side routing. No Redux — auth state is managed with React Context, which is sufficient for this scope.

---

## AI Usage

AI (Claude via Windsurf/Cascade) was used to:
- Scaffold the initial project structure and boilerplate
- Generate Marshmallow schema definitions
- Write pytest fixtures and test cases
- Generate React component skeletons

**Critical review applied:**
- State machine logic was written and verified manually — AI-generated transitions were checked against the spec
- All Marshmallow schemas were reviewed for missing `required` fields and incorrect types
- Test fixtures were reviewed to ensure proper teardown (in-memory SQLite, not shared state)
- AI-suggested `db.session.execute(raw_sql)` was rejected in favor of ORM queries

**Where AI fell short:**
- Initial Vite scaffold created a nested directory structure that had to be manually corrected
- AI occasionally suggested importing business logic directly into route handlers (rejected)

---

## Observability

- `/health` endpoint returns `{"status": "ok"}` for uptime checks
- All unhandled exceptions return structured JSON `{"error": "..."}` via centralized error handlers
- AI service failures are logged with `app.logger.error()` and do not crash the request
- Validation errors return field-level detail: `{"errors": {"field": ["message"]}}`

---

## Risks and Weaknesses

| Risk | Severity | Mitigation |
|------|----------|------------|
| AI enrichment blocks request | Medium | Move to background task in production |
| JWT in localStorage (XSS risk) | Medium | Acceptable for demo; use HttpOnly cookies in production |
| No rate limiting | Low | Add Flask-Limiter for production |
| SQLite FK constraints need PRAGMA | Low | Handled via SQLAlchemy event listener |
| No pagination on list endpoints | Low | Add `limit`/`offset` query params when dataset grows |

---

## Extension Approach

To add a new feature (e.g., "Decision Comments"):

1. Add `Comment` model in `app/models/comment.py` with FK to `Decision`
2. Add `CommentSchema` in `app/schemas/comment.py`
3. Add `comment_service.py` with `create_comment()`, `list_comments()` functions
4. Add routes in `app/routes/comments.py`, register blueprint in `app/__init__.py`
5. Add tests in `tests/test_comments.py`
6. Add `commentsApi` in `frontend/src/api/comments.ts`
7. Add UI in `DecisionDetailPage.tsx`

The layer separation means each step is isolated — adding comments does not touch auth, projects, or the state machine.
