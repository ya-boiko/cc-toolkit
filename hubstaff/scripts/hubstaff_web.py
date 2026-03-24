#!/usr/bin/env python3
"""Web dashboard for Hubstaff daily reports — calendar sidebar + report viewer."""

import argparse
import json
import os
import re
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

REPORTS_DIR = os.path.expanduser("~/.hubstaff-daily")

# ---------------------------------------------------------------------------
# HTML / CSS / JS — embedded as a single string constant
# ---------------------------------------------------------------------------

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>hubstaff daily</title>
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
  height: 100vh;
  display: flex;
  flex-direction: column;
}
header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  flex-shrink: 0;
}
header h1 {
  font-size: 15px;
  font-weight: 600;
  color: var(--accent);
}
header .status {
  font-size: 11px;
  color: var(--text-dim);
}
.main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* --- Calendar sidebar --- */
.sidebar {
  width: 240px;
  flex-shrink: 0;
  border-right: 1px solid var(--border);
  background: var(--surface);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}
.cal-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px 8px;
}
.cal-nav button {
  background: none;
  border: none;
  color: var(--accent);
  cursor: pointer;
  font-size: 16px;
  padding: 2px 6px;
  border-radius: 4px;
}
.cal-nav button:hover { background: var(--surface2); }
.cal-nav .cal-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
}
.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  padding: 4px 12px 12px;
  text-align: center;
  font-size: 12px;
}
.cal-grid .cal-dow {
  color: var(--text-dim);
  font-size: 10px;
  padding: 4px 0;
}
.cal-grid .cal-day {
  padding: 4px 0;
  border-radius: 4px;
  color: var(--text-dim);
  cursor: default;
  user-select: none;
}
.cal-grid .cal-day.empty { visibility: hidden; }
.cal-grid .cal-day.has-report {
  color: var(--accent);
  cursor: pointer;
  font-weight: 600;
}
.cal-grid .cal-day.has-report:hover {
  background: var(--surface2);
}
.cal-grid .cal-day.active {
  background: var(--accent);
  color: var(--bg);
}
.cal-grid .cal-day.today:not(.active) {
  outline: 1px solid var(--accent-dim);
}
.sidebar-footer {
  padding: 8px 16px;
  border-top: 1px solid var(--border);
  font-size: 11px;
  color: var(--text-dim);
  flex-shrink: 0;
}

/* --- Report panel --- */
.report {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
}
.report-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-dim);
  font-size: 14px;
}
.report-date {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 20px;
  color: var(--text);
}
.project-block {
  margin-bottom: 24px;
}
.project-header {
  font-size: 14px;
  font-weight: 600;
  color: var(--accent);
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
}
.project-header .project-time {
  color: var(--green);
  font-weight: 400;
}
.task-item {
  margin-bottom: 12px;
  padding-left: 14px;
  border-left: 2px solid var(--accent-dim);
}
.task-name {
  font-weight: 600;
  color: var(--text);
}
.task-time {
  color: var(--green);
  margin-left: 8px;
  font-weight: 400;
}
.task-desc {
  color: var(--text-dim);
  margin-top: 2px;
  font-size: 12px;
  cursor: pointer;
  border-radius: 3px;
  padding: 2px 4px;
  margin-left: -4px;
}
.task-desc:hover { background: var(--surface2); }
.task-desc p { margin: 4px 0; }
.task-desc ul { margin: 4px 0 4px 16px; }
.task-desc li { margin: 2px 0; }
.task-desc code {
  background: var(--surface2);
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 11px;
}
.task-desc-empty {
  color: var(--text-dim);
  opacity: 0.5;
  margin-top: 2px;
  font-size: 12px;
  cursor: pointer;
  border-radius: 3px;
  padding: 2px 4px;
  margin-left: -4px;
  font-style: italic;
}
.task-desc-empty:hover { background: var(--surface2); }
textarea.edit-area {
  width: 100%;
  min-height: 40px;
  margin-top: 2px;
  padding: 6px 8px;
  background: var(--surface2);
  color: var(--text);
  border: 1px solid var(--accent-dim);
  border-radius: 4px;
  font-family: inherit;
  font-size: 12px;
  line-height: 1.5;
  resize: vertical;
  outline: none;
}
textarea.edit-area:focus { border-color: var(--accent); }
.notes-section {
  margin-top: 32px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}
