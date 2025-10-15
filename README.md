# iheitlager does dotfiles

## dotfiles

Your dotfiles are how you personalize your system. These are mine specific for working on OSX.
My workflow is all about Homebrew, bash, iTerm2 and vim.

I believe everything should be versioned and scripted.  Your laptop is your personal workstation for which you have to tweak your personal workflow. As such I am a fan of the [dotfiles philosophy](https://dotfiles.github.io/). 
I therefore started with [holmans dotfiles](https://github.com/holman/dotfiles) and created my own, although mine is bash centric instead of zsh. 
This dotfile system is basic scripting with some topical modularization, no fancy agent convergence based config management.
While working with vim and tmux, I found that iTerm2 really is a better match
due to better mouse handling.

## install

Run this:

```sh
# need to install homebrew on a clean laptop to make sure git is there
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
$ eval "$(/opt/homebrew/bin/brew shellenv)"    # make sure homebrew is known

$ git clone git@github.com:iheitlager/dotfiles.git ~/.dotfiles
$ chsh -s /bin/bash  # we love to run bash instead of zshell
$ cd ~/.dotfiles
$ script/bootstrap # run this once to configure dotfile
$ dot              # run this to install or upgrade packages, run anytime/anywhere
```

NB: be sure to setup ssh and add your keys in your `.ssh/config`

There are two commands to run every now and then:
* `dot` to upgrade homebrew
* `vimstall` to do Vundle based vim packages

You have to run your npm, pip, etc updates yourself

## topical

Everything is configured and tweaked within `~/.dotfiles`. The actual dotfiles are symlinked from this folder during the bootstrap.
This should remain on your system, and offers one place for versioning of your dotfiles, and for example allows .ssh to be excluded.
Everything's built around topic areas. If you're adding a new area to your
forked dotfiles — say, "Java" — you can simply add a `java` directory and put files in there. 
The complete dotfiles system consists of install time and runtime parts, in total four parts:

1. symlinks to dotfiles
2. topical extensions to be loaded by `.bash_profile`
3. topical brew based installers during `script\bootstrap` (run these with `dot`)
4. topical installers during `script\bootstrap`


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

Do not forget to never checkin secrets in any of these files, use ~/.localrc for this (sourced by `.bash_profile`)

## credits
- Main inspiration comes from https://github.com/holman/dotfiles
- More about the dotfile stuff: https://dotfiles.github.io/
