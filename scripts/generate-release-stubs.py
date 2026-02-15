#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPOS_FILE = Path("data/repo/repos.txt")
RELEASES_DIR = Path("data/releases")

GITHUB_BASE_URL = os.environ.get("AUTORELEASENOTES_GITHUB_BASE_URL", "https://github.com").rstrip("/")
TIMEOUT_SECONDS = 5
RETRIES = 1


@dataclass(frozen=True)
class RepoId:
    owner: str
    repo: str

    @property
    def normalized(self) -> str:
        return f"{self.owner}/{self.repo}"

    @property
    def output_filename(self) -> str:
        return f"{self.owner}__{self.repo}.md"

    @property
    def output_path(self) -> Path:
        return RELEASES_DIR / self.output_filename

    @property
    def web_url(self) -> str:
        return f"{GITHUB_BASE_URL}/{self.owner}/{self.repo}"


_RE_OWNER_REPO = re.compile(r"^(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+)$")
_RE_GH_HTTPS = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)


def iter_repo_lines(text: str) -> Iterable[str]:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.lstrip().startswith("#"):
            continue
        yield line


def parse_repo_ref(line: str) -> RepoId | None:
    m = _RE_OWNER_REPO.match(line)
    if m:
        return RepoId(owner=m.group("owner"), repo=m.group("repo"))

    m = _RE_GH_HTTPS.match(line)
    if m:
        owner = m.group("owner")
        repo = m.group("repo")
        return RepoId(owner=owner, repo=repo)

    return None


def dedup_repos(repos: Iterable[RepoId]) -> list[RepoId]:
    seen: set[str] = set()
    out: list[RepoId] = []
    for r in repos:
        key = r.normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def http_reachable(url: str, *, timeout_seconds: int = TIMEOUT_SECONDS, retries: int = RETRIES) -> tuple[bool, int | None, str | None]:
    last_err: str | None = None
    attempts = 0
    max_attempts = 1 + max(0, retries)

    while attempts < max_attempts:
        attempts += 1
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "AutoReleaseNotes"})

        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                status = getattr(resp, "status", None)
                if status is None:
                    return True, None, None
                if 200 <= status < 400:
                    return True, status, None
                if status in (401, 403, 404):
                    return False, status, f"http-{status}"
                return False, status, f"http-{status}"
        except urllib.error.HTTPError as e:
            status = getattr(e, "code", None)
            if status in (401, 403, 404):
                return False, status, f"http-{status}"
            last_err = f"http-{status}" if status is not None else "http-error"
        except Exception as e:  # noqa: BLE001
            last_err = type(e).__name__

        if attempts < max_attempts:
            time.sleep(0.1)

    return False, None, last_err


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def create_empty_file_if_missing(path: Path) -> bool:
    if path.exists():
        return False
    ensure_dir(path.parent)
    path.touch(exist_ok=False)
    return True


@dataclass
class Summary:
    processed: int = 0
    parsed: int = 0
    reachable: int = 0
    created: int = 0
    skipped_unreachable: int = 0
    skipped_duplicate: int = 0
    skipped_exists: int = 0


def main() -> int:
    repos_path = REPOS_FILE

    if not repos_path.exists():
        print(f"Missing repo list: {repos_path}", file=sys.stderr)
        return 1

    raw_text = repos_path.read_text(encoding="utf-8")
    lines = list(iter_repo_lines(raw_text))

    summary = Summary(processed=len(lines))

    parsed_repos: list[RepoId] = []
    for line in lines:
        repo = parse_repo_ref(line)
        if repo is None:
            continue
        parsed_repos.append(repo)

    summary.parsed = len(parsed_repos)

    # De-duplicate before network checks
    normalized_keys = [r.normalized.lower() for r in parsed_repos]
    unique_repos = dedup_repos(parsed_repos)
    summary.skipped_duplicate = len(normalized_keys) - len(unique_repos)

    for repo in unique_repos:
        ok, _, _ = http_reachable(repo.web_url)
        if not ok:
            summary.skipped_unreachable += 1
            continue
        summary.reachable += 1

        created = create_empty_file_if_missing(repo.output_path)
        if created:
            summary.created += 1
        else:
            summary.skipped_exists += 1

    print(
        " ".join(
            [
                f"processed={summary.processed}",
                f"parsed={summary.parsed}",
                f"reachable={summary.reachable}",
                f"created={summary.created}",
                f"skipped_unreachable={summary.skipped_unreachable}",
                f"skipped_duplicate={summary.skipped_duplicate}",
                f"skipped_exists={summary.skipped_exists}",
            ]
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
