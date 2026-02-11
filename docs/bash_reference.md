# Bash Reference: Special Variables & Parameter Expansion

A comprehensive guide to bash's `$` variables, parameter expansion, and string manipulation patterns used throughout this dotfiles repository.

---

## Table of Contents

- [Special Variables](#special-variables)
- [Parameter Expansion](#parameter-expansion)
  - [Default Values](#default-values)
  - [String Operations](#string-operations)
  - [Pattern Matching](#pattern-matching)
  - [Case Modification](#case-modification)
- [Array Operations](#array-operations)
- [Real-World Examples](#real-world-examples)
- [Quick Reference](#quick-reference)

---

## Special Variables

### Process & Exit Status

```bash
$$        # Current shell's PID
$!        # PID of last background job
$?        # Exit status of last command (0 = success)
$0        # Name of the script/shell
$_        # Last argument of previous command
$-        # Current shell options (set flags)
```

**Examples:**

```bash
# Get current shell PID
echo $$           # → 12345

# Get background job PID
sleep 10 &
echo $!           # → 12346

# Check exit status
ls /nonexistent
echo $?           # → 2 (error)

ls /tmp
echo $?           # → 0 (success)

# Get last argument
echo "hello" "world"
echo $_           # → world

# Check shell options
echo $-           # → himBHs (interactive, monitor mode, etc.)
```

### Positional Parameters

```bash
$1, $2, $3...  # Script/function arguments (1-9 directly, ${10}+ for higher)
$#             # Number of arguments
$@             # All arguments as separate words (proper for iteration)
$*             # All arguments as single word (rarely needed)
```

**Example script:**

```bash
#!/bin/bash
# script.sh

echo "Script name: $0"
echo "Argument count: $#"
echo "First argument: $1"
echo "Second argument: $2"
echo "All arguments: $@"

# Iterate over arguments
for arg in "$@"; do
    echo "  - $arg"
done
```

```bash
# Run: ./script.sh foo bar baz
# Output:
# Script name: ./script.sh
# Argument count: 3
# First argument: foo
# Second argument: baz
# All arguments: foo bar baz
#   - foo
#   - bar
#   - baz
```

### Common Shell Variables

```bash
$BASH_VERSION  # Bash version string
$HOSTNAME      # Machine hostname
$RANDOM        # Random number (0-32767)
$LINENO        # Current line number in script
$PWD           # Current working directory
$OLDPWD        # Previous working directory
$HOME          # Home directory path
$USER          # Current username
$UID           # User ID (numeric)
$SHELL         # Path to current shell
$TERM          # Terminal type
$EDITOR        # Default editor
$PATH          # Executable search path
```

**Examples:**

```bash
echo "Bash: $BASH_VERSION"    # → 5.2.15(1)-release
echo "Host: $HOSTNAME"         # → macbook.local
echo "Random: $RANDOM"         # → 23847
echo "User: $USER ($UID)"      # → iheitlager (501)
```

---

## Parameter Expansion

### Default Values

Use these to provide fallback values when variables are unset or empty.

```bash
${var:-default}    # Use default if var is unset or empty (doesn't modify var)
${var:=default}    # Assign default if var is unset or empty (modifies var)
${var:?error}      # Print error and exit if var is unset or empty
${var:+alternate}  # Use alternate if var is set and non-empty
```

**Examples:**

```bash
# Use default (variable unchanged)
echo "${USER:-nobody}"        # → iheitlager (USER is set)
echo "${UNDEFINED:-fallback}" # → fallback (UNDEFINED not set)
echo "$UNDEFINED"             # → (still empty)

# Assign default (modifies variable)
unset NAME
NAME=${NAME:=Claude}
echo "$NAME"                  # → Claude
echo "$NAME"                  # → Claude (now set)

# Error if unset
echo "${REQUIRED:?Variable REQUIRED must be set}"
# → bash: REQUIRED: Variable REQUIRED must be set

# Use alternate if set
DEBUG=1
echo "${DEBUG:+--verbose}"    # → --verbose
unset DEBUG
echo "${DEBUG:+--verbose}"    # → (empty)

# Practical: optional flags
VERBOSE=${VERBOSE:+--verbose}
command $VERBOSE arg1 arg2    # Only adds --verbose if VERBOSE is set
```

**Common patterns in dotfiles:**

```bash
# XDG Base Directory defaults
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"

# Fallback to system default
EDITOR="${EDITOR:-vim}"
BROWSER="${BROWSER:-firefox}"

# Config file location
CONFIG_FILE="${CONFIG_FILE:-$HOME/.config/app/config.conf}"
```

### String Length

```bash
${#var}        # Length of string in characters
${#array[@]}   # Number of array elements
${#array[*]}   # Also number of elements
```

**Examples:**

```bash
TEXT="hello world"
echo ${#TEXT}              # → 11

FILES=(a.txt b.txt c.txt)
echo ${#FILES[@]}          # → 3

# Check if empty
if [[ ${#TEXT} -eq 0 ]]; then
    echo "Empty string"
fi
```

### Substring Extraction

```bash
${var:offset}          # From offset to end
${var:offset:length}   # Substring of specified length
${var: -n}             # Last n characters (note: space before minus)
${var:0:-n}            # All except last n characters
```

**Examples:**

```bash
TEXT="hello world"
echo ${TEXT:6}         # → world
echo ${TEXT:0:5}       # → hello
echo ${TEXT:6:3}       # → wor
echo ${TEXT: -5}       # → world (last 5 chars, note space!)
echo ${TEXT:0:-6}      # → hello (all except last 6)

# Extract year/month/day from ISO date
DATE="2026-02-11"
YEAR=${DATE:0:4}       # → 2026
MONTH=${DATE:5:2}      # → 02
DAY=${DATE:8:2}        # → 11
```

### Pattern Removal

Remove patterns from the beginning or end of strings.

```bash
${var#pattern}     # Remove shortest match from beginning
${var##pattern}    # Remove longest match from beginning
${var%pattern}     # Remove shortest match from end
${var%%pattern}    # Remove longest match from end
```

**Patterns use shell globbing:**
- `*` - matches any characters
- `?` - matches single character
- `[...]` - matches character class

**Examples:**

```bash
FILE="path/to/file.tar.gz"

# Remove from beginning (# = left side)
echo ${FILE#*/}        # → to/file.tar.gz (remove first dir/)
echo ${FILE##*/}       # → file.tar.gz (remove all dirs/ - basename!)

# Remove from end (% = right side)
echo ${FILE%.gz}       # → path/to/file.tar (remove .gz)
echo ${FILE%.*}        # → path/to/file.tar (remove last extension)
echo ${FILE%%.*}       # → path/to/file (remove all extensions)

# Get basename (like basename command)
BASENAME=${FILE##*/}   # → file.tar.gz

# Get dirname (like dirname command)
DIRNAME=${FILE%/*}     # → path/to

# Get file extension
EXT=${FILE##*.}        # → gz
EXT=${FILE#*.}         # → tar.gz (all extensions)

# Remove prefix
URL="https://github.com/user/repo"
echo ${URL#https://}   # → github.com/user/repo
echo ${URL##*/}        # → repo (last component)
```

**Real-world pattern: Convert SSH to HTTPS URL**

```bash
REMOTE="git@github.com:user/repo.git"

# Remove git@ prefix
REMOTE=${REMOTE#git@}           # → github.com:user/repo.git

# Replace : with /
REMOTE=${REMOTE/://}            # → github.com/user/repo.git

# Remove .git suffix
REMOTE=${REMOTE%.git}           # → github.com/user/repo

# Add https://
HTTPS="https://${REMOTE}"       # → https://github.com/user/repo
```

### Pattern Replacement

```bash
${var/pattern/replacement}    # Replace first match
${var//pattern/replacement}   # Replace all matches
${var/#pattern/replacement}   # Replace at beginning only
${var/%pattern/replacement}   # Replace at end only
```

**Examples:**

```bash
TEXT="hello world hello"
echo ${TEXT/hello/hi}      # → hi world hello (first only)
echo ${TEXT//hello/hi}     # → hi world hi (all)
echo ${TEXT/#hello/hi}     # → hi world hello (beginning)
echo ${TEXT/%hello/hi}     # → hello world hi (end)

# Replace spaces with underscores
FILE="my document.txt"
echo ${FILE// /_}          # → my_document.txt

# Replace path separators
PATH_UNIX="/path/to/file"
PATH_WIN=${PATH_UNIX//\//\\}   # → \path\to\file

# Remove all occurrences
TEXT="a-b-c-d"
echo ${TEXT//-/}           # → abcd

# Convert SSH to HTTPS (one-liner)
SSH="git@github.com:user/repo.git"
HTTPS="https://${SSH/git@github.com:/github.com/}"
HTTPS=${HTTPS%.git}        # → https://github.com/user/repo
```

### Case Modification

```bash
${var^}     # Capitalize first character
${var^^}    # Uppercase all characters
${var,}     # Lowercase first character
${var,,}    # Lowercase all characters
${var~}     # Toggle case of first character
${var~~}    # Toggle case of all characters
```

**Examples:**

```bash
NAME="john doe"
echo ${NAME^}        # → John doe
echo ${NAME^^}       # → JOHN DOE

# Capitalize each word (requires word splitting)
name="john doe"
capitalized="${name^} ${name#* }"  # Not ideal for multi-word

UPPER="HELLO WORLD"
echo ${UPPER,}       # → hELLO WORLD
echo ${UPPER,,}      # → hello world

# Toggle case
mixed="HeLLo"
echo ${mixed~~}      # → hEllO
```

---

## Array Operations

### Array Basics

```bash
array=(one two three)     # Create array
echo "${array[0]}"        # First element (0-indexed)
echo "${array[@]}"        # All elements (separate words)
echo "${array[*]}"        # All elements (single word)
echo "${#array[@]}"       # Number of elements
echo "${!array[@]}"       # All indices
```

### Array Expansion

```bash
${array[@]}         # All elements as separate words (use with "$@")
${array[*]}         # All elements as single word
${#array[@]}        # Number of elements
${#array[0]}        # Length of first element (string length)
${!array[@]}        # Array indices (keys)
${array[@]:start}   # Slice from start to end
${array[@]:start:length}  # Slice with length
```

**Examples:**

```bash
FILES=(readme.txt main.sh config.yml)

# Iterate properly (preserves spaces)
for file in "${FILES[@]}"; do
    echo "File: $file"
done

# Length
echo "Count: ${#FILES[@]}"    # → 3
echo "First length: ${#FILES[0]}"  # → 10 (readme.txt)

# Slice
echo "${FILES[@]:1}"          # → main.sh config.yml (from index 1)
echo "${FILES[@]:1:1}"        # → main.sh (1 element starting at 1)

# Indices
echo "${!FILES[@]}"           # → 0 1 2

# Pattern operations work on arrays too
for file in "${FILES[@]}"; do
    echo "Basename: ${file##*/}"
    echo "Extension: ${file##*.}"
done
```

### Associative Arrays (Bash 4+)

```bash
declare -A assoc_array
assoc_array[key1]="value1"
assoc_array[key2]="value2"

echo "${assoc_array[key1]}"   # → value1
echo "${!assoc_array[@]}"     # → key1 key2 (keys)
echo "${assoc_array[@]}"      # → value1 value2 (values)
```

---

## Real-World Examples

### From Our Dotfiles

#### Hyperlink Functions (ghostty/bash_aliases)

```bash
# Use URI as default text if not provided
hyperlink() {
    local uri="$1"
    local text="${2:-$uri}"  # ← Default to URI if no text given
    local id="${3:-}"        # ← Optional parameter
    ...
}

# Get hostname with fallback
hostname="$(hostname 2>/dev/null || echo "localhost")"
# Better with parameter expansion:
hostname="${HOSTNAME:-localhost}"

# Get basename if text not provided
file_link() {
    local filepath="$1"
    local text="${2:-}"

    # Resolve absolute path
    if [[ ! "$filepath" =~ ^/ ]]; then
        filepath="$(realpath "$filepath" 2>/dev/null || echo "$PWD/$filepath")"
    fi

    # Default to basename
    if [[ -z "$text" ]]; then
        text="${filepath##*/}"  # ← Strip directory path
    fi
    ...
}

# Convert git remote URL to HTTPS
git_commit_link() {
    local remote_url
    remote_url="$(git config --get remote.origin.url 2>/dev/null)"

    # Convert SSH to HTTPS
    if [[ "$remote_url" =~ ^git@github\.com:(.+)\.git$ ]]; then
        remote_url="https://github.com/${BASH_REMATCH[1]}"
    elif [[ "$remote_url" =~ ^https://github\.com/(.+)\.git$ ]]; then
        remote_url="https://github.com/${BASH_REMATCH[1]}"
    fi

    # Remove .git suffix
    remote_url="${remote_url%.git}"
    ...
}
```

#### XDG Base Directory (common pattern)

```bash
# ~/.bashrc or similar
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"

# Use in scripts
CONFIG_DIR="${XDG_CONFIG_HOME}/myapp"
DATA_DIR="${XDG_DATA_HOME}/myapp"
CACHE_DIR="${XDG_CACHE_HOME}/myapp"
```

#### Error Checking

```bash
# Require variable to be set
: "${DOTFILES:?ERROR: DOTFILES environment variable must be set}"
: "${HOME:?ERROR: HOME not set}"

# Validate argument
function deploy() {
    local env="${1:?Usage: deploy <environment>}"
    echo "Deploying to: $env"
}
```

#### Path Manipulation

```bash
# Get script directory (handle symlinks)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get project root (go up from script dir)
PROJECT_ROOT="${SCRIPT_DIR%/*}"

# Get filename without extension
FILE="script.sh"
NAME="${FILE%.*}"              # → script
EXT="${FILE##*.}"              # → sh

# Construct paths
CONFIG_FILE="${XDG_CONFIG_HOME}/app/${NAME}.conf"
LOG_FILE="${XDG_STATE_HOME}/app/${NAME}.log"
```

#### String Cleaning

```bash
# Remove leading/trailing whitespace
text="  hello world  "
text="${text#"${text%%[![:space:]]*}"}"  # Remove leading
text="${text%"${text##*[![:space:]]}"}"  # Remove trailing

# Simpler with extglob
shopt -s extglob
text="${text##*( )}"  # Remove leading spaces
text="${text%%*( )}"  # Remove trailing spaces

# Replace multiple spaces with single space
text="${text//  / }"

# Remove all whitespace
text="${text//[[:space:]]/}"
```

#### URL Manipulation

```bash
# Extract components from URL
URL="https://github.com/user/repo/blob/main/README.md"

PROTOCOL="${URL%%://*}"      # → https
REMAINDER="${URL#*://}"      # → github.com/user/repo/blob/main/README.md
HOST="${REMAINDER%%/*}"      # → github.com
PATH="${REMAINDER#*/}"       # → user/repo/blob/main/README.md
```

#### Conditional Defaults in Functions

```bash
function backup() {
    local source="${1:?Source directory required}"
    local dest="${2:-$HOME/backups}"
    local timestamp="${3:-$(date +%Y%m%d_%H%M%S)}"

    local backup_file="${dest}/backup_${timestamp}.tar.gz"
    tar czf "$backup_file" "$source"
}
```

---

## Quick Reference

### Special Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `$$` | Current shell PID | `echo $$` → 12345 |
| `$!` | Last background job PID | `sleep 10 & echo $!` → 12346 |
| `$?` | Last exit status | `ls; echo $?` → 0 |
| `$_` | Last argument | `echo foo bar; echo $_` → bar |
| `$0` | Script/shell name | `echo $0` → bash |
| `$1`..`$9` | Positional arguments | `$1` → first arg |
| `${10}` | 10th+ arguments | `${10}` → tenth arg |
| `$#` | Argument count | `echo $#` → 3 |
| `$@` | All arguments (array) | `for arg in "$@"` |
| `$*` | All arguments (string) | `IFS=,; echo "$*"` |

### Parameter Expansion

| Syntax | Description | Example |
|--------|-------------|---------|
| `${var}` | Variable value | `${HOME}` → /Users/name |
| `${var:-default}` | Default if unset/empty | `${EDITOR:-vim}` |
| `${var:=default}` | Assign default | `FOO=${FOO:=bar}` |
| `${var:?error}` | Error if unset | `${REQUIRED:?Missing}` |
| `${var:+value}` | Use value if set | `${DEBUG:+--verbose}` |
| `${#var}` | String length | `${#HOME}` → 12 |
| `${var:n}` | Substring from n | `${TEXT:5}` |
| `${var:n:len}` | Substring length | `${TEXT:0:5}` |
| `${var#pattern}` | Remove shortest prefix | `${FILE#*/}` |
| `${var##pattern}` | Remove longest prefix | `${FILE##*/}` (basename) |
| `${var%pattern}` | Remove shortest suffix | `${FILE%.*}` |
| `${var%%pattern}` | Remove longest suffix | `${FILE%%.*}` |
| `${var/pat/rep}` | Replace first | `${TEXT/foo/bar}` |
| `${var//pat/rep}` | Replace all | `${TEXT//foo/bar}` |
| `${var/#pat/rep}` | Replace at start | `${TEXT/#foo/bar}` |
| `${var/%pat/rep}` | Replace at end | `${TEXT/%foo/bar}` |
| `${var^}` | Capitalize first | `${name^}` → Name |
| `${var^^}` | Uppercase all | `${name^^}` → NAME |
| `${var,}` | Lowercase first | `${NAME,}` → nAME |
| `${var,,}` | Lowercase all | `${NAME,,}` → name |

### Common Patterns

```bash
# XDG defaults
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"

# Basename/dirname
basename="${filepath##*/}"
dirname="${filepath%/*}"

# Extension removal
noext="${filename%.*}"
ext="${filename##*.}"

# Multiple extensions
file.tar.gz → ${file%%.*} → file
file.tar.gz → ${file%.*} → file.tar

# Convert SSH to HTTPS
https="https://${ssh_url/git@github.com:/github.com/}"

# Remove trailing slashes
path="${path%/}"

# Default argument
arg="${1:-default_value}"

# Error if missing
: "${VAR:?ERROR: VAR must be set}"

# Optional flag
verbose="${VERBOSE:+--verbose}"
```

---

## Testing & Debugging

```bash
# Test parameter expansion interactively
$ var="hello world"
$ echo ${var^^}
HELLO WORLD

# Debug with set -x
set -x              # Enable debug mode
echo ${var##* }     # Shows expansion step-by-step
set +x              # Disable debug mode

# Check if variable is set
[[ -n "${var:-}" ]] && echo "Set" || echo "Unset"

# Check if variable is empty
[[ -z "${var:-}" ]] && echo "Empty" || echo "Not empty"
```

---

## Resources

- [Bash Manual: Shell Parameter Expansion](https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html)
- [Bash Manual: Special Parameters](https://www.gnu.org/software/bash/manual/html_node/Special-Parameters.html)
- [Bash Guide: Parameter Expansion](https://mywiki.wooledge.org/BashGuide/Parameters)
- [Advanced Bash-Scripting Guide](https://tldp.org/LDP/abs/html/)

---

*Generated: 2026-02-11*
*See also: `docs/xdg_setup.md`, `docs/coloring.md`*
