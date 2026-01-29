from .cli import main
from .bootstrapper import Bootstrapper
from .updater import SelfUpdater

__all__ = ["Bootstrapper", "SelfUpdater"]

__version__ = "0.1.0"

if __name__ == "__main__":
    main()