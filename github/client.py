"""GitHub REST client for specs and PR comments."""

from __future__ import annotations

import os
from pathlib import Path

from github import Github
from github.PullRequest import PullRequest


SPEC_LABELS = {"qa", "user-story", "feature-spec", "enhancement"}


class GitHubClient:
    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self._gh = Github(self.token) if self.token else None

    @property
    def available(self) -> bool:
        return self._gh is not None

    def _repo(self, full_name: str):
        if not self._gh:
            raise RuntimeError("GITHUB_TOKEN is required for GitHub operations")
        return self._gh.get_repo(full_name)

    def fetch_labeled_issues(self, repo_full_name: str, labels: set[str] | None = None) -> list[dict]:
        """Fetch open issues with QA-related labels."""
        labels = labels or SPEC_LABELS
        repo = self._repo(repo_full_name)
        results = []
        for issue in repo.get_issues(state="open"):
            issue_labels = {lbl.name.lower() for lbl in issue.labels}
            if issue_labels & labels:
                results.append(
                    {
                        "number": issue.number,
                        "title": issue.title,
                        "body": issue.body or "",
                        "labels": list(issue_labels),
                        "url": issue.html_url,
                    }
                )
        return results

    def fetch_pr_body(self, repo_full_name: str, pr_number: int) -> str:
        """Fetch PR description body."""
        repo = self._repo(repo_full_name)
        pr: PullRequest = repo.get_pull(pr_number)
        return pr.body or ""

    def fetch_spec_files(self, repo_full_name: str, paths: list[str] | None = None) -> list[str]:
        """Fetch markdown spec files from the product repo."""
        paths = paths or ["docs/specs/", "CHANGELOG.md", "README.md"]
        repo = self._repo(repo_full_name)
        contents: list[str] = []

        for path in paths:
            try:
                if path.endswith("/"):
                    for item in repo.get_contents(path):
                        if item.path.endswith(".md"):
                            file_content = repo.get_contents(item.path)
                            contents.append(file_content.decoded_content.decode("utf-8"))
                else:
                    file_content = repo.get_contents(path)
                    contents.append(file_content.decoded_content.decode("utf-8"))
            except Exception:
                continue

        return contents

    def post_pr_comment(self, repo_full_name: str, pr_number: int, body: str) -> None:
        """Post a comment on a pull request."""
        repo = self._repo(repo_full_name)
        pr: PullRequest = repo.get_pull(pr_number)
        pr.create_issue_comment(body)

    def download_spec_to_local(
        self,
        repo_full_name: str,
        output_dir: str | Path,
    ) -> list[str]:
        """Download spec content and save locally. Returns local file paths."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        issues = self.fetch_labeled_issues(repo_full_name)
        paths: list[str] = []

        for issue in issues:
            filename = f"issue-{issue['number']}.md"
            path = output_dir / filename
            content = f"# {issue['title']}\n\n{issue['body']}"
            path.write_text(content, encoding="utf-8")
            paths.append(str(path))

        for i, spec_content in enumerate(self.fetch_spec_files(repo_full_name)):
            path = output_dir / f"spec-{i}.md"
            path.write_text(spec_content, encoding="utf-8")
            paths.append(str(path))

        return paths
