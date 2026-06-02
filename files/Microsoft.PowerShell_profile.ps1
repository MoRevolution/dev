# Starship prompt
Invoke-Expression (&starship init powershell)

# Zoxide
Invoke-Expression (& { (zoxide init powershell | Out-String) })

# fnm
fnm env --use-on-cd --shell powershell | Out-String | Invoke-Expression

# --- Aliases ---
Set-Alias -Name cat -Value bat -Option AllScope
Set-Alias -Name lg -Value lazygit
Set-Alias -Name ld -Value lazydocker

# --- Custom commands ---

# Create a directory and cd into it
function mkcd($path) {
    New-Item -ItemType Directory -Path $path -Force | Out-Null
    Set-Location $path
}

# Find a file with fd and jump to its directory with zoxide
function fdz($name) {
    $result = fd --color=never --type f $name | Select-Object -First 1
    if (-not $result) {
        Write-Host "File not found."
        return
    }
    z (Split-Path $result -Parent)
}

# Get public IP
function pubip {
    (Invoke-RestMethod http://ifconfig.me/ip).Trim()
}

# Compile and run C file
function ccr($file) {
    $out = $file -replace '\.c$', ''
    cc $file -o $out
    & "./$out"
}
