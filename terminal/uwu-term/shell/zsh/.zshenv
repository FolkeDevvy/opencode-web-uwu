# ♡ uwu-term: zsh starts here because ZDOTDIR points at this folder.
# Load your real ~/.zshenv, but keep ZDOTDIR pointing here for .zshrc.
__uwu_zdotdir=$ZDOTDIR
ZDOTDIR=${UWU_USER_ZDOTDIR:-$HOME}
[[ -f $ZDOTDIR/.zshenv ]] && source $ZDOTDIR/.zshenv
UWU_USER_ZDOTDIR=$ZDOTDIR
ZDOTDIR=$__uwu_zdotdir
