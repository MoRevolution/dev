#!/usr/bin/env python3
"""Dev Environment Setup - a bit too extra"""

from __future__ import annotations

import argparse
import shutil
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from utils import PackageManager, Platform, run_cmd

# For Python 3.11+, use tomllib. For older versions, fall back to tomli
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Please install tomli for Python < 3.11: pip install tomli")
        sys.exit(1)


# =============================================================================
# Package Manager Protocol & Implementations
# =============================================================================
@dataclass
class WingetManager:
    """Windows Package Manager (winget)."""

    name: str = "winget"
    _installed_cache: set[str] | None = field(default=None, repr=False)

    def is_available(self) -> bool:
        success, _, _ = run_cmd("winget --version")
        return success

    def get_installed_packages(self) -> set[str]:
        if self._installed_cache is not None:
            return self._installed_cache

        success, stdout, _ = run_cmd("winget list --disable-interactivity")
        if success:
            self._installed_cache = {line.lower() for line in stdout.splitlines()}
        else:
            self._installed_cache = set()
        return self._installed_cache

    def is_installed(self, package_id: str) -> bool:
        installed = self.get_installed_packages()
        return any(package_id.lower() in line for line in installed)

    def install(
        self, package_id: str, arguments: str | None = None, dry_run: bool = False
    ) -> bool:
        cmd = f"winget install {package_id} --accept-source-agreements --accept-package-agreements --silent"
        if arguments:
            cmd += f" {arguments}"

        if dry_run:
            return True

        success, _, _ = run_cmd(cmd)
        return success

    def update_cache(self, dry_run: bool = False) -> None:
        # Winget doesn't need cache updates
        pass


@dataclass
class BrewManager:
    """Homebrew Package Manager."""

    name: str = "brew"
    _installed_cache: set[str] | None = field(default=None, repr=False)
    _cache_updated: bool = field(default=False, repr=False)

    def is_available(self) -> bool:
        success, _, _ = run_cmd("brew --version")
        return success

    def get_installed_packages(self) -> set[str]:
        if self._installed_cache is not None:
            return self._installed_cache

        success, stdout, _ = run_cmd("brew list --formula -1 && brew list --cask -1")
        if success:
            self._installed_cache = {pkg.strip().lower() for pkg in stdout.splitlines()}
        else:
            self._installed_cache = set()
        return self._installed_cache

    def is_installed(self, package_id: str) -> bool:
        return package_id.lower() in self.get_installed_packages()

    def install(
        self, package_id: str, arguments: str | None = None, dry_run: bool = False
    ) -> bool:
        cmd = f"brew install {package_id}"
        if arguments:
            cmd += f" {arguments}"

        if dry_run:
            return True

        success, _, _ = run_cmd(cmd)
        return success

    def update_cache(self, dry_run: bool = False) -> None:
        if self._cache_updated or dry_run:
            return
        run_cmd("brew update")
        self._cache_updated = True


@dataclass
class AptManager:
    """APT Package Manager (Debian/Ubuntu)."""

    name: str = "apt"
    _installed_cache: set[str] | None = field(default=None, repr=False)
    _cache_updated: bool = field(default=False, repr=False)

    def is_available(self) -> bool:
        success, _, _ = run_cmd("apt --version")
        return success

    def get_installed_packages(self) -> set[str]:
        if self._installed_cache is not None:
            return self._installed_cache

        success, stdout, _ = run_cmd("dpkg-query -W -f='${Package}\\n'")
        if success:
            self._installed_cache = {pkg.strip().lower() for pkg in stdout.splitlines()}
        else:
            self._installed_cache = set()
        return self._installed_cache

    def is_installed(self, package_id: str) -> bool:
        return package_id.lower() in self.get_installed_packages()

    def install(
        self, package_id: str, arguments: str | None = None, dry_run: bool = False
    ) -> bool:
        cmd = f"sudo apt install -y {package_id}"
        if arguments:
            cmd += f" {arguments}"

        if dry_run:
            return True

        success, _, _ = run_cmd(cmd)
        return success

    def update_cache(self, dry_run: bool = False) -> None:
        if self._cache_updated or dry_run:
            return
        run_cmd("sudo apt update")
        self._cache_updated = True


