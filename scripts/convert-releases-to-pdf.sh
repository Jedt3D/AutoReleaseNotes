#!/usr/bin/env bash
set -euo pipefail

RELEASES_DIR="data/releases"
OUT_DIR="data/pdf"
CSS_FILE="resources/css/styles-print.css"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "Error: pandoc is not installed. Install it first (e.g. brew install pandoc)." >&2
  exit 1
fi

if ! command -v weasyprint >/dev/null 2>&1; then
  echo "Error: weasyprint is not installed. Install it first (e.g. brew install weasyprint)." >&2
  exit 1
fi

if [[ ! -d "${RELEASES_DIR}" ]]; then
  echo "Error: releases directory not found: ${RELEASES_DIR}" >&2
  exit 1
fi

if [[ ! -f "${CSS_FILE}" ]]; then
  echo "Error: CSS file not found: ${CSS_FILE}" >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"

shopt -s nullglob
md_files=("${RELEASES_DIR}"/*.md)
if (( ${#md_files[@]} == 0 )); then
  echo "No .md files found in ${RELEASES_DIR}" >&2
  exit 0
fi

for md in "${md_files[@]}"; do
  base="$(basename "${md}" .md)"
  out="${OUT_DIR}/${base}.pdf"

  echo "Converting: ${md} -> ${out}"
  pandoc "${md}" \
    --from=gfm \
    --pdf-engine=weasyprint \
    --css "${CSS_FILE}" \
    -o "${out}"
done

echo "Done. PDFs are in ${OUT_DIR}"