.notes-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-dim);
  margin-bottom: 8px;
}
textarea.notes-area {
  width: 100%;
  min-height: 80px;
  padding: 8px 10px;
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 4px;
  font-family: inherit;
  font-size: 12px;
  line-height: 1.5;
  resize: vertical;
  outline: none;
}
textarea.notes-area:focus { border-color: var(--accent); }
.save-hint {
  font-size: 10px;
  color: var(--text-dim);
  margin-top: 4px;
  opacity: 0.6;
}
.toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: var(--green);
  color: var(--bg);
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
  z-index: 100;
}
.toast.show { opacity: 1; }
</style>
</head>
<body>
<header>
  <h1>hubstaff daily</h1>
  <span class="status" id="report-count"></span>
</header>
<div class="main">
  <div class="sidebar">
    <div class="cal-nav">
      <button onclick="prevMonth()">&larr;</button>
      <span class="cal-title" id="cal-title"></span>
      <button onclick="nextMonth()">&rarr;</button>
    </div>
    <div class="cal-grid" id="cal-grid"></div>
    <div class="sidebar-footer" id="sidebar-footer"></div>
  </div>
  <div class="report" id="report">
    <div class="report-empty">Loading...</div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
let availableDates = new Set();
let currentYear, currentMonth;
let activeDate = null;
let currentReport = null;

async function init() {
  const resp = await fetch('/api/dates');
  const dates = await resp.json();
  availableDates = new Set(dates);
  document.getElementById('report-count').textContent = dates.length + ' report' + (dates.length === 1 ? '' : 's');
  if (dates.length > 0) {
    const latest = dates[0];
    const [y, m] = latest.split('-').map(Number);
    currentYear = y;
    currentMonth = m - 1;
    selectDate(latest);
  } else {
    const now = new Date();
    currentYear = now.getFullYear();
    currentMonth = now.getMonth();
    renderCalendar();
    document.getElementById('report').innerHTML = '<div class="report-empty">No reports yet.<br>Run /hubstaff summary to generate one.</div>';
  }
}

function renderCalendar() {
  document.getElementById('cal-title').textContent = MONTHS[currentMonth] + ' ' + currentYear;
  const firstDay = new Date(currentYear, currentMonth, 1).getDay();
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
  const offset = (firstDay + 6) % 7;
  const today = new Date();
  const todayStr = today.getFullYear() + '-' + String(today.getMonth() + 1).padStart(2, '0') + '-' + String(today.getDate()).padStart(2, '0');
  let html = '';
  const dows = ['Mo','Tu','We','Th','Fr','Sa','Su'];
  for (const d of dows) html += '<span class="cal-dow">' + d + '</span>';
  for (let i = 0; i < offset; i++) html += '<span class="cal-day empty"></span>';
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = currentYear + '-' + String(currentMonth + 1).padStart(2, '0') + '-' + String(day).padStart(2, '0');
    const classes = ['cal-day'];
    if (availableDates.has(dateStr)) classes.push('has-report');
    if (dateStr === activeDate) classes.push('active');
    if (dateStr === todayStr) classes.push('today');
    const onclick = availableDates.has(dateStr) ? ' onclick="selectDate(\'' + dateStr + '\')"' : '';
    html += '<span class="' + classes.join(' ') + '"' + onclick + '>' + day + '</span>';
  }
  document.getElementById('cal-grid').innerHTML = html;
  let monthReports = 0;
  const prefix = currentYear + '-' + String(currentMonth + 1).padStart(2, '0');
  for (const d of availableDates) { if (d.startsWith(prefix)) monthReports++; }
  document.getElementById('sidebar-footer').textContent = monthReports + ' report' + (monthReports === 1 ? '' : 's') + ' this month';
}

