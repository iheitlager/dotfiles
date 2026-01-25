# The Proof Strength Ladder: A Framework for Code Validity

> **Status:** Draft / Working Document
> **Series:** "Agents Are Coming"
> **Related:** warranted-intelligence-outline.md, formal-methods-rediscovered.md

---

## Overview

This document defines a hierarchical framework for evaluating the strength of proof that code is correct. Each level answers a different question and provides a different level of confidence.

---

## Part I: The Proof Strength Ladder

### The Hierarchy

```
PROOF STRENGTH LADDER
═══════════════════════════════════════════════════════════════════════════════════
Level │ Name                 │ What It Proves              │ Question Answered
═══════════════════════════════════════════════════════════════════════════════════
  1   │ Compiles             │ Syntax valid, types align   │ "Is this valid code?"
  2   │ Static Analysis      │ No obvious smells/vulns     │ "Does this code smell wrong?"
  3   │ Starts               │ Init succeeds, deps resolve │ "Can this run at all?"
──────┼──────────────────────┼─────────────────────────────┼────────────────────────────
  4   │ Unit Tests           │ Specific examples work      │ "Do these cases work?"
  5   │ Integration Tests    │ Components connect          │ "Do the pieces fit?"
  6   │ FIT/Acceptance Tests │ Business scenarios work     │ "Does business get what they asked?"
──────┼──────────────────────┼─────────────────────────────┼────────────────────────────
  7   │ Mutation Testing     │ Tests are meaningful        │ "Would tests catch bugs?"
  8   │ Property Testing     │ Invariants hold randomly    │ "Do properties hold generally?"
  9   │ Formal Verification  │ Proven for all inputs       │ "Is this correct by construction?"
═══════════════════════════════════════════════════════════════════════════════════
```

### Level Descriptions

#### Level 1: Compiles
- **Tool examples:** gcc, javac, tsc, rustc, mypy
- **What passes:** Syntax is valid, type system satisfied
- **What can still fail:** Any runtime behavior, logic errors, edge cases
- **Effort:** Automatic (part of build)

#### Level 2: Static Analysis
- **Tool examples:** ESLint, SonarQube, Semgrep, Bandit, Clippy
- **What passes:** No pattern-matched code smells or vulnerabilities
- **What can still fail:** Anything the patterns don't catch, novel bugs
- **Effort:** Low (CI integration)

#### Level 3: Starts
- **Tool examples:** Smoke tests, health checks, container probes
- **What passes:** Application initializes, dependencies resolve, config valid
- **What can still fail:** All behavior after initialization
- **Effort:** Low (basic deployment verification)

#### Level 4: Unit Tests
- **Tool examples:** pytest, JUnit, Jest, RSpec, go test
- **What passes:** Hand-picked examples produce expected outputs
- **What can still fail:** All non-tested inputs (infinite)
- **Effort:** Medium (developer time per test)

#### Level 5: Integration Tests
- **Tool examples:** pytest + testcontainers, Arquillian, Spring Test
- **What passes:** Components interact correctly at boundaries
- **What can still fail:** Internal logic, edge cases, scale issues
- **Effort:** Medium-High (environment setup, slower execution)

#### Level 6: FIT/Acceptance Tests
- **Tool examples:** Cucumber, FitNesse, Robot Framework, Behave
- **What passes:** Business-readable scenarios execute successfully
- **What can still fail:** Scenarios not specified, edge cases
- **Effort:** Medium (requires business collaboration)
- **Unique value:** Stakeholder-readable proof

#### Level 7: Mutation Testing
- **Tool examples:** PIT (Java), mutmut (Python), Stryker (JS/TS)
- **What passes:** Tests detect injected faults
- **What can still fail:** Mutations not generated, equivalent mutants
- **Effort:** High (10-100x test runtime)
- **Meta-level:** Measures test quality, not code correctness

#### Level 8: Property Testing
- **Tool examples:** Hypothesis (Python), QuickCheck (Haskell), fast-check (JS)
- **What passes:** Invariants hold for thousands of random inputs
- **What can still fail:** Cases randomness didn't generate
- **Effort:** High (requires identifying good properties)