def get_package_manager(platform: Platform, console: Console) -> PackageManager | None:
    """Get the appropriate package manager for the platform."""
    if platform == Platform.WINDOWS:
        mgr = WingetManager()
        if mgr.is_available():
            return mgr
        console.print("[red]Error:[/red] winget not found on Windows")
        return None

    if platform in (Platform.WSL, Platform.MACOS):
        # Try Homebrew first
        brew = BrewManager()
        if brew.is_available():
            return brew

        # Fall back to apt on WSL
        if platform == Platform.WSL:
            apt = AptManager()
            if apt.is_available():
                console.print(
                    "[yellow]Note:[/yellow] Using apt (install Homebrew for better package support)"
                )
                return apt

        console.print(
            f"[red]Error:[/red] No package manager found for {platform.value}"
        )
        return None

    return None


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class Package:
    """A package to install."""

    name: str
    ids: dict[str, str]  # platform/manager key -> package_id
    arguments: dict[str, str] | None = None  # platform -> arguments

    def get_id(self, platform: Platform, manager: PackageManager) -> str | None:
        """Get the package ID for the given platform and manager."""
        # Try manager-specific key first (e.g., "brew", "winget")
        if manager.name in self.ids:
            return self.ids[manager.name]
        # Fall back to platform key
        if platform.value in self.ids:
            return self.ids[platform.value]
        return None

    def get_arguments(self, platform: Platform) -> str | None:
        """Get installation arguments for the platform."""
        if not self.arguments:
            return None
        return self.arguments.get(platform.value) or self.arguments.get("default")


@dataclass
class FileMapping:
    """A file to copy."""

    source: Path
    destinations: dict[str, Path]  # platform -> destination

    def get_destination(self, platform: Platform) -> Path | None:
        """Get the destination path for the platform."""
        dest = self.destinations.get(platform.value)
        if dest:
            return dest.expanduser()
        return None


@dataclass
class Config:
    """Configuration loaded from config.toml."""

    packages: dict[str, list[Package]]  # section -> packages
    files: list[FileMapping]
    meta: dict[str, str]

    @classmethod
    def load(cls, path: Path, console: Console) -> Config | None:
        """Load configuration from a TOML file."""
        if not path.exists():
            console.print(f"[red]Error:[/red] {path} not found")
            return None

        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to parse {path}: {e}")
            return None

        # Parse meta
        meta = data.get("meta", {})

        # Parse packages
        packages: dict[str, list[Package]] = {}
        pkg_sections = data.get("packages", {})

        for section, section_packages in pkg_sections.items():
            packages[section] = []
            for name, pkg_data in section_packages.items():
                if isinstance(pkg_data, str):
                    # Simple format: name = "package_id"
                    packages[section].append(
                        Package(name=name, ids={"default": pkg_data})
                    )
                elif isinstance(pkg_data, dict):
                    # Extract IDs (non-argument keys)
                    ids = {}
                    arguments = {}
                    for key, value in pkg_data.items():
                        if key.endswith("_args"):
                            # e.g., "windows_args" -> arguments["windows"]
                            platform_key = key.rsplit("_", 1)[0]
                            arguments[platform_key] = value
                        elif isinstance(value, str):
                            ids[key] = value

                    packages[section].append(
                        Package(
                            name=name,
                            ids=ids,
                            arguments=arguments if arguments else None,
                        )
                    )

        # Parse files
        files: list[FileMapping] = []
        files_data = data.get("files", {})

        for source, dest_data in files_data.items():
            source_path = Path(source)
            if isinstance(dest_data, str):
                # Same destination for all platforms
                dest_path = Path(dest_data)
                files.append(
                    FileMapping(
                        source=source_path,
                        destinations={
                            "windows": dest_path,
                            "wsl": dest_path,
                            "macos": dest_path,
                        },
                    )
                )
            elif isinstance(dest_data, dict):
                # Platform-specific destinations
                destinations = {k: Path(v) for k, v in dest_data.items()}
                files.append(FileMapping(source=source_path, destinations=destinations))

        return cls(packages=packages, files=files, meta=meta)


# =============================================================================
# Core Operations
# =============================================================================


