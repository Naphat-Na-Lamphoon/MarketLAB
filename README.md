# MarketLab

MarketLab is an experiment workflow for turning a product concept into a 4D hypothesis, drafting assets, approving a budget, running a simulated experiment, evaluating results, and storing evidence.

## Current scaffold

- `backend/`: FastAPI API with in-memory MVP services for hypotheses, approvals, experiments, telemetry, stats, and guardrails.
- `web/`: Next.js dashboard shell and SSR landing-page route.
- `docs/SETUP.md`: separate environment and development guide.
- `docker-compose.yml`: PostgreSQL/pgvector service for the planned persistence layer.

M0 and M1 can currently be developed without Docker or another external application:

- `backend/app/services/stats.py` contains sample-size and two-proportion z-test logic.
- `backend/app/services/rules.py` contains the R2 guardrail, decision rules, and feasibility calculation.
- `Makefile` provides local test, compile, and web type-check commands.
- `backend/app/models/` contains the async SQLAlchemy domain model and
  `backend/migrations/` contains the first schema migration. Local validation uses SQLite.

The database-backed M0 work (PostgreSQL, migrations, authentication, and RBAC) is
partially available locally; PostgreSQL/pgvector verification and the API repository
conversion are deferred until Docker/PostgreSQL is available.

The simulated adapter is the safe default. Real Google Ads is intentionally not wired to live traffic in this initial scaffold.

## Quick start

See [docs/SETUP.md](docs/SETUP.md). The web shell can be started immediately with Node.js. The API requires Python 3.11+.

## VS Code

Open the project folder in VS Code. Recommended extensions and ready-to-run tasks are in [.vscode/](.vscode/).

- `Web: typecheck`
- `Web: build`
- `Web: dev`
- `Infrastructure: start (requires Docker)`

The first three web tasks work with the current Node.js setup. The infrastructure task remains unavailable until Docker Desktop is installed.
