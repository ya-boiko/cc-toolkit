---
allowed-tools: Bash
description: Switch working directory for this session
argument-hint: "<directory>"
---

# /cd — Switch working directory

Switch the working directory for all subsequent operations in this session.

## Steps

1. Run `cd $ARGUMENTS && pwd` to verify the directory exists and resolve the full path.
2. From now on, use this directory as the root for all file operations, bash commands, and searches.
3. Confirm to the user: "Working directory: <full path>"
