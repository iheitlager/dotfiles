# iheitlager does dotfiles

## dotfiles

Your dotfiles are how you personalize your system. These are mine specific for working on OSX.
My workflow is all about bash, terminal, vim and tmux.

I believe everything should be versioned and scripted.  Your laptop is your personal workstation for which you have to tweak your personal workflow. As such I am a fan of the [dotfiles philosophy](https://dotfiles.github.io/). 
I therefore started with [holmans dotfiles](https://github.com/holman/dotfiles) and created my own, although this is bash centric instead of zsh. Furthermore I stayed with Terminals instead of iTerm2.
This dotfile system is basic scripting with some topical modularization, no fancy agent convergence based config management.

## install

Run this:

```sh
git clone https://github.com/iheitlager/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
script/bootstrap
```

There are two commands to run every now and then:
* `dot` to upgrade brewd
* `vimstall` to do Vundle based vim packages

## topical

Everything is configured and tweaked within `~/.dotfiles`. The actual dotfiles are symlinked from this folder during the bootstrap.
This should remain on your system, and offers one place for versioning of your dotfiles, and for example allows .ssh to be excluded.
Everything's built around topic areas. If you're adding a new area to your
forked dotfiles — say, "Java" — you can simply add a `java` directory and put files in there. 
The complete dotfiles system consists of three main parts:
- symlinks to dotfiles
- topical installers during `script\bootstrap
- topical extensions to be loaded by `.bash_profile`.


## components

There's a few special files in the hierarchy.

- **bin/**: `bin/` will get added to your `$PATH` .bash_profile and anything in there will be made available everywhere.
- **topic/bash_aliases**: Any file named `bash_aliases` is loaded by .bash_profile and provides aliases available in your shell
- **topic/bash_env**: Any file named `bash_env` is loaded by .bash_profile and provides environment variables available in your shell
- **topic/bash_completion**: Any file named `bash_completion` is loaded by .bash_profile, is supposed to contain completion statements and is available in your shell
- **topic/brew_packages**: Any file named `brew_packages` is executed when running `dot`, this provides a way to create HomeBrew based installers. It is adviced to also put your package managers in here (like `pip` for python and `npm` for node
- **topic/install.sh**: Any file named `install.sh` is executed when running `script\bootstrap`, this provides a way to create topical installers
- **topic/\*.symlink**: Any files ending in `*.symlink` get symlinked into
  your `$HOME`. This is such that you can keep all of those versioned in your dotfiles directory, 
  but still keep those autoloaded files in your home directory. These files get
  symlinked in when you run `script/bootstrap`.

Do not forget to never checkin secrets in any of these files, use ~/.localrc for this (sourced by `.bash_profile`)

## credits
- Main inspiration comes from https://github.com/holman/dotfiles
- Read about the dotfile philosophy: https://dotfiles.github.io/
- Get more inspiration here: http://www.dotfiles.org/
- TMUX basics: http://mutelight.org/practical-tmux
- Solarized theme from http://ethanschoonover.com/solarized
