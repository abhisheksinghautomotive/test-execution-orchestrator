# Conventional Commits Guide

This project uses the Conventional Commits specification to ensure
consistent commit messages, automated version bumping, and clean changelogs.

## Format

Each commit message must follow:

<type>(optional scope): <short description>

Examples:
- feat(api): add reservation endpoint
- fix(worker): retry logic for DLQ
- chore: update dependencies
- docs: add usage guide
- refactor(queue): simplify task envelope
- perf(worker): reduce startup latency

## Types

- feat: a new feature
- fix: a bug fix
- docs: documentation changes
- style: non-functional formatting changes
- refactor: code change not fixing a bug or adding a feature
- perf: performance improvement
- test: test-related changes
- chore: maintenance tasks (build, config, tooling)
- ci: CI/CD pipeline changes
- revert: revert a previous commit

## Breaking Changes

Use one of:
- Add "BREAKING CHANGE:" in the commit body
- Add an exclamation mark after type/scope, e.g.:

feat(api)!: updated reservation contract

Any of the above triggers a MAJOR version bump.

## Scope (optional)

Use scope to indicate subsystem:
- api
- scheduler
- worker
- adapters
- queue
- cli
- infra
- docs

Example:
fix(scheduler): correct bench allocation logic

## Rules

- Use lowercase type and scope.
- Commit subject should be imperative and short.
- Body is optional but recommended for complex changes.
- References to issues/PRs may be added at the end.

## Examples

feat(cli): add run command  
fix(worker): handle missing artifacts gracefully  
docs: update architecture overview  
refactor(api): extract validation module  
perf(queue): reduce lock contention  
ci: add semantic release workflow  
revert: revert feat(cli) due to regression
