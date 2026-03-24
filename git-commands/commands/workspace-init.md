---
allowed-tools: Bash(cat:*), Bash(ls:*), Write, AskUserQuestion
argument-hint: [work|personal]
description: Create .workspace.md in the current directory to set work or personal mode
model: inherit
---

# Initialize Workspace Mode

Create a `.workspace.md` file in the current directory to configure workspace mode for git commands.

Mode argument: $ARGUMENTS

## Instructions

1. **Determine mode:**
   - If `$ARGUMENTS` is `work` or `personal` — use it directly
   - Otherwise — ask: "Which workspace mode? (work / personal)"

2. **Check if `.workspace.md` already exists** using `ls .workspace.md 2>/dev/null`:
   - If it exists — show its current contents and ask: "`.workspace.md` already exists. Overwrite?"
   - If user says no — abort

3. **Create the file** at `.workspace.md` in the current directory:

```markdown
---
mode: <work|personal>
---
```

4. **Confirm:** "Created `.workspace.md` with mode: `<mode>` in `<current directory>`."

## Notes

- This file is searched upward from `$PWD` by git-commands — placing it in a parent directory applies the mode to all projects underneath it
- Add `.workspace.md` to your global `.gitignore` to avoid committing it
