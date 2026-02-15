# Contracts: CLI / Script Interfaces

This feature is implemented as a scripted pipeline. Contracts below define expected inputs, outputs, and observable behaviors.

## Contract 1: Repository List Input

- **Source of truth**: `data/repo/repos.txt`
- **Accepted line formats**:
  - `owner/repo`
  - `https://github.com/owner/repo`
  - `https://github.com/owner/repo.git`
- **Comments**:
  - Lines starting with `#` are ignored.
  - Blank lines are ignored.

## Contract 2: Markdown Generation Script

- **Command**:

```bash
python3 scripts/generate-release-stubs.py
```

- **Reads**:
  - `data/repo/repos.txt`

- **Writes**:
  - `data/releases/<owner>__<repo>.md` (overwritten if present)

- **Side effects**:
  - Must not write outside repository root.
  - Must not delete files outside allowlisted output directories.

- **Observability**:
  - Progress messages to stdout.
  - Warnings/errors to stderr.

## Contract 3: PDF Conversion Script

- **Command**:

```bash
bash scripts/convert-releases-to-pdf.sh
```

- **Reads**:
  - `data/releases/*.md`
  - `resources/css/styles-print.css`

- **Writes**:
  - `data/pdf/*.pdf`

- **Failure behavior**:
  - If `pandoc` or `weasyprint` is missing, fails early with install hint.
  - Refuses to delete unexpected paths (safety guard).
