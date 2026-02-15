# Fantasy Software Release Notes

Repository: https://github.com/acme-corp/fantasy-software

This document is **sample data** representing GitHub-style release notes for a single repository.

---

## v2.3.0 — 2026-02-14

### Highlights ✨

- New **Quest Mode** for guided onboarding.
- Faster startup and improved print/PDF output.
- Localization updates: ไทย / 日本語 / English.

### Added

- `fantasy doctor` command to validate configuration before publishing.
- Experimental feature flag `quest.mode=true`.

### Changed

1. Standardized config location to `.fantasy/config.yml`.
2. Improved release note generation for tables and nested lists.

### Fixed

- Fixed a crash when parsing tags like `v2.3.0-rc.1`.
- Fixed Markdown escaping for `[` and `]` in headings.

### Compatibility matrix

| Component | Supported | Notes |
|---|---:|---|
| macOS | ✅ | Apple Silicon + Intel |
| Windows | ✅ | PowerShell 7 recommended |
| Linux | ✅ | Tested on Ubuntu 24.04 |
| GitHub Enterprise | ⚠️ | Requires API base URL config |

### Notes (mixed languages)

- English: If you see `HTTP 403`, check token scopes.
- ไทย: แก้ไขการแสดงผลบันทึกการออกรุ่นให้สวยขึ้น และปรับความเร็วในการสร้างไฟล์ PDF ✅
- 日本語: リリースノートの生成が改善されました。印刷用スタイルもサポートします。

---

## v2.2.1 — 2026-01-30

### Fixed 🐛

- Fixed a regression where `fantasy publish` could hang on slow networks.
- Fixed incorrect compare links when repository URL ends with `.git`.

### Security 🔒

- Bumped HTTP client to improve TLS defaults.

---

## v2.2.0 — 2026-01-12

### Highlights

- Added **release summary table** output mode.

### Added

- `fantasy notes --summary`

Example output:

| Version | Date | Key changes |
|---|---|---|
| v2.2.0 | 2026-01-12 | Summary tables, better Markdown |

### Changed

- `fantasy notes` now groups changes by conventional commit type.

---

## v2.1.0 — 2025-12-05

### Added

- Support for monorepo package selection via `--package <name>`.

### Changed

- Improved heading normalization to avoid duplicate anchors.

### Fixed

- Fixed an issue where empty sections were still emitted.

---

## v2.0.0 — 2025-11-01

### Breaking changes ⚠️

1. Renamed CLI binary from `fsr` to `fantasy`.
2. Moved config from `.releaserc` to `.fantasy/config.yml`.

### Migration

- Update scripts:

  - Old: `fsr notes`
  - New: `fantasy notes`

---

## v1.9.0 — 2025-09-10

### Added

- GitHub Actions helper snippets for release pipelines.

### Fixed

- Fixed formatting for nested bullet lists in GitHub Markdown.

---

## v1.8.0 — 2025-08-01

### Highlights

- Initial support for multiple languages in generated notes. 🌏

### Notes

- ไทย: เพิ่มการรองรับข้อความหลายภาษาในบันทึกการออกรุ่น
- 日本語: 多言語メッセージのサポートを追加しました

---

## v1.7.2 — 2025-07-10

### Fixed

- Fixed date parsing when system locale is not English.

---

## v1.7.0 — 2025-06-20

### Added

- `fantasy init` interactive setup wizard.

### Changed

- Default output file for `fantasy notes` is now `RELEASE_NOTES.md`.

---

## v1.6.0 — 2025-05-02

### Added

- Improved linkification for PR references like `(#123)`.

### Contributors

- @octo-kai
- @octo-nok
