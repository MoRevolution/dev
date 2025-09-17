#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil
import time
from pathlib import Path
from rich.console import Console


# For Python 3.11+, use tomllib. For older versions, fall back to tomli
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("X Please install tomli for Python < 3.11: pip install tomli")
        sys.exit(1)


# Simple color codes for terminal
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def log(message, prefix="INFO", color=None):
    timestamp = time.strftime("%H:%M:%S")
    if color:
        print(f"[{timestamp}] {color}{prefix}{Colors.RESET}: {message}")
    else:
        print(f"[{timestamp}] {prefix}: {message}")


def log_success(message):
    log(message, "OK", Colors.GREEN)


def log_error(message):
    log(message, "ERROR", Colors.RED)


def log_warning(message):
    log(message, "WARN", Colors.YELLOW)


def log_info(message):
    log(message, "INFO", Colors.BLUE)


def log_skip(message):
    log(message, "SKIP", Colors.YELLOW)


def is_wsl():
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except Exception:
        return False


def is_windows():
    return os.name == "nt"


def run_cmd(cmd, capture_output=True):
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)


def get_installed_packages(platform):
    """Get list of all installed packages at once"""
    if platform == "windows":
        success, stdout, _ = run_cmd("winget list")
        return stdout.lower() if success else ""
    elif platform == "wsl":
        success, stdout, _ = run_cmd("dpkg -l")
        return stdout.lower() if success else ""
    return ""


def is_package_installed(package_id, installed_list, platform):
    if platform == "windows":
        # winget shows package IDs, check if our package ID is in the list
        return package_id.lower() in installed_list
    elif platform == "wsl":
        # dpkg shows package names, check if our package is installed
        return package_id.lower() in installed_list
    return False


def install_package(package_name, package_id, platform, installed_list=None, arguments=None):
    """Install a package using manager that fits system"""
    
    console = Console()
    
    # Check if already installed first
    if installed_list and is_package_installed(package_id, installed_list, platform):
        console.print(f"[yellow]SKIP[/yellow] {package_name} - already installed")
        return True

    if platform in ["windows", "wsl"]:
        if platform == "windows":
            cmd = f"winget install {package_id} --accept-source-agreements --accept-package-agreements --silent"
        elif platform == "wsl":
            # Update package list on first run
            if not hasattr(install_package, "_apt_updated"):
                console.print("[blue]INFO[/blue] Updating package list (first run)")
                run_cmd("sudo apt update")
                install_package._apt_updated = True
            cmd = f"sudo apt install -y {package_id}"

        if arguments:
            cmd += f" {arguments}"

        with console.status(f"Installing {package_name}...") as status:
            success, stdout, stderr = run_cmd(cmd)
        if success:
            console.print(f"[green]SUCCESS[/green] {package_name} installed")
        else:
            console.print(f"[red]FAILED[/red] {package_name}: {stderr.strip()[:60]}")
        return success

    console.print(f"[red]ERROR[/red] Unknown platform for {package_name}")
    return False


def install_packages():
    """Install packages based on platform and configuration"""
    log_info("Starting package installation")

    config_path = Path("config.toml")
    if not config_path.exists():
        log_error("config.toml not found!")
        return False

    try:
        with open("config.toml", "rb") as f:
            config = tomllib.load(f)
    except Exception as e:
        log_error(f"Error reading config.toml: {e}")
        return False

    platform = "windows" if is_windows() else "wsl" if is_wsl() else "unknown"
    log_info(f"Detected platform: {platform}")

    if platform == "unknown":
        log_error("Unsupported platform!")
        return False

    # Get installed packages list once for efficiency
    log_info("Checking currently installed packages...")
    installed_list = get_installed_packages(platform)

    success_count = 0
    total_count = 0

    # Install common packages
    common_packages = config.get("packages", {}).get("common", {})
    if common_packages:
        log_info(f"Processing {len(common_packages)} common packages")
        for name, pkg_info in common_packages.items():
            if isinstance(pkg_info, dict) and platform in pkg_info:
                package_id = pkg_info[platform]
                arguments = pkg_info.get("arguments")
                total_count += 1
                if install_package(name, package_id, platform, installed_list, arguments):
                    success_count += 1

    # Install GUI packages (only on Windows)
    if platform == "windows":
        gui_packages = config.get("packages", {}).get("gui_only", {})
        if gui_packages:
            print()
            log_info(f"Processing {len(gui_packages)} GUI packages")
            for name, pkg_info in gui_packages.items():
                if isinstance(pkg_info, dict):
                    package_id = pkg_info.get(platform, pkg_info.get("id"))
                    arguments = pkg_info.get("arguments")
                else:
                    package_id = pkg_info
                    arguments = None
                total_count += 1
                if install_package(name, package_id, platform, installed_list, arguments):
                    success_count += 1
    else:
        gui_count = len(config.get("packages", {}).get("gui_only", {}))
        if gui_count > 0:
            log_warning(f"Skipping {gui_count} GUI packages on WSL")

    # Install platform-specific packages
    platform_key = f"{platform}_only"
    platform_packages = config.get("packages", {}).get(platform_key, {})
    if platform_packages:
        print()
        log_info(f"Installing {len(platform_packages)} {platform}-specific packages")
        for name, pkg_info in platform_packages.items():
            if isinstance(pkg_info, dict):
                package_id = pkg_info.get(platform, pkg_info.get("id"))
                arguments = pkg_info.get("arguments")
            else:
                package_id = pkg_info
                arguments = None
            total_count += 1
            if install_package(name, package_id, platform, installed_list, arguments):
                success_count += 1

    log_success(
        f"Completed: {success_count}/{total_count} packages processed successfully"
    )
    return success_count == total_count


