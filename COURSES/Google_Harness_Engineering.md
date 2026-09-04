# Agent = Model + Harness: the six-layer playbook

Source : https://drive.google.com/file/d/1wZeuP0t4WOA2COMxcrU-Uv34IutM13UR/view

## Synthesis

The model provides reasoning. The harness turns that reasoning into a reliable system by controlling execution, verification, state, permissions, and observability.

Many AI agents remain stuck at the prototype stage. The bottleneck is not necessarily model capability, but the lack of infrastructure that makes agent behavior reliable, verifiable, persistent, and safe.

This document frames **harness engineering** as the next era of AI engineering, following prompt engineering in 2023-2024 and context engineering in 2025.

The model reasons. The harness controls everything around that reasoning.

## The same model can improve dramatically with a better harness

| Source       | Model             | Benchmark        | Before   | After    | Delta            |
| ------------ | ----------------- | ---------------- | -------- | -------- | ---------------- |
| Masood       | Claude Sonnet 4.5 | GAIA             | 30.91%   | 74.55%   | +43.64 pts       |
| LangChain    | Same model        | Terminal Bench   | 30th     | 5th      | +25 ranks        |
| Can.ac       | 16 LLMs           | Coding benchmark | Baseline | Improved | Harness only     |
| OpenAI Codex | Codex agents      | Production       | 0 lines  | 1M lines | Zero manual code |

These examples point to the same observation: changing the execution environment, tools, verification mechanisms, or context can produce substantial gains without changing the underlying model.

They are not a single controlled experiment, however. The benchmarks, environments, and methodologies differ.

The broader lesson is that **system design can matter as much as model selection**. A stronger model is not always the highest-leverage way to improve an agent.

## The six layers

### Layer 1: Guides

**Feedforward controls** that the agent reads before execution.

Typical files include `AGENTS.md`, `CLAUDE.md`, and `.cursorrules`.

Each rule should encode a lesson from a previous failure.

**The ratchet principle:**

1. Reproduce the failure
2. Classify the root cause
3. Identify the appropriate fix layer
4. Implement the fix
5. Verify it
6. Add a regression check

The goal is not to fix one conversation. It is to eliminate an entire class of future failures.

**Key idea →** A prompt patch fixes one interaction. A guide rule can fix every future run.

---

### Layer 2: Sensors

**Feedback controls** that run after execution.

Two categories:

**Computational sensors**

* Linters
* Type checkers
* Unit tests
* Schema validators
* Build checks

Fast, cheap, deterministic, and reproducible.

**Inferential sensors**

* LLM-as-judge
* Semantic quality checks
* Other evaluations requiring interpretation

Slower, more expensive, and potentially non-deterministic.

**Design principle → computational sensors first.**

If a property can be expressed as a deterministic rule, use a deterministic check.

For example:

"Does the code compile?" → automated test
"Is this answer sufficiently relevant?" → potentially LLM-as-judge

Do not use an LLM to judge something that a $0 deterministic check can verify.

---

### Layer 3: Agentic loop

A bounded execution loop:

**Plan → Execute → Verify → Fix → Verify again**

The loop needs explicit budgets and hard stops.

Example limits:

* 3 retries
* 30 minutes
* 100K tokens
* $5
* 50 tool calls

These are example values, not universal defaults. Budgets should depend on the task.

When a budget is exhausted, the agent should return:

* The best current artifact
* Completed work
* Unresolved issues
* The reason for stopping

It should **not hide partial failure behind a fluent final answer**.

---

### Layer 4: Memory and state

The key distinction is:

**Memory ≠ chat history.**

The objective is persistent, recoverable **state**.

Five persistence levels can be considered, from a temporary conversation buffer to a permanent knowledge graph.

For many agents, the simplest useful starting point is the filesystem:

* `plan.md` → where the agent is going
* `decisions.md` → why it made important choices
* `progress.json` → where it currently stands

The agent reads these at session start and updates them after meaningful steps.

This makes the agent resumable rather than conversationally dependent.

OpenAI's Codex report also documents that adding negative examples to compacted context improved routing accuracy from 73% to 85%.

---

### Layer 5: Permissions and budgets

Every action should be constrained along four dimensions:

| Dimension     | Question                                             |
| ------------- | ---------------------------------------------------- |
| Scope         | What files, systems, and tools can the agent access? |
| Rate          | How much can it do within a given period?            |
| Reversibility | Which actions require approval before execution?     |
| Visibility    | What actions are recorded and auditable?             |

The harness is the primary security boundary.

The model should not be expected to enforce its own permissions.

