# Architecture Diagram

```mermaid
graph TB
    dotfiles[Dotfiles System<br/>system]
    dotfiles_bootstrap[bootstrap<br/>bash-script]
    dotfiles --> dotfiles_bootstrap
    dotfiles_shell_init[shell-init<br/>bash-source]
    dotfiles --> dotfiles_shell_init
    dotfiles_cli_tools[cli-tools<br/>command-line]
    dotfiles --> dotfiles_cli_tools
    developer[Developer<br/>person]
    shell[Shell Process<br/>system]
    homebrew[Homebrew<br/>package-manager]
    homebrew_brew_api[brew-api<br/>command-line]
    homebrew --> homebrew_brew_api
    github[GitHub<br/>version-control]
    github_gh_api[gh-api<br/>https]
    github --> github_gh_api
    xdg_dirs[XDG Base Directory<br/>filesystem-standard]
    xdg_dirs_config_dir[config-dir<br/>filesystem]
    xdg_dirs --> xdg_dirs_config_dir
    xdg_dirs_data_dir[data-dir<br/>filesystem]
    xdg_dirs --> xdg_dirs_data_dir
    xdg_dirs_cache_dir[cache-dir<br/>filesystem]
    xdg_dirs --> xdg_dirs_cache_dir
    xdg_dirs_state_dir[state-dir<br/>filesystem]
    xdg_dirs --> xdg_dirs_state_dir
    bootstrap_bootstrap_script[Bootstrap Script<br/>bash-script]
    bootstrap_bootstrap_script_bootstrap_entry[bootstrap-entry<br/>bash-script]
    bootstrap_bootstrap_script --> bootstrap_bootstrap_script_bootstrap_entry
    bootstrap_symlink_manager[Symlink Manager<br/>bash-function]
    bootstrap_symlink_manager_link_files[link-files<br/>function-call]
    bootstrap_symlink_manager --> bootstrap_symlink_manager_link_files
    bootstrap_installer_runner[Installer Runner<br/>bash-function]
    bootstrap_installer_runner_run_topic_installers[run-topic-installers<br/>function-call]
    bootstrap_installer_runner --> bootstrap_installer_runner_run_topic_installers
    xdg_xdg_env[XDG Environment Variables<br/>bash-script]
    xdg_xdg_env_export_xdg_vars[export-xdg-vars<br/>bash-source]
    xdg_xdg_env --> xdg_xdg_env_export_xdg_vars
    xdg_config_home[Config Home<br/>directory]
    xdg_config_home_config_read_write[config-read-write<br/>filesystem]
    xdg_config_home --> xdg_config_home_config_read_write
    xdg_data_home[Data Home<br/>directory]
    xdg_data_home_data_read[data-read<br/>filesystem]
    xdg_data_home --> xdg_data_home_data_read
    xdg_cache_home[Cache Home<br/>directory]
    xdg_cache_home_cache_read_write[cache-read-write<br/>filesystem]
    xdg_cache_home --> xdg_cache_home_cache_read_write
    xdg_state_home[State Home<br/>directory]
    xdg_state_home_state_read_write[state-read-write<br/>filesystem]
    xdg_state_home --> xdg_state_home_state_read_write
    homebrew_mgmt_brewfile[Brewfile<br/>config-file]
    homebrew_mgmt_brewfile_brewfile_read[brewfile-read<br/>filesystem]
    homebrew_mgmt_brewfile --> homebrew_mgmt_brewfile_brewfile_read
    homebrew_mgmt_brew_installer[Brew Installer<br/>bash-script]
    homebrew_mgmt_brew_installer_install_homebrew[install-homebrew<br/>bash-script]
    homebrew_mgmt_brew_installer --> homebrew_mgmt_brew_installer_install_homebrew
    homebrew_mgmt_brew_bundle[Brew Bundle<br/>command]
    homebrew_mgmt_brew_bundle_bundle_install[bundle-install<br/>command-line]
    homebrew_mgmt_brew_bundle --> homebrew_mgmt_brew_bundle_bundle_install
    shell_integration_bash_profile[Bash Profile<br/>bash-script]
    shell_integration_bash_profile_login_init[login-init<br/>bash-source]
    shell_integration_bash_profile --> shell_integration_bash_profile_login_init
    shell_integration_bashrc[Bash RC<br/>bash-script]
    shell_integration_bashrc_interactive_init[interactive-init<br/>bash-source]
    shell_integration_bashrc --> shell_integration_bashrc_interactive_init
    shell_integration_topic_discovery[Topic Discovery<br/>bash-function]
    shell_integration_topic_discovery_discover[discover<br/>function-call]
    shell_integration_topic_discovery --> shell_integration_topic_discovery_discover
    caching_system_cache_generator[Cache Generator<br/>bash-function]
    caching_system_cache_generator_generate[generate<br/>function-call]
    caching_system_cache_generator --> caching_system_cache_generator_generate
    caching_system_cache_validator[Cache Validator<br/>bash-function]
    caching_system_cache_validator_validate[validate<br/>function-call]
    caching_system_cache_validator --> caching_system_cache_validator_validate
    caching_system_cache_storage[Cache Storage<br/>directory]
    caching_system_cache_storage_cache_read_write[cache-read-write<br/>filesystem]
    caching_system_cache_storage --> caching_system_cache_storage_cache_read_write
    topic_loader_alias_loader[Alias Loader<br/>bash-function]
    topic_loader_alias_loader_load[load<br/>bash-source]
    topic_loader_alias_loader --> topic_loader_alias_loader_load
    topic_loader_completion_loader[Completion Loader<br/>bash-function]
    topic_loader_completion_loader_load[load<br/>bash-source]
    topic_loader_completion_loader --> topic_loader_completion_loader_load
    topic_loader_function_loader[Function Loader<br/>bash-function]
    topic_loader_function_loader_load[load<br/>bash-source]
    topic_loader_function_loader --> topic_loader_function_loader_load
    topic_loader_env_loader[Environment Loader<br/>bash-function]
    topic_loader_env_loader_load[load<br/>bash-source]
    topic_loader_env_loader --> topic_loader_env_loader_load
    dot_tool[Dot Command<br/>cli-tool]
    dot_tool_dot_cli[dot-cli<br/>command-line]
    dot_tool --> dot_tool_dot_cli
    dot_tool_dot_install[Package Installer<br/>bash-function]
    dot_tool_dot_install_brew_install_cmd[brew-install-cmd<br/>command-line]
    dot_tool_dot_install --> dot_tool_dot_install_brew_install_cmd
    dot_tool_dot_list[Topic Lister<br/>bash-function]
    dot_tool_dot_list_list_topics[list-topics<br/>command-line]
    dot_tool_dot_list --> dot_tool_dot_list_list_topics
    dot_tool_dot_status[System Status<br/>bash-function]
    dot_tool_dot_status_show_status[show-status<br/>command-line]
    dot_tool_dot_status --> dot_tool_dot_status_show_status
    dot_tool_dot_update[Dotfiles Updater<br/>bash-function]
    dot_tool_dot_update_update_dotfiles[update-dotfiles<br/>command-line]
    dot_tool_dot_update --> dot_tool_dot_update_update_dotfiles
    dot_tool_dot_edit[Dotfiles Editor<br/>bash-function]
    dot_tool_dot_edit_edit_dotfiles[edit-dotfiles<br/>command-line]
    dot_tool_dot_edit --> dot_tool_dot_edit_edit_dotfiles
    arch_tool[Arch Command<br/>cli-tool]
    arch_tool_arch_cli[arch-cli<br/>command-line]
    arch_tool --> arch_tool_arch_cli
    arch_tool_arch_list[Resource Lister<br/>python-module]
    arch_tool_arch_list_list_resources[list-resources<br/>command-line]
    arch_tool_arch_list --> arch_tool_arch_list_list_resources
    arch_tool_arch_validate[Model Validator<br/>python-module]
    arch_tool_arch_validate_validate_model[validate-model<br/>command-line]
    arch_tool_arch_validate --> arch_tool_arch_validate_validate_model
    arch_tool_arch_diagram[Diagram Generator<br/>python-module]
    arch_tool_arch_diagram_generate_diagram[generate-diagram<br/>command-line]
    arch_tool_arch_diagram --> arch_tool_arch_diagram_generate_diagram
    arch_tool_arch_loader[Model Loader<br/>python-module]
    arch_tool_arch_loader_load_yaml[load-yaml<br/>python-api]
    arch_tool_arch_loader --> arch_tool_arch_loader_load_yaml
    arch_tool_arch_path_resolver[Path Resolver<br/>python-module]
    arch_tool_arch_path_resolver_resolve_path[resolve-path<br/>python-api]
    arch_tool_arch_path_resolver --> arch_tool_arch_path_resolver_resolve_path
    spec_tool[Spec Command<br/>cli-tool]
    spec_tool_spec_cli[spec-cli<br/>command-line]
    spec_tool --> spec_tool_spec_cli
    spec_tool_spec_browser[Interactive Browser<br/>bash-function]
    spec_tool_spec_browser_browse_specs[browse-specs<br/>command-line]
    spec_tool_spec_browser --> spec_tool_spec_browser_browse_specs
    spec_tool_spec_lister[Spec Lister<br/>bash-function]
    spec_tool_spec_lister_list_specs[list-specs<br/>command-line]
    spec_tool_spec_lister --> spec_tool_spec_lister_list_specs
    spec_tool_spec_status[Status Overview<br/>bash-function]
    spec_tool_spec_status_show_status[show-status<br/>command-line]
    spec_tool_spec_status --> spec_tool_spec_status_show_status

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
    dot_tool_dot_status_show_status -->|Scans topics from $DOTFILES| xdg_data_home_data_read
    dot_tool_dot_update_update_dotfiles -->|Runs bootstrap after git pull| bootstrap_bootstrap_script_bootstrap_entry
    arch_tool_arch_loader_load_yaml -->|Loads architecture from .openspec/architecture/| xdg_config_home_config_read_write
    spec_tool_spec_browser_browse_specs -->|Reads specs from .openspec/specs/| xdg_config_home_config_read_write
    arch_tool_arch_list_list_resources -->|Loads model before listing| arch_tool_arch_loader_load_yaml
    arch_tool_arch_list_list_resources -->|Uses path resolver for filtering| arch_tool_arch_path_resolver_resolve_path
    arch_tool_arch_validate_validate_model -->|Loads model before validation| arch_tool_arch_loader_load_yaml
    arch_tool_arch_diagram_generate_diagram -->|Loads model before diagram generation| arch_tool_arch_loader_load_yaml
    arch_tool_arch_diagram_generate_diagram -->|Resolves paths for relationship rendering| arch_tool_arch_path_resolver_resolve_path
```
