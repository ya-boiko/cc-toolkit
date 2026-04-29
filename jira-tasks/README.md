# jira-tasks

Generates structured Jira task text (title + description) through an interactive dialogue. Input rough notes in any language — output is always English.

## Install

```
/plugin install jira-tasks@paperos
```

Or set in `~/.claude/settings.json`:

```json
"enabledPlugins": { "jira-tasks@paperos": true }
```

## Command `/jira`

```
/jira <task notes>
```

Pass rough notes as the argument (Russian or English, terse or vague). Claude analyzes the input, asks clarifying questions about missing information, and generates ready-to-copy text.

**Example:**

```
/jira need to add caching to the search API, it's too slow under load
```

### Clarifying questions

Claude asks one question at a time, covering only what's missing:

| Topic | Question |
|---|---|
| Context | Why is this needed? What's currently broken or inconvenient? |
| Expected outcome | What should change after completion? |
| Technical details | Which components, services, or APIs are affected? |
| Dependencies | Are there blockers or related tasks? |
| Priority | How urgent is this and why? |

If the input already covers a topic, the question is skipped.

### Output format

```
**Title:** <concise title, under 80 characters>

**Description:**

**Context**
<why this is needed, current state>

**Expected outcome**
<what changes after completion>

**Technical details**
<affected components, APIs, services>

**Dependencies**
<blockers, related tasks>

**Priority**
<urgency and justification>
```

Sections with no relevant information are omitted. Each section is 1–3 sentences.

After generating, Claude offers to revise any part.

## Skill `jira-tasks`

Auto-triggers from conversation context — no explicit invocation needed.

**Fires when** the message contains the word **"Jira"** with task-creation intent:

> "create a Jira task", "make a Jira ticket", "put in Jira", "задачу в Jira", "jira тикет"

**Does not fire** on casual mentions of Jira without intent to create a task.

Uses the current conversation as context — may skip questions already answered in the dialogue.

### Difference between `/jira` and the skill

| | `/jira` | `jira-tasks` skill |
|---|---|---|
| Invocation | Explicit command | Auto from conversation |
| Input | `$ARGUMENTS` | Current conversation context |
| Logic | Same | Same |

## Uninstall

Set `"jira-tasks@paperos": false` in `~/.claude/settings.json` (or remove the entry).
