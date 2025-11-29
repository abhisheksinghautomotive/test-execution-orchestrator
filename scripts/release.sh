#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=${DRY_RUN:-0}

# helpers
msg() { printf '%s\n' "$*"; }

# ensure required tools are available
for cmd in git poetry git-cliff; do
  command -v "$cmd" >/dev/null 2>&1 || { msg "required command missing: $cmd"; exit 1; }
done

# compute commit range
last_tag=$(git describe --tags --abbrev=0 2>/dev/null || true)
if [ -n "$last_tag" ]; then
  range="$last_tag..HEAD"
else
  range="HEAD"
fi

commits=$(git log "$range" --pretty=%B)
bump="patch"

if echo "$commits" | grep -q -E 'BREAKING CHANGE|!:'; then
  bump="major"
elif echo "$commits" | grep -q '^feat'; then
  bump="minor"
else
  bump="patch"
fi

msg "Last tag: ${last_tag:-<none>}"
msg "Determined bump type: $bump"

# bump via poetry
current_version=$(poetry version -s)
msg "Current version: $current_version"

case "$bump" in
  major) poetry version major ;;
  minor) poetry version minor ;;
  patch) poetry version patch ;;
  *) msg "Unknown bump: $bump"; exit 1 ;;
esac

new_version=$(poetry version -s)
msg "New version: $new_version"

# commit version bump if any
git add pyproject.toml

if git diff --staged --quiet; then
  msg "No version changes to commit"
else
  git commit -m "chore(release): v${new_version} [ci skip]" || true
fi

# tag
tag="v${new_version}"
if git rev-parse "$tag" >/dev/null 2>&1; then
  msg "Tag $tag already exists"
else
  git tag "$tag"
  msg "Created tag $tag"
fi

# generate changelog
git-cliff -o CHANGELOG.md || { msg "git-cliff failed"; exit 1; }
if git diff --name-only | grep -q '^CHANGELOG.md$'; then
  git add CHANGELOG.md
  git commit -m "chore(changelog): update for ${tag} [ci skip]" || true
else
  msg "No changelog changes"
fi

# push changes and tag unless dry-run
if [ "$DRY_RUN" = "1" ]; then
  msg "DRY_RUN=1; skipping push"
else
  git push origin HEAD:main
  git push origin "$tag"
  msg "Pushed commits and tag $tag"
fi

msg "Release script completed"
