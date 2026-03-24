---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*), AskUserQuestion
argument-hint: [message] | --no-verify | --amend
description: Create well-formatted commits with conventional commit format
model: inherit
---

# Smart Git Commit

Create well-formatted commit: $ARGUMENTS

## Current Repository State

- Git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Staged changes: !`git diff --cached --stat`
- Unstaged changes: !`git diff --stat`
- Recent commits: !`git log --oneline -5`
- Workspace mode: !`dir=$PWD; while true; do if [ -f "$dir/.workspace.md" ]; then grep -m1 '^mode:' "$dir/.workspace.md" | sed 's/mode:[[:space:]]*//'; break; fi; if [ "$dir" = "$HOME" ] || [ "$dir" = "/" ]; then echo "personal"; break; fi; dir=$(dirname "$dir"); done`

## What This Command Does

1. **If workspace mode is `work`**: ask the user for the Jira task number (e.g. `PRJ-1234`).
2. Unless specified with `--no-verify`, automatically runs pre-commit checks:
   - `pnpm lint` to ensure code quality
   - `pnpm build` to verify the build succeeds
   - `pnpm generate:docs` to update documentation
3. Checks which files are staged with `git status`
4. If 0 files are staged, automatically adds all modified and new files with `git add`
5. Performs a `git diff` to understand what changes are being committed
6. Analyzes the diff to determine if multiple distinct logical changes are present
7. If multiple distinct changes are detected, suggests breaking the commit into multiple smaller commits
8. For each commit (or the single commit if not split), creates a commit message using the format below

## Commit Message Format

- **work mode**: `[PRJ-1234] feat: description`
- **personal mode**: `feat: description`

Type is one of: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`.
Description: present tense, imperative mood. Max 72 characters total.

## Best Practices for Commits

- **Verify before committing**: Ensure code is linted, builds correctly, and documentation is updated
- **Atomic commits**: Each commit should contain related changes that serve a single purpose
- **Split large changes**: If changes touch multiple concerns, split them into separate commits
- **Separate low-cognitive from high-cognitive changes**: Rename/lint/docs/dead code removal in separate commits from business logic — helps reviewers focus
- **Concise first line**: Keep the first line under 72 characters

## Guidelines for Splitting Commits

When analyzing the diff, consider splitting commits based on these criteria:

1. **Different concerns**: Changes to unrelated parts of the codebase
2. **Different types of changes**: Mixing features, fixes, refactoring, etc.
3. **File patterns**: Changes to different types of files (e.g., source code vs documentation)
4. **Logical grouping**: Changes that would be easier to understand or review separately
5. **Size**: Very large changes that would be clearer if broken down

## Examples

Good commit messages (work mode):
- `[PRJ-1234] feat: add user authentication system`
- `[PRJ-1234] fix: resolve memory leak in rendering process`
- `[PRJ-1234] refactor: simplify error handling logic in parser`

Good commit messages (personal mode):
- `feat: add user authentication system`
- `fix: resolve memory leak in rendering process`
- `docs: update API documentation with new endpoints`

Example of splitting commits (low-cognitive first, then business logic):
- First commit: `[PRJ-1234] refactor: rename UserService methods to snake_case`
- Second commit: `[PRJ-1234] fix: resolve linting issues in new code`
- Third commit: `[PRJ-1234] feat: add voice sample generation for speakers`

## Command Options

- `--no-verify`: Skip running the pre-commit checks (lint, build, generate:docs)

## Important Notes

- By default, pre-commit checks (`pnpm lint`, `pnpm build`, `pnpm generate:docs`) will run to ensure code quality
- If these checks fail, you'll be asked if you want to proceed with the commit anyway or fix the issues first
- If specific files are already staged, the command will only commit those files
- If no files are staged, it will automatically stage all modified and new files
- The commit message will be constructed based on the changes detected
- Before committing, the command will review the diff to identify if multiple commits would be more appropriate
- If suggesting multiple commits, it will help you stage and commit the changes separately
- Always reviews the commit diff to ensure the message matches the changes
