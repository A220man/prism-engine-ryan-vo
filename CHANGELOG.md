# Changelog

## 1.8.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.7.1 — work-in-progress checkpoint

### Added
- `frontend/src/components/AgentList.tsx` - Reusable agent list component with search, tag filter, and pagination
- `frontend/src/components/AgentList.test.tsx` - Unit tests for component import and utility functions (totalPages, clampPage, buildAgentListParams)

### Changed
- Updated PLAN.md to mark `frontend-dashboard` as `in_progress`
- Updated STATUS.md with checkpoint status

## 1.7.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.6.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.5.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.4.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

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