def install_packages(
    config: Config,
    platform: Platform,
    manager: PackageManager,
    console: Console,
    dry_run: bool = False,
) -> tuple[int, int, int]:
    """Install packages. Returns (success_count, skip_count, fail_count)."""
    success_count = 0
    skip_count = 0
    fail_count = 0

    # Update package cache once
    if not dry_run:
        with console.status(f"Updating {manager.name} cache..."):
            manager.update_cache(dry_run)

    # Determine which sections to process
    sections_to_process = ["common"]

    if platform == Platform.WINDOWS:
        sections_to_process.extend(["gui_only", "windows_only"])
    elif platform.is_unix:
        sections_to_process.append("unix_only")
        if platform == Platform.WSL:
            sections_to_process.append("wsl_only")
        elif platform == Platform.MACOS:
            sections_to_process.append("macos_only")

    # In dry-run mode, collect all results and display as table
    if dry_run:
        table = Table(title="Packages")
        table.add_column("Package", style="cyan")
        table.add_column("Section", style="dim")
        table.add_column("Package ID", style="dim")
        table.add_column("Action")

        for section in sections_to_process:
            packages = config.packages.get(section, [])
            for pkg in packages:
                package_id = pkg.get_id(platform, manager)
                if not package_id:
                    table.add_row(pkg.name, section, "-", "[dim]SKIP (no ID)[/dim]")
                    skip_count += 1
                elif manager.is_installed(package_id):
                    table.add_row(
                        pkg.name,
                        section,
                        package_id,
                        "[yellow]SKIP (installed)[/yellow]",
                    )
                    skip_count += 1
                else:
                    table.add_row(pkg.name, section, package_id, "[cyan]INSTALL[/cyan]")
                    success_count += 1

        console.print()
        console.print(table)
        return success_count, skip_count, fail_count

    # Normal mode: install packages with progress
    for section in sections_to_process:
        packages = config.packages.get(section, [])
        if not packages:
            continue

        console.print(f"\n[bold blue]Installing {section} packages[/bold blue]")

        for pkg in packages:
            package_id = pkg.get_id(platform, manager)
            if not package_id:
                console.print(
                    f"  [dim]SKIP[/dim] {pkg.name} (no ID for {platform.value})"
                )
                skip_count += 1
                continue

            # Check if already installed
            if manager.is_installed(package_id):
                console.print(f"  [yellow]SKIP[/yellow] {pkg.name} (already installed)")
                skip_count += 1
                continue

            # Install
            arguments = pkg.get_arguments(platform)
            with console.status(f"  Installing {pkg.name}..."):
                success = manager.install(package_id, arguments, dry_run=False)

            if success:
                console.print(f"  [green]OK[/green] {pkg.name}")
                success_count += 1
            else:
                console.print(f"  [red]FAIL[/red] {pkg.name}")
                fail_count += 1

    return success_count, skip_count, fail_count


def copy_files(
    config: Config,
    platform: Platform,
    console: Console,
    dry_run: bool = False,
) -> tuple[int, int, int]:
    """Copy configuration files. Returns (success_count, skip_count, fail_count)."""
    success_count = 0
    skip_count = 0
    fail_count = 0

    # In dry-run mode, collect all results and display as table
    if dry_run:
        table = Table(title="Configuration Files")
        table.add_column("Source", style="cyan")
        table.add_column("Destination", style="dim")
        table.add_column("Action")

        for file_mapping in config.files:
            source = file_mapping.source
            dest = file_mapping.get_destination(platform)

            if not dest:
                table.add_row(str(source), "-", "[dim]SKIP (no destination)[/dim]")
                skip_count += 1
            elif not source.exists():
                table.add_row(
                    str(source), str(dest), "[red]FAIL (source not found)[/red]"
                )
                fail_count += 1
            else:
                table.add_row(str(source), str(dest), "[cyan]COPY[/cyan]")
                success_count += 1

        console.print()
        console.print(table)
        return success_count, skip_count, fail_count

    # Normal mode: copy files with progress
    console.print("\n[bold blue]Copying configuration files[/bold blue]")

    for file_mapping in config.files:
        source = file_mapping.source
        dest = file_mapping.get_destination(platform)

        if not dest:
            console.print(
                f"  [dim]SKIP[/dim] {source} (no destination for {platform.value})"
            )
            skip_count += 1
            continue

        if not source.exists():
            console.print(f"  [red]FAIL[/red] {source} (source not found)")
            fail_count += 1
            continue

        try:
            # Ensure destination directory exists
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            console.print(f"  [green]OK[/green] {source} -> {dest}")
            success_count += 1
        except Exception as e:
            console.print(f"  [red]FAIL[/red] {source}: {e}")
            fail_count += 1

    return success_count, skip_count, fail_count


def show_status(config: Config, platform: Platform, console: Console) -> None:
    """Show installation status."""
    manager = get_package_manager(platform, console)
    if not manager:
        return

    table = Table(title="Package Status")
    table.add_column("Package", style="cyan")
    table.add_column("Section", style="dim")
    table.add_column("Status")

    installed_count = 0
    total_count = 0

    for section, packages in config.packages.items():
        # Skip irrelevant sections
        if section == "gui_only" and platform != Platform.WINDOWS:
            continue
        if section == "windows_only" and platform != Platform.WINDOWS:
            continue
        if section == "unix_only" and not platform.is_unix:
            continue
        if section == "wsl_only" and platform != Platform.WSL:
            continue
        if section == "macos_only" and platform != Platform.MACOS:
            continue

        for pkg in packages:
            package_id = pkg.get_id(platform, manager)
            if not package_id:
                continue

            total_count += 1
            if manager.is_installed(package_id):
                status = "[green]✓ installed[/green]"
                installed_count += 1
            else:
                status = "[red]✗ missing[/red]"

            table.add_row(pkg.name, section, status)

    console.print(table)
    console.print(f"\nSummary: {installed_count}/{total_count} packages installed")


