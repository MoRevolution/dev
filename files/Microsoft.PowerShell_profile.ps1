# oh-my-posh
oh-my-posh init pwsh --config "C:\Users\MoRevolution\zsh-ish.omp.json" | Invoke-Expression

# databricks completions
databricks completion powershell | Out-String | Invoke-Expression

# zoxide
Invoke-Expression (& { (zoxide init powershell | Out-String) })
fnm env --use-on-cd --shell powershell | Out-String | Invoke-Expression