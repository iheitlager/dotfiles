# Getting Help in the Command Line (With Style)

*Part of the series: Software Development with AI*

## Introduction

I spend hours in the terminal. Getting help quickly matters.

But standard help commands are boring. They're hard to read. No colors. No structure.

This is my solution. My dotfiles make help commands beautiful and useful.

Let me show you eight commands that changed my workflow.

## The Problem with Standard Help

Traditional help commands work. But they're not user-friendly.

`man` pages are walls of text. `--help` flags have no syntax highlighting.

Finding what you need takes too long. Scrolling is tedious.

We can do better.

## The Solution: Colorful Command Line Help

I created aliases and functions in my dotfiles. They add color and structure to help commands.

My repo is here: [github.com/iheitlager/dotfiles](https://github.com/iheitlager/dotfiles)

Here are the eight commands I use daily.

## 1. info - Quick Reference with tldr

TODO: Explain tldr and the info alias (alias info=tldr)
- Get this through `brew install tldr`

```bash
# Example usage
info tar
```

## 2. man - Beautiful Manual Pages

TODO: Explain man with bat integration (export MANPAGER="col -b | bat --plain --language=man"). The col is to remove formatting from man, so bat can do its thin.

- get this through `brew install bat`

```bash
# Example usage
man grep
```

## 3. cheat - Quick Cheatsheets

TODO: Explain cheat.sh integration with curl

```bash
# Implementation
cheat() {
    curl -s "cheat.sh/$1" | bat --plain --language=help
}
```

## 4. a - Sorted Alias List

TODO: Explain alias listing

```bash
# Alias definition
alias a='alias | sort | bat --plain --language=bash'
```

## 5. e - Environment Variables

TODO: Explain env command

```bash
# Alias definition
alias e='env | sort | bat --plain --language=bash'
```

## 6. help - Colorized --help Output

TODO: Explain the help function from bash/bash_aliases


```bash
help() {
    if [ $# -eq 0 ]; then
        # Show shell built-in help
        builtin help | bat --plain --language=help
    else
        # Format command help
        "$@" --help 2>&1 | bat --plain --language=help
    fi
}
```


```bash
# Example usage
help docker
```

see how it nicely colors and adds paging as well.

## 7. githelp/gh - Git-Specific Help

TODO: Explain git aliases helper

```bash
# Implementation
cat $DOTFILES/git/bash_aliases | grep alias | grep -v cat | grep --color=auto git
```

## 8. Command Reference Table

| Command | Purpose | Source |
|---------|---------|--------|
| info | Quick reference (tldr) | TODO |
| man | Manual pages with color | TODO |
| cheat | Cheatsheets from cheat.sh | TODO |
| a | List all aliases | bash/bash_aliases |
| e | Show environment vars | TODO |
| help | Colorized --help | bash/bash_aliases |
| githelp/gh | Git aliases help | git/bash_aliases |

## Implementation Details

TODO: Add technical details about:
- bat integration
- Color schemes
- File locations in dotfiles

## Getting Started

TODO: Installation instructions

## Conclusion

TODO: Wrap up the article

## Target
- 800 words
- First person voice
- Simple tone
- Max 15 words per sentence
- Include code examples
- Reference github.com/iheitlager/dotfiles