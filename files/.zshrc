# History
HISTSIZE=10000
SAVEHIST=10000
HISTFILE=~/.zsh_history
setopt HIST_IGNORE_ALL_DUPS HIST_IGNORE_SPACE SHARE_HISTORY

bindkey -e

alias cat='bat'
alias ls='ls --color=auto'
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'
alias copy='copy.exe'

# fnm - must be initialized before use
FNM_PATH="/home/morevolution/.local/share/fnm"
if [ -d "$FNM_PATH" ]; then
  export PATH="$FNM_PATH:$PATH"
  eval "`fnm env`"
  eval "$(fnm env --use-on-cd)"
fi

# zoxide
eval "$(zoxide init zsh)"
export _ZO_DATA_DIR=/mnt/c/Users/MoRevolution/.zoxide_wsl.db

# fzf - use init instead of --zsh if that option doesn't exist
if command -v fzf >/dev/null 2>&1; then
  eval "$(fzf --zsh 2>/dev/null || fzf-completion -zsh; fzf-key-bindings 2>/dev/null)"
fi

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

ccr(){
    # comile and run c
	cc "$1" -o "$1%.c" "${@:2}"  &&  ./"$1%.c"
}

if [[ -d "/home/linuxbrew/.linuxbrew" ]]; then
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
elif [[ -d "/opt/homebrew" ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Robbyrussell-style prompt (overrides Zim's asciiship)
# Arrow is green on success, red on failure. Shows git branch if in repo.
_git_prompt_info() {
  local branch=$(git symbolic-ref --short HEAD 2>/dev/null)
  [[ -n "$branch" ]] || return
  local dirty=""
  [[ -n $(git status --porcelain 2>/dev/null) ]] && dirty=" %F{yellow}✗%f"
  echo " %F{blue}git:(%F{red}${branch}%F{blue})%f${dirty}"
}
setopt PROMPT_SUBST
PROMPT='%(?:%F{green}➜:%F{red}➜)%f %F{cyan}%c%f$(_git_prompt_info) '