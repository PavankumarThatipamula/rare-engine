# RARE Engine - Agent Operational Rules & Directives

This document sets the mandatory rules for any AI agent or automated coding tool working on the `rare-engine` codebase.

## Core Rules

1. **Read Before Modifying:** Always inspect existing code, imports, and tests before making changes.
2. **Never Modify Main Directly:** All work must occur on a dedicated `phase/<number>-<topic>` branch.
3. **Dependency Control:** Do not add third-party packages without explicit human authorization.
4. **No Premature Infrastructure:** Maintain zero unnecessary dependencies (no Redis, Kafka, or vector DBs until scale demands it).
5. **Surgical Changes:** Do not refactor or reformat unrelated modules outside your scope.
6. **Test Coverage Mandatory:** Every new or updated business rule must include accompanying unit/integration tests.
7. **Security Tests Required:** Security-sensitive logic (parsers, file ingestion, path resolution) requires edge-case tests.
8. **Infrastructure-Independent Domain:** Domain logic must remain isolated from frameworks (FastAPI, SQLAlchemy, OpenAI).
9. **No Hard-coded Secrets:** Never embed tokens, API keys, or private identifiers in code or tests.
10. **Synthetic Data Only:** Never introduce real payment tokens, real cardholder data, or real PII into the repository.
11. **Assume Network Flakiness:** Treat all external API interactions (LLMs, storage) as unreliable; provide fallbacks or mocks.
12. **Interface Abstraction:** Prefer pure interfaces/adapters for replaceable components (storage, LLM providers).
13. **Pre-commit Verification:** Always execute pytest, type checking, and linting before marking a task complete.
14. **Document Architectural Shift:** Any change altering module boundaries requires updating `docs/architecture/`.
15. **Keep Pull Requests Small:** Aim for self-contained, reviewable atomic changes.

## Development Commands
- Run Tests: `pytest`
- Run Application CLI: `python -m src.main`