#### Level 9: Formal Verification
- **Tool examples:** Dafny, Coq, Isabelle, SPARK Ada, TLA+, Alloy
- **What passes:** Mathematical proof that specification holds for ALL inputs
- **What can still fail:** Nothing within the specification (spec can be wrong)
- **Effort:** Very High (specialized expertise, weeks per component)

---

## Part II: Coverage as Orthogonal Measurement

Coverage is **not a level** in the ladder. It's a meta-measurement that applies to levels 4-6.

```
                                              ┌─────────────────────┐
                                              │ COVERAGE METRICS    │
                                              │ (Meta-measurement)  │
                                              └──────────┬──────────┘
                                                         │
                                                         │ Measures breadth of
                                                         │ levels 4-6
                                                         ▼
═══════════════════════════════════════════════════════════════════════════
Level │ Name                 │ Coverage Applies?
═══════════════════════════════════════════════════════════════════════════
  1   │ Compiles             │ No
  2   │ Static Analysis      │ No (rules coverage is different concept)
  3   │ Starts               │ No
──────┼──────────────────────┼──────────────────────────────────────────────
  4   │ Unit Tests           │ ✓ Line, branch, function coverage
  5   │ Integration Tests    │ ✓ Line, branch, API endpoint coverage
  6   │ FIT/Acceptance Tests │ ✓ Line, branch, requirement coverage
──────┼──────────────────────┼──────────────────────────────────────────────
  7   │ Mutation Testing     │ No (mutation SCORE is the metric here)
  8   │ Property Testing     │ Partial (coverage of property space)
  9   │ Formal Verification  │ No (100% by definition within spec)
═══════════════════════════════════════════════════════════════════════════
```

### Coverage Types

| Metric | Question | 100% Means |
|--------|----------|------------|
| **Line coverage** | Did this line execute? | Every line ran at least once |
| **Branch coverage** | Did both if/else run? | Every decision evaluated both ways |
| **Path coverage** | Did every path run? | Every combination (exponential, rarely achievable) |
| **Function coverage** | Did this function get called? | Every function invoked at least once |
| **Requirement coverage** | Is every requirement tested? | Every spec item has a test |

### The Coverage Trap

```python
def divide(a, b):
    return a / b

def test_divide():
    assert divide(10, 2) == 5  # 100% line coverage achieved!
    # But: divide(1, 0) → ZeroDivisionError 💥
```

**Coverage tells you:** What code *executed* during tests
**Coverage does NOT tell you:** Whether the code is *correct*

100% coverage with zero edge case testing is common and dangerous.

### Coverage vs Mutation Score

| Metric | Measures | High Score Means |
|--------|----------|------------------|
| **Coverage** | Test breadth | Tests *touched* most code |
| **Mutation Score** | Test depth | Tests *caught* injected faults |

Coverage is necessary but not sufficient. Mutation testing validates that coverage is meaningful.

---

## Part III: Test Strength Evaluation Agent

### Purpose

An LLM-based agent that evaluates the test strength of a codebase against the Proof Strength Ladder framework, identifies gaps, and recommends improvements.

### Agent Specification

```yaml
name: test-strength-evaluator
version: 0.1.0
description: >
  Evaluates codebase test strength against the Proof Strength Ladder,
  identifies gaps, and recommends improvements prioritized by risk.

inputs:
  - codebase_path: string        # Path to codebase root
  - language: string             # Primary language (python, java, typescript, etc.)
  - focus_areas: string[]        # Optional: specific modules to prioritize
  - risk_profile: enum           # low, medium, high, critical
  
outputs:
  - strength_report: StrengthReport
  - gap_analysis: GapAnalysis
  - recommendations: Recommendation[]
```

