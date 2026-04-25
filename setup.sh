#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SETUP_NU="$SCRIPT_DIR/setup.nu"

print_help() {
  cat <<'EOF'
Usage:
  ./setup.sh [setup.nu args...]

Examples:
  ./setup.sh
  ./setup.sh --dry-run
  ./setup.sh packages
  ./setup.sh packages --personal

This wrapper installs Nushell if needed, then runs setup.nu.
EOF
}

install_nushell() {
  local uname_out
  uname_out="$(uname -s)"

  case "$uname_out" in
    Darwin)
      if command -v brew >/dev/null 2>&1; then
        brew install nushell
      else
        echo "Homebrew not found. Install Homebrew first: https://brew.sh"
        exit 1
      fi
      ;;
    Linux)
      if command -v brew >/dev/null 2>&1; then
        brew install nushell
      elif command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y nushell
      else
        echo "No supported package manager found (expected brew or apt-get)."
        exit 1
      fi
      ;;
    MINGW*|MSYS*|CYGWIN*)
      if command -v winget >/dev/null 2>&1; then
        winget install --id Nushell.Nushell --accept-source-agreements --accept-package-agreements
      elif command -v powershell.exe >/dev/null 2>&1; then
        powershell.exe -NoProfile -Command "winget install --id Nushell.Nushell --accept-source-agreements --accept-package-agreements"
      else
        echo "winget not found. Install Nushell manually from https://www.nushell.sh/"
        exit 1
      fi
      ;;
    *)
      echo "Unsupported platform: $uname_out"
      exit 1
      ;;
  esac
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  print_help
  exit 0
fi

if [[ ! -f "$SETUP_NU" ]]; then
  echo "Could not find setup.nu at: $SETUP_NU"
  exit 1
fi

if ! command -v nu >/dev/null 2>&1; then
  echo "Nushell is not installed. Installing it now..."
  install_nushell
fi

if ! command -v nu >/dev/null 2>&1; then
  echo "Nushell installation did not succeed. Please install it manually."
  exit 1
fi

exec nu "$SETUP_NU" "$@"
