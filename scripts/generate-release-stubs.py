#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sys
import time
import urllib.error
import urllib.request
from html import unescape
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


def _detect_project_root() -> Path:
    cwd = Path.cwd().resolve()
    if (cwd / "data").is_dir() or (cwd / "data/repo/repos.txt").exists():
        return cwd
    return Path(__file__).resolve().parents[1]


PROJECT_ROOT = _detect_project_root()
REPOS_FILE = PROJECT_ROOT / "data/repo/repos.txt"
RELEASES_DIR = PROJECT_ROOT / "data/releases"
PDF_DIR = PROJECT_ROOT / "data/pdf"

GITHUB_BASE_URL = os.environ.get("AUTORELEASENOTES_GITHUB_BASE_URL", "https://github.com").rstrip("/")
TIMEOUT_SECONDS = 5
RETRIES = 1
MAX_REDIRECTS = 5
MAX_RELEASES_PER_REPO = 10
MAX_PAGES = 10


def _out(msg: str) -> None:
    print(msg, file=sys.stdout)


def _err(msg: str) -> None:
    print(msg, file=sys.stderr)


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

    @property
    def releases_url(self) -> str:
        return f"{self.web_url}/releases"


@dataclass(frozen=True)
class RepositorySource:
    raw_ref: str
    repo_id: RepoId


@dataclass(frozen=True)
class ReleaseEntry:
    release_id: str
    published_at: str | None
    description: str
    link: str
    kind: str


@dataclass
class RunReport:
    processed_count: int = 0
    parsed_count: int = 0
    reachable_count: int = 0
    success_count: int = 0
    warning_count: int = 0
    failure_count: int = 0
    warnings: list[tuple[str, str, str]] = None  # type: ignore[assignment]
    errors: list[tuple[str, str, str]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []


def _join_url(base: str, href: str) -> str:
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if not href.startswith("/"):
        return f"{base}/{href}"
    return f"{base}{href}"


def _strip_tags_to_text(html_fragment: str) -> str:
    # Minimal deterministic HTML -> markdown-ish text.
    # Rules follow spec FR-006a minimum behavior.
    text = html_fragment

    # Block separators
    text = re.sub(r"(?is)<\s*br\s*/?\s*>", "\n", text)
    text = re.sub(r"(?is)</\s*p\s*>", "\n\n", text)
    text = re.sub(r"(?is)<\s*p\b[^>]*>", "", text)

    # Headings
    for level in range(6, 0, -1):
        text = re.sub(rf"(?is)<\s*h{level}\b[^>]*>", "#" * level + " ", text)
        text = re.sub(rf"(?is)</\s*h{level}\s*>", "\n\n", text)

    # Lists
    text = re.sub(r"(?is)<\s*/\s*ul\s*>", "\n", text)
    text = re.sub(r"(?is)<\s*/\s*ol\s*>", "\n", text)
    text = re.sub(r"(?is)<\s*li\b[^>]*>", "- ", text)
    text = re.sub(r"(?is)</\s*li\s*>", "\n", text)

    # Remove images/media entirely
    text = re.sub(r"(?is)<\s*img\b[^>]*>", "", text)
    text = re.sub(r"(?is)<\s*video\b.*?</\s*video\s*>", "", text)
    text = re.sub(r"(?is)<\s*audio\b.*?</\s*audio\s*>", "", text)
    text = re.sub(r"(?is)<\s*svg\b.*?</\s*svg\s*>", "", text)

    # Links: keep link text only
    text = re.sub(r"(?is)<\s*a\b[^>]*>", "", text)
    text = re.sub(r"(?is)</\s*a\s*>", "", text)

    # Strong/emphasis/code: keep inner text
    text = re.sub(r"(?is)<\s*/?\s*(strong|em|code|span|div|blockquote|pre)\b[^>]*>", "", text)

    # Remove remaining tags
    text = re.sub(r"(?is)<[^>]+>", "", text)

    text = unescape(text)

    # Normalize whitespace
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = text.strip()
    if text:
        text += "\n"
    return text


def _suggestion_for_error(err_code: str | None) -> str:
    if err_code is None:
        return "Verify the repository URL and your network connection."
    if err_code.startswith("http-401") or err_code.startswith("http-403"):
        return "Check whether the repository or releases page requires authentication or is blocked (403/401)."
    if err_code.startswith("http-404"):
        return "Verify the repository exists and the /releases page is accessible (404)."
    if err_code == "redirect-limit":
        return "Check for a redirect loop or unusual /releases URL behavior."
    if err_code in {"timeout", "TimeoutError"}:
        return "Retry later or increase timeout; the host may be slow or rate-limiting."
    if err_code.lower().startswith("urlerror"):
        return "Verify DNS/network connectivity and that the host is reachable."
    return "Verify URL, check rate limiting, and update parsing rules if the /releases page structure changed."


def fetch_url(
    url: str,
    *,
    timeout_seconds: int = TIMEOUT_SECONDS,
    retries: int = RETRIES,
    max_redirects: int = MAX_REDIRECTS,
) -> tuple[str | None, int | None, str | None]:
    last_err: str | None = None
    attempts = 0
    max_attempts = 1 + max(0, retries)
    while attempts < max_attempts:
        attempts += 1
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "AutoReleaseNotes"})
        opener = urllib.request.build_opener(_RedirectLimiter(max_redirects))
        try:
            with opener.open(req, timeout=timeout_seconds) as resp:
                status = getattr(resp, "status", None)
                body = resp.read().decode("utf-8", errors="replace")
                if status is not None and not (200 <= status < 400):
                    return None, status, f"http-{status}"
                return body, status, None
        except urllib.error.HTTPError as e:
            status = getattr(e, "code", None)
            last_err = f"http-{status}" if status is not None else "http-error"
            return None, status, last_err
        except Exception as e:  # noqa: BLE001
            last_err = type(e).__name__
        if attempts < max_attempts:
            time.sleep(0.2)
    return None, None, last_err