# =============================================================================
# CLI
# =============================================================================


def show_help(console: Console) -> None:
    """Display a nice help message using rich."""
    console.print(Panel.fit("[bold]Dev Environment Setup[/bold]", border_style="blue"))
    console.print()
    console.print(
        "[bold]Usage:[/bold] python setup.py [cyan]<command>[/cyan] [dim][options][/dim]"
    )
    console.print()

    # Commands table
    cmd_table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
    cmd_table.add_column("Command", style="cyan")
    cmd_table.add_column("Description")
    cmd_table.add_row("all", "Install packages and copy files [dim](default)[/dim]")
    cmd_table.add_row("packages", "Install packages only")
    cmd_table.add_row("files", "Copy configuration files only")
    cmd_table.add_row("status", "Show installation status")

    console.print("[bold]Commands:[/bold]")
    console.print(cmd_table)
    console.print()

    # Options table
    opt_table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
    opt_table.add_column("Option", style="cyan")
    opt_table.add_column("Description")
    opt_table.add_row("-n, --dry-run", "Preview changes without making them")
    opt_table.add_row(
        "-c, --config", "Path to config file [dim](default: config.toml)[/dim]"
    )
    opt_table.add_row("-h, --help", "Show this help message")

    console.print("[bold]Options:[/bold]")
    console.print(opt_table)
    console.print()

    # Examples
    console.print("[bold]Examples:[/bold]")
    console.print("  python setup.py                [dim]# Install everything[/dim]")
    console.print(
        "  python setup.py status         [dim]# Check what's installed[/dim]"
    )
    console.print("  python setup.py --dry-run      [dim]# Preview changes[/dim]")
    console.print(
        "  python setup.py packages -n    [dim]# Preview package installs[/dim]"
    )


def main() -> int:
    """Main entry point."""
    console = Console()

    # Custom help handling
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help", "help"):
        show_help(console)
        return 0

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "command",
        nargs="?",
        default="all",
        choices=["all", "packages", "files", "status"],
    )
    parser.add_argument("--dry-run", "-n", action="store_true")
    parser.add_argument("--config", "-c", type=Path, default=Path("config.toml"))
    parser.add_argument("--help", "-h", action="store_true")

    args = parser.parse_args()

    if args.help:
        show_help(console)
        return 0

    # Header
    console.print(Panel.fit("[bold]Dev Environment Setup[/bold]", border_style="blue"))

    if args.dry_run:
        console.print("[yellow]DRY RUN MODE - no changes will be made[/yellow]\n")

    # Detect platform
    platform = Platform.detect()
    if platform == Platform.UNKNOWN:
        console.print("[red]Error:[/red] Unsupported platform")
        return 2

    console.print(f"Platform: [cyan]{platform.value}[/cyan]")

    # Load config
    config = Config.load(args.config, console)
    if not config:
        return 2

    start_time = time.time()

    # Status command
    if args.command == "status":
        show_status(config, platform, console)
        return 0

    # Get package manager
    manager = None
    if args.command in ("all", "packages"):
        manager = get_package_manager(platform, console)
        if not manager:
            return 2

    # Run commands
    total_success = 0
    total_skip = 0
    total_fail = 0

    if args.command in ("all", "packages") and manager:
        success, skip, fail = install_packages(
            config, platform, manager, console, args.dry_run
        )
        total_success += success
        total_skip += skip
        total_fail += fail

    if args.command in ("all", "files"):
        success, skip, fail = copy_files(config, platform, console, args.dry_run)
        total_success += success
        total_skip += skip
        total_fail += fail

    # Summary
    elapsed = time.time() - start_time
    console.print()

    summary_style = "green" if total_fail == 0 else "yellow"
    console.print(
        Panel(
            f"[{summary_style}]Completed in {elapsed:.1f}s[/{summary_style}]\n"
            f"Success: {total_success} | Skipped: {total_skip} | Failed: {total_fail}",
            title="Summary",
            border_style=summary_style,
        )
    )

    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
