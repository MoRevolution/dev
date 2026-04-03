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

# --- fnm (Node version manager) ---
try { fnm env --json | from json | load-env }
