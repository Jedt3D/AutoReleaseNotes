# Contract: Generate Release Stubs CLI

**Date**: 2026-02-15
**Feature**: [spec.md](../spec.md)

## Inputs

- **Repo list**: `data/repo/repos.txt`
  - One repository reference per line.
  - Ignore blank/whitespace-only lines.
  - Ignore comment-only lines whose first non-whitespace character is `#`.
  - Supported repo reference formats:
    - `owner/repo`
    - `https://github.com/owner/repo` (optional trailing `/`, optional `.git`)

## Behavior

- Normalize references to `owner/repo`.
- De-duplicate by normalized `owner/repo`.
- For each unique repo:
  - Perform unauthenticated HTTP reachability check against `https://github.com/<owner>/<repo>`.
  - Treat 200/3xx as reachable; treat 401/403/404 and network failures/timeouts as unreachable.
- For each reachable repo:
  - Create `data/releases/<owner>__<repo>.md` if it does not already exist.
  - Newly created files are empty (0 bytes).

## Outputs

- **Created files**: `data/releases/<owner>__<repo>.md`
- **Summary output**: Human-readable counts:
  - processed
  - reachable
  - created
  - skipped (unreachable)
  - skipped (duplicate)
  - skipped (exists)

## Non-goals

- No authentication or private repo access.
- No overwriting of existing Markdown files.
