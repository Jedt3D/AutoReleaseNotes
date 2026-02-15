# Fission-AI/OpenSpec
Source: https://github.com/Fission-AI/OpenSpec/releases

## v1.1.1 | 2026-01-30T22:56:30Z | release
Link: https://github.com/Fission-AI/OpenSpec/releases/tag/v1.1.1

## What's New in v1.1.1

A quick patch to fix OpenCode command references.

### Fixed

- OpenCode command references - Generated files now use the correct /opsx- hyphen format instead of /opsx: colon format, so commands work properly in OpenCode

## New Contributors

- @webrgp made their first contribution in #626

Full Changelog: v1.1.0...v1.1.1
## v0.18.0 | 2026-01-07T08:38:41Z | release
Link: https://github.com/Fission-AI/OpenSpec/releases/tag/v0.18.0

### Minor Changes

-
8dfd824: Add OPSX experimental workflow commands and enhanced artifact system

New Commands:

- /opsx:ff - Fast-forward through artifact creation, generating all needed artifacts in one go

- /opsx:sync - Sync delta specs from a change to main specs

- /opsx:archive - Archive completed changes with smart sync check

Artifact Workflow Enhancements:

- Schema-aware apply instructions with inline guidance and XML output

- Agent schema selection for experimental artifact workflow

- Per-change schema metadata via .openspec.yaml files

- Agent Skills for experimental artifact workflow

- Instruction loader for template loading and change context

- Restructured schemas as directories with templates

Improvements:

- Enhanced list command with last modified timestamps and sorting

- Change creation utilities for better workflow support

Fixes:

- Normalize paths for cross-platform glob compatibility

- Allow REMOVED requirements when creating new spec files
## v0.10.0 | 2025-10-12T04:07:28Z | release
Link: https://github.com/Fission-AI/OpenSpec/releases/tag/v0.10.0

### Minor Changes

- d7e0ce8: Improve init wizard Enter key behavior to allow proceeding through prompts more naturally
## v0.3.0 | 2025-09-17T13:51:20Z | release
Link: https://github.com/Fission-AI/OpenSpec/releases/tag/v0.3.0

## What's Changed

- docs: correct claude code commands by @TabishB in #67

- feat(cli-init): propose additional agent init flow by @TabishB in #68

- feat(cli): add agents md standard support by @TabishB in #69

- docs: improve README Getting Started section by @TabishB in #70

Full Changelog: v0.2.0...v0.3.0
