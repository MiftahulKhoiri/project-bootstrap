import sys
import argparse
from pathlib import Path

from .bootstrapper import Bootstrapper
from .updater import SelfUpdater
from .logger import get_logger

log = get_logger("PROJECT_BOOTSTRAP.CLI")


def main():
    parser = argparse.ArgumentParser("project-bootstrap")
    parser.add_argument("--no-update", action="store_true")
    parser.add_argument("--force-update", action="store_true")
    parser.add_argument("--check-only", action="store_true")

    args = parser.parse_args()

    if args.force_update:
        SelfUpdater(Path.cwd()).hard_reset_update()
        sys.exit(0)

    if args.check_only:
        updater = SelfUpdater(Path.cwd())
        need, local, remote = updater.check_for_updates()
        if need:
            print(f"UPDATE:{local}->{remote}")
            sys.exit(1)
        print("UP_TO_DATE")
        sys.exit(0)

    Bootstrapper().bootstrap(auto_update=not args.no_update)