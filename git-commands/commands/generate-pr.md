---
allowed-tools: Bash(git log:*), Bash(git diff:*), Bash(git branch:*), Bash(mkdir:*), Bash(ls:*), Write
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

## Instructions

1. Analyze all commits between the current branch and target branch
2. Review the diff to understand the full scope of changes
3. Generate a concise PR title (max 72 characters)
4. Generate a structured PR description with the following sections:
   - **Summary**: Brief overview of what this PR does (2-3 sentences)
   - **Changes**: Bullet list of main changes grouped by category

## Output Format

1. Check if `prs/` directory exists using `ls prs`. If the command fails (directory doesn't exist), create it with `mkdir prs`.
2. Save the generated PR content to file with naming pattern: `prs/<source-branch>__to__<target-branch>.md`
   - Example: `prs/bug-fix__to__master.md` or `prs/PROK-8563_voice-samples__to__develop.md`
   - Replace `/` in branch names with `_` to avoid path issues

File structure:

```markdown
<PR Title>

## Summary

<Brief description of the PR purpose>

## Changes

### <Category 1>
- Change 1
- Change 2

### <Category 2>
- Change 3
```

## Guidelines

- **Title**: Should be concise and describe the main purpose (e.g., "Add voice sample generation for speakers")
- **Summary**: Focus on WHY these changes were made, not just WHAT changed
- **Changes**: Group related changes together (e.g., "Domain Model", "API Endpoints", "Tests")

## Important Notes

- Always read all commits to understand the full context
- Use `git diff master..HEAD` to see the actual code changes
- Do NOT include implementation details in the summary - keep it high-level
- The PR description should help reviewers understand the purpose and scope
