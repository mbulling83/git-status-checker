import tempfile
from pathlib import Path
from gsc.scanner import find_repos


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
