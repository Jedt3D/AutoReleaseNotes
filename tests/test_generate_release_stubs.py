import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        # Respond based on path to simulate reachable/unreachable and redirect.
        if self.path in ("/ok-owner/ok-repo/releases", "/redir-owner/redir-repo/releases"):
            if self.path == "/redir-owner/redir-repo/releases":
                self.send_response(302)
                self.send_header("Location", "/ok-owner/ok-repo/releases")
                self.end_headers()
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            # Minimal HTML resembling GitHub releases list structure.
            self.wfile.write(
                (
                    "<html><body>"
                    "<div class=\"release-entry\">"
                    "<a href=\"/ok-owner/ok-repo/releases/tag/v1.0.0\">v1.0.0</a>"
                    "<relative-time datetime=\"2026-01-01T00:00:00Z\"></relative-time>"
                    "<div class=\"markdown-body\"><p>Hello<br>World</p><ul><li>One</li></ul></div>"
                    "</div>"
                    "</body></html>"
                ).encode("utf-8")
            )
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):  # noqa: A002
        # Silence server logs during tests.
        return


@pytest.fixture()
def http_server_base_url():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    host, port = server.server_address
    base_url = f"http://{host}:{port}"

    try:
        yield base_url
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.fixture()
def temp_repo_root(tmp_path: Path):
    (tmp_path / "data/repo").mkdir(parents=True)
    return tmp_path


def _run_script(repo_root: Path, script_path: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    merged_env.update(env)

    return subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(repo_root),
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )


def _parse_summary(stdout: str) -> dict[str, int]:
    parts = [p for p in stdout.strip().split() if "=" in p]
    out: dict[str, int] = {}
    for p in parts:
        k, v = p.split("=", 1)
        out[k] = int(v)
    return out


def test_given_reachable_and_unreachable_when_run_then_create_only_reachable_stub(temp_repo_root: Path, http_server_base_url: str):
    # Given
    repos_txt = temp_repo_root / "data/repo/repos.txt"
    repos_txt.write_text(
        "\n".join(
            [
                "ok-owner/ok-repo",
                "missing-owner/missing-repo",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    script_path = Path(__file__).resolve().parents[1] / "scripts/generate-release-stubs.py"

    # When
    result = _run_script(
        temp_repo_root,
        script_path,
        {
            "AUTORELEASENOTES_GITHUB_BASE_URL": http_server_base_url,
        },
    )

    # Then
    assert result.returncode == 0, result.stderr

    created = temp_repo_root / "data/releases/ok-owner__ok-repo.md"
    missing = temp_repo_root / "data/releases/missing-owner__missing-repo.md"

    assert created.exists()
    assert created.stat().st_size > 0
    assert not missing.exists()


def test_given_redirect_when_run_then_treat_as_reachable(temp_repo_root: Path, http_server_base_url: str):
    # Given
    repos_txt = temp_repo_root / "data/repo/repos.txt"
    repos_txt.write_text("redir-owner/redir-repo\n", encoding="utf-8")

    script_path = Path(__file__).resolve().parents[1] / "scripts/generate-release-stubs.py"

    # When
    result = _run_script(
        temp_repo_root,
        script_path,
        {
            "AUTORELEASENOTES_GITHUB_BASE_URL": http_server_base_url,
        },
    )

    # Then
    assert result.returncode == 0, result.stderr

    created = temp_repo_root / "data/releases/redir-owner__redir-repo.md"
    assert created.exists()
    assert created.stat().st_size > 0


def test_given_existing_stub_when_run_then_do_not_overwrite(temp_repo_root: Path, http_server_base_url: str):
    # Given
    releases_dir = temp_repo_root / "data/releases"
    releases_dir.mkdir(parents=True, exist_ok=True)
    existing = releases_dir / "ok-owner__ok-repo.md"
    existing.write_text("do overwrite", encoding="utf-8")

    repos_txt = temp_repo_root / "data/repo/repos.txt"
    repos_txt.write_text("ok-owner/ok-repo\n", encoding="utf-8")

    script_path = Path(__file__).resolve().parents[1] / "scripts/generate-release-stubs.py"

    # When
    result = _run_script(
        temp_repo_root,
        script_path,
        {
            "AUTORELEASENOTES_GITHUB_BASE_URL": http_server_base_url,
        },
    )

    # Then
    assert result.returncode == 0, result.stderr
    assert "# ok-owner/ok-repo" in existing.read_text(encoding="utf-8")

    summary = _parse_summary(result.stdout)
    assert summary["reachable"] == 1
    assert summary["written"] == 1


def test_given_owner_repo_and_https_url_when_run_then_normalize_and_dedup(temp_repo_root: Path, http_server_base_url: str):
    # Given
    repos_txt = temp_repo_root / "data/repo/repos.txt"
    repos_txt.write_text(
        "\n".join(
            [
                "ok-owner/ok-repo",
                "https://github.com/ok-owner/ok-repo.git",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    script_path = Path(__file__).resolve().parents[1] / "scripts/generate-release-stubs.py"

    # When
    result = _run_script(
        temp_repo_root,
        script_path,
        {
            "AUTORELEASENOTES_GITHUB_BASE_URL": http_server_base_url,
        },
    )

    # Then
    assert result.returncode == 0, result.stderr

    created = temp_repo_root / "data/releases/ok-owner__ok-repo.md"
    assert created.exists()
    assert created.stat().st_size > 0

    summary = _parse_summary(result.stdout)
    assert summary["processed"] == 2
    assert summary["parsed"] == 2
    assert summary["skipped_duplicate"] == 1
    assert summary["written"] == 1


def test_given_comments_and_blank_lines_when_run_then_ignore_them(temp_repo_root: Path, http_server_base_url: str):
    # Given
    repos_txt = temp_repo_root / "data/repo/repos.txt"
    repos_txt.write_text(
        "\n".join(
            [
                "   # comment",
                "",
                "ok-owner/ok-repo",
                "   ",
                "# another",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    script_path = Path(__file__).resolve().parents[1] / "scripts/generate-release-stubs.py"

    # When
    result = _run_script(
        temp_repo_root,
        script_path,
        {
            "AUTORELEASENOTES_GITHUB_BASE_URL": http_server_base_url,
        },
    )

    # Then
    assert result.returncode == 0, result.stderr
    summary = _parse_summary(result.stdout)
    assert summary["processed"] == 1
    assert (temp_repo_root / "data/releases/ok-owner__ok-repo.md").exists()
