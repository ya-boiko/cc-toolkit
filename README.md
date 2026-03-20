# Claude Code Skills & Commands

A collection of Claude Code plugins — commands and skills for everyday development workflow.

## Plugins

| Plugin | Description | Docs |
|---|---|---|
| [jira-tasks](#jira-tasks) | Generate Jira task text | [README](jira-tasks/README.md) |
| [hubstaff](#hubstaff) | Manage Hubstaff time tracking | [README](hubstaff/README.md) |
| [git-commands](#git-commands) | Git workflow helpers | [README](git-commands/README.md) |
| [tododo](#tododo) | Manage TODO comments | [README](tododo/README.md) |

## Dependencies

| Dependency | Required by | Install |
|---|---|---|
| [Claude Code](https://claude.ai/code) | all plugins | — |
| [git](https://git-scm.com) | `git-commands`, `tododo` | `sudo dnf install git` |
| [glab](https://gitlab.com/gitlab-org/cli) | `git-commands` (`/mr`) | `sudo dnf install glab` |
| [Hubstaff desktop app](https://hubstaff.com/downloads) + CLI binary | `hubstaff` | Download from Hubstaff; set path via `HUBSTAFF_CLI` env var |
| Python 3.10+ | `hubstaff`, `tododo` | pre-installed on most systems |

## Installation

```bash
make install          # install all plugins
make install-hubstaff # install a specific plugin
```

---

## jira-tasks

Generates Jira task text (title + description) through an interactive dialogue.

### Install

```bash
cd jira-tasks && ./install.sh
```

### Command `/jira`

```
/jira <task notes>
```

Explicit invocation — pass rough notes as the argument. Claude analyzes them, asks clarifying questions about missing details, and generates ready-to-copy English text.

**Description sections:**
- **Context** — why the task is needed
- **Expected outcome** — what changes after completion
- **Technical details** — affected components and services
- **Dependencies** — blockers and related tasks
- **Priority** — urgency and justification

Sections with no relevant information are omitted.

### Skill `jira-tasks`

Auto-triggers from conversation context — no explicit invocation needed. Fires when a message contains the word **"Jira"** with intent to create a task:

> "create a Jira task", "put in Jira", "make a Jira ticket"

Uses current conversation context and may skip questions already answered in the dialogue.

Both `/jira` and `jira-tasks` implement the same logic — the difference is only in how they are invoked: the command is called explicitly, the skill picks up intent from the conversation.

---

## hubstaff

Manage Hubstaff time tracking via CLI.

### Install

```bash
cd hubstaff && ./install.sh
```

### Command `/hubstaff`

```
/hubstaff [status|projects|tasks|start|stop|resume]
```

| Subcommand | Action |
|---|---|
| `status` (or no arguments) | Current tracker status |
| `projects` | List all projects |
| `tasks [project_id]` | List project tasks (omit ID to use active project) |
| `start [task_id]` | Start tracking a task (omit ID to pick from list) |
| `stop` | Stop the tracker |
| `resume` | Resume the tracker |

Internally uses a Python wrapper over `HubstaffCLI.bin.x86_64` — parses JSON and returns clean text output.

### Skill `hubstaff`

Auto-triggers on keywords: **hubstaff, хабстафф, хб, hb, трекер, трекинг**

Examples:
> "включи трекер", "останови трекер", "статус трекера", "покажи задачи в хб"

---

## git-commands

Git workflow commands.

### Install

```bash
cd git-commands && ./install.sh
```

### Command `/commit`

Creates a git commit in conventional commits format.

```
/commit [message] | --no-verify | --amend
```

- Analyzes the diff and suggests splitting into multiple commits if changes are unrelated
- Runs pre-commit checks by default (`pnpm lint`, `pnpm build`, `pnpm generate:docs`)
- `--no-verify` — skip pre-commit checks
- If nothing is staged — automatically stages all changes

### Command `/generate-pr`

Generates a Pull Request description from the current branch.

```
/generate-pr [target-branch]  # default: master
```

Analyzes commits and diff, saves output to `prs/<source>__to__<target>.md` with:
- Title (max 72 characters)
- **Summary** — the purpose of the PR
- **Changes** — grouped list of changes by category

### Command `/mr`

Creates a GitLab Merge Request via `glab` using a description file from `prs/`.

```
/mr
```

1. Finds files in `prs/` matching the current branch
2. If multiple files found — shows a list with target branch and date, asks which to use
3. Parses title and description from the file
4. Pushes the current branch
5. Creates the MR via `glab mr create`

---

## tododo

Manage TODO/FIXME/HACK/XXX comments across a codebase.

### Install

```bash
cd tododo && ./install.sh
```

### Command `/tododo`

```
/tododo [list|edit|remove|run|explore|assign-ids|next|help] [args...]
```

| Subcommand | Action |
|---|---|
| `list` (or no arguments) | List all TODOs grouped by file |
| `edit <id> <text>` | Change the text of a TODO |
| `remove <id>` | Delete a TODO comment |
| `run [id...]` | Implement a TODO and remove the comment |
| `explore [id...]` | Analyze and rewrite vague TODOs with a concrete plan |
| `assign-ids` | Embed stable IDs into all unnamed TODOs |
| `next` | Surface the most actionable TODO and offer to implement it |
| `help` | Show quick reference |

**Recommended workflow:** `list` → `explore` (clarify vague ones) → `run` or `next`

### Command `/tododo:interface`

Opens a web UI for visual TODO selection and clipboard copy.

### `.todoignore`

Place a `.todoignore` file in your project root to exclude files from scanning — same syntax as `.gitignore`. Searched upward from the project root, so a parent-directory `.todoignore` applies to multiple projects.

### Skill `tododo`

Auto-triggers when the user mentions working with TODO comments:
> "show TODOs", "find all TODOs", "run TODO #3", "implement a TODO"
