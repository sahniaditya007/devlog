# AI Agent Guidance — DevLog

This file constrains how AI agents (Claude, Copilot, Codex, etc.) should behave when working on this codebase.

---

## Role

You are a pair programmer on a production Flask + React application. Your job is to write clean, correct, minimal code that fits the existing architecture. You are NOT the decision-maker — the human engineer reviews and approves all changes.

---

## Hard Rules (never violate)

1. **Never bypass the state machine.** `Decision.transition_to()` is the single source of truth for status changes. Do not set `decision.status` directly anywhere outside that method.
2. **Never skip schema validation.** All incoming API data must pass through a Marshmallow schema before touching the database. Do not add raw `request.json` access in routes.
3. **Never expose passwords or secrets.** Do not log, print, or return `password_hash`. Do not hardcode secrets.
4. **Never delete or weaken tests.** If a test is failing, fix the code — not the test.
5. **Never add a route without JWT protection** unless it is explicitly a public endpoint (health, login, register).
6. **Never cascade-delete without explicit `cascade="all, delete-orphan"`** on the relationship.
7. **Never use `db.session.execute(raw_sql)`** — use SQLAlchemy ORM queries only.

---

## Architecture Constraints

### Backend
- **Layer separation is strict**: models → schemas → services → routes. Business logic lives in `services/`, not in route handlers.
- **Models** contain only: fields, relationships, and domain methods (e.g. `transition_to`). No HTTP logic.
- **Schemas** (Marshmallow) handle all input validation and output serialization. Keep them in `app/schemas/`.
- **Services** contain all business logic. They call models and AI services. They do NOT import Flask request objects.
- **Routes** are thin: parse request → call service → return JSON. Maximum ~20 lines per route handler.
- **Config** is environment-driven. Never hardcode URLs, keys, or database paths.

### Frontend
- **API calls** go through `src/api/` modules only. No direct `fetch()` or `axios` calls in components.
- **Auth state** is managed exclusively through `AuthContext`. Do not store tokens anywhere except `localStorage` via the context.
- **Types** must be defined in `src/types/index.ts`. Do not use `any` unless absolutely unavoidable.
- **Components** are presentational. Pages handle data fetching.

---

## Code Style

- Python: follow PEP 8. Use type hints on all function signatures.
- TypeScript: strict mode. No implicit `any`. Prefer `interface` over `type` for object shapes.
- No commented-out code in commits.
- No `print()` debugging statements left in production code.
- Prefer explicit over clever. A longer but readable function beats a clever one-liner.

---

## When Adding a New Feature

1. Add/update the Marshmallow schema first (defines the contract).
2. Add/update the model if new fields are needed (with migration).
3. Implement the service function.
4. Add the route (thin handler).
5. Write tests covering: happy path, validation failure, auth failure, edge cases.
6. Update this file if the new feature introduces new AI-relevant constraints.

---

## AI Output Review Checklist

Before accepting any AI-generated code, verify:
- [ ] State machine transitions go through `transition_to()` only
- [ ] All inputs validated through Marshmallow schemas
- [ ] JWT `@jwt_required()` on all protected routes
- [ ] No raw SQL
- [ ] Tests added or updated
- [ ] No hardcoded secrets
- [ ] TypeScript strict compliance (no `any`)
- [ ] Service layer used for business logic, not route handlers
