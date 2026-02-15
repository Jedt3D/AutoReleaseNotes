# AutoReleaseNotes Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-15

## Active Technologies
- Python 3 (macOS system Python / `python3`) + Python standard library for fetching/parsing; existing PDF conversion depends on `pandoc` and `weasyprint` (002-repo-releases-harvest)
- Files under the repo root (`data/repo`, `data/releases`, `data/pdf`) (002-repo-releases-harvest)

- Python 3.14+ + Standard library preferred; add a small HTTP client dependency only if needed (decision documented in research). (001-repo-release-stubs)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.14+: Follow standard conventions

## Recent Changes
- 002-repo-releases-harvest: Added Python 3 (macOS system Python / `python3`) + Python standard library for fetching/parsing; existing PDF conversion depends on `pandoc` and `weasyprint`

- 001-repo-release-stubs: Added Python 3.14+ + Standard library preferred; add a small HTTP client dependency only if needed (decision documented in research).

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
