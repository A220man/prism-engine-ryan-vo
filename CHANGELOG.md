# Changelog

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.3.0 — Agent installer feature

### Added
- Agent installer service with multi-target support (Claude Code, Cursor, Aider, Qwen, ZCode)
- Install API endpoints: POST /api/v1/install, GET /api/v1/install/targets
- Identifier sanitization for Qwen/ZCode targets (${identifier} → sanitized)
- Parallel installation with detailed success/failure results per target
- Slug validation for Qwen/ZCode compatibility
- Overwrite protection with optional force flag
- Comprehensive test suite (18 tests: 10 service tests + 8 endpoint tests)

### Changed
- Updated main.py to register install router
- Updated feature-plan.json and PLAN.md to track agent-installer completion

### Fixed
- Test database session commit for proper test isolation
- Module-level function patching for test dependency injection

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Added
- Agent registry CRUD API with SQLite persistence (backend)
- Agent model with name, slug, description, content, version, author, tags
- AgentService with create, get, list, update, delete operations
- Agent API endpoints: POST /agents, GET /agents, GET /agents/{id}, GET /agents/slug/{slug}, PATCH /agents/{id}, DELETE /agents/{id}
- Pagination, search filtering, slug validation
- Backend tests for all agent endpoints (10 tests passing)
- Fixed test database session commit issue
- Fixed test config to use DEMO_MODE

### Changed
- None

### Fixed
- Test database sessions now properly commit transactions
- Test configuration enables DEMO_MODE for pytest runs

### Security
- None