### Agent Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: DISCOVERY                                                          │
│                                                                             │
│ 1. Scan codebase structure                                                  │
│ 2. Identify test frameworks in use                                          │
│ 3. Detect CI/CD configuration                                               │
│ 4. Catalog existing test files                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: LEVEL ASSESSMENT                                                   │
│                                                                             │
│ For each ladder level, determine:                                           │
│ - Present? (yes/no/partial)                                                 │
│ - Tool(s) in use                                                            │
│ - Configuration quality                                                     │
│ - Coverage/score if applicable                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: GAP ANALYSIS                                                       │
│                                                                             │
│ Compare current state to:                                                   │
│ - Risk profile expectations                                                 │
│ - Industry benchmarks                                                       │
│ - Identified critical paths                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: RECOMMENDATIONS                                                    │
│                                                                             │
│ Generate prioritized recommendations:                                       │
│ - Quick wins (low effort, high impact)                                      │
│ - Strategic investments (high effort, high impact)                          │
│ - Specific tooling suggestions                                              │
│ - Example configurations                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Structures

```typescript
interface StrengthReport {
  codebase: string;
  assessed_at: DateTime;
  overall_score: number;  // 0-100
  levels: LevelAssessment[];
  coverage_metrics: CoverageMetrics;
}

interface LevelAssessment {
  level: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9;
  name: string;
  status: 'absent' | 'partial' | 'present' | 'mature';
  tools_detected: string[];
  configuration_quality: 'none' | 'basic' | 'good' | 'excellent';
  evidence: string[];  // File paths, config snippets
  score: number;  // 0-100 for this level
}

interface CoverageMetrics {
  line_coverage: number | null;
  branch_coverage: number | null;
  function_coverage: number | null;
  mutation_score: number | null;
  source: string;  // Where metrics came from
}

interface GapAnalysis {
  risk_profile: 'low' | 'medium' | 'high' | 'critical';
  expected_levels: number[];  // Which levels should be present
  missing_levels: number[];
  underperforming_levels: LevelGap[];
  critical_paths_untested: string[];
}

interface LevelGap {
  level: number;
  current_score: number;
  expected_score: number;
  gap_description: string;
}

interface Recommendation {
  priority: 'critical' | 'high' | 'medium' | 'low';
  level: number;
  title: string;
  description: string;
  effort: 'hours' | 'days' | 'weeks';
  impact: 'low' | 'medium' | 'high';
  implementation: ImplementationGuide;
}

interface ImplementationGuide {
  tools: string[];
  config_example: string;
  first_steps: string[];
  references: string[];
}
```

### Risk Profile Expectations

```yaml
risk_profiles:
  low:
    description: "Internal tools, non-critical systems"
    minimum_levels: [1, 3, 4]
    recommended_levels: [2, 5]
    coverage_target: 60%
    
  medium:
    description: "Customer-facing applications, standard business systems"
    minimum_levels: [1, 2, 3, 4, 5]
    recommended_levels: [6, 7]
    coverage_target: 80%
    mutation_target: 60%
    
  high:
    description: "Financial systems, healthcare, regulated industries"
    minimum_levels: [1, 2, 3, 4, 5, 6, 7]
    recommended_levels: [8]
    coverage_target: 90%
    mutation_target: 80%
    
  critical:
    description: "Safety-critical, life-or-death systems"
    minimum_levels: [1, 2, 3, 4, 5, 6, 7, 8]
    recommended_levels: [9]
    coverage_target: 95%
    mutation_target: 90%
    formal_verification: required_for_critical_paths
```

### Example Agent Output

