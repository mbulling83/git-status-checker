# gsc — Git Status Checker

A CLI tool that scans a directory of locally cloned git repos and shows a color-coded summary of which repos have uncommitted changes, unpushed commits, or are on non-default branches. Drill into any repo to view diffs, commit, and push — all from one place.

## Install

```bash
pip install -e .
```

This registers the `gsc` command.

## Usage

```bash
gsc                    # show status table + interactive menu
gsc status             # just print the table and exit
gsc --all              # include clean repos in the table
gsc --dir /other/path  # scan a different directory (default: ~/repos)
```

### Status table

Each repo gets a row, color-coded:

- **Green** — clean and pushed
- **Yellow** — uncommitted changes
- **Red** — unpushed commits

### Interactive mode

When you run `gsc` without `status`, you can select a repo and:

- **View diff** — syntax-highlighted diff of all changes
- **Commit all** — stage everything and commit with a message you provide
- **Push** — push the current branch to origin

After each action the status refreshes automatically.

## Requirements

- Python 3.10+
- git
