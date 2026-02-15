# Quickstart: Generate Release Stubs

**Date**: 2026-02-15
**Feature**: [spec.md](./spec.md)

## Prerequisites

- Python 3.14+
- `pytest`

## Prepare input

1. Create or update `data/repo/repos.txt`.
2. One repository per line.
3. Supported formats:
   - `owner/repo`
   - `https://github.com/owner/repo` (optional trailing `/`, optional `.git`)
4. Lines whose first non-whitespace character is `#` are comments and are ignored.

## Run

From the repository root:

```bash
uv run python scripts/generate-release-stubs.py
```

## Expected results

- Creates empty files under `data/releases/` named:
  - `<owner>__<repo>.md`
- Skips:
  - unreachable repos
  - duplicates
  - already-existing files

## Run tests

```bash
uv run pytest
```
