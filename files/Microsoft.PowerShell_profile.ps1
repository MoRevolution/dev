# Aliases
Set-Alias -Name cat -Value bat

# Cache directory for faster shell startup
$cacheDir = "$env:USERPROFILE\.ps_cache"
if (-not (Test-Path $cacheDir)) {
    New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
}

# oh-my-posh
$ompConfig = "$env:USERPROFILE\zsh-ish.omp.json"
if (Test-Path $ompConfig) {
    oh-my-posh init pwsh --config $ompConfig | Invoke-Expression
}

# zoxide with caching
$env:_ZO_DATA_DIR = "$env:USERPROFILE\.zoxide.db"
$zoxideCache = "$cacheDir\zoxide_init.ps1"
if (-not (Test-Path $zoxideCache) -or ((Get-Date) - (Get-Item $zoxideCache).LastWriteTime).TotalDays -gt 7) {
    zoxide init powershell | Set-Content -Path $zoxideCache -Encoding utf8
}
. $zoxideCache

# fnm with caching
$fnmCache = "$cacheDir\fnm_env.ps1"
if (-not (Test-Path $fnmCache) -or ((Get-Date) - (Get-Item $fnmCache).LastWriteTime).TotalDays -gt 7) {
    fnm env --use-on-cd --shell powershell | Out-File -FilePath $fnmCache -Encoding utf8
}
. $fnmCache

# databricks completions with caching (optional)
$databricksCache = "$cacheDir\databricks_completion.ps1"
if (Get-Command databricks -ErrorAction SilentlyContinue) {
    if (-not (Test-Path $databricksCache) -or ((Get-Item $databricksCache).LastWriteTime -lt (Get-Date).AddDays(-7))) {
        databricks completion powershell | Out-File -FilePath $databricksCache -Encoding utf8
    }
    . $databricksCache
}

# funcs to stuffs
function mkcd {
    param([Parameter(Mandatory=$true)][string]$Path)
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
    Set-Location -Path $Path
}

function fdz {
    param([Parameter(Mandatory=$true,Position=0)][string]$Name)
    $path = fd --color=never --type f $Name 2>$null | Select-Object -First 1
    if (-not $path) { Write-Host "File not found."; return }
    z (Split-Path -Parent $path)
}


function Get-PubIP {
    (Invoke-WebRequest http://ifconfig.me/ip ).Content
}
