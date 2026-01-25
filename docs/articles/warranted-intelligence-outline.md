# LLMs Guess, Graphs Prove: Warranted Intelligence for Enterprise Transformation

> **Status:** Draft
> **Series:** "Agents Are Coming"
> **Companion to:** skill-security-epistemology.md

---

## The Hook

Everyone asks: "How do we make AI smarter?"

Wrong question.

LLMs are already remarkably capable at understanding code. They navigate unfamiliar codebases in seconds, infer intent from naming conventions, identify architectural patterns across thousands of files, and suggest transformations that would take human analysts days to formulate — all through abductive reasoning. The technology works. We've seen it work. Every developer who has used Copilot, Cursor, or Claude Code knows the almost uncanny feeling of an AI that *gets* what your code is trying to do.

The real question: **How do we make AI trustworthy?**

This isn't a technical limitation — it's an epistemological one. The enterprise architect who needs to justify a $50 million cloud migration can't point to "the AI said so." The compliance officer signing off on data residency can't accept probabilistic confidence scores. The board approving a digital transformation initiative needs findings, not feelings.

Enterprises don't need smarter guesses. They need *warranted* guesses — assertions backed by verifiable evidence that can survive audit, satisfy regulators, and justify investment. That's the gap this article addresses.

---

## Part I: The Trust Problem

### The Capability-Trust Gap

Consider what happens when an LLM analyzes your codebase:

| What LLMs Can Do | Why Enterprises Don't Trust It |
|------------------|-------------------------------|
| "This service handles PII" | How do you know? Show me the evidence. |
| "These modules are coupled" | Prove it. Quantify the coupling. |
| "Migration risk is high here" | Show your work. What specifically creates risk? |

LLMs reason abductively — a term from Charles Sanders Peirce meaning inference to the best explanation. They observe patterns (naming conventions, code structure, import relationships) and infer hypotheses about what the code does and why. This is genuinely intelligent behavior. But abduction produces *hypotheses*, not *findings*. A hypothesis is a starting point for inquiry. A finding is the conclusion of inquiry.

Regulated industries — finance, healthcare, government, critical infrastructure — cannot act on hypotheses. They need findings that can be documented, audited, and defended.

### Rorty's Problem, Enterprise Edition

The philosopher Richard Rorty spent his career arguing that knowledge doesn't mirror reality — it's a social construction mediated by language. For Rorty, all knowledge is:

- **Contingent** — context-dependent, not universal truth
- **Linguistic** — we access it through language, not direct perception
- **Anti-foundational** — there's no bedrock of certainty underneath

This describes LLM outputs precisely. When Claude says "this service handles payment data," that assertion emerges from pattern matching on training data, filtered through linguistic representations, with no direct access to the code's actual runtime behavior. It's not wrong — it's *ungrounded*.

An LLM's confident assertion about your codebase is not truth. It's a plausible story constructed from patterns. The enterprise cannot act on plausible stories. It needs stories that have been verified against reality.

---

## Part II: The Warrant

### Dewey's Contribution: Warranted Assertibility

John Dewey (1859–1952), Peirce's intellectual descendant and America's most influential public philosopher, spent decades refining a single insight: stop asking "Is this true?" and start asking "Is this belief warranted?"

Truth, Dewey argued, is too static a concept. It suggests correspondence with some fixed reality. But inquiry is dynamic — we form beliefs, test them, revise them, test again. What matters isn't whether a belief matches Reality with a capital R. What matters is whether the belief has survived the process of inquiry — whether it has been *warranted* through investigation.

A belief is **warranted** when:
1. It emerges from genuine inquiry (not mere assertion)
2. It survives testing against evidence (not just plausibility)
3. It enables successful action (not just contemplation)

This reframes the AI question entirely. We shouldn't ask "Is the LLM right?" — that's unanswerable in any deep sense. We should ask: "Is the LLM's assertion *warranted*?" Has it been tested? Against what evidence? Can we act on it?

### The Warrant Machine: Deterministic Code Analysis

