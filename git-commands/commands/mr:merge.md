---
allowed-tools: Bash(git:*), Bash(glab:*), Bash(jq:*), Read, AskUserQuestion
description: "Squash-merge the current branch's open GitLab MR, applying the squash-message section from the MR description"
argument-hint: ""
model: inherit
---

# Merge GitLab Merge Request (squash)

Counterpart of `/mr:create`. `/mr:create` writes the squash commit message into the MR description (under `## Squash commit message`); `/mr:merge` reads it back and passes it via `glab mr merge --squash --squash-message`.

## Steps

1. Get the current branch: `git branch --show-current`.

2. Fetch the open MR for the current branch:

   ```bash
   glab mr view --output json
   ```

   Parse with `jq`. Capture: `iid`, `title`, `web_url`, `description`, `state`, `target_branch`.
   - If no MR found — tell the user to run `/mr:create` first and stop.
   - If `state != "opened"` — tell the user the MR is `<state>` and stop.

3. Count the commits in the MR:

   ```bash
   glab api "projects/:fullpath/merge_requests/<iid>/commits" | jq 'length'
   ```

   - **If the count is 1** — skip step 4 entirely. No squash message will be passed; GitLab uses that single commit's message at merge time. Go to step 5 with an empty `<squash-message>`.
   - **If the count is 2+** — proceed to step 4.

4. Extract the squash commit message from `description`:
   - Find the `## Squash commit message` heading.
   - Take the content of the FIRST fenced code block (between ``` fences) after that heading.
   - Trim surrounding whitespace and blank lines.
   - **If the section is not present** — use AskUserQuestion to ask:
     - "Use the MR title as the squash message" — fall back to `<title>` as the squash subject.
     - "Merge without --squash-message" — let GitLab pick the default.
     - "Cancel" — abort.

5. Show a confirmation summary in plain text:
   ```
   MR:     !<iid> <title>
   URL:    <web_url>
   Target: <target_branch>
   Commits: <N>
   Squash message:
     <subject line>
     <body...>            # if 1 commit, write: "(single commit — message kept as-is)"
   Remove source branch: yes
   ```
   Then use AskUserQuestion: "Proceed with squash-merge?" with options `Yes` / `Cancel`.

6. Run the merge.
   - **2+ commits** with a squash message — use a heredoc-quoted variable so quotes/newlines pass through cleanly:
     ```bash
     MSG=$(cat <<'EOF'
     <squash-message>
     EOF
     )
     glab mr merge <iid> --squash --squash-message "$MSG" --remove-source-branch --yes
     ```
   - **1 commit** OR you fell back to "Merge without --squash-message" in step 4 — omit the flag entirely:
     ```bash
     glab mr merge <iid> --squash --remove-source-branch --yes
     ```

7. Print the resulting merge commit SHA / URL from glab's output.

8. Suggest local cleanup (do NOT execute automatically):
   ```bash
   git checkout <target> && git pull && git branch -D <current-branch>
   ```

## Important

- `--squash-message` works only on `glab mr merge`, not on `glab mr create`. The squash message is written into the MR description by `/mr:create` and applied here at merge time.
- `--yes` skips glab's own confirmation — we already confirmed in step 4.
- `--remove-source-branch` deletes the **remote** branch after merge; the local branch is your responsibility.
- If glab refuses (unresolved threads, blocking pipeline, merge conflicts), show the error verbatim and let the user resolve before retrying.
- Do NOT modify the MR description from this command.
