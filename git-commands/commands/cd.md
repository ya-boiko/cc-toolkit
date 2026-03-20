---
allowed-tools: Bash
description: Switch working directory for this session
argument-hint: "<directory>"
---

# /cd — Switch working directory

Switch the working directory for all subsequent operations in this session.

## Steps

If `$ARGUMENTS` is empty or not provided:

1. List subdirectories: `ls -d */ 2>/dev/null`
2. Show the numbered list to the user, ask which one to use.
3. Once they pick — proceed as below.

If `$ARGUMENTS` is provided:

1. Run `cd $ARGUMENTS && pwd` to verify the directory exists and resolve the full path.
2. From now on, use this directory as the root for all file operations, bash commands, and searches.
3. Confirm to the user: "Working directory: <full path>"
