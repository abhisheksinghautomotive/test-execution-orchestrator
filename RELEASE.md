# Release Process

This project uses semantic versioning and an automated release workflow.

## Branching Model
- All changes land via PRs into `main`.
- Merging to `main` triggers the release workflow.

## Versioning Rules
- PATCH: changes with `fix:` or non-breaking updates.
- MINOR: changes with `feat:`.
- MAJOR: commits containing `BREAKING CHANGE:` or `type(scope)!:`.

## Automated Release Steps
The GitHub Actions workflow (`.github/workflows/release.yml`) performs:
1. Determine next version based on commit history.
2. Update version in `pyproject.toml`.
3. Regenerate `CHANGELOG.md`.
4. Commit version and changelog updates.
5. Create tag `vX.Y.Z`.
6. Create GitHub Release with changelog contents.
7. Optionally build and publish the Python package.

## Manual Release (Optional)
If you need to trigger a manual release:
1. Create a branch from `main`.
2. Ensure all commits follow Conventional Commits.
3. Merge PR into `main`.
4. The release workflow will run automatically.

## Hotfix Procedure
1. Create branch `hotfix/<short-description>`.
2. Add a `fix:` commit.
3. Merge into `main`.
4. Automatic release will publish a new PATCH version.

## Rollback
1. Revert the problematic commit(s).
2. Merge the revert PR into `main`.
3. Workflow will generate the next patch version with the revert included.

## Artifacts
- GitHub Release: tag, notes, changelog.
- `CHANGELOG.md`: updated every release.
- Python package build: optional, enabled only if registry credentials are configured.

