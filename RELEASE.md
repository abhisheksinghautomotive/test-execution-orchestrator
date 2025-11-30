# Release Process

This project uses **semantic versioning** and a **fully automated two-stage release workflow**.

## Overview for Developers

When you merge a feature PR into `main`, the release process happens automatically in two stages:

1. **Stage 1 - Release PR Creation** (`.github/workflows/release.yml`)
   - Triggers on any merge to `main` (except release commits)
   - Calculates next version from commit history
   - Updates `pyproject.toml` and `CHANGELOG.md`
   - Creates a release PR with these changes

2. **Stage 2 - Tag & GitHub Release** (`.github/workflows/post-merge-release.yml`)
   - Triggers when the release PR merges
   - Creates the version tag (e.g., `v0.2.0`)
   - Creates the GitHub Release with changelog

**You don't need to do anything manually** — just merge your feature PRs using conventional commits.

## Branching Model

- **All changes** land via PRs into `main`
- **Branch protection** requires PRs (no direct pushes to `main`)
- **Feature branches**: `feat/<description>`, `fix/<description>`, etc.

## Versioning Rules (Conventional Commits)

Your commit messages determine the version bump:

- **PATCH** (0.0.X): `fix:`, `docs:`, `chore:`, `refactor:`, `perf:`
- **MINOR** (0.X.0): `feat:`
- **MAJOR** (X.0.0): Any commit with `BREAKING CHANGE:` in body or `!` after type (e.g., `feat!:`)

### ⚠️ IMPORTANT: When Releases Are Triggered

**Every merge to `main` triggers a release** unless the commit message starts with `chore(release):`.

#### Commits that TRIGGER releases:
```bash
feat(api): add new endpoint           # ✅ Creates MINOR release
fix(worker): handle timeout           # ✅ Creates PATCH release
docs: update README                   # ✅ Creates PATCH release
ci(pr-checks): add workflow          # ✅ Creates PATCH release
refactor(core): simplify logic       # ✅ Creates PATCH release
```

#### Commits that DO NOT trigger releases:
```bash
chore(release): v0.2.1               # ❌ No release (release commit itself)
```

### 💡 How to Avoid Triggering a Release

If you want to merge changes WITHOUT triggering a release:

1. **Accumulate multiple features** - Keep working in feature branches, only merge when ready to release
2. **Use draft PRs** - Mark PRs as draft until ready to release
3. **Manual intervention** - Close the auto-generated release PR if you don't want that release

**Note:** There's currently no commit prefix that merges to main without triggering a release workflow. Every non-release merge initiates the release process.

### Example Commits

```bash
# PATCH bump (triggered immediately on merge)
git commit -m "fix(api): correct timeout handling"

# MINOR bump (triggered immediately on merge)
git commit -m "feat(worker): add retry mechanism"

# MAJOR bump (triggered immediately on merge)
git commit -m "feat!: change API response format"
# or
git commit -m "feat: new API

BREAKING CHANGE: response structure changed"
```

## Standard Release Workflow

### 1. Create Feature Branch

```bash
git checkout -b feat/my-feature
# Make changes
git add .
git commit -m "feat(api): add new endpoint"
git push -u origin feat/my-feature
```

### 2. Open Pull Request

```bash
gh pr create --title "feat(api): add new endpoint" \
  --body "Adds endpoint for X functionality" \
  --base main
```

### 3. Merge Feature PR

⚠️ **Important:** Merging to `main` immediately triggers a release workflow!

After approval and CI passes, merge the PR. **Stage 1** triggers automatically:
- ✅ Release workflow calculates version (e.g., `v0.2.0`)
- ✅ Creates release branch `release/v0.2.0`
- ✅ Opens release PR with version bump

**Options if you don't want to release yet:**
- Keep the PR as draft until ready
- Close the auto-generated release PR (you can create it manually later)
- Wait to merge until you have multiple features ready

### 4. Merge Release PR

When ready to release, merge the release PR. **Stage 2** triggers automatically:
- ✅ Post-merge workflow creates tag `v0.2.0`
- ✅ Creates GitHub Release with changelog
- ✅ No new release PR is created (loop prevention)

### 5. Done! 🎉

Your feature is released. Check the [Releases page](https://github.com/abhisheksinghautomotive/test-execution-orchestrator/releases).

## Loop Prevention

**How we prevent infinite loops:**

- Release commits have `chore(release):` prefix
- The release workflow **skips** if commit message contains `chore(release):`
- The post-merge workflow **only runs** if commit message contains `chore(release):`
- This ensures release PRs don't trigger new release PRs

## Hotfix Procedure

For urgent fixes:

```bash
# 1. Create hotfix branch
git checkout -b fix/critical-bug

# 2. Fix and commit with fix: prefix (PATCH bump)
git commit -m "fix(api): prevent null pointer exception"

# 3. Create PR and merge
gh pr create --title "fix(api): prevent null pointer exception" \
  --body "Fixes #123" --base main

# 4. Merge PR → automatic PATCH release
```

## Rollback

To rollback a problematic release:

```bash
# 1. Revert the commit
git revert <commit-hash>

# 2. Push revert
git commit -m "revert: rollback feature X due to issue Y"

# 3. Merge → automatic release with revert
```

## Artifacts Generated

Each release creates:
- **Git tag**: `vX.Y.Z`
- **GitHub Release**: With changelog notes
- **CHANGELOG.md**: Updated in repository
- **Python package**: (optional, if PyPI credentials configured)

## Troubleshooting

### Release PR created but I don't want to release yet
- **Close the release PR** - It won't create a tag/release until merged
- **Keep the PR open** - You can merge multiple features, then merge the release PR later
- **Note:** The release PR will need manual updates if you merge more features before releasing

### Release PR not created after feature merge
- Check commit message follows conventional commits format
- Verify commit doesn't contain `chore(release):` (should only be in release commits)
- Check [Actions tab](https://github.com/abhisheksinghautomotive/test-execution-orchestrator/actions) for workflow runs

### Tag/Release not created after release PR merge
- Verify release PR commit message contains `chore(release):`
- Check `pyproject.toml` was modified in the release PR
- Check [Actions tab](https://github.com/abhisheksinghautomotive/test-execution-orchestrator/actions) for post-merge workflow

### Multiple release PRs created
- Should not happen due to loop prevention
- If it does, check that release commits have `chore(release):` prefix

### I merged by accident and triggered a release
- **Before merging release PR:** Simply close the release PR - no tag/release created yet
- **After merging release PR:** Tag and release are created; you can delete the release and tag manually if needed

## Manual Version Bump (Not Recommended)

If you need to manually bump version (rare):

```bash
# Edit pyproject.toml and __init__.py manually
poetry version minor  # or major, patch

# Commit with release prefix
git commit -m "chore(release): v0.3.0"

# This will trigger tag/release creation but NOT a new release PR
```
