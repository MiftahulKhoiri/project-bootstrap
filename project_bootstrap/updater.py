import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

from .logger import get_logger

log = get_logger("PROJECT_BOOTSTRAP.UPDATER")


class SelfUpdater:
    """
    Menangani update Git repository
    """

    def __init__(self, repo_dir: Path, branch: str = "main"):
        self.repo_dir = repo_dir
        self.branch = branch

    def _run(self, cmd: list[str], capture: bool = True) -> Optional[str]:
        try:
            if capture:
                result = subprocess.run(
                    cmd,
                    cwd=self.repo_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    raise subprocess.CalledProcessError(
                        result.returncode, cmd, result.stdout, result.stderr
                    )
                return result.stdout.strip()
            else:
                subprocess.check_call(cmd, cwd=self.repo_dir, timeout=30)
                return None
        except Exception as e:
            log.error(f"Gagal menjalankan: {' '.join(cmd)}")
            raise

    def is_git_repo(self) -> bool:
        return (self.repo_dir / ".git").exists()

    def has_any_changes(self) -> bool:
        status = self._run(["git", "status", "--porcelain"])
        return bool(status)

    def get_current_branch(self) -> Optional[str]:
        try:
            return self._run(["git", "branch", "--show-current"])
        except Exception:
            return None

    def check_for_updates(self) -> Tuple[bool, Optional[str], Optional[str]]:
        if not self.is_git_repo():
            return False, None, None

        self._run(["git", "fetch", "--prune", "origin"], capture=False)

        local = self._run(["git", "rev-parse", "HEAD"])
        remote = self._run(["git", "rev-parse", f"origin/{self.branch}"])

        return local != remote, local[:8], remote[:8]

    def update(self) -> bool:
        if not self.is_git_repo():
            log.warning("Bukan git repository")
            return False

        if self.has_any_changes():
            log.warning("Ada perubahan lokal, skip update")
            return False

        need, local, remote = self.check_for_updates()
        if not need:
            log.info(f"Sudah terbaru ({local})")
            return False

        log.warning(f"Update: {local} → {remote}")
        self._run(
            ["git", "pull", "--ff-only", "origin", self.branch],
            capture=False
        )
        log.info("Update berhasil")
        return True

    def hard_reset_update(self) -> bool:
        log.warning("HARD RESET – semua perubahan lokal akan dihapus")
        if sys.stdout.isatty():
            if input("Lanjutkan? (y/N): ").lower() != "y":
                return False

        self._run(["git", "fetch", "origin"], capture=False)
        self._run(
            ["git", "reset", "--hard", f"origin/{self.branch}"],
            capture=False
        )
        self._run(["git", "clean", "-fd"], capture=False)
        log.info("Hard reset selesai")
        return True