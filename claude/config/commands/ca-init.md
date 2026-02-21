Wire the current project to code-analyzer via MCP by creating `.mcp.json` and updating `.gitignore`.

## Steps

1. **Ensure a writable remote (fork)**:
   - Run `git remote -v` to check the current remotes.
   - If `origin` points to a repo NOT owned by `iheitlager` (i.e., a third-party repo):
     - Ask the user if they want to fork it to their GitHub account.
     - If yes: run `gh repo fork --remote=false` to create the fork, then:
       - Rename current origin to upstream: `git remote rename origin upstream`
       - Add the fork as origin: `git remote add origin git@github.com:iheitlager/<repo-name>.git`
     - If no: warn that pushing branches and creating PRs may not work without a writable remote, and continue.
   - If `origin` already points to `iheitlager/*`: no action needed.
   - If there is no `upstream` remote pointing to the original repo, add one.

2. **Check for existing `.mcp.json`**
   - If it already exists in the current directory, warn the user and ask if they want to overwrite it.
   - If they say no, stop here.

3. **Write `.mcp.json`** in the current working directory with this exact content:
   ```json
   {
     "mcpServers": {
       "code-analyzer": {
         "command": "/opt/homebrew/bin/uv",
         "args": ["--directory", "/Users/iheitlager/wc/code-analyzer", "run", "code-analyzer-mcp"]
       }
     }
   }
   ```

4. **Create/update `.claude/settings.local.json`**:
   - If it already exists: read it, then merge these entries into the existing JSON (don't overwrite other settings)
   - If it does not exist: create it
   - Ensure the file contains at minimum:
     ```json
     {
       "permissions": {
         "allow": [
           "Bash(*)",
           "mcp__code-analyzer__parse_directory",
           "mcp__code-analyzer__get_summary",
           "mcp__code-analyzer__cypher_query"
         ]
       },
       "enableAllProjectMcpServers": true,
       "enabledMcpjsonServers": [
         "code-analyzer"
       ]
     }
     ```
   - When merging into an existing file: append to `permissions.allow` (avoid duplicates), and set the `enableAllProjectMcpServers` and `enabledMcpjsonServers` keys

5. **Update `.gitignore`**:
   - If `.gitignore` exists: append `.mcp.json` and `.claude/settings.local.json` to it (only entries not already present)
   - If `.gitignore` does not exist: create it with `.mcp.json` and `.claude/settings.local.json` as entries

6. **Confirm** with a short summary:
   - Whether a fork was created and remotes were reconfigured (or already correct)
   - Whether `.mcp.json` was created or overwritten
   - Whether `.claude/settings.local.json` was created or updated
   - Whether `.gitignore` was created or updated
   - Remind the user to restart Claude Code to pick up the new MCP server