Code analyzers — AST parsers, graph databases, symbol tables, data flow analysis, call graphs — provide what LLMs structurally cannot: **deterministic ground truth**. When a graph query returns 47 call sites between PaymentService and UserService, that's not an inference. It's a fact. When data flow analysis traces PII from input to external endpoint, that's not a hypothesis. It's a finding.

```
┌────────────────────────────────────────────────────────┐
│  LLM ASSERTION (Abductive)                             │
│  "PaymentService is tightly coupled to UserService     │
│   and handles sensitive financial data"                │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│  CODE ANALYZER WARRANT (Deductive)                     │
│                                                        │
│  MATCH (p:Class {name:'PaymentService'})-[:CALLS]->(u) │
│  WHERE u.name = 'UserService'                          │
│  RETURN count(*) → 47 call sites                       │
│                                                        │
│  MATCH (p:Class)-[:HANDLES]->(d:DataType)              │
│  WHERE d.classification = 'PII-Financial'              │
│  RETURN d → [CardNumber, BankAccount, SSN]             │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
              WARRANTED FINDING
              (Actionable in regulated context)
```

The LLM's assertion was correct. But it only becomes *actionable* once warranted by deterministic analysis. Now the architect can document it. The auditor can verify it. The executive can fund the remediation.

---

## Part III: The Extended Philosophical Framework

### Beyond Peirce and Rorty

The epistemology of code understanding draws on a richer tradition than just Peirce and Rorty. Each thinker illuminates a different aspect of how we come to know what software does and what it means.

| Thinker | Concept | Application |
|---------|---------|-------------|
| **Charles Sanders Peirce** | Abduction | LLMs infer hypotheses from patterns |
| **John Dewey** | Warranted assertibility | Validation transforms guess → finding |
| **W.V.O. Quine** | Web of belief | Code graphs *are* belief webs — change propagates |
| **Thomas Kuhn** | Paradigm shifts | Cloud transformation isn't incremental evolution |
| **Imre Lakatos** | Degenerating programmes | Legacy systems with protective belts of workarounds |
| **Michael Polanyi** | Tacit knowledge | LLMs surface what documentation doesn't capture |
| **Gilbert Ryle** | Knowing-how vs knowing-that | Graphs give facts; LLMs approximate practice |
| **Hans-Georg Gadamer** | Hermeneutics | Understanding legacy code requires horizon fusion |

Quine's "web of belief" maps directly to dependency graphs — change one node and the effects ripple outward. Kuhn's paradigm shifts explain why cloud migration can't be incremental; you're not improving the old paradigm, you're replacing it. Lakatos explains legacy systems perfectly: a degenerating core surrounded by an ever-thickening protective belt of workarounds, patches, and exceptions.

Polanyi's tacit knowledge — "we know more than we can tell" — explains why documentation is always incomplete. The senior developer knows things about the system that exist nowhere in writing. LLMs, trained on millions of codebases, have absorbed tacit patterns that let them surface this implicit knowledge. And Gadamer's hermeneutics reminds us that understanding legacy code requires bridging two horizons: the original author's context and our modern assumptions.

### The Epistemological Stack

```
┌─────────────────────────────────────────┐
│  TACIT KNOWLEDGE (Polanyi)              │
│  "We know more than we can tell"        │
│  LLMs surface undocumented intent       │
├─────────────────────────────────────────┤
│  ABDUCTION (Peirce)                     │
│  "This pattern suggests X"              │
│  LLMs generate hypotheses               │
├─────────────────────────────────────────┤
│  WEB OF BELIEF (Quine)                  │
│  "Everything connects"                  │
│  Code graphs map dependencies           │
├─────────────────────────────────────────┤
│  WARRANTED ASSERTIBILITY (Dewey)        │
│  "Validated through inquiry"            │
│  Deterministic analysis confirms        │
└─────────────────────────────────────────┘
```

---

## Part IV: Enterprise Transformation Use Cases

Enterprise software transformation — whether rationalization, cloud migration, compliance remediation, or architectural modernization — is fundamentally an epistemic challenge. You must understand systems that have evolved over decades, often without documentation, frequently with the original authors long departed. The combination of LLM abduction and deterministic warranting addresses this challenge at scale.

