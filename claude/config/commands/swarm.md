Show and manage the swarm task queue for multi-agent coordination.

## Usage

- `/swarm` - Show queue overview + pending tasks with capability scores
- `/swarm active` - Show tasks currently being worked on
- `/swarm done` - Show recently completed tasks
- `/swarm create <title>` - Create a new task for the swarm

## Default: Queue Overview

Show the swarm task queue status:

1. **Summary counts** - pending, active, done
2. **Pending tasks** - Run `claim-task --list` to show tasks with capability scores
3. **Suggest actions** based on queue state

### Environment Setup

Before running `claim-task`, ensure environment is set:
```bash
export AGENT_ID="${AGENT_ID:-agent-1}"
export AGENT_MODEL="${AGENT_MODEL:-opus}"
```

### Paths

Derive paths from git repo:
```bash
REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
SHARED_CONTEXT="$HOME/.local/state/agent-context/$REPO_NAME"
```

## Active Tasks

When argument is `active`, show tasks in `$SHARED_CONTEXT/tasks/active/`:
- Task ID and title
- Who claimed it (`claimed_by`)
- When claimed (`claimed_at`)

## Done Tasks

When argument is `done`, show recent tasks in `$SHARED_CONTEXT/tasks/done/`:
- Task ID and title
- Who completed it
- Result summary (if present)

Limit to last 10 tasks by default.

## Create Task

When argument starts with `create`, create a new task:

1. Generate task ID: `task-$(date +%s)`
2. Parse title from remaining arguments
3. Ask for complexity/priority if not obvious
4. Write YAML to `$SHARED_CONTEXT/tasks/pending/`
5. Log creation to `events.log`

### Task Template

```yaml
id: task-TIMESTAMP
created: ISO_TIMESTAMP
created_by: AGENT_ID
priority: medium
complexity: moderate
recommended_model: sonnet
title: TITLE_HERE
description: |
  DESCRIPTION_HERE
depends_on: []
claimed_by: null
claimed_at: null
completed_at: null
result: null
```

## Output

After showing status, suggest next actions:
- `claim-task` - Claim the best matching task
- `claim-task <id>` - Claim a specific task
- `/swarm create <title>` - Add work to the queue
- `tail -20 $SHARED_CONTEXT/events.log` - View recent activity
