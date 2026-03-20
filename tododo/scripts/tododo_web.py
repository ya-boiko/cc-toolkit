#!/usr/bin/env python3
"""Web dashboard for tododo — browse and select TODOs in the browser."""

import argparse
import json
import os
import subprocess
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

# Resolve scanner path relative to this script
SCANNER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scan_todos.py")

# ---------------------------------------------------------------------------
# HTML / CSS / JS — embedded as a single string constant
# ---------------------------------------------------------------------------

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>tododo</title>
<style>
:root {
  --bg: #1a1b26;
  --surface: #24283b;
  --surface2: #2f3347;
  --border: #3b3f54;
  --text: #c0caf5;
  --text-dim: #565f89;
  --accent: #7aa2f7;
  --accent-dim: #3d59a1;
  --green: #9ece6a;
  --yellow: #e0af68;
  --red: #f7768e;
  --orange: #ff9e64;
  --radius: 6px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: "JetBrains Mono", "Fira Code", "SF Mono", "Cascadia Code", Consolas, monospace;
  font-size: 13px;
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
}
header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}
header h1 {
  font-size: 16px;
  font-weight: 600;
  color: var(--accent);
}
header .status {
  font-size: 11px;
  color: var(--text-dim);
}
.status .dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--green);
  margin-right: 6px;
  vertical-align: middle;
}
.toolbar {
  display: flex;
  gap: 8px;
  padding: 12px 24px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  flex-wrap: wrap;
  align-items: center;
}
.toolbar .count {
  font-size: 12px;
  color: var(--text-dim);
  margin-right: auto;
}
.toolbar button {
  font-family: inherit;
  font-size: 12px;
  padding: 5px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface2);
  color: var(--text);
  cursor: pointer;
  transition: all 0.15s;
}
.toolbar button:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}
.toolbar button:disabled {
  opacity: 0.35;
  cursor: default;
}
.toolbar button.copied {
  border-color: var(--green);
  color: var(--green);
}
.group-toggle {
  display: flex;
  gap: 0;
  margin-right: 8px;
}
.group-toggle .gt {
  padding: 5px 10px;
  border-radius: 0;
  border-right-width: 0;
}
.group-toggle .gt:first-child { border-radius: var(--radius) 0 0 var(--radius); }
.group-toggle .gt:last-child { border-radius: 0 var(--radius) var(--radius) 0; border-right-width: 1px; }
.group-toggle .gt.active {
  background: var(--accent-dim);
  color: var(--text);
  border-color: var(--accent);
}
#content { padding: 12px 24px 80px; }
.file-group {
  margin-bottom: 16px;
}
.file-header {
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
  padding: 6px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}
.file-header .file-count {
  font-weight: 400;
  color: var(--text-dim);
  font-size: 11px;
}
.todo-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 6px 8px 6px 16px;
  border-radius: var(--radius);
  transition: background 0.15s, opacity 0.4s;
}
.todo-item:hover { background: var(--surface); }
.todo-item.selected { background: var(--surface2); }
.todo-item input[type="checkbox"] {
  margin-top: 3px;
  accent-color: var(--accent);
  cursor: pointer;
  flex-shrink: 0;
}
.todo-id {
  color: var(--text-dim);
  min-width: 32px;
  text-align: right;
  flex-shrink: 0;
}
.todo-line {
  color: var(--text-dim);
  min-width: 40px;
  flex-shrink: 0;
}
.todo-keyword {
  font-weight: 700;
  min-width: 44px;
  flex-shrink: 0;
}
.todo-keyword.TODO { color: var(--accent); }
.todo-keyword.FIXME { color: var(--red); }
.todo-keyword.HACK { color: var(--orange); }
.todo-keyword.XXX { color: var(--yellow); }
.todo-text { color: var(--text); word-break: break-word; }
.todo-item.new-item {
  animation: fadeIn 0.4s ease;
}
@keyframes fadeIn {
  from { background: rgba(122, 162, 247, 0.15); }
  to { background: transparent; }
}
.todo-item.removed-item {
  opacity: 0.3;
  text-decoration: line-through;
  transition: opacity 0.5s;
}
.todo-chevron {
  cursor: pointer;
  color: var(--text-dim);
  font-size: 10px;
  user-select: none;
  flex-shrink: 0;
  width: 14px;
  display: inline-block;
  text-align: center;
}
.todo-chevron.dim {
  opacity: 0.2;
  cursor: default;
  pointer-events: none;
}
.todo-context {
  padding: 2px 8px 4px 60px;
  overflow-x: auto;
}
.todo-context pre {
  font-size: 12px;
  font-family: inherit;
  white-space: pre;
  background: var(--surface);
  padding: 4px 8px;
  border-radius: var(--radius);
  margin: 0;
}
.ctx-ln  { color: var(--text-dim); }
.ctx-sep { color: var(--text-dim); }
.ctx-code { color: var(--text); }
.ctx-todo-ln { color: var(--accent); }
.ctx-todo-code { color: var(--accent); }
.empty-state {
  text-align: center;
  padding: 80px 24px;
  color: var(--text-dim);
}
.empty-state h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text);
}
.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%) translateY(100px);
  background: var(--surface2);
  color: var(--green);
  border: 1px solid var(--green);
  padding: 8px 20px;
  border-radius: var(--radius);
  font-size: 12px;
  transition: transform 0.25s ease;
  z-index: 100;
  pointer-events: none;
}
.toast.show { transform: translateX(-50%) translateY(0); }
</style>
</head>
<body>

