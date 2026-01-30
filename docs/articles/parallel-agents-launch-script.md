# Orchestrating the Swarm: Parallel AI Agents with Launch Scripts

*From single agent to agent swarm with shell automation*

*Part 3 of a series on building an agentic development environment*

---

> "The best programs are written so that computing machines can perform them quickly and so that human beings can understand them clearly."
>
> — Donald Knuth

---

In [Part 1](https://stories.lab271.io/the-agents-are-coming-clean-your-home-c8ae7e026c51), I cleaned my home directory with XDG-compliant dotfiles. In [Part 2](LINK_TO_PART_2), I version-controlled my AI agent configuration. Now comes the interesting part: running multiple agents in parallel, each in its own context, each with the same instructions, all coordinated by a single launch script.

Why would you want this? Because one agent writing code while another reviews it, and a third updates documentation, turns out to be faster and more reliable than doing it sequentially. The foundation we built makes this possible.

## The Problem: Context Isolation

Running multiple Claude Code agents simultaneously creates three challenges:

First, **workspace conflicts**. Each agent needs its own working directory. If they share the same git checkout, they'll trip over each other's file changes, creating merge conflicts faster than you can say "git stash".

Second, **state management**. Agents need to share context—what's being worked on, what's complete, what's blocked—without stepping on each other's toes.

Third, **coordination**. Someone has to assign work, track progress, and integrate results. That someone shouldn't be you, manually copying files between terminals.

## Enter Git Worktrees

Git worktrees solve the first problem elegantly. One repository, multiple checkpoints, separate working directories:

```bash
# Main development happens here
~/.dotfiles/

# Agent 1: implementing a feature
~/code/.worktrees/feature-auth/

# Agent 2: reviewing changes  
~/code/.worktrees/review-auth/

# Agent 3: updating docs
~/code/.worktrees/docs-update/
```

Same git history, different branches, isolated file systems. Each agent sees a clean checkout. No conflicts. No confusion.

The magic is that configuration remains centralized. All three worktrees read from `~/.config/claude/` via symlinks. Update your `CLAUDE.md` once, and all agents see the change immediately.

## The Launch Script

My [`launch-agents`](https://github.com/iheitlager/dotfiles/blob/main/local/bin/launch-agents) script orchestrates this. It creates worktrees, launches agents, and manages state—all from one command.

The core workflow:

```bash
#!/usr/bin/env bash

REPO_ROOT="$(git rev-parse --show-toplevel)"
WORKTREE_DIR="$HOME/code/.worktrees"

create_worktree() {
    local branch="$1"
    local path="$WORKTREE_DIR/$branch"
    
    # Create worktree if it doesn't exist
    if [ ! -d "$path" ]; then
        git worktree add "$path" "$branch"
    fi
    
    echo "$path"
}

launch_agent() {
    local worktree="$1"
    local task="$2"
    
    # Launch Claude Code in the worktree
    osascript -e "
        tell application \"Terminal\"
            do script \"cd $worktree && code .\"
        end tell
    "
    
    # Log the task
    echo "$task" > "$XDG_STATE_HOME/agents/$worktree/current-task.txt"
}
```

Usage is simple:

```bash
$ launch-agents feature/auth-system implement review docs
```

This creates three worktrees, launches three Claude Code instances, and logs their assigned tasks. Each agent starts in its own directory with access to the shared configuration.

## State Sharing Through XDG

Remember `XDG_STATE_HOME` from Part 1? This is where it shines. Agents share state through `~/.local/state/agents/`:

```
~/.local/state/agents/
├── context/
│   ├── active-tasks.json       # What's being worked on
│   ├── completed.json          # What's done
│   └── blockers.json           # What's stuck
├── feature-auth/
│   └── current-task.txt        # Agent 1's current focus
├── review-auth/
│   └── current-task.txt        # Agent 2's current focus
└── docs-update/
    └── current-task.txt        # Agent 3's current focus
```

State files are JSON. Simple structure, easy to parse, agents can read and write without coordination:

```json
{
  "tasks": [
    {
      "id": "auth-001",
      "title": "Implement OAuth flow",
      "agent": "feature-auth",
      "status": "in-progress",
      "started": "2026-01-30T10:00:00Z"
    },
    {
      "id": "review-001", 
      "title": "Review authentication PR",
      "agent": "review-auth",
      "status": "waiting",
      "blocked_by": "auth-001"
    }
  ]
}
```

Each agent reads `active-tasks.json` to see what others are doing. Updates its own task status. The launch script aggregates this into a dashboard.

## The Configuration Payoff

This is where the triple-layer architecture from Part 2 pays off. All agents read from the same `CLAUDE.md`:

```markdown
# Global Agent Instructions

## Code Standards
- Follow PEP 8 for Python
- Write tests before implementation
- Document public APIs

## Workflow
- Check active-tasks.json before starting work
- Update your status in current-task.txt
- Mark tasks complete in completed.json
```

One file. All agents follow the same rules. Change it once, behavior updates everywhere.

The `settings.json` allowlist becomes critical here. You don't want parallel agents running arbitrary commands:

```json
{
  "allowedCommands": [
    "git",
    "uv",
    "pytest",
    "ruff"
  ],
  "blockedPatterns": [
    "rm -rf",
    "sudo",
    "curl|sh"
  ]
}
```

Agents can run tests and lint code. They can't delete files or download random scripts. Version controlled. Auditable. Safe.

## Integration Points

The launch script creates natural integration points:

**Task assignment** happens through a simple queue file:

```bash
echo "implement: Add OAuth provider" >> ~/.local/state/agents/queue.txt
```

The next idle agent picks it up.

**Code review** is automatic. One agent implements, another reviews, a third runs tests. The launch script coordinates branches:

```bash
# Agent 1 completes feature
git push origin feature/auth

# Launch script triggers Agent 2
launch-agents --review feature/auth
```

**Documentation** stays current. Any commit to `src/` triggers a docs agent:

```bash
# In .git/hooks/post-commit
if git diff-tree --no-commit-id --name-only -r HEAD | grep -q "^src/"; then
    launch-agents --docs update-api-docs
fi
```

## Why This Matters

Parallel agents aren't just faster—they're better. Code review by a separate agent catches issues the implementing agent misses. Documentation written by an agent that didn't write the code is clearer. Tests written before implementation catch design issues early.

The launch script makes this coordination trivial. What would take an hour of manual git juggling becomes `launch-agents task1 task2 task3`.

The XDG foundation makes it safe. State is isolated. Config is centralized. History is preserved.

And when something goes wrong? Git worktrees mean you can blow away any agent's workspace and recreate it in seconds:

```bash
git worktree remove feature-auth
launch-agents feature/auth implement
```

Clean slate. Same config. No data loss.

## Next Steps

The foundation is complete. XDG-compliant dotfiles from Part 1. Version-controlled agent config from Part 2. Parallel execution from this part.

What's next depends on your workflow. I use this setup for feature development, code review, and documentation maintenance. Others use it for parallel test execution or multi-language projects.

The pattern scales. Add more agents. Add more worktrees. The launch script handles the orchestration.

But first: go launch your first parallel agent swarm. You'll wonder how you ever worked any other way.

---

*My dotfiles and launch scripts are available at [github.com/iheitlager/dotfiles](https://github.com/iheitlager/dotfiles). The `local/bin/launch-agents` script is in the repo.*

## References

- [Part 1: The Agents Are Coming. Clean Your $HOME.](https://stories.lab271.io/the-agents-are-coming-clean-your-home-c8ae7e026c51)
- [Part 2: Teaching Your AI Agent Where It Lives](LINK_TO_PART_2)
- [Git Worktrees Documentation](https://git-scm.com/docs/git-worktree)
- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/)
