#!/bin/bash

# Script to generate .env file with credentials from 1Password
# Author: Claude/Ilja Heitlager
# Usage: ./env.sh [options]
#
# Copyright (c) 2025 Ilja Heitlager. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

#==============================================================================
# CONFIGURATION
#==============================================================================

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Default settings
SILENT=true
VAULT_NAME=""
readonly CONFIG_FILE=".env_vars"
readonly ENV_FILE=".env"

# Global array to store credentials
declare -a CREDENTIALS=()

#==============================================================================
# UTILITY FUNCTIONS
#==============================================================================

print_debug() {
    if [ "$SILENT" = "false" ]; then
        echo -e "${BLUE}[DEBUG]${NC} $1"
    fi
}

print_warning() {
    if [ "$SILENT" = "false" ]; then
        echo -e "${YELLOW}[WARN]${NC} $1"
    fi
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    if [ "$SILENT" = "false" ]; then
        echo -e "${GREEN}[INFO]✅${NC} $1"
    fi
}

print_help() {
    cat << EOF
${BLUE}Usage:${NC} $0 [options]

${BLUE}Options:${NC}
  -V vault_name    Specify the 1Password vault name (optional)
  -v, --verbose    Enable verbose output (default: silent mode)
  -h, --help       Show this help message

${BLUE}Description:${NC}
  This script generates a .env file by retrieving credentials from 1Password
  based on credential mappings defined in the '$CONFIG_FILE' configuration file.
  If no vault is specified, 1Password will search across all accessible vaults.

${BLUE}Configuration:${NC}
  Edit '$CONFIG_FILE' to define credential mappings in the format:
  ENV_VAR_NAME:1password_item_name:field_name

${BLUE}Examples:${NC}
  ANTHROPIC_API_KEY:Anthropic api:credential
  OPENAI_API_KEY:OpenAI API:key

${BLUE}Usage Examples:${NC}
  $0                    # Silent mode, search all vaults
  $0 -v                 # Verbose mode, search all vaults
  $0 -V 'Our Family'    # Silent mode, specific vault
  $0 -v -V 'Work'       # Verbose mode, specific vault
EOF
}

#==============================================================================
# VALIDATION FUNCTIONS
#==============================================================================

check_dependencies() {
    print_debug "Checking dependencies..."
    
    # Check if 1Password CLI is installed
    if ! command -v op &> /dev/null; then
        print_error "1Password CLI (op) is not installed."
        print_error "Please install it from: https://1password.com/downloads/command-line/"
        exit 1
    fi

    # Check if user is signed in to 1Password
    if ! op account list &> /dev/null; then
        print_error "You are not signed in to 1Password CLI."
        print_error "Please sign in using: op signin"
        print_error "Available accounts can be listed with: op account list"
        exit 1
    fi
    
    # Show which account(s) are currently signed in (only in verbose mode)
    if [ "$SILENT" = "false" ]; then
        print_debug "Currently signed in to 1Password account(s):"
        op account list | while read -r line; do
            print_debug "  $line"
        done
    fi
}

create_config_template() {
    print_warning "Configuration file '$CONFIG_FILE' not found. Creating a template..."
    
    cat > "$CONFIG_FILE" << 'EOF'
# Configuration file for env.sh
# Format: ENV_VAR_NAME:1password_item_name:field_name
# Lines starting with # are ignored

ANTHROPIC_API_KEY:Anthropic lit-review:credential

# Add more credentials here as needed:
# OPENAI_API_KEY:OpenAI API:password
# GITHUB_TOKEN:GitHub Token:credential
# DATABASE_URL:Production DB:connection_string
EOF
    
    print_debug "Created template '$CONFIG_FILE' file."
    print_debug "Please edit '$CONFIG_FILE' to configure your credential mappings."
    print_debug "Then run this script again."
    exit 0
}

#==============================================================================
# CORE FUNCTIONS
#==============================================================================

