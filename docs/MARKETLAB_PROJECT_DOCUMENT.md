# MarketLab Project Document

## 1. Executive Summary

MarketLab is a locally runnable product-validation prototype for turning a product concept into measurable experiment evidence. The system guides a team through a 4D hypothesis, draft asset generation, human approval, simulated campaign launch, privacy-aware telemetry, statistical evaluation, and evidence-oriented learning.

This document describes the current implementation status as of November 19, 2026. The current build is suitable for a presentation and product-flow demonstration. It is not yet a production deployment because authentication, persistent API repositories, real database verification, and live advertising integrations remain future milestones.

## 2. Current Demonstration Scope

The presentation-ready flow supports:

1. Creating a hypothesis with Problem, Target Segment, Offer, Pricing, and budget cap.
2. Creating and listing control and treatment variants.
3. Generating a deterministic draft asset.
4. Approving or rejecting a variant.
5. Creating, approving, launching, and pausing a simulated experiment.
6. Recording telemetry with event-id deduplication.
7. Viewing per-variant metrics and evaluating CTR/CVR, z-score, p-value, and decision status.
8. Loading demonstration workspaces for admin, operator, and viewer roles without PostgreSQL.

The default channel is simulated. No live Google Ads request is made by this prototype.

## 3. Product Workflow

```text
Concept
  -> 4D hypothesis
  -> draft asset
  -> human review and approval
  -> simulated experiment launch
  -> telemetry collection
  -> metrics and statistical decision
  -> reusable evidence
```

All generated assets remain drafts until an explicit approval action. Budget approval is checked before a simulated launch.

## 4. Technical Architecture

### Backend

- Python 3.11+
- FastAPI
- Pydantic v2 request and response schemas
- SQLAlchemy 2.0 async domain models
- Alembic initial migration
- SQLite-compatible local validation
- PostgreSQL/pgvector planned for persistent deployment

The current presentation API uses in-memory dictionaries so it can run without Docker or an external database. The database models and migration provide the foundation for the next persistence milestone.

### Frontend

- Next.js App Router
- React
- TypeScript
- CSS-based dashboard shell
- Browser `fetch` API client

Current pages include:

- Dashboard
- Hypothesis Builder
- Asset Review
- Experiment landing-page route

### Safety and Governance Foundation

- Simulated channel is the default.
- Launch is blocked without approval or when the approved cap is exceeded.
- Telemetry can be deduplicated by `event_id`.
- Demo telemetry uses UUID-based identifiers.
- AI output schema is marked as `DRAFT`.
- Live advertising is intentionally disabled in the current prototype.

## 5. Demonstration Roles

The development presentation mode loads three example workspaces in memory:

| Role | Example email | Example password |
|---|---|---|
| Admin | admin@marketlab.local | Admin123! |
| Operator | operator@marketlab.local | Operator123! |
| Viewer | viewer@marketlab.local | Viewer123! |

These are demonstration records only. The current web interface does not yet provide login or enforce role-based access. Authentication and RBAC are scheduled for Milestone 2.

## 6. How to Run the Presentation Demo

### Start the API without PostgreSQL

```powershell
Set-Location backend
$env:ENV = "dev"
uv run --with fastapi --with uvicorn --with pydantic --with SQLAlchemy --with aiosqlite --with greenlet uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API loads presentation data automatically in `ENV=dev`.

### Start the web application

In a second terminal:

```powershell
Set-Location web
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Open:

- Dashboard: `http://localhost:3000`
- API documentation: `http://localhost:8000/docs`
- API health: `http://localhost:8000/health`

The in-memory presentation data is reset when the API process restarts.

## 7. Validation Results

The current validation run completed successfully:

- Backend tests: 28 passed
- Frontend TypeScript check: passed
- Next.js production build: passed
- Patch whitespace check: passed

The backend tests cover rules, statistics, model relationships, API workflow, and idempotent demo seeding.

## 8. Current Limitations

The following items are intentionally not presented as complete:

- API data is not persistent across restarts in presentation mode.
- Authentication and RBAC enforcement are not implemented.
- The frontend dashboard still contains presentation-oriented summary values.
- Gemini is not required or connected in the current demo path.
- PostgreSQL/pgvector has not been verified in this environment.
- Real Google Ads integration is disabled.
- Evidence Graph search is not yet implemented end to end.
- Production observability, rate limiting, backup, and deployment configuration remain open.

## 9. Recommended Next Milestones

1. Complete Milestone 0 environment validation with PostgreSQL/pgvector.
2. Replace in-memory API state with database repositories and services.
3. Implement JWT authentication, roles, authorization dependencies, and audit logging.
4. Complete hypothesis and asset state transitions with approval enforcement.
5. Add the provider interface and safe mock AI workflow before any optional Gemini integration.
6. Add the simulated adapter ledger with persisted idempotency keys.
7. Complete privacy-aware landing-page telemetry and statistical evaluation.
8. Add evidence records, semantic search, CI, monitoring, and deployment checks.

## 10. Presentation Positioning

MarketLab is ready to demonstrate the product concept and the safety-first experiment workflow. The recommended presentation statement is:

> MarketLab is a working local prototype that demonstrates the controlled path from hypothesis to simulated evidence. The current release deliberately keeps persistence, authentication, and live advertising behind later approval and implementation milestones.