<header>
  <h1>tododo</h1>
  <span class="status"><span class="dot"></span>polling</span>
</header>

<div class="toolbar">
  <span class="count" id="sel-count">0 selected</span>
  <span class="group-toggle">
    <button class="gt active" data-mode="file" onclick="setGroup('file')">File</button>
    <button class="gt" data-mode="id" onclick="setGroup('id')">ID</button>
    <button class="gt" data-mode="flat" onclick="setGroup('flat')">Flat</button>
  </span>
  <button id="btn-run" disabled onclick="copyCmd('run')">Copy run</button>
  <button id="btn-explore" disabled onclick="copyCmd('explore')">Copy explore</button>
  <button id="btn-remove" disabled onclick="copyCmd('remove')">Copy remove</button>
</div>

<div id="content">
  <div class="empty-state"><h2>Loading...</h2></div>
</div>

<div class="toast" id="toast"></div>

<script>
const POLL_MS = 3000;
let todos = [];
let selected = new Set(); // stores todoKey values
let prevKeys = new Set();
let groupMode = 'file'; // 'file' | 'id' | 'flat'
let expanded = new Set(); // stores expandKey values
function expandKey(t) { return t.relpath + ':' + t.line_no; }

function todoKey(t) { return t.relpath + ':' + t.line_no + ':' + t.keyword + ':' + t.text; }

async function fetchTodos() {
  try {
    const r = await fetch('/api/todos');
    if (!r.ok) return;
    const data = await r.json();
    updateTodos(data);
  } catch(e) { /* network error, retry next poll */ }
}

function updateTodos(newTodos) {
  const newKeys = new Set(newTodos.map(todoKey));
  const addedKeys = new Set([...newKeys].filter(k => !prevKeys.has(k)));
  selected = new Set([...selected].filter(k => newKeys.has(k)));
  todos = newTodos;
  prevKeys = newKeys;
  render(addedKeys);
}

function setGroup(mode) {
  groupMode = mode;
  document.querySelectorAll('.gt').forEach(b => b.classList.toggle('active', b.dataset.mode === mode));
  render();
}

function render(addedKeys) {
  const content = document.getElementById('content');
  if (todos.length === 0) {
    content.innerHTML = '<div class="empty-state"><h2>No TODOs found</h2><p>Add TODO, FIXME, HACK, or XXX comments to your code.</p></div>';
    updateToolbar();
    return;
  }

  let html = '';
  if (groupMode === 'file') {
    html = renderGroupedByFile(addedKeys);
  } else if (groupMode === 'id') {
    html = renderGroupedById(addedKeys);
  } else {
    html = renderFlat(addedKeys);
  }
  content.innerHTML = html;
  updateToolbar();
}

