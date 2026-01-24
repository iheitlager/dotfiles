# The Agents Are Coming. Clean Your `$HOME`.

*XDG-compliant dotfiles as the foundation for agentic development*

*Part 1 of a series on building an agentic development environment*

---

> "Yak shaving is what you are doing when you're doing some stupid, fiddly little task that bears no obvious relationship to what you're supposed to be working on, but yet a chain of twelve causal relations links what you're doing to the original meta-task."
>
> — Scott Hanselman

---

I'll admit it: I'm slightly OCD. I love to clean. Not just my desk—my file system. There's something deeply satisfying about `ls -la ~` returning a clean, minimal list instead of a graveyard of `.random-app-rc` files from tools I used once in 2019.

This obsession led me down a path that many developers know well: the dotfiles rabbit hole. What started as "I should version control my `.bashrc`" became a full architecture for managing configuration across machines, tools, and—as we'll explore in later articles—AI agents working in parallel.

This is the foundation. Get this right, and everything else becomes easier.

## The Problem: Config Sprawl

Open a terminal on a fresh macOS install. Use it for a week. Now run `ls -la ~ | wc -l`. I'll wait.

The home directory becomes a dumping ground. Every CLI tool, every editor plugin, every language runtime thinks it deserves a dotfile in `~`. Some use `~/.toolrc`. Others prefer `~/.tool/`. A few enlightened ones respect `~/.config/tool/`. Most don't.

**Before** — a typical home directory after a year of development:

```
~/
├── .bash_history
├── .bash_profile
├── .bashrc
├── .gitconfig
├── .lesshst              # less history, why here?
├── .npm/
├── .npmrc
├── .python_history
├── .viminfo
├── .vimrc
├── .vim/
│   ├── bundle/           # plugins mixed with config
│   └── colors/
├── .tmux.conf
├── .zsh_history
├── .zshrc
└── ... strewn across strewn across strewn47 more dotfiles
```

**After** — with XDG compliance:

```
~/
├── .bash_profile         # shell entry point (must stay)
├── .bashrc               # shell config (must stay)
├── .gitconfig            # git entry point (references XDG paths)
├── .config/
│   ├── git/
│   │   └── gitignore     # global gitignore
│   ├── tmux/
│   │   └── tmux.conf
│   └── vim/
│       └── vimrc
├── .local/
│   ├── share/
│   │   └── vim/
│   │       ├── bundle/   # plugins (not versioned)
│   │       └── colors/
│   └── state/
│       ├── bash/
│       │   └── history
│       ├── less/
│       │   └── history
│       └── python/
│           └── history
└── .dotfiles/            # the source of truth (git repo)
```

Config in `~/.config/`. State in `~/.local/state/`. Data in `~/.local/share/`. Home directory: clean.

## Why This Matters

This matters for three reasons:

1. **Version control** — Everything in `~/.config/` can be committed. Everything in `~/.local/state/` should not.
2. **Machine portability** — Clone your dotfiles, run bootstrap, done.
3. **Tool interoperability** — When tools find configs predictably, automation becomes possible.

And there's a fourth reason, the one that prompted this series: **agents need structure**. When you run multiple AI agents in parallel—each in its own git worktree, each needing consistent configuration—you need a single source of truth. When those agents share state through `~/.local/state/agent-context/`, you need the XDG structure already in place.

## Enter XDG Base Directory Specification

The [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/) solved this in 2003. Twenty years later, adoption remains inconsistent.

The spec defines four environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `XDG_CONFIG_HOME` | `~/.config` | User configuration files |
| `XDG_DATA_HOME` | `~/.local/share` | User data files |
| `XDG_STATE_HOME` | `~/.local/state` | Logs, history, runtime data |
| `XDG_CACHE_HOME` | `~/.cache` | Temporary, regenerable data |

Export these in your shell profile, and you've laid the groundwork. The challenge is getting your tools to respect them.

## The Dotfiles Repository Structure

My approach uses topic folders. Each tool gets its own directory containing everything it needs:

```
~/.dotfiles/
├── bash/
│   ├── bash_profile.symlink    # → ~/.bash_profile
│   └── bashrc.symlink          # → ~/.bashrc
├── git/
│   ├── gitconfig.symlink       # → ~/.gitconfig
│   └── config/
│       └── gitignore           # → ~/.config/git/gitignore
├── tmux/
│   └── config/                 # → ~/.config/tmux/
│       └── tmux.conf
├── vim/
│   ├── config/                 # → ~/.config/vim/
│   │   └── vimrc
│   └── install.sh              # plugin setup
└── script/
    └── bootstrap               # the glue
```

Three naming conventions drive everything:

