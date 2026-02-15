# Tasks: Generate Release Stubs

**Input**: Design documents from `/specs/001-repo-release-stubs/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: Included (required by spec: `pytest` with BDD style)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2], [US3])
- All task descriptions include exact file paths.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create script/test directories `scripts/` and `tests/` (repo root)
- [X] T002 Initialize `uv` project and add test dependency in `pyproject.toml` (use `uv`-managed environment)
- [X] T003 [P] Add minimal test configuration in `pytest.ini`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared utilities and contracts that all user stories rely on

- [X] T004 Define CLI contract and constants in `scripts/generate-release-stubs.py` (input/output paths, filename template)
- [X] T005 Implement repo reference normalization/parsing helpers in `scripts/generate-release-stubs.py`
- [X] T006 Implement filesystem helpers (create directories, create-empty-file-no-overwrite) in `scripts/generate-release-stubs.py`
- [X] T007 Implement summary/reporting data structure and stdout output in `scripts/generate-release-stubs.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Generate blank release note files from repo list (Priority: P1) 🎯 MVP

**Goal**: Generate empty stub Markdown files for each reachable repo in `data/repo/repos.txt`.

**Independent Test**: With a repo list containing a reachable and an unreachable repo reference, running the script results in stub creation only for the reachable repo.

### Tests for User Story 1 (BDD-style)

- [X] T008 [P] [US1] Add BDD-style tests for reachability behavior by invoking the CLI via subprocess in `tests/test_generate_release_stubs.py`
- [X] T009 [US1] Add test fixtures for temporary repo root and sample `data/repo/repos.txt` in `tests/test_generate_release_stubs.py`

### Implementation for User Story 1

- [X] T010 [US1] Implement unauthenticated HTTP reachability check with 5s timeout and single retry (200/3xx reachable; 401/403/404/timeout after retry unreachable) in `scripts/generate-release-stubs.py`
- [X] T011 [US1] Implement main flow to read `data/repo/repos.txt`, filter ignored lines, and attempt stub creation for reachable repos in `scripts/generate-release-stubs.py`
- [X] T012 [US1] Ensure newly created stub files are empty (0 bytes) in `scripts/generate-release-stubs.py`

**Checkpoint**: User Story 1 is functional and testable independently

---

## Phase 4: User Story 2 - Safe re-runs without overwriting notes (Priority: P2)

**Goal**: Re-running the script does not overwrite existing files.

**Independent Test**: Pre-create a non-empty file under `data/releases/` and verify it remains unchanged after running the script.

### Tests for User Story 2 (BDD-style)

- [X] T013 [P] [US2] Add BDD-style tests for non-overwrite behavior in `tests/test_generate_release_stubs.py`

### Implementation for User Story 2

- [X] T014 [US2] Add explicit skip logic for existing output files and count as "skipped (exists)" in `scripts/generate-release-stubs.py`

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 - Accept common repo URL formats (Priority: P3)

**Goal**: Accept `owner/repo` and `https://github.com/owner/repo` (optional trailing `/`, optional `.git`) and normalize both to the same identity.

**Independent Test**: Provide the same repo as `owner/repo` and as an equivalent GitHub HTTPS URL and confirm output filename is identical.

### Tests for User Story 3 (BDD-style)

- [X] T015 [P] [US3] Add BDD-style tests for accepted input formats and normalization in `tests/test_generate_release_stubs.py`

### Implementation for User Story 3

- [X] T016 [US3] Extend/confirm parser to accept the two supported formats and normalize them in `scripts/generate-release-stubs.py`

**Checkpoint**: All user stories work independently

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Completeness, robustness, and docs alignment

- [X] T017 [P] Add BDD-style tests for ignoring comment/blank lines in `tests/test_generate_release_stubs.py`
- [X] T018 [P] Add BDD-style tests for de-duplication behavior in `tests/test_generate_release_stubs.py`
- [X] T019 Ensure de-duplication happens before network checks and before file creation in `scripts/generate-release-stubs.py`
- [X] T020 Improve summary output counts (processed, reachable, created, skipped-unreachable, skipped-duplicate, skipped-exists) in `scripts/generate-release-stubs.py`
- [X] T021 Validate quickstart instructions match final CLI and file locations in `specs/001-repo-release-stubs/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: no dependencies
- **Phase 2 (Foundational)**: depends on Phase 1
- **Phase 3+ (User Stories)**: depend on Phase 2
- **Phase 6 (Polish)**: depends on Phases 3–5

### User Story Dependencies

- **US1**: depends on Foundational; no dependency on other stories
- **US2**: depends on US1 implementation utilities (file creation and reporting)
- **US3**: depends on Foundational parsing utilities; can be done after US1 or before polish

### Parallel Opportunities

- Tasks marked **[P]** can be executed in parallel (different files/sections) once prerequisites are satisfied.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

- Complete Phases 1–3 (T001–T012)
- Validate by running the script and the US1 tests (use `uv run python scripts/generate-release-stubs.py` and `uv run pytest`)

### Incremental Delivery

- Add US2 (T013–T014)
- Add US3 (T015–T016)
- Finish polish (T017–T021)
