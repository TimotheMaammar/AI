# LLMs can't track evolving user intent

## About

Title : LLMs get lost in evolving user intent

Link : <https://arxiv.org/abs/2607.20734>

Researchers : Jihoon Tack, Philippe Laban, Jennifer Neville

Institution : Microsoft Research

Date : 07/22/2026

Code : <https://github.com/microsoft/evolving-intent>

## Synthesis

Real conversations are not single-turn. Users rarely state their full intent upfront: they reveal it progressively, correct earlier constraints, and sometimes pivot to a different task mid-conversation. Current LLM evaluations are almost entirely single-turn, where the task is fully specified in one message. This paper tests what happens when that assumption breaks, by converting existing verifiable benchmarks into multi-turn conversations where user intent evolves across turns, without requiring new annotation. Three types of intent transitions are modeled: argument reveal (disclosing a new constraint), argument revision (correcting a previously stated constraint), and function switch (pivoting to a related task with shared context). The source intent is always anchored at the final turn, so the original benchmark verifier applies directly.

The central finding is that strong single-turn performance does not transfer. Across 9 frontier models on GSM8K, BIRD-SQL, BrowseComp+, and SWE-Bench Verified, with 6 intent transitions per conversation (2 reveals + 2 revisions + 2 function switches over 7 turns), the drops are consistent and substantial:

| Model | GSM8K Single | GSM8K Evolve | SWE Single | SWE Evolve |
| --- | --- | --- | --- | --- |
| GPT 5.1 | 98.0 | 82.0 (-16%) | 72.0 | 0.0 (-100%) |
| GPT 5.5 | 99.0 | 80.5 (-19%) | 86.0 | 80.0 (-7%) |
| Gemini 3.1 Pro | 98.0 | 82.0 (-16%) | 86.0 | 84.0 (-2%) |
| DeepSeek V3.2 | 96.5 | 78.5 (-19%) | 76.0 | 76.0 (0%) |
| Mistral Large 3 | 95.5 | 73.5 (-23%) | 56.0 | 0.0 (-100%) |

On SWE-Bench, GPT 5.1, Grok 4.20, and Mistral Large 3 all fall to 0%, exhausting their 100-tool-call budget per turn on exploration (grep, find, sed) rather than execution: fewer than 4 execution calls per 100. Function switches cause the steepest degradation across all models, much steeper than reveals or revisions. The ablation is clear: isolating each transition type on GSM8K, function switch alone drops GPT 5.1 from 98% to 87%, while argument reveal only costs 1 point and revision costs 1.5 points. This is because switches require the agent to actively discard accumulated context rather than just absorbing new information.

The key point of the paper is the explanation of why this happens, and what does not fix it. Enabling extended reasoning mode (chain-of-thought) produces no meaningful improvement: GPT 5.1 instant vs. reasoning mode yields nearly identical results across both datasets tested. Adding more turns without changing intent also has no effect, confirming that the degradation is driven by intent changes, not conversation length. Even an oracle memory mechanism, which explicitly re-states the full current intent at each turn, brings substantial gains but still falls short of single-turn baseline. The bottleneck is not local reasoning ability. It is belief updating: models are trained to use available context to predict the right answer, not to decide which parts of that context to override when the user changes their mind. They accumulate, but do not revise.

A preliminary RL experiment supports this: Qwen3-4B trained for fewer than 50 steps on evolving-intent GSM8K examples using GRPO improves from 64% to 76% on the evolving setting while preserving single-turn performance (94% to 95%), suggesting the framework can also serve as a training data source. The broader implication is that any agent deployed in real collaborative interaction, vibe coding, iterative document editing, deep research, will degrade significantly as soon as a user corrects a constraint or pivots. And this failure is entirely invisible in standard benchmarks.
