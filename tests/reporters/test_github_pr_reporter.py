"""Tests for GitHubPRReporter."""

from __future__ import annotations

from unittest import TestCase
from unittest.mock import MagicMock, patch

from src.reporters.github_pr_reporter import GitHubPRReporter
from src.detectors.base import DetectionResult, Dependency


class TestGitHubPRReporter(TestCase):
    def setUp(self):
        self.reporter = GitHubPRReporter(
            token="ghp_test123",
            repo="acme/myrepo",
            base_branch="main",
            head_branch="depcheck/audit",
        )
        self.sample_results = [
            DetectionResult(
                ecosystem="python",
                manifest="requirements.txt",
                dependencies=[
                    Dependency(name="requests", current_version="2.28.0", latest_version="2.32.0"),
                    Dependency(name="flask", current_version="3.0.0", latest_version="3.0.0"),
                ],
            )
        ]

    def test_headers_contain_auth(self):
        headers = self.reporter._headers
        self.assertIn("Authorization", headers)
        self.assertTrue(headers["Authorization"].startswith("Bearer "))

    def test_api_url_construction(self):
        url = self.reporter._api("/pulls")
        self.assertEqual(url, "https://api.github.com/repos/acme/myrepo/pulls")

    @patch("src.reporters.github_pr_reporter.requests.get")
    def test_find_existing_pr_returns_number(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"number": 42}]
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = self.reporter.find_existing_pr()
        self.assertEqual(result, 42)

    @patch("src.reporters.github_pr_reporter.requests.get")
    def test_find_existing_pr_returns_none_when_empty(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = self.reporter.find_existing_pr()
        self.assertIsNone(result)

    @patch("src.reporters.github_pr_reporter.requests.get")
    @patch("src.reporters.github_pr_reporter.requests.post")
    def test_creates_pr_when_none_exists(self, mock_post, mock_get):
        mock_get.return_value = MagicMock(json=lambda: [], raise_for_status=lambda: None)
        mock_post.return_value = MagicMock(
            json=lambda: {"number": 7, "html_url": "https://github.com/acme/myrepo/pull/7"},
            raise_for_status=lambda: None,
        )

        result = self.reporter.create_or_update_pr("## Report")
        self.assertEqual(result["number"], 7)
        mock_post.assert_called_once()

    @patch("src.reporters.github_pr_reporter.requests.get")
    @patch("src.reporters.github_pr_reporter.requests.patch")
    def test_updates_pr_when_exists(self, mock_patch, mock_get):
        mock_get.return_value = MagicMock(json=lambda: [{"number": 3}], raise_for_status=lambda: None)
        mock_patch.return_value = MagicMock(
            json=lambda: {"number": 3},
            raise_for_status=lambda: None,
        )

        result = self.reporter.create_or_update_pr("## Updated")
        self.assertEqual(result["number"], 3)
        mock_patch.assert_called_once()

    @patch("src.reporters.github_pr_reporter.requests.get")
    @patch("src.reporters.github_pr_reporter.requests.post")
    def test_report_calls_create_or_update_with_markdown(self, mock_post, mock_get):
        mock_get.return_value = MagicMock(json=lambda: [], raise_for_status=lambda: None)
        mock_post.return_value = MagicMock(
            json=lambda: {"number": 1},
            raise_for_status=lambda: None,
        )

        result = self.reporter.report(self.sample_results)
        self.assertIn("number", result)
        _, kwargs = mock_post.call_args
        body = kwargs["json"]["body"]
        self.assertIn("requests", body)
