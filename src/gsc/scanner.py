import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RepoStatus:
    path: Path
    name: str
    branch: str
    uncommitted_files: list[str]
    unpushed_count: int
    is_clean: bool
    has_remote: bool
    error: str | None = None


def find_repos(directory: Path) -> list[Path]:
    """Find all direct child directories that contain a .git folder."""
    repos = []
    for child in sorted(directory.iterdir()):
        if child.is_dir() and (child / ".git").exists():
            repos.append(child)
    return repos


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """Run a git command and return the CompletedProcess."""
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
    )


def get_repo_status(repo_path: Path) -> RepoStatus:
    """Gather git status for a single repo."""
    try:
        branch = _git(repo_path, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()

        porcelain = _git(repo_path, "status", "--porcelain").stdout.strip()
        uncommitted = [line[3:] for line in porcelain.splitlines() if line.strip()] if porcelain else []

        has_remote = _git(repo_path, "remote").stdout.strip() != ""
        unpushed = 0
        if has_remote and branch != "HEAD":
            upstream_result = _git(repo_path, "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}")
            if upstream_result.returncode == 0:
                tracking = upstream_result.stdout.strip()
                count_result = _git(repo_path, "rev-list", "--count", f"{tracking}..HEAD")
                if count_result.returncode == 0:
                    unpushed = int(count_result.stdout.strip() or "0")

        return RepoStatus(
            path=repo_path,
            name=repo_path.name,
            branch=branch,
            uncommitted_files=uncommitted,
            unpushed_count=unpushed,
            is_clean=len(uncommitted) == 0 and unpushed == 0,
            has_remote=has_remote,
        )
    except Exception as e:
        return RepoStatus(
            path=repo_path,
            name=repo_path.name,
            branch="?",
            uncommitted_files=[],
            unpushed_count=0,
            is_clean=False,
            has_remote=False,
            error=str(e),
        )


def scan_all(directory: Path) -> list[RepoStatus]:
    """Scan all repos in directory in parallel, return sorted by name."""
    repos = find_repos(directory)
    if not repos:
        return []
    with ThreadPoolExecutor() as pool:
        results = list(pool.map(get_repo_status, repos))
    return sorted(results, key=lambda r: r.name.lower())
