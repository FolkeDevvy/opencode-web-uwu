# ♡ uwu-term shell integration for fish (loaded with --init-command,
# after your config.fish). Adds OSC 133 marks + OSC 7 so the mascot can react.
if status is-interactive
    function __uwu_preexec --on-event fish_preexec
        printf '\e]133;C\a'
    end
    function __uwu_postexec --on-event fish_postexec
        printf '\e]133;D;%s\a' $status
    end
    function __uwu_prompt --on-event fish_prompt
        printf '\e]7;file://%s%s\a' (hostname) $PWD
        printf '\e]133;A\a'
    end
end
