"""Command-line entry point for the Paint Tracker server.

Usage::

    paint-tracker [--host HOST] [--port PORT] [--no-update-check]

On startup the CLI will:

1. Check PyPI for a newer version and prompt the user to upgrade.
2. Auto-configure the database (SQLite at
   ``~/.local/share/paint-tracker/paint_tracker.db`` unless
   ``DATABASE_URL`` is set).
3. Launch the uvicorn ASGI server.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import subprocess
import sys

from paint_tracker import __version__
from paint_tracker.updater import check_for_update

_BANNER = r"""
 ____       _       _     _____               _
|  _ \ __ _(_)_ __ | |_  |_   _| __ __ _  __| | _____ _ __
| |_) / _` | | '_ \| __|   | || '__/ _` |/ _` |/ / _ \ '__|
|  __/ (_| | | | | | |_    | || | | (_| | (_| |   <  __/ |
|_|   \__,_|_|_| |_|\__|   |_||_|  \__,_|\__,_|\_\___|_|

"""


def _prompt_update(new_version: str) -> bool:
    """Return *True* if the user agrees to upgrade."""
    print(f"\n🔔  A new version of paint-tracker is available: {new_version}")
    print(f"    Currently installed: {__version__}")
    try:
        answer = input("    Upgrade now? [Y/n] ").strip().lower()
    except EOFError:
        return False
    return answer in ("", "y", "yes")


def _do_upgrade() -> None:
    """Run ``pip install --upgrade paint-tracker`` and restart the process."""
    print("⬆️  Upgrading paint-tracker …")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--upgrade", "paint-tracker"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    print("✅  Upgrade complete – restarting …\n")
    # Replace the current process with the freshly installed version.
    import os

    os.execv(sys.executable, [sys.executable, "-m", "paint_tracker"] + sys.argv[1:])


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="paint-tracker",
        description="Start the Paint Tracker server.",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    parser.add_argument(
        "--no-update-check",
        action="store_true",
        help="Skip the PyPI update check on startup.",
    )
    args = parser.parse_args(argv)

    print(_BANNER)

    try:
        installed = importlib.metadata.version("paint-tracker")
    except importlib.metadata.PackageNotFoundError:
        installed = __version__
    print(f"Paint Tracker v{installed}")

    # ── 1. Update check ──────────────────────────────────────────────────────
    if not args.no_update_check:
        print("🔍  Checking PyPI for updates …", end=" ", flush=True)
        new_version = check_for_update()
        if new_version:
            print()  # newline after the ellipsis
            if _prompt_update(new_version):
                _do_upgrade()
                return  # unreachable after execv, but keeps linters happy
        else:
            print("up to date.")

    # ── 2. Database auto-configuration ───────────────────────────────────────
    # Importing the database module triggers directory creation and engine setup.
    from paint_tracker.database import DATABASE_URL  # noqa: F401

    print(f"\n🗄️  Database: {DATABASE_URL}")

    # ── 3. Start server ───────────────────────────────────────────────────────
    print(f"🚀  Starting server on http://{args.host}:{args.port}\n")

    try:
        import uvicorn
    except ImportError as exc:
        sys.exit(f"uvicorn is required to run the server: {exc}")

    uvicorn.run(
        "paint_tracker.main:app",
        host=args.host,
        port=args.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
