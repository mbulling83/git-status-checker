# src/gsc/actions.py
import subprocess
import questionary
from rich.console import Console
from rich.syntax import Syntax
from gsc.scanner import RepoStatus, get_repo_status

console = Console()


def _git(repo: RepoStatus, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=repo.path,
        capture_output=True,
        text=True,
    )


def show_diff(repo: RepoStatus) -> None:
    """Show the full diff for a repo (staged + unstaged)."""
    result = _git(repo, "diff")
    staged = _git(repo, "diff", "--cached")
    untracked = _git(repo, "ls-files", "--others", "--exclude-standard")

    diff_text = ""
    if result.stdout:
        diff_text += result.stdout
    if staged.stdout:
        diff_text += "\n" + staged.stdout
    if untracked.stdout:
        diff_text += "\n--- Untracked files ---\n" + untracked.stdout

    if diff_text.strip():
        syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
        console.print(syntax)
    else:
        console.print("[dim]No changes to show[/dim]")


def commit_repo(repo: RepoStatus) -> bool:
    """Stage all changes and commit with a user-provided message."""
    message = questionary.text("Commit message:").ask()
    if not message:
        console.print("[yellow]Commit cancelled[/yellow]")
        return False

    _git(repo, "add", "-A")
    result = _git(repo, "commit", "-m", message)
    if result.returncode == 0:
        console.print(f"[green]Committed to {repo.name}[/green]")
        return True
    else:
        console.print(f"[red]Commit failed: {result.stderr}[/red]")
        return False


def push_repo(repo: RepoStatus) -> bool:
    """Push the current branch to origin."""
    if not repo.has_remote:
        console.print("[red]No remote configured[/red]")
        return False

    result = _git(repo, "push")
    if result.returncode == 0:
        console.print(f"[green]Pushed {repo.name}/{repo.branch}[/green]")
        return True
    else:
        console.print(f"[red]Push failed: {result.stderr}[/red]")
        return False


def interactive_menu(repos: list[RepoStatus]) -> None:
    """Main interactive loop: pick a repo, then pick an action."""
    dirty_repos = [r for r in repos if not r.is_clean]
    if not dirty_repos:
        console.print("[green]All repos are clean![/green]")
        return

    while True:
        choices = [f"{r.name} ({r.branch}) — {len(r.uncommitted_files)} dirty, {r.unpushed_count} unpushed" for r in dirty_repos]
        choices.append("← Exit")

        selected = questionary.select("Select a repo:", choices=choices).ask()
        if selected is None or selected == "← Exit":
            break

        idx = choices.index(selected)
        repo = dirty_repos[idx]

        while True:
            action = questionary.select(
                f"[{repo.name}] What do you want to do?",
                choices=["View diff", "Commit all", "Push", "← Back"],
            ).ask()

            if action is None or action == "← Back":
                break
            elif action == "View diff":
                show_diff(repo)
            elif action == "Commit all":
                if commit_repo(repo):
                    repo = get_repo_status(repo.path)
                    dirty_repos[idx] = repo
            elif action == "Push":
                if push_repo(repo):
                    repo = get_repo_status(repo.path)
                    dirty_repos[idx] = repo

        repo = get_repo_status(repo.path)
        dirty_repos[idx] = repo
        dirty_repos = [r for r in dirty_repos if not r.is_clean]
        if not dirty_repos:
            console.print("[green]All repos are clean![/green]")
            break