function renderGroupedByFile(addedKeys) {
  const groups = {};
  const order = [];
  for (const t of todos) {
    if (!groups[t.relpath]) { groups[t.relpath] = []; order.push(t.relpath); }
    groups[t.relpath].push(t);
  }
  let html = '';
  for (const file of order) {
    const items = groups[file];
    html += '<div class="file-group">';
    html += '<div class="file-header" onclick="toggleGroupSelect(\'' + escAttr(file) + '\', \'file\')">';
    html += escHtml(file) + ' <span class="file-count">' + items.length + '</span></div>';
    for (const t of items) html += renderItem(t, addedKeys, true);
    html += '</div>';
  }
  return html;
}

function renderGroupedById(addedKeys) {
  const groups = {};
  const order = [];
  for (const t of todos) {
    const id = t.display_id;
    if (!groups[id]) { groups[id] = []; order.push(id); }
    groups[id].push(t);
  }
  let html = '';
  for (const id of order) {
    const items = groups[id];
    html += '<div class="file-group">';
    html += '<div class="file-header" onclick="toggleGroupSelect(\'' + escAttr(id) + '\', \'id\')">';
    html += '[' + escHtml(id) + '] <span class="file-count">' + items.length + '</span></div>';
    for (const t of items) html += renderItem(t, addedKeys, false);
    html += '</div>';
  }
  return html;
}

function renderFlat(addedKeys) {
  let html = '';
  for (const t of todos) html += renderItem(t, addedKeys, true);
  return html;
}

function renderItem(t, addedKeys, showFile) {
  const key = todoKey(t);
  const ekey = expandKey(t);
  const isNew = addedKeys && addedKeys.has(key);
  const isExp = expanded.has(ekey);

  const ctxLines = t.context_lines || [];
  const hasCtx = ctxLines.length > 0;

  const cls = ['todo-item'];
  if (selected.has(key)) cls.push('selected');
  if (isNew) cls.push('new-item');

  const chevronCls = 'todo-chevron' + (hasCtx ? '' : ' dim');
  const chevronChar = isExp ? '&#9660;' : '&#9654;';
  const escEkey = escAttr(ekey);

  let html = '<div class="' + cls.join(' ') + '" data-expand-key="' + escEkey + '">';
  html += '<span class="' + chevronCls + '" onclick="toggleExpand(\'' + escEkey + '\')">' + chevronChar + '</span>';
  html += '<input type="checkbox" ' + (selected.has(key) ? 'checked' : '') + ' onchange="toggle(\'' + escAttr(key) + '\')">';
  html += '<span class="todo-id">[' + escHtml(t.display_id) + ']</span>';
  html += '<span class="todo-line">' + escHtml(t.relpath) + ':' + t.line_no + '</span>';
  html += '<span class="todo-keyword ' + t.keyword + '">' + t.keyword + '</span>';
  html += '<span class="todo-text">' + escHtml(t.text) + '</span>';
  html += '</div>';

  // Context block
  const ctxDisplay = isExp ? 'block' : 'none';
  html += '<div class="todo-context" data-expand-key="' + escEkey + '" style="display:' + ctxDisplay + '">';
  if (hasCtx) {
    html += '<pre>';
    for (const [ln, lt] of ctxLines) {
      const isTodoLine = ln === t.line_no;
      html += '<span class="ctx-ln' + (isTodoLine ? ' ctx-todo-ln' : '') + '">' + String(ln).padStart(4) + '</span>';
      html += '<span class="ctx-sep">:</span>';
      html += '<span class="ctx-code' + (isTodoLine ? ' ctx-todo-code' : '') + '">' + escHtml(lt) + '</span>\n';
    }
    html += '</pre>';
  }
  html += '</div>';

  return html;
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function escAttr(s) {
  return String(s).replace(/\\/g,'\\\\').replace(/'/g,"\\'").replace(/"/g,'&quot;');
}

function toggle(key) {
  if (selected.has(key)) selected.delete(key);
  else selected.add(key);
  render();
}

function toggleExpand(ekey) {
  if (expanded.has(ekey)) expanded.delete(ekey);
  else expanded.add(ekey);

  // Update DOM directly without full re-render
  const chevronChar = expanded.has(ekey) ? '&#9660;' : '&#9654;';
  const display = expanded.has(ekey) ? 'block' : 'none';

  for (const el of document.querySelectorAll('[data-expand-key]')) {
    if (el.dataset.expandKey !== ekey) continue;
    if (el.classList.contains('todo-item')) {
      const ch = el.querySelector('.todo-chevron');
      if (ch) ch.innerHTML = chevronChar;
    } else if (el.classList.contains('todo-context')) {
      el.style.display = display;
    }
  }
}

function toggleGroupSelect(groupVal, mode) {
  const items = mode === 'file'
    ? todos.filter(t => t.relpath === groupVal)
    : todos.filter(t => t.display_id === groupVal);
  const keys = items.map(todoKey);
  const allSelected = keys.every(k => selected.has(k));
  for (const k of keys) {
    if (allSelected) selected.delete(k);
    else selected.add(k);
  }
  render();
}

function updateToolbar() {
  const n = selected.size;
  document.getElementById('sel-count').textContent = n + ' selected';
  document.getElementById('btn-run').disabled = n === 0;
  document.getElementById('btn-explore').disabled = n === 0;
  document.getElementById('btn-remove').disabled = n === 0;
}

function copyCmd(action) {
  const sel = todos.filter(t => selected.has(todoKey(t)));
  if (sel.length === 0) return;
  // Deduplicate display_ids for the command
  const ids = [...new Set(sel.map(t => t.display_id))].join(' ');
  const descs = sel.map(t => t.text ? t.label + ': ' + t.text : t.label).join(', ');
  const cmd = '/tododo ' + action + ' ' + ids + ' \u2014 ' + descs;
  navigator.clipboard.writeText(cmd).then(() => {
    showToast('Copied: ' + cmd);
    const btn = document.getElementById('btn-' + action);
    btn.classList.add('copied');
    setTimeout(() => btn.classList.remove('copied'), 1200);
  }).catch(() => {
    showToast('Copy failed \u2014 use HTTPS or localhost');
  });
}

function showToast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2500);
}