def copy_files():
    """Copy configuration files"""
    log_info("Starting file copying")

    config_path = Path("config.toml")
    if not config_path.exists():
        log_error("config.toml not found!")
        return False

    try:
        with open("config.toml", "rb") as f:
            config = tomllib.load(f)
    except Exception as e:
        log_error(f"Error reading config.toml: {e}")
        return False

    platform = "windows" if is_windows() else "wsl" if is_wsl() else "unknown"
    files_config = config.get("files", {})

    if not files_config:
        log_warning("No files configured to copy")
        return True

    log_info(f"Found {len(files_config)} files to process")

    success_count = 0
    total_count = 0
    skipped_count = 0

    for src, dest in files_config.items():
        total_count += 1

        # Skip platform-specific files
        if platform == "wsl":
            if any(
                skip in src.lower()
                for skip in ["powershell", "wallpaper", "lockscreen"]
            ):
                log_warning(f"Skipping {src} (not needed on WSL)")
                skipped_count += 1
                continue

        src_path = Path(src)
        if not src_path.exists():
            log_error(f"Source file not found: {src}")
            continue

        # Expand user home directory
        dest_path = Path(dest).expanduser()

        # Create destination directory if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(src_path, dest_path)
            log_success(f"Copied {src} -> {dest}")
            success_count += 1
        except Exception as e:
            log_error(f"Failed to copy {src}: {e}")

    if skipped_count > 0:
        log_info(
            f"Copied {success_count}/{total_count - skipped_count} files ({skipped_count} skipped)"
        )
    else:
        log_success(f"Copied {success_count}/{total_count} files successfully")
    return True


def show_status():
    """Show installation status"""
    platform = "windows" if is_windows() else "wsl" if is_wsl() else "unknown"

    print(f"{Colors.BOLD}System Status:{Colors.RESET}")
    print(f"Platform: {Colors.BLUE}{platform}{Colors.RESET}")

    if not Path("config.toml").exists():
        print(f"Config: {Colors.RED}missing{Colors.RESET}")
        return

    try:
        with open("config.toml", "rb") as f:
            config = tomllib.load(f)
    except:
        print(f"Config: {Colors.RED}error{Colors.RESET}")
        return

    print("Checking packages...")
    installed_list = get_installed_packages(platform)

    print(f"\n{Colors.BOLD}Package Status:{Colors.RESET}")
    print("-" * 40)
    print(f"{'Package':<20} {'Status'}")
    print("-" * 40)

    installed = 0
    total = 0

    # Check common packages
    for name, pkg_info in config.get("packages", {}).get("common", {}).items():
        if isinstance(pkg_info, dict) and platform in pkg_info:
            total += 1
            package_id = pkg_info[platform]
            if is_package_installed(package_id, installed_list, platform):
                print(f"{name:<20} {Colors.GREEN}installed{Colors.RESET}")
                installed += 1
            else:
                print(f"{name:<20} {Colors.RED}missing{Colors.RESET}")
        elif isinstance(pkg_info, str):
            total += 1
            if is_package_installed(pkg_info, installed_list, platform):
                print(f"{name:<20} {Colors.GREEN}installed{Colors.RESET}")
                installed += 1
            else:
                print(f"{name:<20} {Colors.RED}missing{Colors.RESET}")

    # Check platform-specific packages
    for section in ["gui_only", f"{platform}_only"]:
        for name, pkg_info in config.get("packages", {}).get(section, {}).items():
            if section == "gui_only" and platform == "wsl":
                continue  # Skip GUI on WSL
            if isinstance(pkg_info, dict):
                package_id = pkg_info.get(platform, pkg_info.get("id"))
            else:
                package_id = pkg_info
            total += 1
            if is_package_installed(package_id, installed_list, platform):
                print(f"{name:<20} {Colors.GREEN}installed{Colors.RESET}")
                installed += 1
            else:
                print(f"{name:<20} {Colors.RED}missing{Colors.RESET}")

    print("-" * 40)
    color = (
        Colors.GREEN
        if installed == total
        else Colors.YELLOW
        if installed > 0
        else Colors.RED
    )
    print(f"Summary: {color}{installed}/{total} installed{Colors.RESET}")


def show_help():
    """Show help message"""
    help_text = """
Enhanced Simple Dev Environment Setup

Usage:
    python setup.py [command]

Commands:
    (no args)    - Install everything (packages + files)
    packages     - Install packages only
    files        - Copy configuration files only
    status       - Show system status
    help         - Show this help message
    """
    print(help_text)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    if cmd in ["help", "-h", "--help"]:
        show_help()
        return

    print("Dev Environment Setup")
    print("=" * 50)

    success = True
    start_time = time.time()

    if cmd in ["all", "packages"]:
        if not install_packages():
            success = False

    if cmd in ["all", "files"]:
        if not copy_files():
            success = False

    if cmd in ["status"]:
        show_status()
        return

    elapsed = time.time() - start_time
    print("\n" + "=" * 50)
    if success:
        log_success(f"Setup completed in {elapsed:.1f}s")
    else:
        log_warning(
            f"Setup completed with errors in {elapsed:.1f}s - check output above"
        )


if __name__ == "__main__":
    main()
