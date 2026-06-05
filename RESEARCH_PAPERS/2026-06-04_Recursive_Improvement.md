# When AI builds itself

## About

Title : When AI builds itself

Link : <https://www.anthropic.com/institute/recursive-self-improvement>

Authors : Marina Favaro (Anthropic Institute), Jack Clark

Company : Anthropic

Date : 06/04/2026


## Synthesis

Recursive self-improvement (RSI) is the idea that an AI system could help improve the very process that produces future AI systems, potentially including itself. This Anthropic Institute report attempts to move the question from theoretical AI safety discourse to internal operational data, arguing that several distinct R&D loops are now being automated at once. The authors are explicit about where the line is: "We are not there yet, and recursive self-improvement is not inevitable. But it could come sooner than most institutions are prepared for."

The report decomposes AI development into two axes: engineering (writing code, standing up infrastructure, overseeing training) and research (choosing what to run, interpreting results, deciding next steps).

**Engineering side (internal data, May 2026):**

- \> 80% of code merged into Anthropic's codebase authored by Claude, up from low single digits before Claude Code launched in February 2025
- Code volume per engineer per day: flat 2021-2024, then 8x the 2024 baseline by Q2 2026 (Anthropic flags this as an overstatement since it measures quantity not quality)
- Internal poll of 130 research-team employees: median self-reported productivity uplift ~4x
- Code quality: somewhat worse than human in late 2025, roughly at parity today, expected strictly better within the year
- Automated Claude reviewer would have caught ~1/3 of bugs behind past claude.ai incidents

**Research side (internal data, isolated settings):**

| Experiment | Result |
| --- | --- |
| Training speed optimization, Claude Opus 4 (May 2025) | 3x speedup vs human baseline of 4x in 4-8h |
| Training speed optimization, Mythos Preview (April 2026) | 52x speedup |
| Weak-to-strong researcher agents vs 2 humans on alignment question | 97% of gap recovered (agents, 800 compute-hours, ~$18k) vs 23% (humans, ~1 week) |
| Research navigation, 129 hard moments, Nov 2025 model | Beat human next step 51% of the time |
| Research navigation, 129 hard moments, Mythos Preview (April 2026) | Beat human next step 64% of the time |

Caveats from Anthropic itself: results from the weak-to-strong experiment did not transfer cleanly to production-scale models; humans still defined the problem and the scoring rubric in all research-side experiments.

**Public benchmarks:**

| Benchmark | Trend |
| --- | --- |
| SWE-bench (automated bug repair on real codebases) | Low single digits two years ago to near-saturation |
| CORE-Bench (reproducing published research) | ~20% in 2024 to near-saturation 15 months later |
| METR long-task horizon | Doubling roughly every 4 months; Claude Opus 4.6 handles 12h tasks |

All three sets of numbers should be read as Anthropic's interpretation, not settled consensus: benchmark versions matter and internal measurements are not independently replicated.
