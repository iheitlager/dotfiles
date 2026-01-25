Show and manage the swarm job queue for multi-agent coordination.

## Terminology

- **Issue** — GitHub issue (external tracking, source of truth)
- **Job** — Swarm queue item (cross-agent coordination, ephemeral)
- **Task** — LLM session item (in-agent execution, personal scratchpad)

## Usage

- `/swarm` - Show queue overview + pending jobs with capability scores
- `/swarm active` - Show jobs currently being worked on
- `/swarm done` - Show recently completed jobs
- `/swarm create <title>` - Create a new job for the swarm

## Default: Queue Overview

Show the swarm job queue status:

1. **Summary counts** - pending, active, done
2. **Pending jobs** - Run `swarm-job list` to show jobs with capability scores
3. **Suggest actions** based on queue state

### Environment Setup

Before running `swarm-job`, ensure environment is set:
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

## Active Jobs

When argument is `active`, show jobs in `$SHARED_CONTEXT/jobs/active/`:
- Job ID and title
- Who claimed it (`claimed_by`)
- When claimed (`claimed_at`)

## Done Jobs

When argument is `done`, show recent jobs in `$SHARED_CONTEXT/jobs/done/`:
- Job ID and title
- Who completed it
- Result summary (if present)

Limit to last 10 jobs by default.

## Create Job

When argument starts with `create`, create a new job:

1. Generate job ID: `job-$(date +%s)`
2. Parse title from remaining arguments
3. Ask for complexity/priority if not obvious
4. Write YAML to `$SHARED_CONTEXT/jobs/pending/`
5. Log creation to `events.log`

### Job Template

```yaml
id: job-TIMESTAMP
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
- `swarm-job claim` - Claim the best matching job
- `swarm-job claim <id>` - Claim a specific job
- `/swarm create <title>` - Add work to the queue
- `tail -20 $SHARED_CONTEXT/events.log` - View recent activity