```json
{
  "strength_report": {
    "codebase": "/path/to/payment-service",
    "assessed_at": "2026-01-25T14:30:00Z",
    "overall_score": 62,
    "levels": [
      {"level": 1, "name": "Compiles", "status": "mature", "score": 100},
      {"level": 2, "name": "Static Analysis", "status": "present", "score": 75},
      {"level": 3, "name": "Starts", "status": "present", "score": 80},
      {"level": 4, "name": "Unit Tests", "status": "present", "score": 70},
      {"level": 5, "name": "Integration Tests", "status": "partial", "score": 45},
      {"level": 6, "name": "FIT/Acceptance", "status": "absent", "score": 0},
      {"level": 7, "name": "Mutation Testing", "status": "absent", "score": 0},
      {"level": 8, "name": "Property Testing", "status": "absent", "score": 0},
      {"level": 9, "name": "Formal Verification", "status": "absent", "score": 0}
    ],
    "coverage_metrics": {
      "line_coverage": 72,
      "branch_coverage": 58,
      "mutation_score": null,
      "source": "coverage.xml from CI"
    }
  },
  "gap_analysis": {
    "risk_profile": "high",
    "expected_levels": [1, 2, 3, 4, 5, 6, 7],
    "missing_levels": [6, 7],
    "underperforming_levels": [
      {"level": 5, "current_score": 45, "expected_score": 80, "gap_description": "Integration tests cover only 3 of 12 external service boundaries"}
    ],
    "critical_paths_untested": [
      "src/payment/processor.py:process_refund",
      "src/payment/validator.py:validate_card_number"
    ]
  },
  "recommendations": [
    {
      "priority": "critical",
      "level": 5,
      "title": "Add integration tests for payment processor",
      "description": "The refund processing path has no integration test coverage",
      "effort": "days",
      "impact": "high",
      "implementation": {
        "tools": ["pytest", "testcontainers"],
        "config_example": "# See examples/integration_test_setup.py",
        "first_steps": [
          "Add testcontainers to dev dependencies",
          "Create fixture for payment gateway mock",
          "Write test for process_refund happy path",
          "Write test for process_refund failure scenarios"
        ]
      }
    },
    {
      "priority": "high", 
      "level": 7,
      "title": "Introduce mutation testing",
      "description": "Unit tests exist but quality is unknown. Mutation testing will validate test effectiveness.",
      "effort": "hours",
      "impact": "medium",
      "implementation": {
        "tools": ["mutmut"],
        "config_example": "[tool.mutmut]\npaths_to_mutate = \"src/\"\ntests_dir = \"tests/\"",
        "first_steps": [
          "pip install mutmut",
          "Run mutmut on critical modules first",
          "Target 70% mutation score initially"
        ]
      }
    }
  ]
}
```

### Agent Prompts

#### Discovery Prompt
```
Analyze this codebase to identify the testing infrastructure:

1. What test frameworks are present? (Look for pytest, junit, jest, etc.)
2. What CI/CD system is configured? (GitHub Actions, GitLab CI, Jenkins, etc.)
3. What static analysis tools are configured? (eslint, sonar, etc.)
4. Is there evidence of:
   - Mutation testing (mutmut, pit, stryker configs)
   - Property testing (hypothesis, quickcheck, fast-check imports)
   - Formal verification (dafny, tla+, alloy files)
   - Acceptance tests (cucumber, behave, robot framework)

Return structured findings with file paths as evidence.
```

#### Assessment Prompt
```
For proof strength level {level} ({name}):

Evaluate the current implementation quality:
- Is it present, partial, or absent?
- What tools are in use?
- How well is it configured?
- What evidence supports this assessment?

Score from 0-100 based on:
- 0: Absent
- 25: Present but minimal
- 50: Partial implementation
- 75: Good implementation
- 100: Mature, well-configured

Provide specific file paths and configuration snippets as evidence.
```

#### Recommendation Prompt  
```
Given:
- Risk profile: {risk_profile}
- Current gaps: {gaps}
- Codebase language: {language}

Generate prioritized recommendations to improve test strength.

For each recommendation:
1. Which ladder level does it address?
2. What is the effort/impact ratio?
3. What specific tools should be used?
4. What are concrete first steps?

Prioritize quick wins for immediate improvement, then strategic investments.
```

---

## Part IV: Future Work

- [ ] Implement agent as Claude Code command
- [ ] Add language-specific tool detection heuristics
- [ ] Create benchmark datasets for evaluation
- [ ] Integrate with CI/CD for continuous strength monitoring
- [ ] Add visualization dashboard for strength reports
- [ ] Develop "test strength badge" for repositories

---

## References

- Turing, A. — "On Computable Numbers" (1936)
- Dijkstra, E. — "Program Testing Can Be Used To Show The Presence Of Bugs, But Never To Show Their Absence"
- Claessen, K., Hughes, J. — "QuickCheck: A Lightweight Tool for Random Testing" (2000)
- Jia, Y., Harman, M. — "An Analysis and Survey of the Development of Mutation Testing" (2011)
- Leino, K.R.M. — "Dafny: An Automatic Program Verifier for Functional Correctness" (2010)

---

*Part of the "Agents Are Coming" series.*
*Working document — to be developed into agent implementation.*
