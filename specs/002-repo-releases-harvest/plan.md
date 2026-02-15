# Implementation Plan: Repository Release Notes Harvest

**Branch**: `002-repo-releases-harvest` | **Date**: 2026-02-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-repo-releases-harvest/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Generate deterministic, print-friendly release note markdown files under `data/releases/` by reading repository URLs from `data/repo/repos.txt`, fetching each repository’s `/releases` pages (including drafts and pre-releases), collecting the latest 10 release descriptions (following pagination), and overwriting the per-repo markdown files. After markdown generation, run the existing PDF pipeline (`scripts/convert-releases-to-pdf.sh`) to produce PDFs in `data/pdf/`.

## Technical Context

**Language/Version**: Python 3 (macOS system Python / `python3`)  
**Primary Dependencies**: Python standard library for fetching/parsing; existing PDF conversion depends on `pandoc` and `weasyprint`  
**Storage**: Files under the repo root (`data/repo`, `data/releases`, `data/pdf`)  
**Testing**: Lightweight script-level/integration checks (command runs + file outputs)  
**Target Platform**: macOS (constitution: macOS default tooling; Bash 3.2)  
**Project Type**: Scripted pipeline (Python + Bash)  
**Performance Goals**: Process typical repo lists in seconds to low minutes; fetch at most the first pages required to collect 10 releases per repo  
**Constraints**: Deterministic outputs for identical inputs; safe writes restricted to allowlisted project directories; warnings/errors to stderr  
**Scale/Scope**: Dozens of repositories; 10 releases per repo; output is one markdown + one PDF per repo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

* **Deterministic, readable artifacts**: Plan enforces deterministic markdown given same inputs; print readability is prioritized over web fidelity.
* **Script portability (macOS-first)**: Any shell steps must run on macOS default Bash; Python should rely on the standard library where possible.
* **Safety by default**: Writes restricted to `data/releases/` and `data/pdf/` (already allowlisted by repo); no writes outside repo root.
* **Clear I/O and idempotent runs**:
  - Inputs: `data/repo/repos.txt`
  - Markdown outputs: `data/releases/*.md`
  - PDF outputs: `data/pdf/*.pdf` via `scripts/convert-releases-to-pdf.sh`
  - Re-running converges (overwrite markdown; PDF script removes/rebuilds PDFs in allowlisted output dir).
* **Small changes, fast feedback**: Prefer extending the existing Python script(s) and reusing existing PDF pipeline; provide a quickstart command.

## Project Structure

### Documentation (this feature)

```text
specs/002-repo-releases-harvest/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
scripts/
├── generate-release-stubs.py
└── convert-releases-to-pdf.sh
 
data/
├── repo/repos.txt
├── releases/*.md
└── pdf/*.pdf
 
resources/
└── css/styles-print.css
```

**Structure Decision**: Scripted pipeline (Python fetch/format + Bash PDF conversion) using existing `scripts/` and `data/` directories.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
