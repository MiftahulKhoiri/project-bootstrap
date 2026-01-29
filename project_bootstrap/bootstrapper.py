import os
import sys
import subprocess
import hashlib
import time
from pathlib import Path
from typing import Optional

from .logger import get_logger
from .updater import SelfUpdater

log = get_logger("PROJECT_BOOTSTRAP.BOOTSTRAP")


class Bootstrapper:
    """
    Mengatur:
    - virtualenv
    - dependency
    - auto update
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.cwd()
        self.venv_dir = self.base_dir / "venv"
        self.req_file = self.base_dir / "requirements.txt"
        self.req_hash_file = self.venv_dir / ".req_hash"

        if sys.platform == "win32":
            self.bin_dir = self.venv_dir / "Scripts"
        else:
            self.bin_dir = self.venv_dir / "bin"

        self.python_bin = self.bin_dir / "python"
        self.pip_bin = self.bin_dir / "pip"

    # ---------- VENV ----------
    def in_venv(self) -> bool:
        return sys.prefix != sys.base_prefix

    def create_venv(self):
        log.warning("Membuat virtualenv...")
        subprocess.check_call(
            [sys.executable, "-m", "venv", str(self.venv_dir)]
        )

    def restart_in_venv(self):
        log.warning("Restart ke virtualenv...")
        time.sleep(0.1)
        os.execv(str(self.python_bin), [str(self.python_bin)] + sys.argv)

    def ensure_venv(self):
        if not self.venv_dir.exists():
            self.create_venv()
        if not self.in_venv():
            self.restart_in_venv()

    # ---------- DEPENDENCY ----------
    def _hash_requirements(self) -> Optional[str]:
        if not self.req_file.exists():
            return None
        h = hashlib.sha256()
        with open(self.req_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()

    def install_requirements(self):
        current = self._hash_requirements()
        saved = self.req_hash_file.read_text().strip() \
            if self.req_hash_file.exists() else None

        if current and current == saved:
            log.info("Dependency sudah siap")
            return

        log.warning("Install dependency...")
        subprocess.check_call(
            [str(self.pip_bin), "install", "-r", str(self.req_file)]
        )
        if current:
            self.req_hash_file.write_text(current)

    # ---------- BOOTSTRAP ----------
    def bootstrap(self, auto_update: bool = True):
        log.info("Memulai bootstrap...")
        self.ensure_venv()
        self.install_requirements()

        if auto_update:
            updater = SelfUpdater(self.base_dir)
            if updater.update():
                self.restart_in_venv()

        log.info("Bootstrap selesai")