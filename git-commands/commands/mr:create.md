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
3. **If no files found** — tell the user to run `/mr:describe` first.
4. **If one file** — use it.
5. **If multiple files** — show a numbered list with: filename, target branch (parsed from `__to__<target>.md`), and file modification date (`ls -l`). Ask the user to pick one.
6. Read the chosen file. The first line is the MR title, the rest is the description body.
7. Parse the target branch from the filename: `<source>__to__<target>.md` → target is after `__to__` and before `.md`.
8. Count commits in the branch ahead of target:
   ```bash
   git fetch origin <target> --quiet 2>/dev/null || true
   git log origin/<target>..HEAD --pretty=format:"%s" 2>/dev/null \
     || git log <target>..HEAD --pretty=format:"%s"
   ```
9. **If 2 or more commits** — generate a squash commit message (see format below) and append a `## Squash commit message` section to the description body. The section content is the squash message wrapped in a fenced code block (use ``` fences) so it copies cleanly. Whoever merges the MR copies this block into GitLab's squash-message field (or passes it via `glab mr merge --squash --squash-message "..."`).

   **If only 1 commit** — skip this step. GitLab will use that commit's message at squash time.
10. Push the current branch: `git push -u origin <current-branch>`
11. Create the MR:

```bash
glab mr create --title "<title>" --description "<description>" --target-branch <target> --no-editor --push
```

12. Show the MR URL from glab output.

## Squash Commit Message Format

- **work**: `[PRJ-1234] feat: add Easter egg to the header`
- **personal**: `feat: add Easter egg to the header`

Rules:
- Keep the `[TASK-NUMBER]` prefix from the title if present (work mode)
- Choose the type (`feat`, `fix`, `refactor`, `docs`, `chore`, `test`) from the PR content
- First line (subject): lowercase, imperative mood, max 72 characters
- Optional body: bullet points with key details, separated from subject by a blank line. Use the individual commit subjects from step 8 as the source of truth — they describe what each commit did.
- Descriptive enough to understand the change without reading the PR

## Important

- Always push before creating the MR.
- `glab mr create` does not support `--squash-message` (that flag exists only on `glab mr merge`). The squash message is communicated via the description section and applied at merge time.
- If `glab mr create` fails, show the error and suggest possible fixes.
- Do NOT modify the PR description file in `prs/` — append the squash section only to the `--description` argument passed to `glab`.
