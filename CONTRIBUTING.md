# Contributing

Thanks for considering contributing to WildfireWatch UK.

## Development principles

- Keep the proof of concept reproducible.
- Preserve raw source data; derive new tables instead of overwriting inputs.
- Record assumptions in `DECISIONS.md`.
- Record unresolved issues in `ISSUES.md`.
- Add tests for core feature calculations and API behavior.
- Avoid future-data leakage in all retrospective features.

## Setup

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

## Pull requests

Use small, logical pull requests with:

- summary of changes
- data sources touched
- test evidence
- known limitations

## Safety-sensitive changes

Any change that affects public messaging, active-incident language, or risk interpretation must preserve the project's safety guardrails.
