Create a spike (experimental exploration) in `./tests/spikes/`.

## Purpose

Spikes are hypothesis-driven explorations that answer specific technical questions before committing to implementation. Use when:
- Evaluating a new technology or approach
- Testing performance characteristics
- Validating architectural decisions
- Exploring unknown territory

## Process

1. **Define the question** - What are we trying to learn?
2. **Form hypothesis** - What do we expect to happen?
3. **Set success criteria** - How will we measure results?
4. **Create spike structure**
5. **Suggest branch**

## Required Information

### Problem Statement
- What decision are we making?
- What gap in knowledge exists?

### Hypothesis
- **H1 (Primary)**: "[Approach X] will achieve [outcome Y] under [constraints Z]"
- **H0 (Null)**: What would disprove the hypothesis?

### Success Criteria
| Metric | Target | Priority |
|--------|--------|----------|
| ... | ... | High/Medium/Low |

### Scope
- **Time-box**: How long to spend? (typically 1-3 days)
- **Deliverables**: Working code? Report? Both?

## Spike Structure

```
tests/spikes/NNN_descriptive_name/
├── README.md          # Hypothesis and results (use template)
├── spike_main.py      # Main exploration code
├── requirements.txt   # Dependencies (if any)
└── results/           # Output data, benchmarks, screenshots
```

## File Naming

Format: `NNN_short_description/`

1. Check existing spikes: `ls tests/spikes/`
2. Use next sequential number (3 digits)
3. Use lowercase, underscores for name

## README Template

Follow `0002-spike-hypothesis-template.md`:
- Problem Statement
- Hypothesis (H1, H0, alternatives)
- Research Design (success criteria, experimental design)
- Results (findings, data, analysis)
- Conclusion (accept/reject hypothesis, recommendations)

## Output

After gathering info:
1. Create directory structure
2. Generate README.md with hypothesis template
3. Create starter spike_main.py
4. Suggest branch: `spike/descriptive-name`

Example:
```bash
mkdir -p tests/spikes/015_postgres_fulltext/results
# Create README.md and spike_main.py
git checkout -b spike/postgres-fulltext
```

Ask user to confirm before creating.
