# dev

dotfiles + setup. was 850 lines of python. now it's nushell + starship.

## get nushell

**windows:**

```
winget install Nushell.Nushell
```

**macos / wsl:** install [homebrew](https://brew.sh) first, then:

```
brew install nushell
```

## run setup

```
nu setup.nu                      # everything
nu setup.nu --dry-run            # see what it would do
```

or just the parts you want:

```
nu setup.nu packages             # install tools
nu setup.nu files                # copy configs
nu setup.nu post-install         # gh auth, fnm lts, etc
nu setup.nu status               # check what's installed
```

## what's in `config.toml`

nushell reads toml natively so the whole config is just a file. no parsing libraries.

**all platforms** — git, nushell, starship, miniconda, uv, gh, fnm, fzf, fd, zoxide, ripgrep, lazygit, lazydocker, bat, vscode, raycast

**windows** — terminal, powertoys, flow launcher, firefox, 7zip, autohotkey

**unix** — tmux, htop, tree, vim, neovim, wget

## what's in the configs

`setup.nu files` copies these to the right place per platform:

- `starship.toml` — prompt theme
- `env.nu` — starship, zoxide, fnm init
- `config.nu` — aliases, custom commands
- `.gitconfig` — git aliases
- `Media Keys.ahk` — media keys (windows only)

## after setup

restart nushell and everything should work.

set nushell as default:

- **unix** — `chsh -s (which nu)`
- **windows** — set as default profile in windows terminal settings

config lives at:

- **windows** — `~/AppData/Roaming/nushell/`
- **linux/wsl** — `~/.config/nushell/`
- **macos** — `~/Library/Application Support/nushell/`

## custom commands

these come with `config.nu`:

- `mkcd foo` — mkdir + cd
- `fdz name` — find file with fd, jump to its dir
- `pubip` — public ip
- `z dir` — zoxide smart cd
- `cat` → `bat`
- `lg` → `lazygit`
- `ld` → `lazydocker`
