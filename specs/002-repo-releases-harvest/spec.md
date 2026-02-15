# Feature Specification: Repository Release Notes Harvest
 
**Feature Branch**: `002-repo-releases-harvest`  
**Created**: 2026-02-15  
**Status**: Draft  
**Input**: User description: "Fetch last 10 release descriptions from each reachable repo URL /releases page, reformat into per-repo markdown in data/releases, then run convert-releases-to-pdf.sh; report warnings/errors with suggestions before fixing"

## Clarifications

### Session 2026-02-15

- Q: Include pre-releases/drafts or only “stable” releases when selecting the last 10? → A: Include everything (drafts, pre-releases, and full releases).
- Q: Output file naming for each repository markdown? → A: Use `<owner>__<repo>.md`.
- Q: Where do the repository URLs come from? → A: Read URLs from a versioned file in the repo.
- Q: How should pagination on `/releases` be handled? → A: Follow pagination until 10 releases are collected (or no more pages).
- Q: What should happen if the output file already exists? → A: Always overwrite the existing file.

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

### User Story 1 - Generate per-repository release note markdown (Priority: P1)
 
As a release-notes curator, I want the system to pull the most recent release descriptions from each reachable repository’s `/releases` page and produce a clean, consistent markdown summary per repository, so I can review and share release information quickly.
 
**Why this priority**: This is the core value: generating the normalized release note summaries.
 
**Independent Test**: Can be fully tested by providing a small list of reachable repository URLs and verifying a markdown file is produced for each, containing up to the latest 10 release descriptions.
 
**Acceptance Scenarios**:
 
1. **Given** a reachable repository URL, **When** the system fetches the repository’s `/releases` page, **Then** it extracts up to the latest 10 releases and writes a formatted markdown file for that repository.
2. **Given** a repository with fewer than 10 releases, **When** the system runs, **Then** it includes all available release descriptions without failing.

---

### User Story 2 - Actionable warnings and safe failure behavior (Priority: P2)
 
As a release-notes curator, I want the system to report warnings and errors clearly (including suggestions) when a repository cannot be processed, so I understand what happened and what to do next without losing progress from other repositories.
 
**Why this priority**: The feature depends on external sites; clear reporting prevents silent data loss and reduces debugging time.
 
**Independent Test**: Can be tested by including at least one unreachable URL and one reachable URL and verifying the run completes, produces output for the reachable repository, and emits actionable warnings/errors for the unreachable one.
 
**Acceptance Scenarios**:
 
1. **Given** a mix of reachable and unreachable repository URLs, **When** the system runs, **Then** it completes processing for reachable repositories and reports a warning/error for each unreachable repository.
2. **Given** a repository releases page that does not match the expected structure, **When** the system runs, **Then** it reports a warning describing the mismatch and suggests next steps (for example: verify URL, check authentication, or update parsing rules).

---

### User Story 3 - Produce PDFs after markdown generation (Priority: P3)
 
As a release-notes curator, I want the system to trigger the existing PDF conversion process after markdown files are generated, so I can distribute the release notes in PDF format without extra steps.
 
**Why this priority**: PDF output is valuable but depends on the markdown generation being correct.
 
**Independent Test**: Can be tested by running the system on a known repository list and confirming that the PDF conversion process is invoked after markdown creation.
 
**Acceptance Scenarios**:
 
1. **Given** that markdown outputs were generated successfully, **When** the run finishes, **Then** the PDF conversion process is started.
2. **Given** that markdown generation produced only warnings (not fatal failures), **When** the run finishes, **Then** the PDF conversion process is still started and the warnings are surfaced to the user.

---

### Edge Cases

- A repository URL is reachable but its `/releases` page returns an unexpected status (redirect loop, 403, 404).
- A repository has fewer than 10 releases.
- A release entry exists but has an empty/very short description.
- Release descriptions contain HTML, images, or unusual formatting.
- Releases are paginated and the most recent 10 are not on the first page.
- Pagination exists but ends before 10 releases are collected.
- Version labels are not semantic versions (for example: dates, build numbers) or include prefixes (for example: `v1.2.3`).
- Duplicate version labels appear (re-releases) or drafts/pre-releases appear among the latest items.
- The latest 10 releases include drafts and/or pre-releases.
- Rate limiting or temporary network errors occur while fetching.
- Repository URL formats differ (with/without trailing slash) or contain extra paths.

## Scope

### In Scope

