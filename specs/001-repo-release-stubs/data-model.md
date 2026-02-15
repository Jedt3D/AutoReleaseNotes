# Data Model: Generate Release Stubs

**Date**: 2026-02-15
**Feature**: [spec.md](./spec.md)

## Entities

### RepositoryEntry

Represents one raw line from `data/repo/repos.txt` after pre-processing.

- **raw_line**: original text line
- **trimmed_line**: raw line with leading/trailing whitespace removed
- **kind**: one of
  - comment (ignored)
  - blank (ignored)
  - repo_ref (candidate repository reference)

### RepositoryRef

Normalized identity derived from a valid repo reference.

- **owner**: GitHub owner/org name
- **repo**: GitHub repository name
- **normalized**: `<owner>/<repo>`
- **web_url**: `https://github.com/<owner>/<repo>`
- **output_filename**: `<owner>__<repo>.md`
- **output_path**: `data/releases/<owner>__<repo>.md`

### ReachabilityResult

Outcome of checking `web_url`.

- **status**: reachable | unreachable
- **http_status**: integer or null (if network failure)
- **reason**: short string (e.g., timeout, 404, 403)

## Validation & Rules

- Only these repo reference formats are valid:
  - `owner/repo`
  - `https://github.com/owner/repo` (optional trailing `/`, optional `.git`)
- Comment lines are those where the first non-whitespace character is `#`.
- De-duplicate by `normalized` (`owner/repo`) before performing reachability checks.
- Reachability check:
  - reachable if HTTP status is 200 or 3xx
  - unreachable if HTTP status is 401/403/404 or on network failures/timeouts
- Output files:
  - created only for reachable repos
  - created only if file does not already exist
  - created empty (0 bytes)
