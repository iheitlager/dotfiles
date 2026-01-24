# iheitlager does dotfiles

## dotfiles

Your dotfiles are how you personalize your system. These are mine, specific for working on OSX.
My workflow is all about Homebrew, bash, iTerm2, vscode and claude. It is also very XDG inspired. 

I believe everything should be versioned and scripted.  Your laptop is your personal workstation for which you have to tweak your personal workflow. That way it also becomes shareable between various workstations like your private and workmachines. As such I am a fan of the [dotfiles philosophy](https://dotfiles.github.io/). I therefore started with [holmans dotfiles](https://github.com/holman/dotfiles) and created my own, although I am very much bash centric instead of zsh. Do not really know the value of another shell.

This dotfile system is basic scripting with some topical modularization, no fancy agent convergence based config management.
Modern CLI tools (eza, bat, ripgrep, fd, delta, fzf) provide rich colored output and better defaults.

## install

Run this:

```sh
# need to install homebrew on a clean laptop to make sure git is there
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
$ eval "$(/opt/homebrew/bin/brew shellenv)"    # make sure homebrew is known

$ git clone git@github.com:iheitlager/dotfiles.git ~/.dotfiles
$ ~/.dotfiles/script/bootstrap                 # run this once to configure dotfile
$ dot                                          # run anywhere to install or upgrade packages
```

There are two commands to run every now and then:
* `dot` to upgrade homebrew
* `vimstall` to do Vundle based vim packages

You have to run your npm, pip, etc updates yourself

## topical

Everything is configured and tweaked within `~/.dotfiles`. The actual dotfiles are symlinked from this folder during the bootstrap.
This should remain on your system, and offers one place for versioning of your dotfiles, and for example allows .ssh to be excluded.
Everything's built around topic areas. If you're adding a new area to your
forked dotfiles — say, "Python" — you can simply add a `python` directory and put files in there. 
The complete dotfiles system consists of install time and runtime parts, in total four parts:

1. create an XDG compliant .config structure
1. symlinks to dotfiles into .config and .local
2. topical extensions to be loaded by `.bash_profile`
3. topical brew based installers during `script\bootstrap [--no-brew]` (run these with `dot`)
4. `install.sh` scripts to finalize

## components

There's a few special files in the hierarchy.

- **bin/**: `bin/` will get added to your `$PATH` .bash_profile and anything in there will be made available everywhere.
- **topic/bash_aliases**: Any file named `bash_aliases` is loaded by .bash_profile and provides aliases available in your shell
- **topic/bash_env**: Any file named `bash_env` is loaded by .bash_profile and provides environment variables available in your shell
- **topic/bash_completion**: Any file named `bash_completion` is loaded by .bash_profile, is supposed to contain completion statements and is available in your shell
- **topic/brew_packages**: Any file named `brew_packages` is executed when running `dot`, this provides a way to create HomeBrew based installers. It is adviced to also put your package managers in here (like `pip` for python and `npm` for node)
- **topic/install.sh**: Any file named `install.sh` is executed when running `script\bootstrap`, this provides a way to create topical installers
- **topic/\*.symlink**: Any files ending in `*.symlink` get symlinked into
  your `$HOME`. This is to keep your files versioned in your dotfiles., while keeping them where they belong in your home directory. 
  These files get symlinked in when you run `script/bootstrap`.
- **topic/config/**: Any directory named `config` inside a topic gets symlinked to `~/.config/<topic>/` for XDG compliance
- **config/\<app\>/**: The central `config/` directory also gets linked: `config/<app>/` → `~/.config/<app>/`
- **local/bin/**: The central `.local/` directory also gets linked: `local/bin/<app>` → `~/.local/bin/<app>`

Do not forget to never checkin secrets in any of these files, use `~/.config/secrets` for this (sourced by `.bash_profile`). This file is excluded from version control for that reason.

## XDG Base Directory

This dotfiles setup follows the [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/):

| Variable | Location | Purpose |
|----------|----------|---------|
| `XDG_CONFIG_HOME` | `~/.config` | User configuration files |
| `XDG_DATA_HOME` | `~/.local/share` | User data files |
| `XDG_STATE_HOME` | `~/.local/state` | User state (logs, history) |
| `XDG_CACHE_HOME` | `~/.cache` | Non-essential cached data |

Applications configured for XDG compliance include: vim, bat, ripgrep, tmux, pip, docker, colima, ipython, matplotlib, ollama, and history files for bash, python, psql, and less.

See [docs/xdg_setup.md](docs/xdg_setup.md) for detailed documentation.

## credits
- Main inspiration comes from https://github.com/holman/dotfiles
- More about the dotfile stuff: https://dotfiles.github.io/