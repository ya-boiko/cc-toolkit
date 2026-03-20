---
allowed-tools: Bash
description: Launch Hubstaff daily reports dashboard in the browser
argument-hint: "[--port PORT]"
---

# /hubstaff:interface — Daily reports dashboard

Launch the Hubstaff daily reports dashboard in the user's browser.

## Steps

1. Parse arguments: if `$ARGUMENTS` contains `--port <N>`, use that port. Otherwise default to **8788**.

2. Start the web server in the background:
   ```bash
   python3 ~/.claude/scripts/hubstaff/hubstaff_web.py --port <PORT> &
   ```

3. Tell the user:
   - Dashboard is running at `http://localhost:<PORT>`
   - Use the calendar sidebar to browse daily reports
   - Days with reports are highlighted in the calendar
   - To stop: close the terminal or `kill %1`
