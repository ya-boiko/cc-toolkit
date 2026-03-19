---
description: "Generate a Jira task (title + description) from rough notes"
argument-hint: "<task notes>"
---

# /jira — Generate Jira Task Text

Generate a well-structured Jira task (title + description) in English from rough notes provided by the user.

## Input: `$ARGUMENTS`

If empty — ask the user to describe the task.

## Process

1. **Analyze** the provided notes. Identify what information is present and what is missing.
2. **Ask clarifying questions** — only about missing information. One question at a time; batch 2-3 closely related questions when appropriate. Possible topics:
   - Context: why is this needed, what's broken or inconvenient
   - Expected outcome: what should change after completion
   - Technical details: affected components, services, APIs
   - Dependencies: blockers, related tasks
   - Priority: urgency and justification
3. **Generate** the task text in English (regardless of input language).
4. **Offer to revise** — adjust title, rephrase sections, add details if requested.

Skip questions for topics already covered by the input.

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

Omit sections that have no relevant information. Each section — 1-3 sentences, no fluff.