- Processing a user-provided list of repository URLs.
- For each reachable repository, extracting up to the latest 10 release descriptions from the repository’s `/releases` page.
- Producing one normalized markdown document per repository in `data/releases`.
- Triggering the existing PDF conversion process after markdown generation.
- Providing a run summary and actionable warnings/errors.

### Out of Scope

- Creating, editing, or publishing releases in any repository.
- Authenticating into private repositories or bypassing access controls.
- Guaranteeing a stable extraction result if a repository changes its releases page structure.

## Assumptions & Dependencies

- The input repository URLs are intended to be publicly reachable from the environment where the system runs.
- The repository URL input list is maintained in a versioned file within this repository.
- Each repository exposes human-readable release descriptions on a `/releases` page.
- The existing PDF conversion script remains available and is able to run in the current environment.
- External availability and rate limiting of repository hosts may affect extraction reliability; the system reports these as warnings/errors.

## Requirements *(mandatory)*

### Functional Requirements
 
- **FR-001**: System MUST read a list of repository URLs from a versioned file in this repository.
- **FR-002**: For each input repository URL, the system MUST determine whether the URL is reachable before attempting extraction.
- **FR-002a**: Reachability check MUST be performed via an HTTP GET request to the derived `/releases` page URL with:
  - a finite timeout
  - a bounded redirect limit
  - a non-empty `User-Agent` header
- **FR-002b**: The system MUST treat a non-success HTTP status (for example: 403, 404) or network failure (DNS, timeout) as unreachable and report an actionable warning/error.
- **FR-003**: For each reachable repository, the system MUST fetch content from the repository’s `/releases` page.
- **FR-003a**: If releases are paginated, the system MUST follow pagination until 10 release descriptions are collected or no further pages are available.
- **FR-004**: System MUST detect the release list structure and extract release items including:
  - A release identifier (version label or tag)
  - A release publication date when present
  - The release description text (the narrative content associated with the release)
  - A canonical link back to the release entry
- **FR-005**: System MUST extract only the latest 10 release descriptions per repository (or fewer if fewer exist), counting drafts, pre-releases, and full releases.
- **FR-006**: System MUST rewrite and reformat extracted release descriptions into a consistent markdown format.
- **FR-006a**: Markdown normalization MUST be deterministic for identical fetched HTML inputs and MUST apply the following minimum rules:
  - Convert common block separators (for example: paragraphs and line breaks) into markdown newlines.
  - Preserve list structure as markdown bullet lists where detectably present.
  - Remove or ignore images and other non-text media.
  - Normalize whitespace (trim trailing spaces, collapse excessive blank lines).
  - Use consistent line endings and ensure the document ends with a newline.
- **FR-007**: System MUST write one markdown file per repository into `data/releases`.
- **FR-007a**: Each repository markdown filename MUST follow the convention `<owner>__<repo>.md`.
- **FR-007b**: If the target repository markdown file already exists, the system MUST overwrite it.
- **FR-008**: Each repository markdown file MUST clearly identify the repository and contain a section per release, ordered newest-to-oldest.
- **FR-009**: System MUST preserve essential meaning of release descriptions while normalizing formatting (for example: headings, bullet lists, whitespace).
- **FR-010**: System MUST report warnings/errors for any repository that cannot be processed, including a suggestion for likely remediation.
- **FR-011**: A failure to process one repository MUST NOT prevent processing of other repositories.
- **FR-012**: After markdown generation completes, the system MUST trigger the existing PDF conversion process for the generated outputs.
- **FR-013**: System MUST provide a run summary indicating:
  - Count of repositories processed successfully
  - Count of repositories with warnings
  - Count of repositories that failed
  - Location of generated markdown outputs

### Key Entities *(include if feature involves data)*
 
- **Repository Source**: A repository reference provided as a URL; includes reachability status and the derived releases page URL.
- **Release Entry**: A single release item (identifier, optional date, description text, canonical link).
- **Repository Release Document**: The generated markdown artifact for one repository containing up to 10 Release Entries.
- **Run Report**: A summary of processing outcomes (successes, warnings, failures) and suggested remediation steps.

## Success Criteria *(mandatory)*

### Measurable Outcomes
 
- **SC-001**: For any reachable repository URL in the input list, the system produces exactly one markdown file in `data/releases` for that repository.
- **SC-002**: Each produced repository markdown file contains no more than 10 releases and is ordered newest-to-oldest.
- **SC-003**: For unreachable or unparseable repositories, the system completes the run and emits a warning/error that includes a suggested next step.
- **SC-004**: The PDF conversion process is started after markdown generation completes, producing PDFs in `data/pdf`.
