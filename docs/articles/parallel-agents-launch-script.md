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

Running multiple Claude Code agents simultaneously creates four challenges:

First, **workspace conflicts**. Each agent needs its own working directory. If they share the same git checkout, they'll trip over each other's file changes, creating merge conflicts faster than you can say "git stash".

Second, **configuration**. Each agent needs access to the same generic configuration—coding standards, allowed commands, workflow rules—but also needs to know *who it is*. Is it the implementer? The reviewer? The documentation writer? Generic config plus agent identity.

Third, **coordination**. Someone has to assign work, track progress, and integrate results. Agents need shared context—what's being worked on, what's complete, what's blocked. GitHub Issues turns out to be perfect for this: it's already your task tracker, agents can read and update issues, and you get a natural audit trail.

Fourth, **visibility**. Running three agents means three terminal windows. Or does it? You could use split panes in your terminal—iTerm2, Ghostty, WezTerm all support this. I chose tmux. One terminal, multiple panes, all agents visible at once. Tmux deserves its own article, but for now: it's essential infrastructure for agent swarms.

## Enter Git Worktrees

Git worktrees solve the first problem elegantly. One repository, multiple checkpoints, separate working directories. I've [written about worktrees before](https://medium.com/lab271/stop-switching-branches-a-better-git-workflow-with-worktrees-4353509b73b4)—they're underrated. For parallel agents, they're essential.

My convention: if a project lives at `~/wc/<project>`, worktrees go in `~/wc/<project>-worktree/`. This keeps the main checkout clean while letting me navigate to worktrees with predictable paths:

```bash
# Main development happens here
~/wc/myproject/

# Agent 1: its own workspace, creates branches as needed
~/wc/myproject-worktree/agent-1/

# Agent 2: same repo, isolated checkout
~/wc/myproject-worktree/agent-2/

# Agent 3: you get the pattern
~/wc/myproject-worktree/agent-3/
```

Each agent gets a numbered worktree. Inside that worktree, it creates and switches branches as needed—`feature/auth`, `fix/typo`, whatever the task requires. Same git history, isolated file systems. Each agent sees a clean checkout. No conflicts. No confusion.

## Configuration: Central Plus Identity

Git worktrees solve workspace isolation. The second challenge, configuration, is solved in another way. Each agent needs the same rules *and* its own identity.

The solution is three layers:

