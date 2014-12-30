alias more='less'

alias ll='ls -FGlAhp'
alias ls='ls -G'
alias a='alias'
alias h='history'
alias c='clear'
alias f='open -a Finder ./'

alias pubkey="more ~/.ssh/id_rsa.pub | pbcopy | echo '=> Public key copied to pasteboard.'"
alias path='echo -e ${PATH//:/\\n}'
alias recent="ls -lAt | head"

alias ..='cd ../'
alias ...='cd ../..'
alias cd..='cd ../'
alias ~='cd ~'

