#!/bin/bash
    _cabine_completion() {
        local cur prev
        COMPREPLY=()
        cur="${COMP_WORDS[COMP_CWORD]}"
        prev="${COMP_WORDS[COMP_CWORD-1]}"
        opts=""
        pos=""

  opts_cabine="--help -h"
  subs_cabine="daemon load service"
    opts_cabine_daemon="--help --pidfile --scenario -h -p -s"
    subs_cabine_daemon="ninja"
    opts_cabine_load="--help --scenario -h -s"
    subs_cabine_load="biloute"
    opts_cabine_service="--help --install --reinstall --uninstall -h -i -r -u"
    subs_cabine_service=""

    case "$cur" in
        /*|./*|../*|~/*) # Si l'utilisateur tape un chemin
            COMPREPLY=( $(compgen -f -- "$cur") )
            return 0
            ;;
    esac
    
    case "$prev" in
        daemon) opts="$opts_cabine_daemon $subs_cabine_daemon" ;;
        load) opts="$opts_cabine_load $subs_cabine_load" ;;
        service) opts="$opts_cabine_service $subs_cabine_service" ;;
        *) opts="$opts_cabine $subs_cabine" ;;
    esac

    COMPREPLY=( $(compgen -W "$opts" -- $cur) )
    return 0
}
complete -F _cabine_completion cabine
