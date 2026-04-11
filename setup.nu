#!/usr/bin/env nu
# =============================================================================
# Platform detection stuffs
# =============================================================================

def get-platform [] {
    match $nu.os-info.name {
        "windows" => "windows"
        "macos" => "macos"
        "linux" => {
            if ("/proc/version" | path exists) {
                let ver = (open /proc/version | str downcase)
                if ($ver | str contains "microsoft") { "wsl" } else { "linux" }
            } else { "linux" }
        }
        _ => "unknown"
    }
}

def is-unix [platform: string] { $platform in ["wsl", "macos", "linux"] }

# =============================================================================
# Package manager helpers
# =============================================================================

def get-manager [platform: string] {    
    if $platform == "windows" {
        "winget"
    } else if (which brew | is-not-empty) {
        "brew"
    } else if (which apt | is-not-empty) {
        "apt"
    } else {
        null
    }
}

def pkg-is-installed [manager: string, id: string] {
    match $manager {
        "winget" => {
            let list = (^winget list --disable-interactivity | str downcase)
            $list | str contains ($id | str downcase)
        }
        "brew" => {
            let installed = (^brew list --formula -1 | lines) ++ (^brew list --cask -1 | lines)
            ($id | str downcase) in ($installed | each { str downcase })
        }
        "apt" => {
            let installed = (^dpkg-query -W -f '${Package}\n' | lines | each { str trim })
            ($id | str downcase) in ($installed | each { str downcase })
        }
    }
}

def pkg-install [manager: string, id: string, args?: string] {
    match $manager {
        "winget" => {
            if ($args | is-empty) {
                ^winget install $id --accept-source-agreements --accept-package-agreements --silent | complete
            } else {
                ^winget install $id --accept-source-agreements --accept-package-agreements --silent $args | complete
            }
        }
        "brew" => { ^brew install $id | complete }
        "apt" => { ^sudo apt install -y $id | complete }
    }
}

# =============================================================================
# Section filtering
# =============================================================================

def sections-for-platform [platform: string, personal: bool] {
    mut sections = ["common"]
    if $platform == "windows" {
        $sections = ($sections | append ["gui_only" "windows_only"])
    } else {
        $sections = ($sections | append "unix_only")
        if $platform == "macos" { $sections = ($sections | append ["gui_only" "macos_only"]) }
        if $platform == "wsl" { $sections = ($sections | append "wsl_only") }
    }
    if $personal { $sections = ($sections | append "personal") }
    $sections
}

def pkg-id-for [pkg: record, platform: string, manager: string] {
    # Try manager key first (brew/winget), then platform key
    if ($manager in ($pkg | columns)) {
        $pkg | get $manager
    } else if ($platform in ($pkg | columns)) {
        $pkg | get $platform
    } else {
        null
    }
}

# =============================================================================
# Commands
# =============================================================================

