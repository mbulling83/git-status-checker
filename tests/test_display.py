from pathlib import Path
from io import StringIO
from rich.console import Console
from gsc.scanner import RepoStatus
from gsc.display import build_table


def _make_status(name="repo", branch="main", uncommitted=None, unpushed=0, has_remote=True, error=None):
    uncommitted = uncommitted or []
    return RepoStatus(
        path=Path(f"/fake/{name}"),
        name=name,
        branch=branch,
        uncommitted_files=uncommitted,
        unpushed_count=unpushed,
        is_clean=len(uncommitted) == 0 and unpushed == 0 and error is None,
        has_remote=has_remote,
        error=error,
    )


def test_build_table_excludes_clean_by_default():
    repos = [
        _make_status("clean-repo"),
        _make_status("dirty-repo", uncommitted=["file.txt"]),
    ]
    table = build_table(repos, show_all=False)
    console = Console(file=StringIO(), width=120)
    console.print(table)
    output = console.file.getvalue()
    assert "dirty-repo" in output
    assert "clean-repo" not in output


def test_build_table_includes_clean_with_show_all():
    repos = [
        _make_status("clean-repo"),
        _make_status("dirty-repo", uncommitted=["file.txt"]),
    ]
    table = build_table(repos, show_all=True)
    console = Console(file=StringIO(), width=120)
    console.print(table)
    output = console.file.getvalue()
    assert "dirty-repo" in output
    assert "clean-repo" in output
