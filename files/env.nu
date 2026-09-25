# env.nu — Nushell environment config
# Loaded before config.nu on every shell start

# --- Platform-specific PATH ---
if ($nu.os-info.name == "linux") {
    # Homebrew on Linux/WSL
    if ("/home/linuxbrew/.linuxbrew/bin" | path exists) {
        $env.PATH = ($env.PATH | prepend "/home/linuxbrew/.linuxbrew/bin")
    }
    # fnm path
    let fnm_path = $"($env.HOME)/.local/share/fnm"
    if ($fnm_path | path exists) {
        $env.PATH = ($env.PATH | prepend $fnm_path)
    }
} else if ($nu.os-info.name == "macos") {
    if ("/opt/homebrew/bin" | path exists) {
        $env.PATH = ($env.PATH | prepend "/opt/homebrew/bin")
    }
}

# --- Docker Desktop CLI (symlinks in ~/.docker/bin) ---
# zsh gets this via `export PATH="$HOME/.docker/bin:$PATH"` in ~/.zshrc,
# which nushell never sources — so ensure it here instead of relying on inheritance.
let docker_bin = ($env.HOME | path join ".docker" "bin")
if ($docker_bin | path exists) and ($docker_bin not-in $env.PATH) {
    $env.PATH = ($env.PATH | prepend $docker_bin)
}

# --- fnm (Node version manager) ---
# NB: `fnm env --json` does not include PATH (fnm 1.39+), so prepend this
# shell's multishell bin explicitly — this mirrors what `eval "$(fnm env)"`
# does for zsh. The multishell path is stable per shell instance, so later
# `fnm use <version>` switches keep working without further PATH changes.
try {
    fnm env --json | from json | load-env
    if "FNM_MULTISHELL_PATH" in $env {
        let multishell_bin = ($env.FNM_MULTISHELL_PATH | path join "bin")
        if ($multishell_bin not-in $env.PATH) {
            $env.PATH = ($env.PATH | prepend $multishell_bin)
        }
    }
}
