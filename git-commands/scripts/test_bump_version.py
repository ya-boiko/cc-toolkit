#!/usr/bin/env python3
"""Tests for bump_version.py"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent / "bump_version.py"


def run(file_path: str, version: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), file_path, version],
        capture_output=True, text=True
    )


class TestPackageJson(unittest.TestCase):
    def test_bumps_version(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "package.json"
            path.write_text(json.dumps({"name": "my-app", "version": "1.0.0"}))
            result = run(str(path), "1.2.3")
            self.assertEqual(result.returncode, 0)
            data = json.loads(path.read_text())
            self.assertEqual(data["version"], "1.2.3")

    def test_exit_nonzero_when_no_version_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "package.json"
            path.write_text(json.dumps({"name": "my-app"}))
            result = run(str(path), "1.2.3")
            self.assertNotEqual(result.returncode, 0)

    def test_exit_nonzero_when_file_not_found(self):
        result = run("/nonexistent/package.json", "1.2.3")
        self.assertNotEqual(result.returncode, 0)


class TestPyprojectToml(unittest.TestCase):
    def test_bumps_project_version(self):
        content = '[project]\nname = "myapp"\nversion = "0.1.0"\n'
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "pyproject.toml"
            path.write_text(content)
            result = run(str(path), "0.2.0")
            self.assertEqual(result.returncode, 0)
            self.assertIn('version = "0.2.0"', path.read_text())

    def test_bumps_poetry_version(self):
        content = '[tool.poetry]\nname = "myapp"\nversion = "1.0.0"\n'
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "pyproject.toml"
            path.write_text(content)
            result = run(str(path), "2.0.0")
            self.assertEqual(result.returncode, 0)
            self.assertIn('version = "2.0.0"', path.read_text())

    def test_bumps_both_sections(self):
        content = (
            '[project]\nversion = "1.0.0"\n\n'
            '[tool.poetry]\nversion = "1.0.0"\n'
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "pyproject.toml"
            path.write_text(content)
            result = run(str(path), "1.1.0")
            self.assertEqual(result.returncode, 0)
            text = path.read_text()
            self.assertEqual(text.count('version = "1.1.0"'), 2)

    def test_handles_short_version_string(self):
        content = '[project]\nversion = "0.1"\n'
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "pyproject.toml"
            path.write_text(content)
            result = run(str(path), "0.2.0")
            self.assertEqual(result.returncode, 0)
            self.assertIn('version = "0.2.0"', path.read_text())

    def test_exit_nonzero_when_no_version(self):
        content = '[project]\nname = "myapp"\n'
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "pyproject.toml"
            path.write_text(content)
            result = run(str(path), "1.0.0")
            self.assertNotEqual(result.returncode, 0)


class TestCargoToml(unittest.TestCase):
    def test_bumps_version(self):
        content = '[package]\nname = "myapp"\nversion = "0.1.0"\n'
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "Cargo.toml"
            path.write_text(content)
            result = run(str(path), "0.2.0")
            self.assertEqual(result.returncode, 0)
            self.assertIn('version = "0.2.0"', path.read_text())


if __name__ == "__main__":
    unittest.main()
