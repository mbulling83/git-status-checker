from rich.console import Console
from rich.table import Table
from gsc.scanner import RepoStatus

console = Console()


def _row_style(repo: RepoStatus) -> str:
    if repo.error:
        return "red"
    if repo.unpushed_count > 0:
        return "red"
    if repo.uncommitted_files:
        return "yellow"
    return "green"


def build_table(repos: list[RepoStatus], show_all: bool = False) -> Table:
    """Build a rich Table from repo statuses."""
    table = Table(title="Git Status Overview")
    table.add_column("Repo", style="bold")
    table.add_column("Branch")
    table.add_column("Uncommitted", justify="right")
    table.add_column("Unpushed", justify="right")
    table.add_column("Status")

    for repo in repos:
        if repo.is_clean and not show_all:
            continue

        style = _row_style(repo)

        if repo.error:
            status = f"ERROR: {repo.error}"
        elif repo.is_clean:
            status = "Clean"
        else:
            parts = []
            if repo.uncommitted_files:
                parts.append("Dirty")
            if repo.unpushed_count > 0:
                parts.append("Unpushed")
            if not repo.has_remote:
                parts.append("No remote")
            status = ", ".join(parts)

        table.add_row(
            repo.name,
            repo.branch,
            str(len(repo.uncommitted_files)),
            str(repo.unpushed_count),
            status,
            style=style,
        )

    return table


def render_table(repos: list[RepoStatus], show_all: bool = False) -> None:
    """Print the status table to the console."""
    table = build_table(repos, show_all)
    console.print(table)
