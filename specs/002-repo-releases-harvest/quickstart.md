# Quickstart: Repository Release Notes Harvest

## Prerequisites

- `python3` available
- `pandoc` installed
- `weasyprint` installed

## Inputs

- Repository list: `data/repo/repos.txt`

## Run

1. Generate/refresh markdown release notes:

```bash
python3 scripts/generate-release-stubs.py
```

2. Convert markdown to PDFs:

```bash
bash scripts/convert-releases-to-pdf.sh
```

## Outputs

- Markdown: `data/releases/*.md`
- PDFs: `data/pdf/*.pdf`

## Expected Behavior

- The markdown generation step overwrites per-repository markdown files.
- The PDF conversion step regenerates PDFs under `data/pdf/`.
- Warnings and errors are printed to stderr; progress messages to stdout.