# Install packages from config
def "main packages" [
    --dry-run (-n)  # Preview without installing
    --personal (-p)  
    --config (-c): string = "config.toml"  # Config file path
] {
    let platform = get-platform
    let manager = get-manager $platform
    if ($manager == null) {
        print $"(ansi red)Error:(ansi reset) No package manager found"
        return
    }

    let cfg = open $config
    let sections = sections-for-platform $platform $personal
    let all_pkgs = $cfg.packages
    let pad = 22

    print $"Packages  \((ansi cyan)($platform)(ansi reset) / (ansi cyan)($manager)(ansi reset)\)\n"

    # Update package cache once before installing
    if (not $dry_run and $manager == "brew") {
        print $"  (ansi dark_gray)updating brew cache...(ansi reset)" --no-newline
        ^brew update out+err> /dev/null
        print $"(char cr)  (ansi dark_gray)brew cache updated     (ansi reset)"
    }

    mut installed_count = 0
    mut skipped_count = 0
    mut failed_count = 0

    for section in $sections {
        if not ($section in ($all_pkgs | columns)) { continue }
        let pkgs = $all_pkgs | get $section

        for col in ($pkgs | columns) {
            let pkg = $pkgs | get $col
            let id = pkg-id-for $pkg $platform $manager
            if ($id == null) { continue }  # not for this platform
            let name_padded = ($col | fill -w $pad -c ' ' -a l)

            if (pkg-is-installed $manager $id) {
                print $"  (ansi dark_gray)✓ ($name_padded) skip(ansi reset)"
                $skipped_count = $skipped_count + 1
                continue
            }

            if $dry_run {
                print $"  (ansi cyan)○ ($name_padded) install(ansi reset)"
                $installed_count = $installed_count + 1
                continue
            }

            # Show installing indicator, then overwrite with result
            print $"  (ansi dark_gray)◌ ($name_padded) installing...(ansi reset)" --no-newline
            let args = if ("windows_args" in ($pkg | columns)) { $pkg.windows_args } else { null }
            let result = (pkg-install $manager $id $args)
            let ok = ($result.exit_code == 0)

            if $ok {
                print $"(char cr)  (ansi green)✓ ($name_padded) installed(ansi reset)     "
                $installed_count = $installed_count + 1
            } else {
                print $"(char cr)  (ansi red)✗ ($name_padded) failed(ansi reset)        "
                $failed_count = $failed_count + 1
                let log = ([($result.stdout | default "") ($result.stderr | default "")] | str join "\n" | str trim)
                if (not ($log | is-empty)) {
                    print $"    (ansi dark_gray)($log)(ansi reset)"
                }
            }
        }
    }

    print $"\n  (ansi green)($installed_count) installed(ansi reset) · ($skipped_count) skip · (ansi red)($failed_count) failed(ansi reset)"
}

# Copy configuration files
def "main files" [
    --dry-run (-n)
    --config (-c): string = "config.toml"
] {
    let platform = get-platform
    let cfg = open $config
    let files = $cfg.files

    print $"Platform: (ansi cyan)($platform)(ansi reset)\n"

    mut results = []

    for entry in ($files | transpose source dest_data) {
        let source = $entry.source
        let dest_data = $entry.dest_data

        # Resolve destination for this platform
        let dest = if ($dest_data | describe | str starts-with "record") {
            if ($platform in ($dest_data | columns)) { $dest_data | get $platform } else { null }
        } else {
            $dest_data  # simple string = all platforms
        }

        if ($dest == null) {
            $results = ($results | append { source: $source, dest: "-", action: "SKIP (no dest)" })
            continue
        }

        if not ($source | path exists) {
            $results = ($results | append { source: $source, dest: $dest, action: "FAIL (not found)" })
            continue
        }

        if $dry_run {
            $results = ($results | append { source: $source, dest: $dest, action: "COPY" })
        } else {
            let result = try {
                let dest_expanded = ($dest | path expand)
                let dest_dir = if (($dest_expanded | str ends-with "/") or ($dest_expanded | str ends-with "\\")) {
                    $dest_expanded
                } else {
                    $dest_expanded | path dirname
                }
                mkdir $dest_dir
                cp $source $dest_expanded
                "OK"
            } catch {|e| $"FAIL: ($e.msg)" }
            $results = ($results | append { source: $source, dest: $dest, action: $result })
        }
    }

    $results | table
}

# Generate init files for starship and zoxide
def "main init" [
    --dry-run (-n)
    --config (-c): string = "config.toml"
] {
    let nuconfig_dir = $nu.default-config-dir

    mkdir $nuconfig_dir

    # Ensure source targets exist even before the tools are installed.
    for f in ["starship.nu" "zoxide.nu"] {
        let path = $"($nuconfig_dir)/($f)"
        if not ($path | path exists) {
            "" | save --force $path
        }
    }

    if not $dry_run {
        try {
            print "  Generating starship init..."
            ^starship init nu | save --force $"($nuconfig_dir)/starship.nu"
        } catch { print "  (starship not found yet)" }

        try {
            print "  Generating zoxide init..."
            ^zoxide init nushell | save --force $"($nuconfig_dir)/zoxide.nu"
        } catch { print "  (zoxide not found yet)" }
    }
}

