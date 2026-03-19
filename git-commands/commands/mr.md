---
allowed-tools: Bash(git:*), Bash(glab:*), Bash(ls:*), Read, Glob
description: "Create GitLab merge request from a PR description file in prs/"
argument-hint: ""
model: inherit
---

# Create GitLab Merge Request

Create a merge request in GitLab using a previously generated PR description from `prs/`.

## Steps

1. Get the current branch: `git branch --show-current`
2. Find matching files in `prs/` that start with the current branch name (replace `/` with `_` when matching). Use `ls prs/` and filter by prefix.
3. **If no files found** — tell the user to run `/generate-pr` first.
4. **If one file** — use it.
5. **If multiple files** — show a numbered list with: filename, target branch (parsed from `__to__<target>.md`), and file modification date (`ls -l`). Ask the user to pick one.
6. Read the chosen file. The first line is the MR title, the rest is the description body.
7. Parse the target branch from the filename: `<source>__to__<target>.md` → target is after `__to__` and before `.md`.
8. Push the current branch: `git push -u origin <current-branch>`
9. Create the MR:

```bash
glab mr create --title "<title>" --description "<description>" --target-branch <target> --no-editor --push
```

10. Show the MR URL from glab output.

## Important

- Always push before creating the MR.
- If `glab mr create` fails, show the error and suggest possible fixes.
- Do NOT modify the PR description file.