def parse_releases_page(html: str, *, base_url: str) -> tuple[list[ReleaseEntry], str | None]:
    entries: list[ReleaseEntry] = []

    # GitHub release entries commonly include "release-entry".
    blocks = re.split(r'(?is)\bclass="[^"]*release-entry[^"]*"', html)
    if len(blocks) <= 1:
        # Fallback: try to find markdown-body blocks directly.
        blocks = ["", html]

    for block in blocks[1:]:
        # Link and id
        link_m = re.search(r"(?is)href=\"(?P<href>/[^\"]+/releases/(?:tag|download)/[^\"]+)\"", block)
        if not link_m:
            link_m = re.search(r"(?is)href=\"(?P<href>/[^\"]+/releases/[^\"]+)\"", block)
        if not link_m:
            continue
        href = link_m.group("href")
        link = _join_url(base_url, href)
        release_id = href.rstrip("/").split("/")[-1]

        kind = "unknown"
        if re.search(r"(?is)\bDraft\b", block):
            kind = "draft"
        elif re.search(r"(?is)\bPre-?release\b", block):
            kind = "prerelease"
        elif re.search(r"(?is)\bRelease\b", block):
            kind = "release"

        dt_m = re.search(r"(?is)<relative-time\b[^>]*datetime=\"(?P<dt>[^\"]+)\"", block)
        published_at = dt_m.group("dt") if dt_m else None

        desc_m = re.search(r'(?is)<div\b[^>]*class="[^"]*markdown-body[^"]*"[^>]*>(?P<body>.*?)</div>', block)
        if not desc_m:
            description = ""
        else:
            description = _strip_tags_to_text(desc_m.group("body"))

        entries.append(
            ReleaseEntry(
                release_id=release_id,
                published_at=published_at,
                description=description,
                link=link,
                kind=kind,
            )
        )

    # Next page
    next_m = re.search(r"(?is)rel=\"next\"\s+href=\"(?P<href>[^\"]+)\"", html)
    next_url = _join_url(base_url, next_m.group("href")) if next_m else None
    return entries, next_url


def render_repo_markdown(repo: RepoId, entries: list[ReleaseEntry]) -> str:
    lines: list[str] = []
    lines.append(f"# {repo.normalized}\n")
    lines.append(f"Source: {repo.releases_url}\n")
    lines.append("\n")
    for e in entries:
        header_parts = [e.release_id]
        if e.published_at:
            header_parts.append(e.published_at)
        if e.kind and e.kind != "unknown":
            header_parts.append(e.kind)
        header = " | ".join(header_parts)
        lines.append(f"## {header}\n")
        lines.append(f"Link: {e.link}\n")
        lines.append("\n")
        if e.description.strip():
            lines.append(e.description.rstrip("\n") + "\n")
        else:
            lines.append("\n")
    out = "".join(lines)
    out = out.replace("\r\n", "\n").replace("\r", "\n")
    out = re.sub(r"\n{3,}", "\n\n", out)
    if not out.endswith("\n"):
        out += "\n"
    return out


