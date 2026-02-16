Coordinate an architectural analysis team: you (Sonnet) orchestrate, Opus runs as the Synthesizer in a new tmux window.

1. Verify `code-analyzer` MCP is connected. If not, stop and tell the user to run `/ca-init` and restart.

2. Get project path (cwd unless user specified). Note any analysis focus from the user's arguments.

3. Launch the Synthesizer in a new tmux window:
   ```bash
   SESS=$(tmux display-message -p '#S')
   tmux new-window -t "$SESS" -n "synthesizer"
   tmux send-keys -t "$SESS:synthesizer" "claude --model claude-opus-4-6" Enter
   sleep 2
   tmux send-keys -t "$SESS:synthesizer" "You are the Synthesizer agent. Project path: <path>. Start with parse_directory then get_summary. Focus: <user focus, or 'full architectural overview'>." Enter
   ```

4. Tell the user the Synthesizer is running in the `synthesizer` tmux window. Stay available in this session for questions and relay key findings as they arrive.
