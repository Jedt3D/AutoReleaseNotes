#!/usr/bin/env bash
set -euo pipefail

RELEASES_DIR="data/releases"
OUT_DIR="data/pdf"
CSS_FILE="resources/css/styles-print.css"

remove_existing_pdf() {
  local out_pdf="$1"

  if [[ -f "${out_pdf}" ]]; then
    if [[ "${out_pdf}" == "${OUT_DIR}/"*.pdf ]]; then
      echo "Removing existing PDF: ${out_pdf}"
      rm -f "${out_pdf}"
    else
      echo "Error: refusing to delete unexpected path: ${out_pdf}" >&2
      exit 1
    fi
  fi
}

get_highlight_args() {
  if [[ "${PANDOC_SYNTAX_HIGHLIGHTING:-1}" != "1" ]]; then
    return 0
  fi

  if pandoc --help 2>/dev/null | grep -q -- '--syntax-highlighting'; then
    echo "--syntax-highlighting"
    return 0
  fi

  if pandoc --help 2>/dev/null | grep -q -- '--highlight-style'; then
    echo "--highlight-style"
    echo "pygments"
    return 0
  fi
}

convert_one() {
  local md="$1"
  local out="$2"
  local -a highlight_args

  while IFS= read -r line; do
    highlight_args+=("${line}")
  done < <(get_highlight_args || true)

  if (( ${#highlight_args[@]} > 0 )); then
    if pandoc "${md}" \
      --from=gfm \
      "${highlight_args[@]}" \
      --pdf-engine=weasyprint \
      --css "${CSS_FILE}" \
      -o "${out}"; then
      return 0
    fi

    echo "Warning: pandoc conversion with syntax highlighting failed; retrying without highlighting." >&2
  fi

  pandoc "${md}" \
    --from=gfm \
    --pdf-engine=weasyprint \
    --css "${CSS_FILE}" \
    -o "${out}"
}

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

  remove_existing_pdf "${out}"
  echo "Converting: ${md} -> ${out}"
  convert_one "${md}" "${out}"
done

echo "Done. PDFs are in ${OUT_DIR}"
