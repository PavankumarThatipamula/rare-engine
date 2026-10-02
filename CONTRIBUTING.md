# Contributing to RARE Engine

## Branching & Git Workflow

We follow a strict **Local-First Branching Strategy**:

1. `main` is protected and represents production-ready baseline code.
2. Development occurs on localized phase branches (`phase/XX-<description>`).
3. Changes are developed and verified locally using tests before pushing.
4. Merge into `main` occurs via Pull Request after CI passes and review is completed.

### Branch Naming Conventions
- `phase/00-baseline`
- `phase/01-foundation`
- `phase/02-domain-architecture`
- `feature/<description>`
- `fix/<description>`

## Quality Standards
Before opening a Pull Request, run:
```bash
pytest
```
Ensure all tests pass and no temporary debug files or credentials are saved.