def write_atomic(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


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


class _RedirectLimiter(urllib.request.HTTPRedirectHandler):
    def __init__(self, max_redirects: int) -> None:
        super().__init__()
        self._max_redirects = max_redirects
        self._redirects = 0

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[override]
        self._redirects += 1
        if self._redirects > self._max_redirects:
            raise urllib.error.HTTPError(req.full_url, code, "redirect-limit", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def http_reachable(
    url: str,
    *,
    timeout_seconds: int = TIMEOUT_SECONDS,
    retries: int = RETRIES,
    max_redirects: int = MAX_REDIRECTS,
) -> tuple[bool, int | None, str | None]:
    last_err: str | None = None
    attempts = 0
    max_attempts = 1 + max(0, retries)

    while attempts < max_attempts:
        attempts += 1
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "AutoReleaseNotes"})
        opener = urllib.request.build_opener(_RedirectLimiter(max_redirects))

        try:
            with opener.open(req, timeout=timeout_seconds) as resp:
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
    written: int = 0
    skipped_unreachable: int = 0
    skipped_duplicate: int = 0
    failed: int = 0


def main() -> int:
    repos_path = REPOS_FILE

    ensure_dir(REPOS_FILE.parent)
    ensure_dir(RELEASES_DIR)
    ensure_dir(PDF_DIR)

    if not repos_path.exists():
        _err(
            " ".join(
                [
                    f"Missing repo list: {REPOS_FILE}",
                    f"cwd={Path.cwd()}",
                    f"tried={REPOS_FILE}",
                ]
            )
        )
        return 1

    raw_text = repos_path.read_text(encoding="utf-8")
    lines = list(iter_repo_lines(raw_text))

    if not lines:
        _err(f"Repo list is empty: {repos_path}")
        return 1

    summary = Summary(processed=len(lines))
    report = RunReport(processed_count=len(lines))

    parsed_repos: list[RepoId] = []
    for line in lines:
        repo = parse_repo_ref(line)
        if repo is None:
            continue
        parsed_repos.append(repo)

    summary.parsed = len(parsed_repos)
    report.parsed_count = len(parsed_repos)

    # De-duplicate before network checks
    normalized_keys = [r.normalized.lower() for r in parsed_repos]
    unique_repos = dedup_repos(parsed_repos)
    summary.skipped_duplicate = len(normalized_keys) - len(unique_repos)

    for repo in unique_repos:
        ok, status, err_code = http_reachable(repo.releases_url)
        if not ok:
            summary.skipped_unreachable += 1
            report.warning_count += 1
            suggestion = _suggestion_for_error(err_code)
            report.warnings.append((repo.normalized, f"unreachable:{err_code or 'unknown'}", suggestion))
            _err(f"WARN {repo.normalized} unreachable status={status} err={err_code} suggestion={suggestion}")
            continue
        summary.reachable += 1
        report.reachable_count += 1

        try:
            entries: list[ReleaseEntry] = []
            next_url: str | None = repo.releases_url
            pages = 0
            while next_url and len(entries) < MAX_RELEASES_PER_REPO and pages < MAX_PAGES:
                pages += 1
                body, _, fetch_err = fetch_url(next_url)
                if body is None:
                    raise RuntimeError(fetch_err or "fetch-failed")
                page_entries, next_url = parse_releases_page(body, base_url=GITHUB_BASE_URL)
                if not page_entries and pages == 1:
                    raise RuntimeError("parse-mismatch")
                entries.extend(page_entries)

            entries = entries[:MAX_RELEASES_PER_REPO]
            md = render_repo_markdown(repo, entries)
            write_atomic(repo.output_path, md)
            summary.written += 1
            report.success_count += 1
            _out(f"WROTE {repo.output_path}")
        except Exception as e:  # noqa: BLE001
            summary.failed += 1
            report.failure_count += 1
            err_code = type(e).__name__
            suggestion = _suggestion_for_error(str(e))
            report.errors.append((repo.normalized, f"failed:{err_code}", suggestion))
            _err(f"ERROR {repo.normalized} err={err_code} suggestion={suggestion}")
            continue

    print(
        " ".join(
            [
                f"processed={summary.processed}",
                f"parsed={summary.parsed}",
                f"reachable={summary.reachable}",
                f"written={summary.written}",
                f"skipped_unreachable={summary.skipped_unreachable}",
                f"skipped_duplicate={summary.skipped_duplicate}",
                f"failed={summary.failed}",
            ]
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