Prompt injection risk should therefore be addressed through **architectural separation** between:

**Trusted instructions**

* System instructions
* Guide files
* Explicit policies

**Untrusted data**

* User-provided content
* Retrieved documents
* Web pages
* Tool outputs

The model may reason about untrusted data, but the harness should determine what actions are actually permitted.

**Key idea →** Do not ask the model to enforce boundaries that the environment can enforce mechanically.

---

### Layer 6: Observability

An agent that fails silently cannot be reliably improved.

Useful telemetry includes:

* Start and finish timestamps
* Tool actions and outcomes
* Guide version
* Sensors executed and results
* Attempt count
* Token and financial cost
* Generated artifacts
* Approvals
* Escalations

**Trip wires** should detect abnormal behavior, such as:

* External write spike
* Same error repeated 3 times
* Cost exceeding 2x the average
* Sensor pass rate dropping
* New or unexpected domain contacted

**The real metric →** the percentage of tasks completed correctly, with sufficient evidence, without manual intervention.

Not model calls.
Not tokens.
Not messages.

## The core feedback loop

The six layers are not independent features. Together they create a compounding improvement loop:

**Failure → Reproduce → Diagnose → Fix at the right layer → Verify → Add regression protection**

A recurring human correction should progressively move down the reliability ladder.

### Control reliability ladder

| Layer       | Example                  | Reliability | Cost to add |
| ----------- | ------------------------ | ----------- | ----------- |
| Memory      | Prior correction in chat | Low         | Zero        |
| Prompt      | Task instruction         | Low-medium  | Minutes     |
| Guide       | `AGENTS.md` rule         | Medium      | Minutes     |
| Sensor      | Automated test           | High        | Hours       |
| Environment | Permission, schema, CI   | Highest     | Hours-days  |

Lauren Tan's principle at Cursor captures this progression:

When a human reviewer writes the same review comment more than three times, it should become a structural constraint.

A practical progression is:

**First occurrence:** add a guide rule
**Second:** verify the guide rule is being followed
**Third:** convert it into a sensor that blocks the violation
**Fourth:** should never happen

The goal is to move recurring knowledge from increasingly fragile layers toward increasingly reliable ones.

## Seven-day build path

| Day | Build                                     | Exit test                           |
| --- | ----------------------------------------- | ----------------------------------- |
| 1   | `AGENTS.md` with build/test/lint commands | Agent runs all 3 correctly          |
| 2   | 3 guide rules from observed failures      | Agent avoids all 3 anti-patterns    |
| 3   | First computational sensor                | Agent runs tests after every change |
| 4   | Agentic loop + retry budget               | Agent retries, then escalates       |
| 5   | File-based state checkpoint               | Agent resumes after restart         |
| 6   | Permissions + cost budget                 | Agent cannot exceed scope           |
| 7   | Structured logging + trip wire            | Trip wire fires on simulated spike  |

### Scale gate

Only expand the agent when:

* Completion rate is ≥80% without manual correction
* No task exceeds its cost budget
* The agent has correctly escalated at least once
* State survives at least one restart
* A trip wire fires on a simulated anomaly
* The permission boundary blocks at least one forbidden action

## When not to build a harness

| Scenario                | Harness? | Why                                             |
| ----------------------- | -------- | ----------------------------------------------- |
| One-off question        | No       | No recurrence, limited consequence              |
| Creative brainstorming  | No       | Output is exploratory and difficult to verify   |
| Daily code review agent | Yes      | Repeated task with meaningful consequences      |
| Research digest agent   | Yes      | Recurring task requiring evidence and citations |
| Customer support triage | Yes      | External-facing and reliability-sensitive       |
| CI/CD pipeline agent    | Yes      | Runs repeatedly and failures can block the team |
| Personal note-taking    | No       | Low stakes and limited external effect          |

Three simple tests:

**Would you notice if the agent silently produced a wrong result?**
→ If yes, you need a sensor.

**Would you need to explain the same context again next session?**
→ If yes, you need persistent state.

**Could a mistake create external consequences?**
→ If yes, you need permission boundaries.

## The key idea

The model is a **capability**. The harness turns that capability into a **system**.

A prompt correction improves one interaction.

A guide rule can prevent the same failure across future runs.

A sensor can detect the failure even when the model ignores the guide.

A permission boundary can prevent the agent from causing the failure in the first place.

Every recurring failure should become a structural improvement that applies to every future run.

The objective is not to build an agent that produces impressive answers.

It is to build a system that reliably completes tasks, verifies its own work, preserves state, respects boundaries, exposes failures, and improves after each failure.
