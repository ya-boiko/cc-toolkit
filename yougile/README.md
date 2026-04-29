# yougile

Claude Code plugin: subagent + Python CLI for managing YouGile tasks via the REST API v2.

## Install

This plugin lives in the `paperos` marketplace.

```
/plugin install yougile@paperos
```

Or set in `~/.claude/settings.json`: `"yougile@paperos": true`.

For terminal use of the `yougile` CLI, create a one-time symlink:

```bash
ln -sf "$(pwd)/bin/yougile" ~/.local/bin/yougile
```

(run from the `yougile/` plugin folder, or substitute the absolute path). Make sure `~/.local/bin` is in your `PATH`. Tests need `pip install requests pytest responses`.

## Bootstrap

Interactive (recommended for first run):

```bash
yougile bootstrap
# enter login (email) and password when prompted
```

Non-interactive (scripting):

```bash
YOUGILE_PASSWORD='…' yougile bootstrap --login you@example.com [--company <uuid>]
```

Config is written to `~/.config/yougile/config.json` with `chmod 600`. Password is never stored on disk.

## Quick CLI reference

```text
yougile auth status                       # check API key validity
yougile auth reset                        # delete local config
yougile context show
yougile context set --project <id> [--board <id>] [--column <id>]
yougile context clear

yougile tasks list [--column <id>] [--assignee <id>] [--limit 50]
yougile tasks get <id>
yougile tasks create --title "…" --column <id> [--assignee <id>] [--deadline 2026-05-01]
yougile tasks update <id> --column <id>|- --completed true|false ...
yougile tasks update <id> --assignee-add <uid> | --assignee-remove <uid> | --assignee-set <uid>,<uid>
yougile tasks move <id> --column <id>
yougile tasks done <id>
yougile tasks add-subtask <parent-id> <child-id>
yougile tasks remove-subtask <parent-id> <child-id>

yougile comments list <task-id>
yougile comments add <task-id> --text "…"

yougile projects list [/get <id>]
yougile boards list [--project <id>] [/get <id>]
yougile columns list --board <id>
yougile users list [--query <substr>]

yougile stickers list [--type string|sprint]
yougile stickers states <sticker-id> [--type string|sprint]
```

Add `--json` to any command for machine-readable output.

## Subagent

Once installed, the `yougile` subagent activates when you mention YouGile / ЮГайл / ю-гайл / ю-джайл and an action verb. It calls the same `yougile` CLI under the hood, asks for confirmation before any state-changing operation (POST/PUT), and prefers stored context defaults for project/board/column.

## Manual acceptance scenarios

Run these after a clean install + bootstrap to verify end-to-end behavior:

1. **Bootstrap → first task creation.**
   ```bash
   yougile auth status                   # → company info, no context
   yougile projects list                 # pick a project id
   yougile boards list --project <pid>   # pick a board id
   yougile columns list --board <bid>    # pick a column id
   yougile context set --project <pid> --board <bid> --column <cid>
   yougile tasks create --title "Smoke test" --column <cid>
   ```
   Expected: `✓ создано: <new-id>`.

2. **Move task between columns.**
   ```bash
   yougile tasks list --column <source-col> --limit 5
   yougile tasks move <task-id> --column <target-col>
   yougile tasks get <task-id>           # confirm columnId changed
   ```

3. **Comment on a task.**
   ```bash
   yougile comments add <task-id> --text "Тест от CLI"
   yougile comments list <task-id> --limit 5
   ```
   Expected: the new comment appears at the top.

4. **My open tasks.**
   ```bash
   yougile users list --query <your-name>     # find your user id
   yougile tasks list --assignee <your-uid>
   ```

## Tests

```bash
cd ~/cc_skills/yougile
.venv/bin/pytest -v
```

All tests are HTTP-mocked via `responses` — no real API calls.

## Uninstall

Set `"yougile@paperos": false` in `~/.claude/settings.json` (or remove the entry). Then:

```bash
rm ~/.local/bin/yougile                  # remove the CLI symlink
rm ~/.config/yougile/config.json          # optional, removes saved API key
```

## Architecture

See the design spec at `<repo>/docs/superpowers/specs/2026-04-26-yougile-agent-design.md` (in the YouGile workspace, not in this repo).

## Known limitations

- `--assignee-add/-remove`, `add-subtask`, `remove-subtask` are GET-then-PUT (the API has no delta endpoint) — not atomic under concurrent edits.
- `auth reset` removes the local config only; the API key on the YouGile side is not deleted.
- Rate limit (50 req/min per company) is not enforced client-side; requests that hit 429 fail with exit code 6.
- No write operations on projects/boards/columns/users — by design (do those in the YouGile UI).