### 1. Code Rationalization

**The problem:** Large enterprises accumulate thousands of modules over decades. Teams merge, products pivot, temporary solutions become permanent. Eventually, nobody knows what's dead, what's duplicated, or what's critical. Tribal knowledge has dispersed. Documentation, where it exists, lies.

**LLM contribution (Abductive):**
- "This module appears to be dead code — the naming suggests a deprecated feature"
- "These three services seem to implement the same business logic with slight variations"
- "The naming pattern `*_temp_*` and the 2014 date in comments suggest this was a temporary fix"

**Analyzer warrant (Deductive):**
- Call graph proves: zero incoming references, last modification 2019
- Similarity analysis confirms: 73% code overlap, identical business logic
- Git archaeology shows: TODO comment from 2014, commit message says "temporary workaround"

**Warranted finding:** "Module X is confirmed dead — safe to remove, saving $Y in maintenance. Services Y, Z are duplication candidates — consolidation saves $W annually. Technical debt item W has quantified remediation cost of $V."

### 2. Cloud Transformation

**The problem:** Cloud migration is not lift-and-shift. Some components are cloud-ready. Others require re-architecture. Still others have hidden dependencies — filesystem assumptions, connection pooling models, state management — that will fail catastrophically in containerized environments. Identifying which is which, across millions of lines of code, exceeds human capacity.

**LLM contribution:**
- "This service appears stateless and cloud-ready — no persistent local storage"
- "This component has filesystem dependencies that suggest re-architecture needed"
- "The connection pooling pattern here assumes long-lived processes — won't survive container orchestration"

**Analyzer warrant:**
- Data flow analysis: no persistent state, all storage via external services ✓
- I/O analysis: 14 hardcoded filesystem paths, 3 temp file assumptions ✗
- Resource analysis: static connection pool initialized at startup, no dynamic scaling ✗

**Kuhn's insight applies here:** The LLM identifies where paradigm shifts are needed versus where normal refactoring suffices. Some code can evolve; some must be revolutionized. Knowing which is which before you start saves millions.

### 3. Sovereignty & Compliance

**The problem:** Regulatory requirements increasingly demand proof of data residency, PII handling, and cross-border data flows. GDPR, CCPA, sovereignty requirements — all require demonstrable evidence of where data goes and how it's protected. "We think it stays in the EU" is not an acceptable answer.

**LLM contribution:**
- "This field name `user_ssn` suggests it contains personal data requiring protection"
- "The flow pattern here looks like it sends user data to external analytics — potential compliance issue"
- "This encryption approach uses patterns common before 2020 — may not meet current GDPR standards"

**Analyzer warrant:**
- Data classification: field `ssn` tagged PII-Critical in schema analysis
- Data flow graph: PII originates at UserService → flows to AnalyticsService → exits to external endpoint (US-hosted)
- Crypto analysis: using SHA-1 for hashing, no salt — deprecated by NIST since 2011

**Gadamer's insight:** Regulatory requirements are texts requiring interpretation in your specific context. The regulation says "appropriate technical measures." What does that mean for *your* system? The LLM interprets the semantic intent; the analyzer grounds it in your actual implementation.

### 4. Adaptive Architecture / Modernization

**The problem:** You need to evolve the architecture without breaking the business. But where are the seams? What can be extracted into microservices? What's so entangled that extraction would cause more harm than good? Domain-driven design talks about bounded contexts — but where are yours, actually?

**LLM contribution:**
- "This looks like a natural bounded context boundary — minimal cross-cutting concerns"
- "These modules have high conceptual cohesion — they represent a single business capability"
- "The interface here is already functioning as an anti-corruption layer — good extraction candidate"

**Analyzer warrant:**
- Coupling metrics: inter-module calls = 3 (low), intra-module calls = 847 (high cohesion)
- Interface analysis: 94% of cross-boundary calls go through defined API contracts
- Change coupling (from git): these 12 files change together 89% of the time — they're a unit

