import subprocess
import tempfile
from pathlib import Path
from gsc.scanner import find_repos, get_repo_status, RepoStatus


def _run_git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=True)


def _init_repo(path: Path) -> Path:
    """Create a real git repo with one commit."""
    path.mkdir(parents=True, exist_ok=True)
    _run_git(path, "init")
    _run_git(path, "config", "user.email", "test@test.com")
    _run_git(path, "config", "user.name", "Test")
    (path / "README.md").write_text("hello")
    _run_git(path, "add", ".")
    _run_git(path, "commit", "-m", "init")
    return path


def test_find_repos_discovers_git_directories():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        (base / "repo-a" / ".git").mkdir(parents=True)
        (base / "repo-b" / ".git").mkdir(parents=True)
        (base / "not-a-repo").mkdir()
        (base / "parent" / "nested" / ".git").mkdir(parents=True)

        repos = find_repos(base)
        names = sorted(r.name for r in repos)
        assert names == ["repo-a", "repo-b"]


def test_find_repos_returns_empty_for_no_repos():
    with tempfile.TemporaryDirectory() as tmp:
        assert find_repos(Path(tmp)) == []


def test_get_repo_status_clean():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _init_repo(Path(tmp) / "myrepo")
        status = get_repo_status(repo)

        assert status.name == "myrepo"
        assert status.branch in ("main", "master")
        assert status.uncommitted_files == []
        assert status.unpushed_count == 0
        assert status.is_clean is True


def test_get_repo_status_uncommitted():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _init_repo(Path(tmp) / "dirty")
        (repo / "new_file.txt").write_text("uncommitted")

        status = get_repo_status(repo)

        assert len(status.uncommitted_files) == 1
        assert status.is_clean is False
