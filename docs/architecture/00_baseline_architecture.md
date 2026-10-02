# Baseline Architecture Audit (Phase 0)

## Overview
RARE Engine currently exists as an initial prototype containing evidence processing, rule synthesis, and rebuttal export capabilities.

## Source Code Ingestion Map (`src/`)

- `src/config.py`: System environment configuration, path definitions for data directories (`synthetic_docs/`, `rebuttals/`, `test_cases.json`).
- `src/document_agent.py`: Evidence extraction module using Pydantic models for validation and metadata handling.
- `src/rag_engine.py`: Rules retrieval engine providing network rule lookup and dispute defense synthesis.
- `src/exporter.py`: Defense packet exporter producing PDF and TXT output formats in `data/rebuttals/`.
- `src/synthetic_generator.py`: Dataset generation utility populating sample disputes and synthetic evidence files.
- `src/main.py`: Dual-purpose CLI orchestrator and basic FastAPI application entrypoint.

## Data Artifacts (`data/`)
- `data/synthetic_docs/`: Storage location for generated sample PDF documents.
- `data/rebuttals/`: Target directory for generated defense packages.
- `data/test_cases.json`: Test dispute dataset used by the test suite.

## Baseline Constraints & Debt
1. Coupling between extraction logic and external AI calls.
2. In-memory data structures lacking persistent storage adapter interfaces.
3. Lack of strict separation between domain logic and presentation layers.