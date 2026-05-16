"""GitHub PR reporter: creates or updates a pull request with the dependency audit summary."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

import requests

from src.detectors.registry import summary as build_summary
from src.reporters.markdown_reporter import MarkdownReporter


GITHUB_API_BASE = "https://api.github.com"


@dataclass
class GitHubPRReporter:
    """Opens or updates a GitHub PR with the dependency audit report."""

    token: str
    repo: str  # e.g. "owner/repo"
    base_branch: str = "main"
    head_branch: str = "depcheck/audit"
    pr_title: str = "chore: dependency audit report"
    labels: list[str] = field(default_factory=lambda: ["dependencies", "automated"])

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _api(self, path: str) -> str:
        return f"{GITHUB_API_BASE}/repos/{self.repo}{path}"

    def find_existing_pr(self) -> Optional[int]:
        """Return the PR number if a depcheck PR already exists, else None."""
        resp = requests.get(
            self._api("/pulls"),
            headers=self._headers,
            params={"head": f"{self.repo.split('/')[0]}:{self.head_branch}", "state": "open"},
            timeout=15,
        )
        resp.raise_for_status()
        prs = resp.json()
        return prs[0]["number"] if prs else None

    def create_or_update_pr(self, body: str) -> dict:
        """Create a new PR or update the body of an existing one."""
        pr_number = self.find_existing_pr()
        if pr_number:
            resp = requests.patch(
                self._api(f"/pulls/{pr_number}"),
                headers=self._headers,
                json={"body": body},
                timeout=15,
            )
        else:
            resp = requests.post(
                self._api("/pulls"),
                headers=self._headers,
                json={
                    "title": self.pr_title,
                    "head": self.head_branch,
                    "base": self.base_branch,
                    "body": body,
                },
                timeout=15,
            )
        resp.raise_for_status()
        return resp.json()

    def report(self, detection_results: list) -> dict:
        """Build markdown from detection results and open/update a PR."""
        reporter = MarkdownReporter()
        summary = build_summary(detection_results)
        body = reporter.render(detection_results, summary)
        return self.create_or_update_pr(body)
