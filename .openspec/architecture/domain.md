# Architecture Diagram

```mermaid
graph TB
    dotfiles[Dotfiles System<br/>system]
    developer[Developer<br/>person]
    shell[Shell Process<br/>system]
    homebrew[Homebrew<br/>package-manager]
    github[GitHub<br/>version-control]
    xdg_dirs[XDG Base Directory<br/>filesystem-standard]
    subgraph cluster_bootstrap["Bootstrap System"]
        bootstrap_bootstrap_script[Bootstrap Script<br/>bash-script]
        bootstrap_symlink_manager[Symlink Manager<br/>bash-function]
        bootstrap_installer_runner[Installer Runner<br/>bash-function]
    end
    subgraph cluster_xdg["XDG Base Directory Integration"]
        xdg_xdg_env[XDG Environment Variables<br/>bash-script]
        xdg_config_home[Config Home<br/>directory]
        xdg_data_home[Data Home<br/>directory]
        xdg_cache_home[Cache Home<br/>directory]
        xdg_state_home[State Home<br/>directory]
    end
    subgraph cluster_homebrew_mgmt["Homebrew Management"]
        homebrew_mgmt_brewfile[Brewfile<br/>config-file]
        homebrew_mgmt_brew_installer[Brew Installer<br/>bash-script]
        homebrew_mgmt_brew_bundle[Brew Bundle<br/>command]
    end
    subgraph cluster_shell_integration["Shell Integration"]
        shell_integration_bash_profile[Bash Profile<br/>bash-script]
        shell_integration_bashrc[Bash RC<br/>bash-script]
        shell_integration_topic_discovery[Topic Discovery<br/>bash-function]
    end
    subgraph cluster_caching_system["Caching System"]
        caching_system_cache_generator[Cache Generator<br/>bash-function]
        caching_system_cache_validator[Cache Validator<br/>bash-function]
        caching_system_cache_storage[Cache Storage<br/>directory]
    end
    subgraph cluster_topic_loader["Topic Loader"]
        topic_loader_alias_loader[Alias Loader<br/>bash-function]
        topic_loader_completion_loader[Completion Loader<br/>bash-function]
        topic_loader_function_loader[Function Loader<br/>bash-function]
        topic_loader_env_loader[Environment Loader<br/>bash-function]
    end
    dot_tool[Dot Command<br/>cli-tool]
    arch_tool[Arch Command<br/>cli-tool]
    spec_tool[Spec Command<br/>cli-tool]

    developer -->|Runs script/bootstrap to install dotfiles| dotfiles_bootstrap
    shell -->|Sources bash_profile and bashrc on shell start| dotfiles_shell_init
    developer -->|Executes dot, arch, spec commands| dotfiles_cli_tools
    dotfiles_bootstrap -->|Installs packages via brew bundle| homebrew_brew_api
    dotfiles_cli_tools -->|Interacts with GitHub (issues, PRs) via gh CLI| github_gh_api
    dotfiles_shell_init -->|Reads config from $XDG_CONFIG_HOME| xdg_dirs_config_dir
    dotfiles_shell_init -->|Reads scripts from $XDG_DATA_HOME| xdg_dirs_data_dir
    dotfiles_shell_init -->|Reads/writes cache files to $XDG_CACHE_HOME| xdg_dirs_cache_dir
    dotfiles_shell_init -->|Reads/writes state to $XDG_STATE_HOME| xdg_dirs_state_dir
    bootstrap_bootstrap_script_bootstrap_entry -->|Ensures Homebrew is installed (step 1)| homebrew_mgmt_brew_installer_install_homebrew
    bootstrap_bootstrap_script_bootstrap_entry -->|Installs packages from Brewfile (step 3)| homebrew_mgmt_brew_bundle_bundle_install
    bootstrap_bootstrap_script_bootstrap_entry -->|Creates symlinks for dotfiles (step 4)| bootstrap_symlink_manager_link_files
    bootstrap_bootstrap_script_bootstrap_entry -->|Runs topic install.sh scripts (step 5)| bootstrap_installer_runner_run_topic_installers
    bootstrap_bootstrap_script_bootstrap_entry -->|Sources XDG environment variables| xdg_xdg_env_export_xdg_vars
    xdg_xdg_env_export_xdg_vars -->|Sets XDG_CONFIG_HOME path| xdg_config_home_config_read_write
    xdg_xdg_env_export_xdg_vars -->|Sets XDG_DATA_HOME path| xdg_data_home_data_read
    xdg_xdg_env_export_xdg_vars -->|Sets XDG_CACHE_HOME path| xdg_cache_home_cache_read_write
    xdg_xdg_env_export_xdg_vars -->|Sets XDG_STATE_HOME path| xdg_state_home_state_read_write
    homebrew_mgmt_brew_bundle_bundle_install -->|Reads package list from Brewfile| homebrew_mgmt_brewfile_brewfile_read
    shell_integration_bash_profile_login_init -->|Discovers topics on login| shell_integration_topic_discovery_discover
    shell_integration_bash_profile_login_init -->|Loads environment variables from all topics| topic_loader_env_loader_load
    shell_integration_bashrc_interactive_init -->|Checks if cache is valid| caching_system_cache_validator_validate
    shell_integration_bashrc_interactive_init -->|Regenerates cache if stale| caching_system_cache_generator_generate
    shell_integration_bashrc_interactive_init -->|Loads aliases (from cache if valid)| topic_loader_alias_loader_load
    shell_integration_bashrc_interactive_init -->|Loads completions (from cache if valid)| topic_loader_completion_loader_load
    shell_integration_bashrc_interactive_init -->|Loads functions (from cache if valid)| topic_loader_function_loader_load
    caching_system_cache_generator_generate -->|Discovers topics before caching| shell_integration_topic_discovery_discover
    caching_system_cache_generator_generate -->|Writes generated cache files| caching_system_cache_storage_cache_read_write
    caching_system_cache_validator_validate -->|Checks cache file mtime| caching_system_cache_storage_cache_read_write
    topic_loader_alias_loader_load -->|Sources bash_aliases.sh from cache| caching_system_cache_storage_cache_read_write
    topic_loader_completion_loader_load -->|Sources bash_completion.sh from cache| caching_system_cache_storage_cache_read_write
    topic_loader_function_loader_load -->|Sources bash_functions.sh from cache| caching_system_cache_storage_cache_read_write
    caching_system_cache_storage_cache_read_write -->|Uses $XDG_CACHE_HOME for cache storage| xdg_cache_home_cache_read_write
    shell_integration_topic_discovery_discover -->|Scans topics from $DOTFILES directory| xdg_data_home_data_read
```
