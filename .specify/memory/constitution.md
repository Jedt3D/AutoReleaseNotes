# AutoReleaseNotes Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

## Core Principles

### I. Deterministic, Readable Artifacts
<!-- Example: I. Library-First -->
All outputs (generated PDFs) must be deterministic given the same inputs.

Prefer readability in print over perfect fidelity to web rendering.

CSS changes must be validated against sample release notes to avoid regressions in pagination, code blocks, and tables.
<!-- Example: Every feature starts as a standalone library; Libraries must be self-contained, independently testable, documented; Clear purpose required - no organizational-only libraries -->

### II. Script Portability (macOS-First)
<!-- Example: II. CLI Interface -->
Shell scripts must run on macOS default tooling (notably Bash 3.2) unless explicitly documented otherwise.

Avoid non-portable Bash 4+ builtins and GNU-only flags.

If a dependency is required (e.g. `pandoc`, `weasyprint`), detect it early and fail with a clear install hint.
<!-- Example: Every library exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support JSON + human-readable formats -->

### III. Safety by Default (NON-NEGOTIABLE)
<!-- Example: III. Test-First (NON-NEGOTIABLE) -->
Do not delete or overwrite user data outside project-controlled output directories.

When removing or replacing generated artifacts, use allowlisted paths and explicit guards.

Any command that could be destructive must be narrowly scoped and clearly logged.
<!-- Example: TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced -->

### IV. Clear Inputs/Outputs and Idempotent Runs
<!-- Example: IV. Integration Testing -->
Define a single source of truth for inputs and outputs:

- Github Repo: `data/repo/repos.txt`
- Input Markdown: `data/releases/*.md`
- Output PDFs: `data/pdf/*.pdf`
- Print styling: `resources/css/styles-print.css`

Scripts should be idempotent: running them repeatedly should converge to the same outputs without manual cleanup.
<!-- Example: Focus areas requiring integration tests: New library contract tests, Contract changes, Inter-service communication, Shared schemas -->

### V. Small Changes, Fast Feedback
<!-- Example: V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
Prefer minimal, targeted changes over refactors.

Always keep at least one sample release note in the repo to validate formatting.

When behavior changes, include a quick reproduction command and expected outcome in the PR/spec.
<!-- Example: Text I/O ensures debuggability; Structured logging required; Or: MAJOR.MINOR.BUILD format; Or: Start simple, YAGNI principles -->

## Constraints & Standards
<!-- Example: Additional Constraints, Security Requirements, Performance Standards, etc. -->

- **Dependencies**
  - Must support `pandoc` and `weasyprint` as the PDF generation stack.
  - Syntax highlighting is best-effort (scripts must fall back gracefully if highlighting flags/styles differ by pandoc version).

- **Output Location**
  - Generated artifacts belong under `data/pdf/`.
  - The project must never write outside the repo root without an explicit opt-in flag.

- **Logging**
  - Normal progress messages go to stdout.
  - Warnings and errors go to stderr.

- **CSS for Print**
  - Prefer properties supported by WeasyPrint; treat unsupported CSS warnings as signals to simplify.
<!-- Example: Technology stack requirements, compliance standards, deployment policies, etc. -->

## Development Workflow & Quality Gates
<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->

- **Local validation (required for changes touching scripts/CSS/templates)**
  - Run `bash scripts/convert-releases-to-pdf.sh`.
  - Confirm PDFs are produced under `data/pdf/`.

- **Compatibility**
  - Scripts must work with macOS default Bash.

- **Review focus**
  - Any change impacting generated output must be reviewed for:
    - Pagination regressions
    - Code block readability
    - Table layout
    - Link rendering
<!-- Example: Code review requirements, testing gates, deployment approval process, etc. -->

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

- This constitution supersedes other local conventions.
- Amendments require:
  - A short written rationale
  - A migration note if behavior changes (e.g. output paths, CSS defaults)
  - Re-running the PDF generation script to ensure the repo remains in a working state
<!-- Example: All PRs/reviews must verify compliance; Complexity must be justified; Use [GUIDANCE_FILE] for runtime development guidance -->

**Version**: 1.0.0 | **Ratified**: 2026-02-15 | **Last Amended**: 2026-02-15
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