1. **`*.symlink`** — Files linked directly to `~/` as dotfiles
2. **`config/`** — Directories linked to `~/.config/<topic>/`
3. **`install.sh`** — Topic-specific setup scripts

## The Bootstrap Script

The [bootstrap script](https://github.com/iheitlager/dotfiles/blob/main/script/bootstrap) orchestrates setup. Its core is two linking functions.

For traditional dotfiles:

```bash
install_dotfiles () {
  for src in $(find "$DOTFILES" -maxdepth 2 -name '*.symlink'); do
    dst="$HOME/.$(basename "${src%.*}")"
    link_file "$src" "$dst"
  done
}
```

This finds every `*.symlink` file and creates `~/.name` pointing to it. Simple, predictable, debuggable.

For XDG-compliant tools:

```bash
link_config_files () {
  for src in $(find "$DOTFILES" -maxdepth 2 -type d -name 'config'); do
    local topic=$(basename $(dirname "$src"))
    local dst="$HOME/.config/$topic"
    link_file "$src" "$dst"
  done
}
```

Any `config/` directory inside a topic becomes `~/.config/<topic>/`.

## Four Patterns for XDG Adoption

Not every tool plays nice with XDG. Here are four patterns I use, from cleanest to most coercive:

### 1. Native XDG Support — tmux

Since version 3.1, tmux checks `~/.config/tmux/tmux.conf` automatically. No environment variables, no symlinks to legacy paths. Just put your config in the right place:

```
~/.dotfiles/tmux/config/tmux.conf → ~/.config/tmux/tmux.conf
```

The bootstrap handles this via the `config/` directory convention. Done.

### 2. Hybrid Approach — git

Git still wants `~/.gitconfig`, but it supports XDG paths internally. My gitconfig is a thin entry point that references XDG locations:

```ini
[include]
    path = ~/.local/gitconfig           # machine-specific secrets

[core]
    excludesfile = ~/.config/git/gitignore
```

The global gitignore lives in `~/.config/git/`. Machine-specific settings (name, email, signing key) live in `~/.local/gitconfig`—generated by the bootstrap script, never committed. Best of both worlds.

### 3. Config/Data Separation — vim

Vim supports XDG for config (`~/.config/vim/vimrc`) but plugins and colorschemes are data, not config. They shouldn't be version controlled—they're installed, not authored.

```
Config:  ~/.config/vim/vimrc           → versioned in dotfiles
Data:    ~/.local/share/vim/bundle/    → plugins via Vundle
         ~/.local/share/vim/colors/    → colorschemes
```

The `install.sh` script creates the data directories and runs `:PluginInstall`:

```bash
mkdir -p "$XDG_DATA_HOME/vim/bundle"
mkdir -p "$XDG_DATA_HOME/vim/colors"
git clone https://github.com/gmarik/Vundle.vim.git "$XDG_DATA_HOME/vim/bundle/Vundle.vim"
vim -es -u "$XDG_CONFIG_HOME/vim/vimrc" -c "PluginInstall" -c "qa"
```

### 4. Environment Variable Coercion — less

Some tools don't support XDG at all but let you override paths via environment variables. `less` is a classic example—it wants to dump `.lesshst` in your home directory.

Fix it in your shell profile:

```bash
export LESSHISTFILE="$XDG_STATE_HOME/less/history"
```

History is state, not config, so it goes in `~/.local/state/`. One line, and `.lesshst` never pollutes `~/` again.

### Pattern Summary

| Tool | Pattern | How |
|------|---------|-----|
| **tmux** | Native XDG | Just works since 3.1 |
| **git** | Hybrid | Legacy entry point, XDG internals |
| **vim** | Config/data split | Config versioned, plugins installed |
| **less** | Env var coercion | `LESSHISTFILE` redirects state |

## Why This Foundation Matters

This isn't just about a clean home directory. It's infrastructure for what comes next.

The dotfiles repository becomes the spine of an agentic development environment. The XDG specification gives it structure. The symlink conventions make it portable. When you want to version control your agent instructions alongside your shell config, they live in the same repo, following the same patterns.

In the next article, we'll explore how to configure AI coding agents—and why some of them need an extra layer of symlink indirection to play nice with this setup.

But first: go clean your home directory. Trust me, you'll feel better.

---

*My dotfiles are available at [github.com/iheitlager/dotfiles](https://github.com/iheitlager/dotfiles). Clone, fork, or steal—that's the dotfiles way.*

## References

- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/)
- [Arch Wiki: XDG Base Directory](https://wiki.archlinux.org/title/XDG_Base_Directory)
- [dotfiles.github.io](https://dotfiles.github.io/) — Community dotfiles inspiration
- [Scott Hanselman on Yak Shaving](https://www.hanselman.com/blog/yak-shaving-defined-ill-get-that-done-as-soon-as-i-shave-this-yak)