function prevMonth() {
  currentMonth--;
  if (currentMonth < 0) { currentMonth = 11; currentYear--; }
  renderCalendar();
}
function nextMonth() {
  currentMonth++;
  if (currentMonth > 11) { currentMonth = 0; currentYear++; }
  renderCalendar();
}

async function selectDate(dateStr) {
  activeDate = dateStr;
  renderCalendar();
  const panel = document.getElementById('report');
  panel.innerHTML = '<div class="report-empty">Loading...</div>';
  try {
    const resp = await fetch('/api/report/' + dateStr);
    if (!resp.ok) { panel.innerHTML = '<div class="report-empty">Failed to load report.</div>'; return; }
    currentReport = await resp.json();
    renderReport();
  } catch (e) {
    panel.innerHTML = '<div class="report-empty">Error: ' + escHtml(e.message) + '</div>';
  }
}

function renderReport() {
  const data = currentReport;
  const panel = document.getElementById('report');
  if (!data.projects || data.projects.length === 0) {
    panel.innerHTML = '<div class="report-date">' + escHtml(data.date) + '</div>' +
      '<div style="color: var(--text-dim)">No tracked time for this day.</div>' +
      renderNotesSection(data.notes || '');
    return;
  }
  let html = '<div class="report-date">' + escHtml(data.date) + '</div>';
  for (let pi = 0; pi < data.projects.length; pi++) {
    const proj = data.projects[pi];
    html += '<div class="project-block">';
    html += '<div class="project-header"><span>' + escHtml(proj.name) + '</span>';
    if (proj.tracked) html += '<span class="project-time">' + escHtml(proj.tracked) + '</span>';
    html += '</div>';
    if (proj.tasks && proj.tasks.length > 0) {
      for (let ti = 0; ti < proj.tasks.length; ti++) {
        const task = proj.tasks[ti];
        html += '<div class="task-item">';
        html += '<div><span class="task-name">' + escHtml(task.name) + '</span>';
        if (task.tracked) html += '<span class="task-time">' + escHtml(task.tracked) + '</span>';
        html += '</div>';
        if (task.description) {
          html += '<div class="task-desc" onclick="editDesc(' + pi + ',' + ti + ')">' + renderMarkdown(task.description) + '</div>';
        } else {
          html += '<div class="task-desc-empty" onclick="editDesc(' + pi + ',' + ti + ')">+ add description</div>';
        }
        html += '</div>';
      }
    }
    html += '</div>';
  }
  html += renderNotesSection(data.notes || '');
  panel.innerHTML = html;
}

function renderNotesSection(notes) {
  return '<div class="notes-section">' +
    '<div class="notes-label">Notes</div>' +
    '<textarea class="notes-area" placeholder="Add notes for this day..." onblur="saveNotes(this)">' + escHtml(notes) + '</textarea>' +
    '<div class="save-hint">auto-saves on blur</div>' +
    '</div>';
}

function editDesc(pi, ti) {
  const task = currentReport.projects[pi].tasks[ti];
  const items = document.querySelectorAll('.task-item');
  let idx = 0;
  for (let p = 0; p < currentReport.projects.length; p++) {
    const tasks = currentReport.projects[p].tasks || [];
    for (let t = 0; t < tasks.length; t++) {
      if (p === pi && t === ti) {
        const item = items[idx];
        const descEl = item.querySelector('.task-desc, .task-desc-empty');
        if (!descEl || descEl.tagName === 'TEXTAREA') return;
        const ta = document.createElement('textarea');
        ta.className = 'edit-area';
        ta.value = task.description || '';
        ta.setAttribute('data-pi', pi);
        ta.setAttribute('data-ti', ti);
        ta.onblur = function() { saveDesc(this); };
        ta.onkeydown = function(e) {
          if (e.key === 'Escape') { this.blur(); }
        };
        descEl.replaceWith(ta);
        ta.focus();
        return;
      }
      idx++;
    }
  }
}

