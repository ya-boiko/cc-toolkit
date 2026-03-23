---
allowed-tools: Bash(git log:*), Bash(git diff:*), Bash(git branch:*), Bash(mkdir:*), Bash(ls:*), Bash(bash:*), Write, AskUserQuestion
argument-hint: [target-branch] (default: master)
description: Generate PR title and description from current branch to target branch
model: inherit
---

# Generate Pull Request Description

Generate title and description for a pull request from current branch to target branch.

Target branch: $ARGUMENTS (default: master)

## Current Repository State

- Current branch: !`git branch --show-current`
- Target branch: master
- Commits in branch: !`git log master..HEAD --oneline`
- Files changed: !`git diff master..HEAD --stat | tail -20`
- Workspace mode: !`dir=$PWD; while true; do if [ -f "$dir/.workspace.md" ]; then grep -m1 '^mode:' "$dir/.workspace.md" | sed 's/mode:[[:space:]]*//'; break; fi; if [ "$dir" = "$HOME" ] || [ "$dir" = "/" ]; then echo "personal"; break; fi; dir=$(dirname "$dir"); done`

## Instructions

### If workspace mode is `work`

1. Ask the user for the Jira task number (e.g. `PRJ-1234`) and the full Jira task URL.
2. Ask the user if this is a continuation PR (bug fix, follow-up, etc.). If yes, ask for the suffix (e.g. `.2`, `.3`).
3. Analyze all commits and the full diff.
4. Generate title and description using the **work formats** below.

### If workspace mode is `personal`

1. Analyze all commits and the full diff.
2. Generate title and description using the **personal formats** below.

---

## Work Formats

**Title:**
- Main PR: `[PRJ-1234] Description of the feature`
- Continuation PR: `[PRJ-1234.2] Description of the follow-up`
- Max 72 characters total.

**Description:**
```
https://jira.link/to-the-task

Short description of what was done:
- Bullet point 1
- Bullet point 2
```
First line is the Jira URL. Then a blank line. Then 1–2 sentences on the value delivered, followed by a short bullet list. Focus on WHY, not implementation details.

---

## Personal Formats

**Title:** concise description of the feature/fix, max 72 characters.

**Description:**
```
Short description of what was done:
- Bullet point 1
- Bullet point 2
```
1–2 sentences on the purpose, followed by a short bullet list.

---

## Output Format

1. Check if `prs/` directory exists using `ls prs`. If not, create it with `mkdir prs`.
2. Save to: `prs/<source-branch>__to__<target-branch>.md` (replace `/` with `_` in branch names).
3. The first line of the file is the PR title; the rest is the description body.

## Important Notes

- Always read all commits to understand the full context.
- Use `git diff master..HEAD` to see the actual code changes.
- Keep the description concise — help reviewers understand purpose and scope.
