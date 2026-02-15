# Feature Specification: Generate Release Stubs

**Feature Branch**: `001-repo-release-stubs`  
**Created**: 2026-02-15  
**Status**: Draft  
**Input**: User description: "Create a script that reads data/repo/repos.txt (one GitHub repo per line), checks accessibility, ignores unreachable repos, and creates blank markdown files in data/releases named after each repo."

## Clarifications

### Session 2026-02-15

- Q: How should the script decide whether a GitHub repo is “reachable”? → A: Public HTTP check only; treat unauthenticated success (200/3xx) as reachable; skip 401/403/404/timeouts.
- Q: What timeout/retry policy should be used for reachability checks? → A: Use a 5-second timeout per attempt and retry once (at most 2 total attempts) before marking unreachable.
- Q: In `data/repo/repos.txt`, should the script support comments and whitespace-only lines? → A: Ignore blank/whitespace-only lines and ignore comment lines whose first non-whitespace character is `#`.
- Q: When deriving the stub Markdown filename, should it use only `repo` or include `owner` too? → A: Include `owner` and `repo` to guarantee uniqueness (use `<owner>__<repo>.md`).
- Q: When creating a new stub file, what should its initial contents be? → A: Completely empty file (0 bytes).
- Q: Which input formats should be considered valid repo references for `data/repo/repos.txt`? → A: Support `owner/repo` and `https://github.com/<owner>/<repo>` URLs (optional trailing slash / `.git`).
- Q: What should happen if `data/repo/repos.txt` contains duplicate repositories? → A: Ignore duplicates; process each unique repository at most once.

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Generate blank release note files from repo list (Priority: P1)

As a maintainer, I want to provide a list of GitHub repositories and automatically create placeholder Markdown release note files for each reachable repo, so I can fill them in later and keep naming consistent.

**Why this priority**: This is the core workflow needed before any PDF generation; without the stub files, there is nothing to author or convert.

**Independent Test**: Can be fully tested by running the script against a small `data/repo/repos.txt` containing a mix of reachable and unreachable entries and verifying that only the expected new `.md` files are created in `data/releases/`.

**Acceptance Scenarios**:

1. **Given** `data/repo/repos.txt` contains at least one reachable GitHub repo, **When** the script is run, **Then** a new blank Markdown file is created under `data/releases/` named `<owner>__<repo>.md`.
2. **Given** `data/repo/repos.txt` contains unreachable/invalid entries, **When** the script is run, **Then** those entries are ignored and no files are created for them.

---

### User Story 2 - Safe re-runs without overwriting notes (Priority: P2)

As a maintainer, I want to be able to re-run the script without losing any existing authored release notes.

**Why this priority**: Repo lists evolve over time; re-running should be safe and support incremental additions.

**Independent Test**: Pre-create a Markdown file in `data/releases/`, run the script, and verify the file contents and timestamp are not modified.

**Acceptance Scenarios**:

1. **Given** a target stub file already exists in `data/releases/`, **When** the script is run, **Then** the script MUST NOT overwrite the existing file.

---

### User Story 3 - Accept common repo URL formats (Priority: P3)

As a maintainer, I want to paste GitHub HTTPS repo URLs or `owner/repo` so I don't have to normalize them manually.

**Why this priority**: It reduces friction and prevents input format issues.

**Independent Test**: Provide `owner/repo` and the equivalent `https://github.com/owner/repo` and verify they resolve to the same output filename.

**Acceptance Scenarios**:

1. **Given** a mix of `https://github.com/owner/repo` and `owner/repo`, **When** the script is run, **Then** all reachable entries result in correctly named stub files.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when `data/repo/repos.txt` does not exist or is empty?
- How does the system handle blank/whitespace-only lines, comment-only lines, or trailing whitespace?
- What happens when two different input lines refer to the same repo (duplicates)?
- What happens when a repo name would collide with an existing file (already authored notes)?
- What happens when the repo URL returns a redirect (should be treated as reachable)?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Technology Constraints

- Implementation language MUST be Python 3.14+.
- Tests MUST use `pytest` and follow a BDD style.

### Functional Requirements

- **FR-001**: The system MUST read repository entries from `data/repo/repos.txt`, one entry per line.
- **FR-002**: The system MUST ignore blank/whitespace-only lines, MUST ignore comment-only lines whose first non-whitespace character is `#`, and MUST ignore leading/trailing whitespace on repository entries.
- **FR-002a**: The system MUST accept repository references in either `owner/repo` form or `https://github.com/owner/repo` form. For URL forms, optional trailing `/` and optional `.git` suffix MUST be tolerated.
- **FR-002b**: The system MUST de-duplicate repository entries by normalized `owner/repo` identity (after trimming and URL normalization) so that each unique repository is processed at most once per run.
- **FR-003**: The system MUST determine whether a repository is reachable before generating a stub by performing an unauthenticated HTTP request to the GitHub web URL with a 5-second timeout per attempt and a single retry (at most 2 total attempts); HTTP success responses (200/3xx) MUST be treated as reachable; HTTP 401/403/404 and network failures/timeouts after retries MUST be treated as unreachable.
- **FR-004**: For each reachable repository, the system MUST derive the repository owner and name (the `owner/repo` identity) and use it as the Markdown filename: `data/releases/<owner>__<repo>.md`.
- **FR-005**: The system MUST create `data/releases/` if it does not already exist.
- **FR-006**: If the target Markdown file already exists, the system MUST NOT overwrite it.
- **FR-007**: The system SHOULD report a summary of how many repos were processed, how many stubs were created, how many were skipped due to being unreachable, and how many were skipped due to existing files.
- **FR-008**: Newly created stub files MUST be empty (0 bytes).

### Key Entities *(include if feature involves data)*

- **Repository Entry**: A single line from `data/repo/repos.txt` representing a GitHub repository reference.
- **Reachability Check**: A determination that the referenced repository can be accessed (e.g., via an HTTP request returning a successful response).
- **Release Stub File**: A Markdown file under `data/releases/` created as a placeholder for future release notes.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Given a repo list containing at least 1 reachable repository, running the script results in a corresponding `.md` file being created in `data/releases/` for each reachable repo that does not already have a file.
- **SC-002**: Given a repo list containing at least 1 unreachable/invalid repository, running the script completes successfully and creates no stub file for unreachable entries.
- **SC-003**: Re-running the script on the same inputs does not change or overwrite any existing `.md` files.
- **SC-004**: The script completes and provides a human-readable summary of created vs skipped items.
