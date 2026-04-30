# dev

i've had to set up 9 laptops/vms over the past 3 years (4 in the past 5 months as of april 2026, don't ask why), and i'm tired. this is my attempt to semi-automate that and make myself less irritable.

> **note** nushell 0.111 has a [bug](https://github.com/nushell/nushell/issues/17719) where `nu setup.nu -h` shows duplicated subcommands. fixed in 0.112.1, but not on brew yet as of me writing this

> **another note:** i haven't tested this as much on wsl or other linux flavors so feel free to open an issue or a PR

to get started...

## get nushell first

**windows:** `winget install Nushell.Nushell`

**macos / wsl:** install [homebrew](https://brew.sh), then `brew install nushell`

## run the setup script

```nushell
nu setup.nu                      # run everything
nu setup.nu packages             # install tools
nu setup.nu init                 # generate starship/zoxide init files
nu setup.nu files                # copy configs to the right place
nu setup.nu post-install         # gh auth, fnm lts, default shell, wallpaper
nu setup.nu status               # see what's installed
```

add `--dry-run` to preview without doing anything.

## what gets installed

everything lives in `config.toml` — edit it to swap in your own. mine are pretty basic right now and i'll probably keep adding to it.

- **everywhere** — git, nushell, starship, uv, gh, fnm, fzf, fd, zoxide, ripgrep, etc.
- **unix** — tmux, htop, neovim
- **macos** — aerospace, ghostty
- **windows** — terminal, powertoys, autohotkey
- **personal** (add `--personal` flag) — zotero, sioyek, etc., the stuff you wouldn't want on a work laptop

## what gets copied

anything you put in the `[files]` section of `config.toml` gets copied to the right place per platform. i have all my configs under `files/` so everything there that matters get copied over

## after setup

restart your terminal and set nushell as default: `chsh -s (which nu)` on unix, or set it in windows terminal settings.
