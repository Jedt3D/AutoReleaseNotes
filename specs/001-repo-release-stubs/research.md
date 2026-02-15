# Research: Generate Release Stubs

**Date**: 2026-02-15
**Feature**: [spec.md](./spec.md)

## Decisions

### 1) HTTP client choice

- **Decision**: Use Python standard library (`urllib.request`) for HTTP reachability checks.
- **Rationale**: Keeps dependencies minimal and works on macOS by default.
- **Alternatives considered**:
  - `requests`: simpler API but adds an external dependency.

### 2) Reachability definition

- **Decision**: Perform an unauthenticated HTTP request to the GitHub web URL; treat HTTP 200/3xx as reachable; treat 401/403/404 and network failures/timeouts as unreachable.
- **Rationale**: Matches clarified spec; avoids tokens/auth.
- **Alternatives considered**:
  - Git-based `ls-remote` checks: more complex and depends on git/ssh config.
  - Authenticated API checks: requires credential management.

### 3) Timeout and failure behavior

- **Decision**: Use a fixed per-repo timeout for network checks and continue on failure.
- **Rationale**: Prevents the run from hanging on a single repo; aligns with “skip unreachable without failing whole run”.
- **Alternatives considered**:
  - No timeout: unacceptable for reliability.

### 4) Input normalization and de-duplication

- **Decision**: Normalize supported inputs (`owner/repo` and `https://github.com/owner/repo` with optional trailing `/` and optional `.git`), then de-duplicate by normalized `owner/repo`.
- **Rationale**: Makes duplicate handling deterministic and predictable.
- **Alternatives considered**:
  - Accepting arbitrary URLs: increases ambiguity and risk of incorrect parsing.

### 5) Output naming

- **Decision**: Use `data/releases/<owner>__<repo>.md`.
- **Rationale**: Avoids collisions across different owners.
- **Alternatives considered**:
  - Repo-only filenames: collision risk.
  - Subdirectories: adds complexity for downstream tooling.
