---
allowed-tools: Bash
description: Launch tododo web dashboard for visual TODO selection
argument-hint: "[--port PORT]"
---

# /tododo:interface — Launch web dashboard

Launch the tododo web dashboard in the user's browser.

## Steps

1. Parse arguments: if `$ARGUMENTS` contains `--port <N>`, use that port. Otherwise default to **8787**.

2. Start the web server in the background:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tododo_web.py --port <PORT> . &
   ```

3. Tell the user:
   - Dashboard is running at `http://localhost:<PORT>`
   - Select TODOs with checkboxes, then click **Copy run** / **Copy explore** / **Copy remove**
   - Paste the copied command back into Claude Code
   - The server auto-refreshes every 3 seconds
   - To stop: close the terminal or `kill %1`