async function saveDesc(ta) {
  const pi = parseInt(ta.getAttribute('data-pi'));
  const ti = parseInt(ta.getAttribute('data-ti'));
  const newDesc = ta.value.trim();
  currentReport.projects[pi].tasks[ti].description = newDesc;
  await saveReport();
  renderReport();
}

async function saveNotes(ta) {
  const newNotes = ta.value.trim();
  if (newNotes === (currentReport.notes || '')) return;
  currentReport.notes = newNotes;
  await saveReport();
  showToast('Saved');
}

async function saveReport() {
  try {
    const resp = await fetch('/api/report/' + activeDate, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(currentReport),
    });
    if (resp.ok) {
      showToast('Saved');
    } else {
      showToast('Save failed');
    }
  } catch (e) {
    showToast('Save error: ' + e.message);
  }
}

function showToast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 1500);
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function renderMarkdown(s) {
  const escaped = escHtml(s);
  const lines = escaped.split('\n');
  let html = '';
  let inList = false;
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith('- ')) {
      if (!inList) { html += '<ul>'; inList = true; }
      html += '<li>' + formatInline(trimmed.slice(2)) + '</li>';
    } else {
      if (inList) { html += '</ul>'; inList = false; }
      if (trimmed) html += '<p>' + formatInline(trimmed) + '</p>';
    }
  }
  if (inList) html += '</ul>';
  return html;
}