**Lakatos's insight:** Is this architecture progressive (worth extending, still generating value) or degenerating (a rotting core protected by an ever-thickening belt of workarounds)? The metrics don't lie. When the protective belt exceeds the core, it's time for revolution, not evolution.

---

## Part V: The Architecture of Warranted Intelligence

Moving from philosophy to practice requires architecture. How do you actually build a system that generates warranted findings at scale? The key insight is separation of concerns: let the LLM do what it does best (semantic understanding, pattern recognition, hypothesis generation) and let deterministic analysis do what it does best (verification, quantification, proof).

### The Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   INGEST    │────▶│   ANALYZE   │────▶│   WARRANT   │
│             │     │             │     │             │
│ Source code │     │ LLM reasons │     │ Graph query │
│ Git history │     │ abductively │     │ validates   │
│ Config      │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────────────────────────┐
                    │         FINDINGS STORE          │
                    │                                 │
                    │  { assertion: "...",            │
                    │    confidence: 0.87,            │
                    │    warrant: { query: "...",     │
                    │               result: "..." },  │
                    │    status: WARRANTED }          │
                    └─────────────────────────────────┘
```

The ingest layer builds the deterministic foundation: parse code into ASTs, resolve symbols, construct call graphs, analyze data flows, store everything in a queryable graph database. This is expensive but one-time (with incremental updates). The analyze layer runs LLM inference against the codebase, generating assertions with confidence scores. The warrant layer attempts to verify each assertion against the graph, recording both the query and its result.

### Trust Levels

Not all findings need the same level of warrant. Internal exploration can tolerate unwarranted assertions — they're starting points, not conclusions. But anything that reaches an auditor needs full deterministic proof.

| Level | Description | Enterprise Use |
|-------|-------------|----------------|
| **Unwarranted** | LLM assertion only | Internal exploration, brainstorming |
| **Partially warranted** | Some graph confirmation | Technical discussion, prioritization |
| **Fully warranted** | Complete deterministic proof | Audit, compliance, executive decision |
| **Contradicted** | Graph disproves LLM | Flag for investigation — something interesting |

### The Feedback Loop

When the analyzer *contradicts* the LLM, that's not failure — it's signal. Two possibilities exist:

1. **The LLM hallucinated** — common, expected, the system is working as designed
2. **The code structure doesn't reflect reality** — the LLM detected semantic intent that the code doesn't implement

Both are valuable findings. The first prevents false positives from reaching decisions. The second surfaces a different kind of technical debt: code that doesn't do what its structure suggests it should. Documentation lies; the LLM detected the lie.

---

## Part VI: The Limits of Warrant — Structure vs Behavior

### The Testing Question

A natural objection arises: "Why not use unit tests as warrants? If the tests pass, isn't that deterministic proof?"

No. And understanding why illuminates something fundamental about the nature of software knowledge.

Unit tests verify *behavior* against *expectations*. They sample the infinite input space — never exhaustively. They're assertions about what code *should do*, not what it *is*. A test suite that passes tells you "the code behaves as expected for these specific cases." A graph query tells you "these 47 call sites exist." The first is verification of expectation; the second is ground truth about structure.

The epistemological gap is unbridgeable: tests operate in the domain of behavior, which is infinite. Code analyzers operate in the domain of structure, which is finite.

### The Finite-Infinite Divide

A codebase has a **finite** number of:
- Call sites (enumerable)
- Data flows (traceable)
- Dependencies (graphable)
- Symbols (parseable)
- Files, classes, methods (countable)

But it has an **infinite** number of:
- Possible inputs
- Execution paths through time
- State combinations
- Runtime behaviors

You cannot enumerate infinity. Testing is always sampling. This isn't a limitation of current tools — it's a mathematical certainty. The halting problem proved this in 1936: you cannot, in general, determine what a program will do without running it on all possible inputs.

Structure is knowable completely. Behavior is knowable only through sampling or formal proof.

### Strengthening Behavioral Warrants

If testing cannot provide deterministic warrant, can it provide *stronger* inductive warrant? Yes. The hierarchy:

**Code coverage** — deterministic measurement, weak behavioral warrant:
- 100% line coverage = "every line executed at least once"
- But execution ≠ correctness
- The line `if (balance > 0)` executes whether you test with `balance=100` or `balance=-50`
- Coverage tells you *what ran*, not *what's right*

**Mutation testing** — stronger inductive warrant:
- "Did tests catch when I changed `>` to `>=`?"
- High mutation score = tests are *sensitive* to changes
- Proves tests aren't trivially passing
- But still sampling from infinite mutation space
- A 95% mutation score means "we tried N mutations and caught 95%" — not "all possible mutations would be caught"

**Property-based testing** (QuickCheck, Hypothesis) — stronger still:
- Generate thousands of random inputs
- Test invariants rather than specific cases
- "For all integers x and y, `add(x, y) == add(y, x)`"
- Still inductive — couldn't find counterexample in N tries
- But much stronger than example-based tests

The difference is profound. Consider testing a function that sorts a list:

```python
# Example-based testing (weak inductive)
def test_sort_specific_cases():
    assert sort([3, 1, 2]) == [1, 2, 3]
    assert sort([]) == []
    assert sort([1]) == [1]
    assert sort([1, 1, 1]) == [1, 1, 1]
    # We tested 4 cases. What about the infinite others?

