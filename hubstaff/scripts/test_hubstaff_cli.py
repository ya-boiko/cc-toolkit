#!/usr/bin/env python3
"""Tests for hubstaff_cli.py wrapper."""
import datetime
import json
import subprocess
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import hubstaff_cli


def mock_cli_response(data, returncode=0, stderr=""):
    """Create a mock subprocess.run result."""
    result = MagicMock()
    result.stdout = json.dumps(data) if isinstance(data, dict) else data
    result.stderr = stderr
    result.returncode = returncode
    return result


class TestStatus(unittest.TestCase):
    @patch("hubstaff_cli.run_cli")
    def test_tracking_with_task(self, mock_run):
        mock_run.return_value = {
            "active_project": {"id": 657263, "name": "Proko", "tracked_today": "2:53:45"},
            "active_task": {"id": 159784427, "name": "migrate data"},
            "tracking": True,
        }
        output = hubstaff_cli.cmd_status()
        self.assertIn("Proko", output)
        self.assertIn("migrate data", output)
        self.assertIn("2:53:45", output)

    @patch("hubstaff_cli.run_cli")
    def test_tracking_without_task(self, mock_run):
        mock_run.return_value = {
            "active_project": {"id": 657263, "name": "Proko", "tracked_today": "1:00:00"},
            "active_task": None,
            "tracking": True,
        }
        output = hubstaff_cli.cmd_status()
        self.assertIn("Proko", output)
        self.assertIn("1:00:00", output)

    @patch("hubstaff_cli.run_cli")
    def test_not_tracking(self, mock_run):
        mock_run.return_value = {"tracking": False}
        output = hubstaff_cli.cmd_status()
        self.assertEqual(output, "Not tracking")


class TestProjects(unittest.TestCase):
    @patch("hubstaff_cli.run_cli")
    def test_list_projects(self, mock_run):
        mock_run.return_value = {
            "projects": [
                {"id": 657263, "name": "Proko"},
                {"id": 123456, "name": "Other"},
            ]
        }
        output = hubstaff_cli.cmd_projects()
        self.assertIn("[657263] Proko", output)
        self.assertIn("[123456] Other", output)


class TestTasks(unittest.TestCase):
    @patch("hubstaff_cli.run_cli")
    def test_tasks_with_project_id(self, mock_run):
        mock_run.return_value = {
            "tasks": [
                {"id": 100, "summary": "Task A"},
                {"id": 200, "summary": "Task B"},
            ]
        }
        output = hubstaff_cli.cmd_tasks("657263")
        self.assertIn("[100] Task A", output)
        self.assertIn("[200] Task B", output)

    @patch("hubstaff_cli.run_cli")
    def test_tasks_from_status(self, mock_run):
        mock_run.side_effect = [
            {"active_project": {"id": 657263, "name": "Proko", "tracked_today": "0:00:00"}, "tracking": True},
            {"tasks": [{"id": 100, "summary": "Task A"}]},
        ]
        output = hubstaff_cli.cmd_tasks(None)
        self.assertIn("[100] Task A", output)

    @patch("hubstaff_cli.run_cli")
    def test_tasks_no_project_not_tracking(self, mock_run):
        mock_run.return_value = {"tracking": False}
        with self.assertRaises(SystemExit):
            hubstaff_cli.cmd_tasks(None)


class TestStart(unittest.TestCase):
    @patch("hubstaff_cli.run_cli")
    def test_start_task(self, mock_run):
        mock_run.return_value = {
            "active_task": {"id": 100, "name": "Task A"},
            "tracking": True,
        }
        output = hubstaff_cli.cmd_start("100")
        self.assertIn("Started", output)
        self.assertIn("Task A", output)


class TestStop(unittest.TestCase):
    @patch("hubstaff_cli.run_cli")
    def test_stop(self, mock_run):
        mock_run.return_value = {"status": "Stopped the timer"}
        output = hubstaff_cli.cmd_stop()
        self.assertEqual(output, "Stopped")


class TestResume(unittest.TestCase):
    @patch("hubstaff_cli.run_cli")
    def test_resume(self, mock_run):
        mock_run.return_value = {"status": "Started tracking task foo"}
        output = hubstaff_cli.cmd_resume()
        self.assertEqual(output, "Resumed")


class TestSummary(unittest.TestCase):
    @patch("hubstaff_cli._try_cli_command")
    def test_per_task_data_from_daily_activities(self, mock_try):
        def side_effect(*args):
            if args[0] == "daily_activities":
                return {
                    "daily_activities": [
                        {"project": {"name": "Proko"}, "task": {"name": "migrate data"}, "tracked": "2:10:00"},
                        {"project": {"name": "Proko"}, "task": {"name": "add RBAC"}, "tracked": "3:13:00"},
                    ]
                }
            return None
        mock_try.side_effect = side_effect
        result = json.loads(hubstaff_cli.cmd_summary())
        self.assertTrue(result["per_task"])
        self.assertEqual(len(result["projects"]), 1)
        self.assertEqual(result["projects"][0]["name"], "Proko")
        self.assertEqual(len(result["projects"][0]["tasks"]), 2)
        self.assertEqual(result["projects"][0]["tasks"][0]["name"], "migrate data")

    @patch("hubstaff_cli.run_cli")
    @patch("hubstaff_cli._try_cli_command")
    def test_fallback_to_status_when_no_activities_command(self, mock_try, mock_run):
        mock_try.return_value = None
        mock_run.return_value = {
            "active_project": {"name": "Proko", "tracked_today": "5:23:00"},
            "tracking": True,
        }
        result = json.loads(hubstaff_cli.cmd_summary())
        self.assertFalse(result["per_task"])
        self.assertEqual(result["projects"][0]["name"], "Proko")
        self.assertEqual(result["projects"][0]["tracked"], "5:23:00")
        self.assertEqual(result["projects"][0]["tasks"], [])

    @patch("hubstaff_cli.run_cli")
    @patch("hubstaff_cli._try_cli_command")
    def test_fallback_when_not_tracking(self, mock_try, mock_run):
        mock_try.return_value = None
        mock_run.return_value = {"tracking": False}
        result = json.loads(hubstaff_cli.cmd_summary())
        self.assertFalse(result["per_task"])
        self.assertEqual(result["projects"], [])

    @patch("hubstaff_cli.run_cli")
    @patch("hubstaff_cli._try_cli_command")
    def test_summary_includes_date(self, mock_try, mock_run):
        mock_try.return_value = None
        mock_run.return_value = {"tracking": False}
        result = json.loads(hubstaff_cli.cmd_summary())
        self.assertEqual(result["date"], datetime.date.today().isoformat())


class TestRunCli(unittest.TestCase):
    @patch("subprocess.run")
    def test_json_error(self, mock_run):
        mock_run.return_value = mock_cli_response(
            {"error": "Scripted control is prompting user"}, returncode=1
        )
        with self.assertRaises(SystemExit):
            hubstaff_cli.run_cli("status")

    @patch("subprocess.run")
    def test_stderr_error(self, mock_run):
        result = MagicMock()
        result.stdout = ""
        result.stderr = "Connection refused"
        result.returncode = 1
        mock_run.return_value = result
        with self.assertRaises(SystemExit):
            hubstaff_cli.run_cli("status")

    @patch("subprocess.run")
    def test_cli_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        with self.assertRaises(SystemExit):
            hubstaff_cli.run_cli("status")


if __name__ == "__main__":
    unittest.main()
