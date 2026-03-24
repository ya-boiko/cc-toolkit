---
allowed-tools: Bash(git:*), Bash(glab:*), Bash(ls:*), Bash(python3:*), Read, Glob
description: "Create GitLab merge request from a PR description file in prs/"
argument-hint: ""
model: inherit
---

# Create GitLab Merge Request

Create a merge request in GitLab using a previously generated PR description from `prs/`.

## Current State

- Workspace mode: !`python3 -c "exec('import os,sys\nd=os.getcwd()\nh=os.path.expanduser(chr(126))\nwhile True:\n f=os.path.join(d,\".workspace.md\")\n if os.path.isfile(f):\n  for line in open(f):\n   if line.startswith(\"mode:\"):\n    print(line.split(\":\",1)[1].strip());sys.exit()\n  break\n if d==h or d==\"/\":break\n d=os.path.dirname(d)\nprint(\"personal\")')"`

## Steps

1. Get the current branch: `git branch --show-current`
2. Find matching files in `prs/` that start with the current branch name (replace `/` with `_` when matching). Use `ls prs/` and filter by prefix.
3. **If no files found** — tell the user to run `/generate-pr` first.
4. **If one file** — use it.
5. **If multiple files** — show a numbered list with: filename, target branch (parsed from `__to__<target>.md`), and file modification date (`ls -l`). Ask the user to pick one.
6. Read the chosen file. The first line is the MR title, the rest is the description body.
7. Parse the target branch from the filename: `<source>__to__<target>.md` → target is after `__to__` and before `.md`.
8. Generate the squash commit message from the MR title and content (see format below).
9. Push the current branch: `git push -u origin <current-branch>`
10. Create the MR:

```bash
glab mr create --title "<title>" --description "<description>" --squash-message "<squash-message>" --target-branch <target> --no-editor --push
```

11. Show the MR URL from glab output.

## Squash Commit Message Format

- **work**: `[PRJ-1234] feat: add Easter egg to the header`
- **personal**: `feat: add Easter egg to the header`

Rules:
- Keep the `[TASK-NUMBER]` prefix from the title if present (work mode)
- Choose the type (`feat`, `fix`, `refactor`, `docs`, `chore`, `test`) from the PR content
- First line (subject): lowercase, imperative mood, max 72 characters
- Optional body: bullet points with key details, separated from subject by a blank line
- Descriptive enough to understand the change without reading the PR

## Important

- Always push before creating the MR.
- If `glab mr create` fails, show the error and suggest possible fixes.
- Do NOT modify the PR description file.
