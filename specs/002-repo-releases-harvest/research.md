# Research: Repository Release Notes Harvest

## Decisions

- **Decision**: Use the existing repository input source of truth at `data/repo/repos.txt`.
  - **Rationale**: Matches constitution-defined input path and existing script conventions.
  - **Alternatives considered**:
    - CLI-provided list (harder to make deterministic/reproducible across runs).
    - Scanning local clones (adds environment coupling).

- **Decision**: Treat the repository `/releases` page as the authoritative source for release descriptions and follow pagination until 10 release entries are collected (or no more pages).
  - **Rationale**: Matches user requirement to fetch last 10 and avoids silent truncation for high-activity repos.
  - **Alternatives considered**:
    - First page only (can produce fewer than 10).
    - Page cap (can under-fetch unexpectedly).

- **Decision**: Include drafts and pre-releases in the “latest 10” selection.
  - **Rationale**: Explicit user clarification; simplifies selection rules (take latest 10 items as presented).
  - **Alternatives considered**:
    - Stable releases only (common default but rejected by clarification).

- **Decision**: Output one markdown file per repo under `data/releases/`, named `<owner>__<repo>.md`, overwriting any existing file.
  - **Rationale**: Aligns with existing naming conventions already present in `data/releases/` and supports idempotent runs that converge.
  - **Alternatives considered**:
    - Timestamped files (safe but not convergent/idempotent).
    - Merge/append (hard to keep deterministic without more rules).

- **Decision**: Reuse the existing PDF conversion pipeline `scripts/convert-releases-to-pdf.sh` and its output path `data/pdf/`.
  - **Rationale**: Constitution standardizes these paths and stack (`pandoc` + `weasyprint`), and script already has safety guards.
  - **Alternatives considered**:
    - Different PDF engine or custom HTML rendering (not needed; increases complexity).

## Operational Notes

- **Determinism**: Ensure markdown content ordering is stable (newest-to-oldest) and formatting normalization does not depend on nondeterministic factors.
- **Safety**: Only overwrite within `data/releases/` and only delete PDFs within `data/pdf/` (already guarded by `convert-releases-to-pdf.sh`).
- **Portability**: Keep shell steps compatible with macOS default Bash; prefer Python standard library.
- **Error handling**: Print progress to stdout and warnings/errors to stderr per constitution.