# Property-based testing (strong inductive)
from hypothesis import given
import hypothesis.strategies as st

@given(st.lists(st.integers()))
def test_sort_properties(lst):
    result = sort(lst)
    # Property 1: Output has same length as input
    assert len(result) == len(lst)
    # Property 2: Output is ordered
    assert all(result[i] <= result[i+1] for i in range(len(result)-1))
    # Property 3: Output is a permutation of input
    assert sorted(result) == sorted(lst)
    # Hypothesis generates 100+ random lists automatically
```

The example-based test verifies 4 specific inputs. The property-based test verifies *properties that must hold for all inputs*, then generates hundreds of random inputs to hunt for violations. If Hypothesis finds a counterexample, it even shrinks it to the minimal failing case.

This is still inductive — we haven't proven the properties hold for *all* lists, just that we couldn't find a counterexample. But it's dramatically stronger than hand-picked examples, which tend to reflect the developer's assumptions (and blind spots).

**Formal verification** — the deductive endpoint:

What if we want to *prove* the sort is correct for all possible inputs, not just the ones we tested? This requires formal methods. Here's the same example in Dafny, a verification-aware language:

```dafny
// Formal specification: what does "sorted" mean?
predicate Sorted(s: seq<int>)
{
  forall i, j :: 0 <= i < j < |s| ==> s[i] <= s[j]
}

// Formal specification: s2 is a permutation of s1
predicate Permutation(s1: seq<int>, s2: seq<int>)
{
  multiset(s1) == multiset(s2)
}

// The method with its contract
method Sort(a: array<int>) returns (sorted: array<int>)
  ensures Sorted(sorted[..])                    // Output is sorted
  ensures Permutation(a[..], sorted[..])        // Output is permutation of input
  ensures |sorted[..]| == |a[..]|               // Length preserved
{
  // ... implementation here ...
  // Dafny's verifier PROVES these properties hold
  // for ALL possible input arrays, not just tested ones
}
```

The Dafny verifier uses SMT solvers (Z3) to mathematically prove that `Sort` satisfies its specification for *every possible input* — not billions of random samples, but the infinite set of all integer arrays. If the proof fails, Dafny shows exactly which case breaks the contract.

The warrant progression for the same claim ("this function correctly sorts"):

| Approach | Inputs Checked | Warrant Type | Confidence |
|----------|---------------|--------------|------------|
| Example-based tests | 4 hand-picked | Weak inductive | Low |
| Property-based tests | ~1000 random | Strong inductive | Medium |
| Formal verification | ∞ (all possible) | Deductive | Complete |

The cost progression is inverse: example tests take minutes, property tests take hours to write well, formal verification takes days or weeks and requires specialized expertise. The enterprise chooses based on risk: payment processing might justify formal verification; internal tooling might not.

### The Deductive Path: Formal Methods

What *would* make behavioral claims deterministic? Formal methods — techniques that prove properties mathematically rather than testing them empirically.

| Technique | What It Proves | Practical Limitation |
|-----------|---------------|---------------------|
| **Symbolic execution** | "This path is reachable with these constraints" | Limited scale, path explosion |
| **Model checking** | "This property holds for all reachable states" | State space explosion |
| **Theorem proving** (Coq, Isabelle, Lean) | "This implementation satisfies this specification" | Extremely expensive, requires expertise |
| **Design by Contract** (SPARK Ada, Eiffel) | "Pre/postconditions hold at runtime" | Requires discipline, partial coverage |
| **Dependent types** (Idris, Agda) | "This program is correct by construction" | Steep learning curve, limited adoption |

Formal verification turns behavioral claims deductive — but at enormous cost. NASA uses it for spacecraft. Financial institutions use it for smart contracts. Most enterprises cannot afford it for general codebases.

The pragmatist asks: when is the cost justified?

### The Warrant Strength Hierarchy

Not all warrants are equal. The enterprise must choose warrant level based on risk tolerance and cost constraints.

```
WARRANT STRENGTH
──────────────────────────────────────────────────────────────────
                              │ Complete │ Practical │ Cost
