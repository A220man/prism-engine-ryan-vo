# Changelog

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

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