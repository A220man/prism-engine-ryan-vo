# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

project-skeleton

## Roadmap

### project-skeleton — FastAPI + React project skeleton with Docker, CI, and auth foundation

Status: done

Acceptance:
- Backend FastAPI app runs with /health endpoint
- Frontend Vite+React+TS builds and serves
- Docker Compose runs backend, frontend, Keycloak, PostgreSQL
- CI workflow runs backend tests, frontend build/test, Docker builds
- OIDC Keycloak authentication configured with demo mode

Implementation: `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/core/security.py`, `backend/app/api/v1/health.py`, `backend/requirements.txt`, `frontend/package.json`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `docker-compose.yaml`, `backend/Dockerfile`, `frontend/Dockerfile`, `.github/workflows/ci.yml`

Tests: `backend/tests/test_health.py`, `frontend/src/App.test.tsx`

### agent-registry — Agent registry CRUD API with SQLite persistence

Status: planned

Acceptance:
- Create, list, get, update, delete agents via API
- SQLite persistent storage with SQLAlchemy
- Pagination, filtering, validation
- UTC timestamps, audit log

Implementation: `backend/app/models/agent.py`, `backend/app/services/agent_service.py`, `backend/app/api/v1/agents.py`, `backend/tests/test_agents.py`

Tests: `backend/tests/test_agents.py`

### agent-installer — Agent installation workflow with multi-target conversion

Status: planned

Acceptance:
- Install agents to Claude Code, Cursor, Aider, Qwen, ZCode targets
- Handle ${identifier} sanitization for Qwen/ZCode
- Parallel installation with diagnosable failures
- Slug validation for empty names

Implementation: `backend/app/services/installer.py`, `backend/app/api/v1/install.py`, `backend/tests/test_installer.py`

Tests: `backend/tests/test_installer.py`

### frontend-dashboard — React dashboard for agent browsing and installation

Status: planned

Acceptance:
- Agent list with search/filter/pagination
- Agent detail view with install button
- Installation progress and results
- Authentication integration

Implementation: `frontend/src/components/AgentList.tsx`, `frontend/src/components/AgentDetail.tsx`, `frontend/src/components/InstallModal.tsx`, `frontend/src/api/client.ts`

Tests: `frontend/src/components/AgentList.test.tsx`

### llm-adapters — LLM provider adapters (OpenAI-compatible, Anthropic, Gemini, Ollama)

Status: planned

Acceptance:
- Unified interface for all providers
- Configurable via env vars only
- Bounded timeouts, redacted errors
- Opt-in explanations labeled advisory

Implementation: `backend/app/services/llm/base.py`, `backend/app/services/llm/openai_compat.py`, `backend/app/services/llm/anthropic.py`, `backend/app/services/llm/gemini.py`, `backend/app/services/llm/ollama.py`

Tests: `backend/tests/test_llm_adapters.py`

