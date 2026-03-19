---
name: jira-tasks
description: "Generate Jira task text. Use when the user mentions 'Jira' with intent to create, formalize, or write a task/ticket/issue — e.g., 'create Jira task', 'make a Jira ticket', 'put in Jira', 'jira тикет', 'задачу в Jira'"
---

# Jira Task Generator

Generate a Jira task (title + description) in English from conversation context or user-provided notes.

## When Triggered

Activate only when the user explicitly wants to create or formalize a Jira task. Do not activate on mere mention of Jira without task-creation intent.

## Process

1. **Gather context** from the current conversation. Identify what information is already available.
2. **Ask clarifying questions** about missing information only. One at a time; batch 2-3 related questions when appropriate. Topics: context, expected outcome, technical details, dependencies, priority.
3. **Generate** task text in English.
4. **Offer to revise** if needed.

## Output Format

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

Omit sections with no relevant information. Each section — 1-3 sentences, no fluff.
