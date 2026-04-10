# GSC (Git Status Checker) — CLI Design Spec

## Purpose

A CLI tool that scans a directory of locally cloned git repos and shows a color-coded summary of which repos have uncommitted changes, unpushed commits, or are on non-default branches. Users can then drill into any repo to view diffs, commit, and push — all from one place.

## Target User

Developer with many local repos (~66 in `~/repos/`) who wants a single-command overview of git state across all of them.

## CLI Interface

```
gsc                    # scan ~/repos, show summary table, enter interactive mode
gsc --dir /other/path  # scan a different directory
gsc --all              # include clean repos in the table
gsc status             # non-interactive: just print the table and exit
```

- Default (no subcommand): interactive dashboard
- `gsc status`: print table and exit (for scripting / quick glances)

## Core Flow

1. **Scan** the target directory for all direct child directories containing a `.git` folder (one level deep only)
2. **Gather status** for each repo in parallel using `concurrent.futures.ThreadPoolExecutor`:
   - Uncommitted changes (staged + unstaged + untracked)
   - Unpushed commits (ahead of remote tracking branch)
   - Current branch name (or "detached HEAD" if in that state)
   - Whether on a non-default branch (not `main` or `master`)
   - If a repo errors during scanning, capture the error and show it in the table rather than crashing
3. **Display a summary table** (via `rich`) — one row per repo, color-coded:
   - Green: clean and pushed
   - Yellow: uncommitted changes
   - Red: unpushed commits
   - If both uncommitted and unpushed: red (worse state wins)
   - Columns: repo name, branch, uncommitted file count, unpushed commit count
4. **Interactive menu** (via `questionary`) — select a repo to drill into:
   - View diff (syntax-highlighted via `rich`)
   - Stage all + commit (prompts for message)
   - Push
   - Back to summary table (re-scans the selected repo to refresh its status)
5. Clean repos hidden by default; shown with `--all` flag

## Architecture

```
git-status-checker/
├── pyproject.toml          # package config, entry point, dependencies
├── src/
│   └── gsc/
│       ├── __init__.py
│       ├── cli.py          # argument parsing, entry point
│       ├── scanner.py      # find git repos, gather status in parallel
│       ├── display.py      # rich table rendering
│       └── actions.py      # interactive menu, commit, push, diff viewing
```

### Module Responsibilities

**scanner.py**
- `find_repos(directory: Path) -> list[Path]`: walk directory for `.git` folders (non-recursive, top-level only)
- `get_repo_status(repo_path: Path) -> RepoStatus`: run git commands, return a dataclass with branch, uncommitted count, unpushed count, file lists
- `scan_all(directory: Path) -> list[RepoStatus]`: parallel execution of `get_repo_status` across all found repos

**display.py**
- `render_table(repos: list[RepoStatus], show_all: bool)`: build and print the rich table with color coding

**actions.py**
- `interactive_menu(repos: list[RepoStatus])`: questionary-based repo selection loop
- `show_diff(repo: RepoStatus)`: display syntax-highlighted diff
- `commit_repo(repo: RepoStatus)`: stage all, prompt for message, commit
- `push_repo(repo: RepoStatus)`: push current branch to origin

**cli.py**
- Parse args with `argparse`
- Orchestrate: scan -> display -> (optionally) interactive menu

### Data Model

```python
@dataclass
class RepoStatus:
    path: Path
    name: str
    branch: str
    uncommitted_files: list[str]
    unpushed_count: int
    is_clean: bool
    has_remote: bool
```

## Dependencies

- `rich` — table rendering, syntax-highlighted diffs
- `questionary` — interactive selection menus
- Python 3.10+ (for modern type hints)

## Installation

```
pip install -e .
```

Registers `gsc` as a console script entry point.