──────────────────────────────────────────────────────────────────
Structural analysis (graphs)  │    ✓     │     ✓     │  Low
Formal verification           │    ✓     │     ✗     │  Very High
Mutation + coverage combined  │    ✗     │     ✓     │  Medium
Property-based testing        │    ✗     │     ✓     │  Medium
Unit tests alone              │    ✗     │     ✓     │  Low
LLM assertion                 │    ✗     │     ✓     │  Very Low
──────────────────────────────────────────────────────────────────
```

Or visualized as warrant strength:

```
WARRANT STRENGTH SPECTRUM
────────────────────────────────────────────────────────────────
Structural analysis     │████████████████████│  Deductive (complete)
Formal verification     │████████████████████│  Deductive (expensive)
Mutation + coverage     │████████████████░░░░│  Strong inductive
Property-based tests    │██████████████░░░░░░│  Strong inductive
Unit tests alone        │████████░░░░░░░░░░░░│  Weak inductive
LLM assertion           │████░░░░░░░░░░░░░░░░│  Abductive (hypothesis)
────────────────────────────────────────────────────────────────
```

### Matching Warrant to Claim Type

The insight: **different claims require different warrant types**.

| Claim Type | Example | Appropriate Warrant |
|------------|---------|---------------------|
| **Structural** | "Service A calls Service B" | Graph analysis (deductive) |
| **Dependency** | "Module X depends on library Y" | Dependency analysis (deductive) |
| **Data flow** | "PII flows from input to external API" | Taint analysis (deductive) |
| **Behavioral** | "This function handles edge cases correctly" | Mutation testing (strong inductive) |
| **Correctness** | "This algorithm produces correct results" | Formal proof OR extensive testing |
| **Semantic** | "This module implements payment processing" | LLM + human review (abductive + expertise) |

The enterprise transformation use cases from Part IV map to this framework:

- **Code rationalization** ("Is this dead code?") — Structural warrant (graph shows no incoming calls)
- **Cloud transformation** ("Is this stateless?") — Data flow warrant (no persistent state detected)
- **Compliance** ("Does PII leave the EU?") — Data flow warrant (trace shows external endpoint)
- **Architecture** ("Is this a good extraction boundary?") — Structural + behavioral (coupling metrics + change coupling from git)

### Dewey Revisited: Inquiry as Process

This hierarchy illuminates Dewey's concept of warranted assertibility more deeply. Dewey never claimed all warrants are equal. He emphasized that warrant comes through **inquiry** — the systematic process of testing beliefs against evidence.

The strength of a warrant depends on:
1. **The rigor of the inquiry** — How thoroughly was the belief tested?
2. **The completeness of the evidence** — Does it cover all cases or sample them?
3. **The relevance to action** — Does the warrant support the decision being made?

A structural claim warranted by graph analysis has undergone complete inquiry — every call site was examined. A behavioral claim warranted by unit tests has undergone partial inquiry — some inputs were tested. Both are warranted, but differently.

The enterprise architect choosing to extract a microservice needs structural warrant (coupling metrics) more than behavioral warrant (test coverage). The compliance officer certifying data handling needs data flow warrant (PII tracing) more than semantic warrant (LLM interpretation).

**Matching warrant type to decision type is the art of warranted intelligence.**

### The Pragmatic Synthesis

For enterprise transformation, the practical guidance:

1. **Structural claims** → Use graph analysis. It's deterministic, complete, and relatively cheap. This is your foundation.

2. **Behavioral claims** → Use mutation testing + coverage thresholds. Aim for >80% mutation score on critical paths. Accept that this is strong inductive, not deductive.

3. **Semantic claims** → Use LLM hypotheses + human expert review. The LLM surfaces what to look at; the human provides domain warrant.

4. **High-risk behavioral claims** → Consider formal methods for critical components. Payment processing, security boundaries, safety-critical code.

5. **Accept the hierarchy** — Don't treat all warrants as equal. A graph-based structural finding is stronger than a high-coverage behavioral finding, which is stronger than an LLM assertion. Document the warrant type alongside the finding.

The warranted intelligence system should track not just *whether* an assertion is warranted, but *how strongly* and *by what method*:

```json
{
  "assertion": "PaymentService is stateless and cloud-ready",
  "warrants": [
    {
      "type": "structural",
      "method": "data_flow_analysis", 
      "strength": "deductive",
      "result": "no persistent state variables detected"
    },
    {
      "type": "behavioral",
      "method": "mutation_testing",
      "strength": "strong_inductive", 
      "result": "94% mutation score on state-related tests"
    }
  ],
  "combined_confidence": "high",
  "suitable_for": ["technical_decision", "architecture_review"],
  "not_sufficient_for": ["formal_certification", "safety_critical"]
}
```

This is epistemological honesty: we know what we know, we know how we know it, and we know the limits of that knowing.

---

## Part VII: The Synthesis

### What Changes

The warranted intelligence paradigm represents a genuine shift in how enterprises can approach AI adoption — not as replacement for human judgment, nor as untrustworthy black box, but as a new kind of tool that generates testable hypotheses at machine scale.

| Old World | New World |
|-----------|-----------|
| Trust humans, verify with tools | Trust neither; triangulate |
| LLMs are unreliable | LLMs are *unwarranted* (different claim) |
| Code analysis is complete | Code analysis is *foundational* |
| AI replaces analysts | AI hypothesizes, analysts verify, tools warrant |
| All evidence is equal | Warrant strength varies by method |
| Testing proves correctness | Testing strengthens inductive warrant |

The shift from "unreliable" to "unwarranted" is crucial. Unreliable suggests random failure. Unwarranted suggests systematic incompleteness — the output is good but needs grounding. That's a solvable problem.

The recognition that warrant strength varies is equally important. Not all verification is equal. Structural analysis provides complete, deductive warrant. Behavioral testing provides strong but incomplete inductive warrant. LLM assertions provide abductive hypotheses. Each has its place; none substitutes for the others.

### The Enterprise Value Proposition

> "We don't ask you to trust AI. We ask you to trust a validation pipeline where AI generates hypotheses and deterministic analysis proves them."

This sentence is the entire pitch. It acknowledges enterprise skepticism about AI. It doesn't ask for blind faith. It offers a process that produces auditable, explainable, verifiable findings. The AI is a hypothesis generator — powerful, fast, insightful, but not authoritative. The authority comes from the warrant.

This is auditable — every finding traces to a query and its result. This is explainable — the warrant shows exactly why we believe the assertion. This satisfies the regulator — deterministic proof, not probabilistic confidence.

### Peirce's Full Circle

We end where we began, but with fuller understanding. Peirce didn't just give us abduction. He gave us the **scientific method** itself:

1. **Abduction** — form a hypothesis (the creative leap)
2. **Deduction** — derive testable predictions from the hypothesis
3. **Induction** — test predictions against evidence

LLMs do (1) extraordinarily well. They form hypotheses about code at a scale and speed no human team can match. Code analyzers enable (2) and (3) — they derive the queries that would confirm or deny the hypothesis, and they execute those queries against the actual codebase.

But Peirce's triad reveals something deeper when we examine warrant strength:

- **Structural analysis** completes the cycle with **deduction** — we derive what must be true and verify it completely
- **Behavioral testing** completes it with **induction** — we sample and generalize, accepting incompleteness
- **Formal methods** achieve **deductive warrant for behavior** — but at costs most cannot bear

The enterprise choosing its warrant strategy is choosing where to invest in each leg of Peirce's triad. More investment in deduction (formal methods) yields stronger warrant but higher cost. More investment in induction (testing) yields weaker warrant but broader coverage. The art is matching investment to risk.

We're not replacing the scientific method with AI. We're *implementing* it, at scale, for the first time in the history of software engineering. And we're doing so with clear-eyed recognition that different implementations of the method yield different strengths of warrant.

---

## Conclusion: From Assertion to Warrant

The question was never "Can AI understand code?"

It can. Remarkably well. Anyone who has watched an LLM navigate an unfamiliar codebase, identify the authentication flow, locate the database access patterns, and summarize the architectural decisions — all in minutes — knows that the capability is real.

The question is: "Can we *trust* AI's understanding?"

Not directly. Not as raw output. But we can **warrant** it.

The code analyzer isn't competing with the LLM. It's not a replacement, not an alternative, not a fallback. It's the epistemological foundation that transforms probabilistic inference into actionable intelligence. It provides what Rorty said we lack and Dewey said we need: a basis for warranted belief.

But warranting isn't binary. We've seen that:

- **Structural warrants** are deductive and complete — the graph contains all the facts
- **Behavioral warrants** are inductive and partial — tests sample the infinite space of execution  
- **Semantic warrants** are abductive and human-mediated — experts interpret what the code means

The mature enterprise doesn't ask "Is this warranted?" but "How strongly is this warranted, and is that strength sufficient for this decision?"

A $50 million migration decision needs stronger warrant than a refactoring suggestion. A compliance certification needs different warrant than an architecture discussion. The warranted intelligence system should make these distinctions explicit, traceable, and auditable.

Peirce gave us the guess — abduction, the creative leap, the only logical operation that introduces new ideas.

Dewey gave us the warrant — the process of inquiry that transforms assertion into justified belief.

The synthesis gives us **warranted intelligence**: AI reasoning that enterprises can actually use, because it's been tested, verified, and grounded in evidence whose strength we understand and can defend.

That's not a limitation of AI. That's AI, properly deployed — with epistemological honesty about what we know, how we know it, and how strongly we can claim to know it.

---

## References

- Peirce, C. S. — Collected Papers, especially on abduction and the scientific method
- Dewey, J. — *Logic: The Theory of Inquiry* (1938), warranted assertibility
- Quine, W.V.O. — "Two Dogmas of Empiricism" (1951), web of belief
- Kuhn, T. — *The Structure of Scientific Revolutions* (1962)
- Lakatos, I. — *The Methodology of Scientific Research Programmes* (1978)
- Polanyi, M. — *The Tacit Dimension* (1966)
- Ryle, G. — *The Concept of Mind* (1949), knowing-how vs knowing-that
- Gadamer, H-G. — *Truth and Method* (1960), hermeneutics
- Rorty, R. — *Philosophy and the Mirror of Nature* (1979)
- Turing, A. — "On Computable Numbers" (1936), the halting problem
- DeMillo, R., Lipton, R., Perlis, A. — "Social Processes and Proofs of Theorems and Programs" (1979)
- Dijkstra, E. — "Program Testing Can Be Used To Show The Presence Of Bugs, But Never To Show Their Absence"
- Claessen, K., Hughes, J. — "QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs" (2000)
- Jia, Y., Harman, M. — "An Analysis and Survey of the Development of Mutation Testing" (2011)

---

*Part of the "Agents Are Coming" series.*
