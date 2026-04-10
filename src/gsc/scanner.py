from pathlib import Path


def find_repos(directory: Path) -> list[Path]:
    """Find all direct child directories that contain a .git folder."""
    repos = []
    for child in sorted(directory.iterdir()):
        if child.is_dir() and (child / ".git").exists():
            repos.append(child)
    return repos