# Run post-install commands
def "main post-install" [
    --dry-run (-n)
    --config (-c): string = "config.toml"
] {
    let platform = get-platform
    let cfg = open $config
    let post = if ("post_install" in ($cfg | columns)) { $cfg.post_install } else { null }

    if ($post == null) {
        print "No post-install commands defined."
        return
    }

    mut commands = []

    # Collect "all" platform commands
    if ("all" in ($post | columns)) {
        let all_cmds = $post.all
        for col in ($all_cmds | columns) {
            $commands = ($commands | append { name: $col, cmd: ($all_cmds | get $col) })
        }
    }

    # Collect platform-specific commands
    let platform_keys = match $platform {
        "macos" => ["unix" "macos"]
        "wsl" => ["unix" "wsl"]
        "linux" => ["unix" "linux"]
        _ => [$platform]
    }
    for platform_key in $platform_keys {
        if ($platform_key in ($post | columns)) {
            let plat_cmds = $post | get $platform_key
            for col in ($plat_cmds | columns) {
                $commands = ($commands | append { name: $col, cmd: ($plat_cmds | get $col) })
            }
        }
    }

    if ($commands | is-empty) {
        print "No post-install commands for this platform."
        return
    }

    for entry in $commands {
        if $dry_run {
            print $"  [DRY RUN] ($entry.name): ($entry.cmd)"
        } else {
            print $"  ($entry.name)... " --no-newline
            try {
                nu -c $entry.cmd
                print $"(ansi green)OK(ansi reset)"
            } catch {
                print $"(ansi yellow)SKIP(ansi reset)"
            }
        }
    }
}

# Show installation status
def "main status" [
    --personal (-p) 
    --config (-c): string = "config.toml"
] {
    let platform = get-platform
    let manager = get-manager $platform
    if ($manager == null) {
        print $"(ansi red)Error:(ansi reset) No package manager found"
        return
    }

    let cfg = open $config
    let sections = sections-for-platform $platform $personal
    let all_pkgs = $cfg.packages
    let pad = 22

    print $"Status  \((ansi cyan)($platform)(ansi reset) / (ansi cyan)($manager)(ansi reset)\)\n"

    mut installed_count = 0
    mut total = 0

    for section in $sections {
        if not ($section in ($all_pkgs | columns)) { continue }
        let pkgs = $all_pkgs | get $section

        for col in ($pkgs | columns) {
            let pkg = $pkgs | get $col
            let id = pkg-id-for $pkg $platform $manager
            if ($id == null) { continue }
            let name_padded = ($col | fill -w $pad -c ' ' -a l)
            $total = $total + 1

            if (pkg-is-installed $manager $id) {
                print $"  (ansi green)✓(ansi reset) ($name_padded) (ansi dark_gray)installed(ansi reset)"
                $installed_count = $installed_count + 1
            } else {
                print $"  (ansi red)✗(ansi reset) ($name_padded) (ansi dark_gray)missing(ansi reset)"
            }
        }
    }

    print $"\n  ($installed_count)/($total) installed"
}

# Run full setup (packages + files + init + post-install)
def main [
    --dry-run (-n)  # Preview without making changes
    --personal (-p)  # Include personal 
    --config (-c): string = "config.toml"  # Config file path
] {
    print $"(ansi blue_bold)Dev Environment Setup(ansi reset)\n"

    if $dry_run { print $"(ansi yellow)DRY RUN MODE(ansi reset)\n" }

    print "── Packages ──"
    main packages --dry-run=$dry_run --personal=$personal --config $config

    print "\n── Files ──"
    main files --dry-run=$dry_run --config $config

    print "\n── Init ──"
    main init --dry-run=$dry_run --config $config

    print "\n── Post-install ──"
    main post-install --dry-run=$dry_run --config $config

    print $"\n(ansi green_bold)Done!(ansi reset)"
}
