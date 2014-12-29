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

This will symlink the appropriate files in `.dotfiles` to your home directory.
Everything is configured and tweaked within `~/.dotfiles`.


## credits
https://github.com/holman/dotfiles
