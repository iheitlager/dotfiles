# iheitlager does dotfiles

## dotfiles

Your dotfiles are how you personalize your system. These are mine.

I believe everything should be versioned and scripted.  Your laptop is your personal workstation for which you tweak your personal workflow. As such I am a fan of the [dotfiles philosophy](https://dotfiles.github.io/). 
I therefore started with [holmans dotfiles](https://github.com/holman/dotfiles) and created my own, although this is more bash centric.
You might also want to start [this github page on the subject](https://dotfiles.github.io/).

## install

Run this:

```sh
git clone https://github.com/iheitlager/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
script/bootstrap
```

Everything is configured and tweaked within `~/.dotfiles`.

## topical

Everything's built around topic areas. If you're adding a new area to your
forked dotfiles — say, "Java" — you can simply add a `java` directory and put
files in there. Specific files with extension `.sh` will get automatically
included into your shell. Anything with an extension of `.symlink` will get
symlinked without extension into `$HOME` when you run `script/bootstrap`.


## components

There's a few special files in the hierarchy.

- **bin/**: `bin/` will get added to your `$PATH` and anything in there will be made available everywhere.
- **topic/aliases.sh**: Any file named `aliases.sh` is loaded by .bash_profile and available in your shell
- **topic/install.sh**: Any file named `install.sh` is executed when running `script\bootstrap`
- **topic/\*.symlink**: Any files ending in `*.symlink` get symlinked into
  your `$HOME`. This is so you can keep all of those versioned in your dotfiles
  but still keep those autoloaded files in your home directory. These get
  symlinked in when you run `script/bootstrap`.

## credits
https://github.com/holman/dotfiles
