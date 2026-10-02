# ♡ uwu-term shell integration for bash (loaded with --rcfile)
# Loads your usual bashrc first, then adds OSC 133 marks (command start / end +
# exit code) and OSC 7 (current folder) so the mascot can react to commands.
[ -f /etc/bash.bashrc ] && . /etc/bash.bashrc
[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"

if [[ $- == *i* && -z ${__uwu_loaded:-} ]]; then
  __uwu_loaded=1
  __uwu_ran=0
  # PS0 is printed right before a command runs. The array subscript is an
  # arithmetic expression evaluated in this shell, so it also flags that a
  # command ran, without a DEBUG trap (which would clash with other tools).
  PS0="${PS0:-}"'${__uwu_nil[__uwu_ran=1]}'$'\e]133;C\a'
  __uwu_precmd() {
    local ec=$?
    if [[ $__uwu_ran == 1 ]]; then printf '\e]133;D;%s\a' "$ec"; fi
    __uwu_ran=0
    printf '\e]7;file://%s%s\a' "${HOSTNAME:-localhost}" "$PWD"
    printf '\e]133;A\a'
    return $ec
  }
  # run first, so it sees the exit code of your command
  if [[ $(declare -p PROMPT_COMMAND 2>/dev/null) == "declare -a"* ]]; then
    PROMPT_COMMAND=(__uwu_precmd "${PROMPT_COMMAND[@]}")
  else
    PROMPT_COMMAND="__uwu_precmd${PROMPT_COMMAND:+; $PROMPT_COMMAND}"
  fi
fi
