# Architecture Diagram

```mermaid
graph TB
    dotfiles[Dotfiles System]
    developer[Developer]
    shell[Shell Process]
    homebrew[Homebrew]
    github[GitHub]
    xdg_dirs[XDG Base Directory]
    bootstrap[Bootstrap System]
    xdg[XDG Base Directory Integration]
    homebrew_mgmt[Homebrew Management]
    shell_integration[Shell Integration]
    caching_system[Caching System]
    topic_loader[Topic Loader]
    dot_tool[Dot Command]
    arch_tool[Arch Command]
    spec_tool[Spec Command]

    developer -->|Runs script/bootstrap to install dotfiles| dotfiles_bootstrap
    shell -->|Sources bash_profile and bashrc on shell start| dotfiles_shell_init
    developer -->|Executes dot, arch, spec commands| dotfiles_cli_tools
    dotfiles_bootstrap -->|Installs packages via brew bundle| homebrew_brew_api
    dotfiles_cli_tools -->|Interacts with GitHub (issues, PRs) via gh CLI| github_gh_api
    dotfiles_shell_init -->|Reads config from $XDG_CONFIG_HOME| xdg_dirs_config_dir
    dotfiles_shell_init -->|Reads scripts from $XDG_DATA_HOME| xdg_dirs_data_dir
    dotfiles_shell_init -->|Reads/writes cache files to $XDG_CACHE_HOME| xdg_dirs_cache_dir
    dotfiles_shell_init -->|Reads/writes state to $XDG_STATE_HOME| xdg_dirs_state_dir
```
