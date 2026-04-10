# src/gsc/cli.py
import argparse
from pathlib import Path

from gsc.scanner import scan_all
from gsc.display import render_table
from gsc.actions import interactive_menu


def main():
    parser = argparse.ArgumentParser(
        prog="gsc",
        description="Git Status Checker — overview of all your repos",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path.home() / "repos",
        help="Directory to scan for git repos (default: ~/repos)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="show_all",
        help="Show clean repos too",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default=None,
        choices=["status"],
        help="'status' for non-interactive mode",
    )

    args = parser.parse_args()

    if not args.dir.is_dir():
        print(f"Error: {args.dir} is not a directory")
        raise SystemExit(1)

    repos = scan_all(args.dir)
    if not repos:
        print(f"No git repos found in {args.dir}")
        raise SystemExit(0)

    render_table(repos, show_all=args.show_all)

    if args.command is None:
        interactive_menu(repos)


if __name__ == "__main__":
    main()
