---

description: "Tasks for implementing repository release notes harvest"
---

# Tasks: Repository Release Notes Harvest

**Input**: Design documents from `/specs/002-repo-releases-harvest/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in spec.md. This task list focuses on implementation + manual/CLI verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure existing scripts and directories align with the plan’s pipeline expectations.

- [ ] T001 Validate required input/output directories exist (or are created) for `data/repo/`, `data/releases/`, `data/pdf/`
- [ ] T002 [P] Validate `data/repo/repos.txt` contains at least one repository entry and document accepted formats in `data/repo/repos.txt`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared plumbing needed before implementing user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Add a small internal data model (dataclasses) for Repository Source, Release Entry, and Run Report in `scripts/generate-release-stubs.py`
- [ ] T004 Implement repo reference parsing + normalization (supports `owner/repo`, `https://github.com/owner/repo`, `.../repo.git`) in `scripts/generate-release-stubs.py`
- [ ] T005 Implement deterministic, repo-safe output path builder (`data/releases/<owner>__<repo>.md`) in `scripts/generate-release-stubs.py`
- [ ] T006 Implement stdout/stderr routing helpers (progress to stdout; warnings/errors to stderr) in `scripts/generate-release-stubs.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Generate per-repository release note markdown (Priority: P1) 🎯 MVP

**Goal**: Fetch up to the latest 10 releases (including drafts and pre-releases) per repository and write a normalized markdown file per repo under `data/releases/`.

**Independent Test**: Put 1-2 reachable GitHub repos into `data/repo/repos.txt`, run `python3 scripts/generate-release-stubs.py`, and verify:
- a corresponding `data/releases/<owner>__<repo>.md` is overwritten/created
- file contains <= 10 release sections ordered newest-to-oldest

### Implementation for User Story 1

- [ ] T007 [US1] Implement reachability check via HTTP GET to the derived `/releases` URL with finite timeout, bounded redirect limit, and non-empty `User-Agent` header; treat non-success status or network failure as unreachable in `scripts/generate-release-stubs.py`
- [ ] T008 [US1] Derive canonical `/releases` URL from each repository URL/ref in `scripts/generate-release-stubs.py`
- [ ] T009 [US1] Fetch `/releases` HTML and follow pagination until 10 release entries are collected (or no next page) in `scripts/generate-release-stubs.py`
- [ ] T010 [US1] Parse release list structure from HTML into Release Entry objects (id/tag, optional date, link, kind, description) in `scripts/generate-release-stubs.py`
- [ ] T011 [US1] Normalize release description content to deterministic markdown with minimum rules (paragraph/line break to newlines; preserve list structure as markdown bullets where detectably present; remove/ignore images/non-text media; normalize whitespace including trimming trailing spaces and collapsing excessive blank lines; consistent line endings; ensure final newline) in `scripts/generate-release-stubs.py`
- [ ] T012 [US1] Render final per-repo markdown document (repo header + per-release sections, newest-to-oldest) in `scripts/generate-release-stubs.py`
- [ ] T013 [US1] Write/overwrite `data/releases/<owner>__<repo>.md` atomically (write temp + replace) in `scripts/generate-release-stubs.py`

**Checkpoint**: User Story 1 produces deterministic markdown for reachable repositories

---

## Phase 4: User Story 2 - Actionable warnings and safe failure behavior (Priority: P2)

**Goal**: Continue processing other repositories if one fails, and emit actionable warnings/errors with suggestions.

**Independent Test**: Add one reachable and one unreachable/invalid repo ref to `data/repo/repos.txt`, run `python3 scripts/generate-release-stubs.py`, and verify:
- reachable repo output is produced
- stderr contains a clear warning/error for the failing repo with a remediation suggestion
- exit code behavior is sensible (non-zero only on overall fatal failure, if any)

### Implementation for User Story 2

- [ ] T014 [US2] Add per-repo exception boundary so a failure does not stop other repos in `scripts/generate-release-stubs.py`
- [ ] T015 [US2] Add structured warning/error records to Run Report (repo + reason + suggestion) in `scripts/generate-release-stubs.py`
- [ ] T016 [US2] Implement actionable suggestions for common failures (DNS/timeout, 403/404, redirect loop, parse mismatch, rate limiting) in `scripts/generate-release-stubs.py`
- [ ] T017 [US2] Print end-of-run summary (counts + output directory) to stdout and warnings/errors summary to stderr in `scripts/generate-release-stubs.py`
- [ ] T018 [US2] Ensure deterministic behavior (stable repo ordering, de-dup by `owner/repo` case-insensitive, stable warning ordering) in `scripts/generate-release-stubs.py`

**Checkpoint**: Mixed-success runs complete with actionable stderr output

---

## Phase 5: User Story 3 - Produce PDFs after markdown generation (Priority: P3)

**Goal**: Trigger `scripts/convert-releases-to-pdf.sh` after markdown generation finishes.

**Independent Test**: Run `python3 scripts/generate-release-stubs.py` and verify it invokes the PDF conversion script and produces/refreshes PDFs under `data/pdf/`.

### Implementation for User Story 3

- [ ] T019 [US3] Add a post-processing step to invoke `bash scripts/convert-releases-to-pdf.sh` after markdown generation in `scripts/generate-release-stubs.py`
- [ ] T020 [US3] Ensure PDF conversion runs even when markdown generation produced warnings (but not overall fatal failure) in `scripts/generate-release-stubs.py`
- [ ] T021 [US3] Surface PDF conversion failures clearly (stderr output + install hints already provided by script) in `scripts/generate-release-stubs.py`

**Checkpoint**: End-to-end pipeline generates markdown then PDFs

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improve usability, resilience, and alignment with the documented contracts/quickstart.

- [ ] T022 [P] Align script output paths and messages with `specs/002-repo-releases-harvest/contracts/cli.md` in `scripts/generate-release-stubs.py`
- [ ] T023 Add basic rate-limit friendliness (user-agent header, small backoff/retry on transient 429/5xx) in `scripts/generate-release-stubs.py`
- [ ] T024 [P] Validate `specs/002-repo-releases-harvest/quickstart.md` commands succeed on macOS and adjust `scripts/generate-release-stubs.py` behavior to match (stdout/stderr expectations)
- [ ] T025 [P] Update README usage section (if needed) to mention the new behavior and outputs in `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational
- **User Story 2 (Phase 4)**: Depends on Foundational; can be developed after US1 is functional but must not break US1
- **User Story 3 (Phase 5)**: Depends on US1 completing markdown generation (and should integrate cleanly with US2 warning behavior)
- **Polish (Phase 6)**: Depends on desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Core functionality; enables all subsequent stories
- **US2 (P2)**: Builds on US1 flow to add robust reporting and safe failure
- **US3 (P3)**: Requires markdown generation; should run even with US2 warnings

### Parallel Opportunities

- **T001/T002** can be done immediately.
- In Phase 2, some tasks are sequential in the same file; avoid parallel edits to `scripts/generate-release-stubs.py` unless you split work into non-overlapping sections.
- In Phase 6, documentation tasks (T024/T025) are parallelizable with code hardening (T023).

---

## Parallel Example: Phase 6

```bash
Task: "Add basic rate-limit friendliness ... in scripts/generate-release-stubs.py"
Task: "Update README usage section ... in README.md"
Task: "Validate quickstart commands ... in specs/002-repo-releases-harvest/quickstart.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3 (US1)
3. **STOP and VALIDATE** using the US1 independent test

### Incremental Delivery

1. Add US2 robustness and summary reporting
2. Add US3 PDF invocation
3. Finish with Polish tasks