function formatInline(s) {
  return s.replace(/`([^`]+)`/g, '<code>$1</code>')
          .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
}

init();
</script>
</body>
</html>"""


def _parse_report(filepath):
    """Parse a daily report markdown file into structured data.

    Expected format:
        # YYYY-MM-DD
        ## ProjectName — H:MM:SS
        ### Task name — H:MM:SS
        Description text.
        ## Notes
        Free text notes.
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    date = None
    projects = []
    notes = ""
    current_project = None
    current_task = None
    in_notes = False

    for line in lines:
        line_stripped = line.strip()

        # Date header: # 2026-03-20
        m = re.match(r"^#\s+(\d{4}-\d{2}-\d{2})\s*$", line_stripped)
        if m:
            date = m.group(1)
            in_notes = False
            continue

        # Notes section: ## Notes
        if re.match(r"^##\s+Notes\s*$", line_stripped, re.IGNORECASE):
            in_notes = True
            current_project = None
            current_task = None
            continue

        if in_notes:
            if notes:
                notes += "\n" + line.rstrip()
            elif line_stripped:
                notes = line.rstrip()
            continue

        # Project header: ## ProjectName — H:MM:SS
        m = re.match(r"^##\s+(.+?)(?:\s*[—–-]\s*(\d+:\d{2}:\d{2}))?\s*$", line_stripped)
        if m:
            current_task = None
            current_project = {
                "name": m.group(1).strip(),
                "tracked": m.group(2) or "",
                "tasks": [],
            }
            projects.append(current_project)
            continue

        # Task header: ### Task name — H:MM:SS
        m = re.match(r"^###\s+(.+?)(?:\s*[—–-]\s*(\d+:\d{2}:\d{2}))?\s*$", line_stripped)
        if m and current_project is not None:
            current_task = {
                "name": m.group(1).strip(),
                "tracked": m.group(2) or "",
                "description": "",
            }
            current_project["tasks"].append(current_task)
            continue

        # Description lines (non-empty, not a heading)
        if line_stripped and not line_stripped.startswith("#") and current_task is not None:
            if current_task["description"]:
                current_task["description"] += "\n" + line_stripped
            else:
                current_task["description"] = line_stripped

    result = {"date": date or os.path.basename(filepath).replace(".md", ""), "projects": projects}
    if notes.strip():
        result["notes"] = notes.strip()
    return result


def _write_report(filepath, data):
    """Write structured report data back to markdown."""
    lines = ["# " + data.get("date", ""), ""]

    for proj in data.get("projects", []):
        header = "## " + proj["name"]
        if proj.get("tracked"):
            header += " \u2014 " + proj["tracked"]
        lines.append(header)
        lines.append("")

        for task in proj.get("tasks", []):
            task_header = "### " + task["name"]
            if task.get("tracked"):
                task_header += " \u2014 " + task["tracked"]
            lines.append(task_header)
            if task.get("description"):
                lines.append(task["description"])
            lines.append("")

    notes = data.get("notes", "").strip()
    if notes:
        lines.append("## Notes")
        lines.append("")
        lines.append(notes)
        lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _list_report_dates(reports_dir):
    """List available report dates, newest first."""
    if not os.path.isdir(reports_dir):
        return []
    dates = []
    for name in os.listdir(reports_dir):
        if re.match(r"^\d{4}-\d{2}-\d{2}\.md$", name):
            dates.append(name.replace(".md", ""))
    dates.sort(reverse=True)
    return dates


class ReportHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the hubstaff daily reports dashboard."""

    reports_dir: str = REPORTS_DIR

    def do_GET(self):
        if self.path == "/":
            self._serve_html()
        elif self.path == "/api/dates":
            self._serve_dates()
        elif self.path.startswith("/api/report/"):
            date_str = self.path[len("/api/report/"):]
            self._serve_report(date_str)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path.startswith("/api/report/"):
            date_str = self.path[len("/api/report/"):]
            self._save_report(date_str)
        else:
            self.send_error(404)

    def _serve_html(self):
        body = HTML_PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_dates(self):
        dates = _list_report_dates(self.reports_dir)
        self._json_response(200, dates)

    def _serve_report(self, date_str):
        # Validate date format to prevent path traversal
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            self._json_response(400, {"error": "invalid date format"})
            return
        filepath = os.path.join(self.reports_dir, date_str + ".md")
        if not os.path.isfile(filepath):
            self._json_response(404, {"error": "report not found"})
            return
        try:
            data = _parse_report(filepath)
            self._json_response(200, data)
        except Exception as e:
            self._json_response(500, {"error": str(e)})

    def _save_report(self, date_str):
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            self._json_response(400, {"error": "invalid date format"})
            return
        filepath = os.path.join(self.reports_dir, date_str + ".md")
        if not os.path.isfile(filepath):
            self._json_response(404, {"error": "report not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)
            data["date"] = date_str
            _write_report(filepath, data)
            self._json_response(200, {"ok": True})
        except (json.JSONDecodeError, ValueError) as e:
            self._json_response(400, {"error": str(e)})
        except Exception as e:
            self._json_response(500, {"error": str(e)})

    def _json_response(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        if args and isinstance(args[0], str) and "/api" in args[0]:
            return
        super().log_message(fmt, *args)


def main():
    parser = argparse.ArgumentParser(description="Hubstaff daily reports dashboard")
    parser.add_argument(
        "--port", type=int, default=8788, help="Port to listen on (default: 8788)"
    )
    parser.add_argument(
        "--dir", default=REPORTS_DIR, help="Reports directory (default: ~/.hubstaff-daily)"
    )
    args = parser.parse_args()

    reports_dir = os.path.abspath(args.dir)
    if not os.path.isdir(reports_dir):
        print(f"Reports directory '{reports_dir}' does not exist yet.", file=sys.stderr)
        print("Run /hubstaff summary to generate a report first.", file=sys.stderr)
        # Still start — the dir might appear later
        os.makedirs(reports_dir, exist_ok=True)

    ReportHandler.reports_dir = reports_dir

    server = HTTPServer(("127.0.0.1", args.port), ReportHandler)
    print(f"hubstaff daily → http://localhost:{args.port}")
    print(f"reports: {reports_dir}")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
        server.server_close()


if __name__ == "__main__":
    main()
