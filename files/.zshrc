# Aliases
alias cat='bat'
alias ls='ls --color=auto'
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'



plugins=(git)
source $ZSH/oh-my-zsh.sh

# zoxide
eval "$(zoxide init zsh)"
export _ZO_DATA_DIR=/mnt/c/Users/MoRevolution/.zoxide_wsl.db

eval "$(fnm env --use-on-cd)"
eval "$(fzf --zsh)"


# History settings
HISTSIZE=10000
SAVEHIST=10000
HISTFILE=~/.zsh_history
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE
setopt SHARE_HISTORY

# Functions
mkcd() {
    mkdir -p "$1" && cd "$1"
}

fdz() {
    local path=$(fd --color=never --type f "$1" 2>/dev/null | head -1)
    if [[ -z "$path" ]]; then
        echo "File not found."
        return 1
    fi
    z "$(dirname "$path")"
}

pubip() {
    curl -s http://ifconfig.me/ip
}

if [[ -d "/home/linuxbrew/.linuxbrew" ]]; then
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
elif [[ -d "/opt/homebrew" ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi
