# Data Model: Repository Release Notes Harvest

## Entities

### Repository Source

- **Represents**: One repository reference derived from a line in `data/repo/repos.txt`.
- **Fields**:
  - `raw_ref`: Original text line (after trimming/comment removal).
  - `owner`: Repository owner/organization identifier.
  - `repo`: Repository name identifier.
  - `normalized_id`: Canonical identifier `owner/repo`.
  - `releases_url`: Canonical releases page URL derived from repository URL.

### Release Entry

- **Represents**: One release-like item shown on the repository’s `/releases` page.
- **Fields**:
  - `release_id`: Version label or tag as presented.
  - `published_at`: Publication date/time when present (optional).
  - `description`: Human-readable release description text.
  - `link`: Canonical link back to the release entry.
  - `kind`: One of `draft`, `prerelease`, `release` when detectable; otherwise `unknown`.

### Repository Release Document

- **Represents**: The generated markdown artifact for a repository.
- **Fields**:
  - `repo`: Reference to Repository Source.
  - `entries`: Up to 10 Release Entries, ordered newest-to-oldest.
  - `output_path`: `data/releases/<owner>__<repo>.md`.

### Run Report

- **Represents**: Summary of a single run.
- **Fields**:
  - `processed_count`: Total input lines considered.
  - `parsed_count`: Repositories parsed successfully.
  - `reachable_count`: Repositories deemed reachable.
  - `success_count`: Repositories written successfully.
  - `warning_count`: Repositories with warnings.
  - `failure_count`: Repositories that failed.
  - `warnings`: List of warning records (repo + reason + suggestion).
  - `errors`: List of error records (repo + reason + suggestion).

## Validation & Constraints

- Repository entries are de-duplicated by `normalized_id` case-insensitively.
- Output filenames are stable: `<owner>__<repo>.md`.
- Output content is deterministic for identical fetched inputs.
- Runs overwrite existing markdown files under `data/releases/`.
