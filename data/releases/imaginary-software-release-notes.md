# Imaginary Software Release Notes

Repository: https://github.com/acme-corp/imaginary-software

This document is **sample data** representing GitHub-style release notes for a single repository.

---

## v1.9.0 — 2026-02-10

### Highlights

- Added **Policy-as-Code** checks for release pipelines.
- Reduced cold-start time by **35%** for the CLI.

### Added

- New `release doctor` command to validate local environment before publishing.
- Support for `--output json` in `release status`.

### Changed

1. Updated default branch detection to prefer `main`, then `master`.
2. Standardized timestamps to RFC 3339 in logs.

### Fixed

- Fixed an issue where changelog generation could skip the first commit after a tag.
- Fixed Windows path normalization when reading `.releaserc`.

### Upgrade notes

- If you rely on legacy `RELEASE_TOKEN`, migrate to `GITHUB_TOKEN` or `IMAGINARY_TOKEN`.

---

## v1.8.2 — 2026-01-22

### Fixed

- Fixed a regression in v1.8.1 where `release publish` could hang when Git remotes required SSO re-auth.
- Fixed Markdown rendering when release notes contained nested lists.

### Security

- Bumped dependency `minimatch` to address a high-severity ReDoS advisory.

---

## v1.8.1 — 2026-01-09

### Changed

- Improved error messages when GitHub API rate limits are hit.

### Fixed

- Fixed tag sorting for versions containing pre-release identifiers (e.g., `1.8.1-rc.1`).

---

## v1.8.0 — 2025-12-18

### Highlights

- Introduced **Release Channels**: `stable`, `beta`, and `nightly`.

### Added

- `release channel set <name>`
- `release channel list`

### Changed

- Release note templates now support simple variables:

  - `${version}`
  - `${date}`
  - `${compare_url}`

### Example

```md
## v${version} — ${date}

### Changed

- See full diff: ${compare_url}
```

---

## v1.7.0 — 2025-11-21

### Added

- Support for monorepo “package mode” with `--package <name>`.
- New configuration file: `.imaginary/release.yml`.

### Changed

- `release notes` now groups commits by conventional commit type.

### Fixed

- Fixed an edge case where empty sections (e.g., no `Fixed`) were still emitted.

### Known issues

- `release publish` may fail on very large repositories (>100k commits). Workaround: use `release notes --since <tag>`.

---

## v1.6.3 — 2025-10-30

### Fixed

- Fixed incorrect comparison links when repository is a GitHub Enterprise instance.
- Fixed trimming behavior that removed trailing backticks in inline code.

---

## v1.6.2 — 2025-10-11

### Fixed

- Fixed parsing for release titles that include emojis or non-ASCII characters.

### Changed

- Normalized line endings to `\n` in generated Markdown output.

---

## v1.6.0 — 2025-09-15

### Highlights

- New `release init` interactive setup.

### Added

- Wizard for creating a minimal config:

  1. Choose versioning strategy (SemVer recommended).
  2. Choose changelog style (Keep a Changelog or GitHub style).
  3. Validate GitHub auth.

### Changed

- Default output file for `release notes` is now `RELEASE_NOTES.md`.

---

## v1.5.0 — 2025-08-07

### Added

- Support for linking PRs automatically when commits contain `(#123)`.
- `release notes --include-authors` to attribute changes.

### Fixed

- Fixed duplicate entries when merge commits included multiple conventional commits.

### Contributors

- @octo-alice
- @octo-bob

---

## v1.4.0 — 2025-07-01

### Highlights

- Performance improvements to changelog generation.

### Changed

- Switched the default grouping order to:

  1. Added
  2. Changed
  3. Fixed
  4. Security

### Fixed

- Fixed a case where `release notes` produced invalid Markdown when a bullet contained a colon:

  - Example: `Fix: handle URLs` would render as a broken list in some renderers.

### Links

- Full Changelog: https://github.com/acme-corp/imaginary-software/compare/v1.3.0...v1.4.0
