Wire the current project to code-analyzer via MCP by creating `.mcp.json` and updating `.gitignore`.

## Steps

1. **Check for existing `.mcp.json`**
   - If it already exists in the current directory, warn the user and ask if they want to overwrite it.
   - If they say no, stop here.

2. **Write `.mcp.json`** in the current working directory with this exact content:
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

3. **Update `.gitignore`**:
   - If `.gitignore` exists: append `.mcp.json` to it (only if not already present)
   - If `.gitignore` does not exist: create it with `.mcp.json` as the only entry

4. **Confirm** with a short summary:
   - Whether `.mcp.json` was created or overwritten
   - Whether `.gitignore` was created or updated (or already had `.mcp.json`)
   - Remind the user to restart Claude Code to pick up the new MCP server