fetchTodos();
setInterval(fetchTodos, POLL_MS);
</script>
</body>
</html>"""


class TodoHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the tododo web dashboard."""

    root: str = "."

    def do_GET(self):
        if self.path == "/":
            self._serve_html()
        elif self.path == "/api/todos":
            self._serve_todos()
        else:
            self.send_error(404)

    def _serve_html(self):
        body = HTML_PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_todos(self):
        try:
            result = subprocess.run(
                [sys.executable, SCANNER_PATH, "--json", "--context", "3", "--after", "5", self.root],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                self._json_response(500, {"error": result.stderr.strip()})
                return
            stdout = result.stdout.strip()
            if not stdout:
                self._json_response(200, [])
                return
            data = json.loads(stdout)
            self._json_response(200, data)
        except subprocess.TimeoutExpired:
            self._json_response(500, {"error": "scanner timed out"})
        except json.JSONDecodeError:
            self._json_response(500, {
                "error": "scanner returned invalid JSON",
                "stdout": result.stdout[:500] if result.stdout else "",
                "stderr": result.stderr[:500] if result.stderr else "",
            })

    def _json_response(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # Quieter logging: only errors
        if args and isinstance(args[0], str) and args[0].startswith("GET /api"):
            return
        super().log_message(fmt, *args)


def main():
    parser = argparse.ArgumentParser(description="tododo web dashboard")
    parser.add_argument("root", nargs="?", default=".", help="Project root directory")
    parser.add_argument(
        "--port", type=int, default=8787, help="Port to listen on (default: 8787)"
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"Error: '{root}' is not a directory", file=sys.stderr)
        sys.exit(1)

    TodoHandler.root = root

    server = HTTPServer(("127.0.0.1", args.port), TodoHandler)
    print(f"tododo web → http://localhost:{args.port}")
    print(f"scanning: {root}")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
        server.server_close()


if __name__ == "__main__":
    main()
