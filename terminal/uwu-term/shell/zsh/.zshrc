# ♡ uwu-term shell integration for zsh
# Loads your usual .zshrc, then adds OSC 133 marks (command start / end + exit
# code) and OSC 7 (current folder) so the mascot can react.
ZDOTDIR=${UWU_USER_ZDOTDIR:-$HOME}
[[ -f $ZDOTDIR/.zshrc ]] && source $ZDOTDIR/.zshrc

if [[ -o interactive ]]; then
  autoload -Uz add-zsh-hook
  typeset -g __uwu_ran=0
  __uwu_preexec() { __uwu_ran=1; print -n '\e]133;C\a' }
  __uwu_precmd() {
    local ec=$?
    (( __uwu_ran )) && print -n "\e]133;D;${ec}\a"
    __uwu_ran=0
    print -n "\e]7;file://${HOST:-localhost}${PWD}\a"
    print -n '\e]133;A\a'
  }
  add-zsh-hook preexec __uwu_preexec
  precmd_functions=(__uwu_precmd $precmd_functions)
fi
