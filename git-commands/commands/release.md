---
allowed-tools: Bash(git branch:*), Bash(git status:*), Bash(git log:*), Bash(git describe:*), Bash(git tag:*), Bash(git remote:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(git reset:*), Bash(gh:*), Bash(glab:*), Bash(python3:*), Bash(find:*), Bash(mktemp:*), Bash(rm:*), AskUserQuestion
argument-hint: [patch|minor|major]
description: Create a release — version bump, changelog, tag, and publish to GitHub or GitLab
model: inherit
---

# Create Release

Automate the full release flow: version bump, changelog, git tag, and publish to GitHub or GitLab.

Version type argument: $ARGUMENTS

## Current State

- Workspace mode: !`dir=$PWD; while true; do if [ -f "$dir/.workspace.md" ]; then grep -m1 '^mode:' "$dir/.workspace.md" | sed 's/mode:[[:space:]]*//'; break; fi; if [ "$dir" = "$HOME" ] || [ "$dir" = "/" ]; then echo "personal"; break; fi; dir=$(dirname "$dir"); done`
- Current branch: !`git branch --show-current`
- Git status: !`git status --porcelain`
- Last tag: !`git describe --tags --abbrev=0 2>/dev/null || echo "none"`
- Remote URL: !`git remote get-url origin 2>/dev/null || echo "none"`

## Instructions

### Pre-flight checks

Before doing anything:

1. If `Current branch` is empty (detached HEAD) — abort with: "Cannot create a release from a detached HEAD. Please check out a named branch first."
2. If `Git status` is non-empty — warn the user: "There are uncommitted changes in the working tree." Ask whether to proceed or stop.

### Step 1 — Detect platform

Parse the remote URL:
- contains `github.com` → platform is **GitHub**, use `gh release create`
- contains `gitlab.com` → platform is **GitLab**, use `glab release create`
- anything else → ask: "Detected unknown host `<host>`. Is this GitHub or GitLab?"

### Step 2 — Determine version

Read the last tag from Current State (use `v0.0.0` if "none").

Parse SemVer `vMAJOR.MINOR.PATCH` and propose the three next versions:
- patch: `vMAJOR.MINOR.(PATCH+1)`
- minor: `vMAJOR.(MINOR+1).0`
- major: `v(MAJOR+1).0.0`

If `$ARGUMENTS` contains `patch`, `minor`, or `major` — pre-select that type. Otherwise ask the user which to use.

Check if the proposed version tag already exists: `git tag -l <proposed-version>`. If it does — abort with: "Tag <version> already exists. Delete it first with `git tag -d <version>` or choose a different version."

Ask the user to confirm: "Release version will be `<version>`. Confirm?"

### Step 3 — Generate changelog

Run: `git log <last-tag>..HEAD --oneline` (use `git log --oneline` if no previous tags).

If no commits returned — warn: "No commits since last tag." Ask whether to proceed anyway.

Filter out merge commits (lines starting with "Merge").

Parse each commit subject:
- work mode regex: `^\[([A-Z]+-\d+)\]\s+(\w+):\s+(.+)$` → groups: task, type, description
- personal mode regex: `^(\w+):\s+(.+)$` → groups: type, description
- no match → type = "other", description = full subject

Group into sections:
- **Added** — type `feat`
- **Fixed** — type `fix`
- **Other** — everything else

Format changelog (shown to user, includes version header):

```
## <version>

### Added
- <description> [TASK]    ← work mode only

### Fixed
- <description>

### Other
- <description>
```

Omit empty sections. In personal mode, omit task numbers.

Show the changelog to the user and ask: "Edit the changelog? (paste new text, or press Enter to confirm)"
Accept the user's edited version if provided.

### Step 4 — Bump version files

Search the project root for: `package.json`, `pyproject.toml`, `Cargo.toml`.

For each found file, run:
```bash
python3 "$(find ~/.claude -name "bump_version.py" 2>/dev/null | head -1)" <file-path> <version-without-v>
```
(e.g. for `v1.2.0`, pass `1.2.0`)

If a file is not found — skip silently. If the script exits non-zero — show the error and abort.

### Step 5 — Version bump commit

**work mode:** Run `git log <last-tag>..HEAD --oneline` and extract all unique task IDs matching `^\[([A-Z]+-\d+)\]`. Show the list to the user:

> "Tasks included in this release:
> - [PRJ-1] add Easter egg to header
> - [PRJ-2] fix snowflake animation
>
> Type IDs to remove (comma-separated), add new ones, or press Enter to confirm."

Build the confirmed task list.

**Commit message:**

*work mode:*
```
chore: bump version to <version>

[PRJ-1] <first commit description>
[PRJ-2] <second commit description>
```

*personal mode:*
```
chore: bump version to <version>
```

Stage version files and commit:
```bash
git add <only the version files that were actually found and updated in Step 4>
git commit -m "<message>"
```

### Step 6 — Tag

```bash
git tag -a <version> -m "<version>"
```

### Step 7 — Push

```bash
git push origin HEAD && git push origin <version>
```

If this fails — inform the user that the tag was NOT pushed. Print rollback instructions:
```
To undo the local commit and tag:
  git tag -d <version>
  git reset --hard HEAD~1
```
Then abort.

### Step 8 — Create release

Write the changelog body (without the `## <version>` header) to a temp file:
```bash
tmp=$(mktemp)
cat > "$tmp" << 'CHANGELOG'
<changelog body without version header>
CHANGELOG
```

**GitHub:**
```bash
gh release create <version> --title "<version>" --notes-file "$tmp"
```

**GitLab:**
```bash
glab release create <version> --name "<version>" --notes-file "$tmp"
```

If the release creation command **succeeds** — clean up and show the URL:
```bash
rm "$tmp"
```

If the release creation command **fails** — do NOT delete the temp file. Inform the user that the tag is already pushed, and print the exact retry command referencing the temp file path:
```bash
# GitHub retry:
gh release create <version> --title "<version>" --notes-file "$tmp"

# GitLab retry:
glab release create <version> --name "<version>" --notes-file "$tmp"
```
