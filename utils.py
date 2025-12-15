import subprocess
from enum import Enum
from typing import Protocol


class Platform(Enum):
    """Supported platforms."""

    WINDOWS = "windows"
    WSL = "wsl"
    MACOS = "macos"
    UNKNOWN = "unknown"

    @classmethod
    def detect(cls) -> "Platform":
        """Detect the current platform."""
        if hasattr(cls, "_cached"):
            return cls._cached  # type: ignore[return-value]

        import os
        import platform as plat

        result = cls.UNKNOWN

        if os.name == "nt":
            result = cls.WINDOWS
        elif plat.system() == "Darwin":
            result = cls.MACOS
        else:
            # Check for WSL
            try:
                with open("/proc/version") as f:
                    if "microsoft" in f.read().lower():
                        result = cls.WSL
            except (FileNotFoundError, PermissionError):
                pass

        cls._cached = result  # type: ignore[attr-defined]
        return result

    @property
    def is_unix(self) -> bool:
        """Check if platform is Unix-like (WSL or macOS)."""
        return self in (Platform.WSL, Platform.MACOS)

    @property
    def uses_brew(self) -> bool:
        """Check if platform should use Homebrew."""
        return self in (Platform.WSL, Platform.MACOS)


class PackageManager(Protocol):
    """Protocol for package managers."""

    name: str

    def is_available(self) -> bool:
        """Check if the package manager is available on the system."""
        ...

    def install(
        self, package_id: str, arguments: str | None = None, dry_run: bool = False
    ) -> bool:
        """Install a package."""
        ...

    def is_installed(self, package_id: str) -> bool:
        """Check if a package is installed."""
        ...

    def update_cache(self, dry_run: bool = False) -> None:
        """Update the package cache."""
        ...

    def get_installed_packages(self) -> set[str]:
        """Get set of installed package IDs."""
        ...


def run_cmd(
    cmd: str, capture: bool = True, check: bool = False
) -> tuple[bool, str, str]:
    """Run a shell command and return (success, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture,
            text=True,
            check=check,
        )
        return result.returncode == 0, result.stdout or "", result.stderr or ""
    except subprocess.CalledProcessError as e:
        return False, e.stdout or "", e.stderr or ""
    except Exception as e:
        return False, "", str(e)