load_credentials() {
    print_debug "Loading credential mappings from '$CONFIG_FILE'..."

    # Check if configuration file exists
    if [ ! -f "$CONFIG_FILE" ]; then
        create_config_template
    fi

    # Read credentials from the configuration file
    while IFS= read -r line; do
        # Trim leading/trailing whitespace
        line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        # Skip empty lines and comments (lines starting with #)
        if [[ -n "$line" && ! "$line" =~ ^# ]]; then
            CREDENTIALS+=("$line")
            if [ "$SILENT" = "false" ]; then
                print_debug "  Loaded: $line"
            fi
        fi
    done < "$CONFIG_FILE"

    # Check if any credentials were loaded
    if [ ${#CREDENTIALS[@]} -eq 0 ]; then
        print_error "No credential mappings found in '$CONFIG_FILE'."
        print_error "Please check the file content and ensure it has valid mappings in the format:"
        print_error "ENV_VAR_NAME:1password_item_name:field_name"
        print_error ""
        print_error "Current content of '$CONFIG_FILE':"
        cat "$CONFIG_FILE" | while read -r line; do
            print_error "  $line"
        done
        exit 1
    fi

    print_debug "Loaded ${#CREDENTIALS[@]} credential mapping(s) from '$CONFIG_FILE'"
}

generate_env_file() {
    if [ -n "$VAULT_NAME" ]; then
        print_debug "Retrieving credentials from 1Password vault: $VAULT_NAME"
    else
        print_debug "Retrieving credentials from 1Password (searching all accessible vaults)"
    fi

    print_debug "Generating $ENV_FILE file..."

    # Start creating the .env file
    cat > "$ENV_FILE" << EOF
# Project: $(basename "$PWD")
# Generated on $(date)
# By env.sh from the $CONFIG_FILE configuration file
$([ -n "$VAULT_NAME" ] && echo "# Using vault: $VAULT_NAME")
# Use source .env to activate

EOF

    # Process each credential mapping
    for credential_mapping in "${CREDENTIALS[@]}"; do
        # Split the mapping into components
        IFS=':' read -r env_var item_name field_name <<< "$credential_mapping"
        
        print_debug "Retrieving $env_var from '$item_name.$field_name'..."
        
        # Retrieve the value from 1Password
        # Use --vault flag only if VAULT_NAME is set
        if [ -n "$VAULT_NAME" ]; then
            print_debug "Running: op item get \"$item_name\" --vault \"$VAULT_NAME\" --field \"$field_name\""
            value=$(op item get "$item_name" --vault "$VAULT_NAME" --field "$field_name" 2>&1)
            exit_code=$?
        else
            print_debug "Running: op item get \"$item_name\" --field \"$field_name\""
            value=$(op item get "$item_name" --field "$field_name" 2>&1)
            exit_code=$?
        fi
        
        print_debug "1Password command exit code: $exit_code"
        print_debug "1Password command output: $value"
        
        if [ $exit_code -ne 0 ] || [ -z "$value" ]; then
            print_error "Failed to retrieve $env_var from 1Password."
            print_error "Please check that:"
            if [ -n "$VAULT_NAME" ]; then
                print_error "  - The vault '$VAULT_NAME' exists"
                print_error "  - The item '$item_name' exists in that vault"
            else
                print_error "  - The item '$item_name' exists in one of your accessible vaults"
            fi
            print_error "  - The item has a field named '$field_name'"
            print_error "  - You have access to the vault and item"
            exit 1
        fi
        
        # Append to .env file
        echo "$env_var=$value" >> "$ENV_FILE"
        print_debug "Added $env_var to .env"
    done

    # Set appropriate permissions (readable by owner only)
    chmod 600 "$ENV_FILE"
}

setup_gitignore() {
    # Check if $ENV_FILE is in .gitignore
    if [ -f ".gitignore" ]; then
        if ! grep -q "^$ENV_FILE$" .gitignore; then
            print_warning "Make sure $ENV_FILE is added to your .gitignore to prevent committing secrets."
            print_warning "$ENV_FILE is not found in .gitignore. Adding it now..."
            echo "$ENV_FILE" >> .gitignore
            print_debug "Added $ENV_FILE to .gitignore"
        else
            print_debug "$ENV_FILE is already in .gitignore"
        fi
        
        # Also check for .env_vars in .gitignore (optional - user might want to commit this)
        if ! grep -q "^\$CONFIG_FILE$" .gitignore; then
            print_warning "$CONFIG_FILE is not in .gitignore. Use echo '$CONFIG_FILE' >> .gitignore"
        fi
    else
        print_warning ".gitignore file not found. Creating one with .env entry..."
        cat > .gitignore << 'EOF'
.env
# Uncomment the next line if .env_vars contains sensitive information:
# .env_vars
EOF
        print_success "Created .gitignore with $ENV_FILE entry"
    fi
}

show_summary() {
    # Always show this final completion message
    print_debug "Environment setup complete! Generated $ENV_FILE with ${#CREDENTIALS[@]} variable(s)"
    print_success "Use: ${YELLOW}source $ENV_FILE${NC} to activate environment variables"

    # Show detailed summary only in verbose mode
    if [ "$SILENT" = "false" ]; then
        print_debug "🎉 Setup complete! You can now use: ${YELLOW}source $ENV_FILE${NC}"
        print_debug "Environment variables configured:"

        # Show summary of what was added
        while IFS= read -r line; do
            if [[ $line =~ ^[A-Z_]+=.* ]]; then
                var_name=$(echo "$line" | cut -d'=' -f1)
                print_debug "  - $var_name"
            fi
        done < "$ENV_FILE"
    fi
}

#==============================================================================
# MAIN FUNCTION
#==============================================================================

main() {
    check_dependencies
    load_credentials
    generate_env_file
    setup_gitignore
    show_summary
}

#==============================================================================
# COMMAND LINE ARGUMENT PARSING
#==============================================================================

# Parse command line arguments
while getopts "V:vh-:" opt; do
    case $opt in
        V)
            VAULT_NAME="$OPTARG"
            ;;
        v)
            SILENT=false
            ;;
        h)
            print_help
            exit 0
            ;;
        -)
            case "$OPTARG" in
                verbose)
                    SILENT=false
                    ;;
                help)
                    print_help
                    exit 0
                    ;;
                *)
                    print_error "Invalid long option: --$OPTARG"
                    print_help
                    exit 1
                    ;;
            esac
            ;;
        \?)
            print_error "Invalid option: -$OPTARG"
            print_help
            exit 1
            ;;
    esac
done

#==============================================================================
# SCRIPT EXECUTION
#==============================================================================

# Run the main function
main "$@"