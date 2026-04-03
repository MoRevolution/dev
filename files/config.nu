# config.nu — Nushell shell config
# Loaded after env.nu on every interactive shell start

# --- Source pre-generated inits ---
let nu_config_dir = match $nu.os-info.name {
    "windows" => $"($env.APPDATA)\nushell"
    _ => $"($env.HOME)/.config/nushell"
}

if ($"($nu_config_dir)/starship.nu" | path exists) { source $"($nu_config_dir)/starship.nu" }
if ($"($nu_config_dir)/zoxide.nu" | path exists) { source $"($nu_config_dir)/zoxide.nu" }

# --- Shell settings ---
$env.config.show_banner = false
$env.config.history = {
    max_size: 10000
    sync_on_enter: true
    file_format: "sqlite"
}
$env.config.completions = {
    case_sensitive: false
    quick: true
    partial: true
    algorithm: "fuzzy"
}
$env.config.cursor_shape = {
    emacs: "line"
    vi_insert: "line"
    vi_normal: "block"
}

# --- Aliases ---
alias cat = bat
alias lg = lazygit
alias ld = lazydocker

# --- Custom commands ---

# Create a directory and cd into it
def mkcd [path: string] {
    mkdir $path
    cd $path
}

# Find a file with fd and jump to its directory with zoxide
def fdz [name: string] {
    let result = (fd --color=never --type f $name | lines | first)
    if ($result | is-empty) {
        print "File not found."
        return
    }
    z ($result | path dirname)
}

# Get public IP
def pubip [] {
    http get http://ifconfig.me/ip | str trim
}

# Compile and run C file
def ccr [file: string, ...args: string] {
    let out = ($file | str replace ".c" "")
    cc $file -o $out ...$args
    ^$"./($out)"
}
