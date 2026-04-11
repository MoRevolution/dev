# Project Context

Dotfiles + cross-platform dev environment setup, written in Nushell.

## Structure

- `setup.nu` — main setup script. Installs packages, copies config files, generates shell init files, runs post-install commands. Supports `--dry-run` and `--personal` flags.
- `config.toml` — declarative manifest: packages (by platform/section), file mappings (source → per-platform destination), post-install commands.
- `github-ssh.nu` — standalone script to generate ed25519 SSH key and upload to GitHub via `gh`.
- `files/` — config files that get copied to their destinations:
  - `starship.toml` — Starship prompt theme
  - `env.nu` — Nushell environment config (PATH, fnm)
  - `config.nu` — Nushell shell config (aliases, custom commands, sources starship.nu/zoxide.nu)
  - `aerospace.toml` — AeroSpace tiling WM config (macOS only)
  - `.gitconfig`, `Media Keys.ahk`, wallpapers, etc.
- `Dockerfile` + `.devcontainer/` — for testing the setup in a container

## Platforms

- **Windows**: winget, Nushell config in `~/AppData/Roaming/nushell/`
- **macOS**: brew, Nushell config in `~/Library/Application Support/nushell/`, AeroSpace for tiling
- **WSL**: brew, Nushell config in `~/.config/nushell/`

## Package sections in config.toml

- `common` — all platforms
- `gui_only` — Windows + macOS (skipped on WSL/headless Linux)
- `personal` — only installed when `--personal` flag is passed (zotero, sioyek)
- `windows_only`, `unix_only`, `wsl_only`, `macos_only` — platform-specific

## Key patterns

- Platform detection: `$nu.os-info.name` + `/proc/version` check for WSL
- Package manager: winget (Windows), brew (macOS/WSL), apt (fallback)
- Nushell idioms: `| complete` to capture exit code/stdout/stderr, `char cr` for line-overwriting progress, `fill -w N` for padding
- Mutable variables can't be captured in try/catch — use `let ok = try { ...; true } catch { false }` pattern
- `else if` must be on the same line as `}`