**Layer 1: Central config** at `~/.claude/`. This is where `CLAUDE.md` lives, along with `commands/`, `skills/`, and `agents/` directories. I maintain this through my dotfiles, as described in [Part 2](https://medium.com/lab271/teaching-claude-code-where-to-live-52e1acfed96b). All agents read from here. Coding standards, workflow rules, allowed tools—shared everywhere.

**Layer 2: Agent identity** via `AGENT.md`. This is injected at launch time through the command line. It tells each agent who it is, what its role is, and that it's part of a swarm:

```markdown
# Agent Identity

You are agent-2 in a parallel swarm of 3 agents.
Your role: code reviewer
Your worktree: ~/wc/myproject-worktree/agent-2/

## Coordination
- Check ~/.local/state/agents/ for task status
- Your task file: agent-2/current-task.txt
- Other agents are working in parallel—don't duplicate effort
```

The `launch-agents` script generates and injects this dynamically. Same generic config, unique identity per agent.

**Layer 3: Project-local `CLAUDE.md`**. Each project can still have its own instructions in the repository root. Project-specific conventions, architecture decisions, domain knowledge. This layer remains untouched—agents pick it up automatically from their worktree.

The `settings.json` also lives centrally in `~/.claude/settings.json`. Command allowlists, blocked patterns, model preferences—all version controlled in my dotfiles, applied to every agent instance.

This provided three layers with a clear separation: global rules, agent identity, project specifics.

## The Launch Script

My [`launch-agents`](https://github.com/iheitlager/dotfiles/blob/main/local/bin/launch-agents) script orchestrates this. It creates worktrees, launches agents, and manages state—all from one command.

The core workflow:

```bash
#!/usr/bin/env bash

REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
WORKTREE_ROOT="$HOME/wc/${REPO_NAME}-worktree"
SESSION="claude-${REPO_NAME}"

setup_worktree() {
    local agent=$1
    local worktree_path="$WORKTREE_ROOT/agent-$agent"
    
    [[ -d "$worktree_path" ]] && return
    mkdir -p "$WORKTREE_ROOT"
    git branch "agent-$agent" 2>/dev/null || true
    git worktree add "$worktree_path" "agent-$agent"
}

generate_agent_manifest() {
    local agent=$1
    cat > "$WORKTREE_ROOT/agent-$agent/AGENTS.md" << EOF
# Agent Identity
You are agent-$agent in a parallel swarm for project: $REPO_NAME
Worktree: $WORKTREE_ROOT/agent-$agent
EOF
}

launch_agents() {
    local count=$1
    
    # Create tmux session with agent panes
    tmux new-session -d -s "$SESSION" -c "$WORKTREE_ROOT/agent-1"
    tmux split-window -h -t "$SESSION" -c "$WORKTREE_ROOT/agent-2"
    
    for i in $(seq 1 $count); do
        # Inject AGENTS.md via --append-system-prompt
        # This makes the agent aware of its number and role
        tmux send-keys -t "$SESSION.$i" \
            "claude --append-system-prompt \"\$(cat AGENTS.md)\"" C-m
    done
}
```

Usage is simple:

```bash
$ launch-agents start    # Creates worktrees, tmux panes, launches agents
```

This creates three worktrees, launches three Claude Code instances, and logs their assigned tasks. Each agent starts in its own directory with access to the shared configuration.

## Coordination Through GitHub Issues

For coordination, I use what's already there: GitHub Issues. Each issue becomes a task. The workflow is simple: start with an issue, create a branch, end with a PR.

Inside any agent, two slash commands handle the flow:

```
/issue Implement OAuth flow with Google provider
```

This creates a GitHub issue with proper labels, say #42. The agent can break down work into issues for itself or others.

```
/take #42
```

This claims issue #42. The agent reads the issue, creates a feature branch, does the work, and opens a PR when done. The PR references the issue, so closing the PR closes the issue. Standard GitHub flow, driven by agents.

The audit trail lives in GitHub where it belongs. Issues track what needs doing. PRs track what got done. Branch history shows how.

## Why This Matters

Parallel agents aren't just faster—they're better. Code review by a separate agent catches issues the implementing agent misses. Documentation written by an agent that didn't write the code is clearer. Tests written before implementation catch design issues early.

The launch script makes this coordination trivial. What would take an hour of manual git juggling becomes easier when setup before with these conventions. The XDG foundation makes it safe. State is isolated. Config is centralized. History is preserved.

And when something goes wrong? Git worktrees mean you can blow away any agent's workspace and recreate it in seconds. Providing a clean slate with the same config and no data loss.

## Next Steps

The foundation is complete. XDG-compliant dotfiles from Part 1. Version-controlled agent config from Part 2. Parallel execution from this part.

What's next depends on your workflow. I use this setup for feature development, code review, and documentation maintenance. Others use it for parallel test execution or multi-language projects. I am currnetly working on synchronization and my own role in the workflow. That is ongoing stuff.

But first: go launch your first parallel agent swarm. You'll wonder how you ever worked any other way.

---

*My dotfiles and launch scripts are available at [github.com/iheitlager/dotfiles](https://github.com/iheitlager/dotfiles). The `local/bin/launch-agents` script is in the repo.*

## References

- [Part 1: The Agents Are Coming. Clean Your $HOME.](https://stories.lab271.io/the-agents-are-coming-clean-your-home-c8ae7e026c51)
- [Part 2: Teaching Your AI Agent Where It Lives](LINK_TO_PART_2)
- [Git Worktrees Documentation](https://git-scm.com/docs/git-worktree)
- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/)
