# CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA Kernel Generation

## About

Title : CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA Kernel Generation    

Links : 
- <https://arxiv.org/abs/2602.24286>
- <https://cuda-agent.github.io/>
- <https://huggingface.co/datasets/BytedTsinghua-SIA/CUDA-Agent-Ops-6K>
  
Researchers : Weinan Dai, Hanlin Wu (co-first authors), Qiying Yu, Huan-ang Gao, Jiahao Li, Chengquan Jiang, Weiqiang Lou, Yufan Song, Hongli Yu, Jiaze Chen, Wei-Ying Ma, Ya-Qin Zhang, Jingjing Liu, Mingxuan Wang, Xin Liu, Hao Zhou

Date : 03/02/2026

## Synthesis

Writing optimized CUDA kernels by hand is a narrow engineering specialty, requiring GPU algorithmic thinking and deep hardware knowledge at once, and very few engineers do it well. LLMs remain non-competitive against compiler-based systems like torch.compile on this task, despite strong general-purpose coding performance. CUDA Agent is a large-scale agentic RL system that develops this capability through three components: a scalable data synthesis pipeline, a CUDA environment augmented with "skills" and automated verification/profiling for reliable reward signals, and RL techniques that keep training stable. Result: 100%, 100%, and 92% faster-than-torch.compile rates on KernelBench's Level-1, Level-2, and Level-3 splits, beating Claude Opus 4.5 and Gemini 3 Pro by about 40% on the hardest split (Level-3), with an average 2.11x speedup, a gain with direct production relevance (fewer GPUs needed, lower cost, lower latency).

RL training needs a large corpus of reference operators, missing from public datasets. The authors build one (CUDA-Agent-Ops-6K, 6,000 samples) by extracting operators from torch/transformers, having an LLM compose them together (up to 5 fused operators, which creates a non-trivial optimization problem distinct from optimizing each in isolation), then filtering by execution (correctness, no stochasticity, anti-hacking checks, AST-similarity decontamination against KernelBench).

The agent follows a standard ReAct loop (OpenHands-style), guided by a SKILL.md file that formalizes the workflow: profile the native PyTorch implementation, write a custom CUDA kernel targeting the identified bottleneck, compile/evaluate in a sandbox, iterate until a validated speedup is reached. The reward is discrete (4 levels, from -1 on a correctness failure to 3 if the kernel beats both Eager and Compile) rather than raw speedup, to avoid biasing training toward easy kernels, with 5 anti-reward-hacking mechanisms (file permissions, a ban on falling back to torch.nn.functional, validation on random inputs, profiling with device sync/warm-up, no web access for the agent).

The paper's real technical contribution lies elsewhere: the first RL attempt collapsed after only 17 steps, because CUDA data makes up less than 0.01% of pretraining, and the BF16/FP16 mismatch between training and inference blows up importance-sampling variance on these rare tokens. The fix is a 3-stage procedure (single-turn PPO warm-up, actor initialization via fine-tuning on filtered trajectories, critic pretraining via GAE), which makes training stable over 200 steps instead of 17.

Setup: base model Seed1.6 (MoE, 23B active / 230B total), 128 dedicated H20 GPUs for the verification sandbox, KernelBench Level 1-3 benchmark, compared against Claude Opus 4.5, Gemini 3 Pro, GLM 4.6, Kimi K2 (the ChatGPT-5 models refused CUDA prompts and could not be evaluated).

**Main results:**

| Model | Pass Rate | Faster Rate vs Compile | Speedup vs Compile (GM) |
| --- | --- | --- | --- |
| Seed1.6 (base) | 74.0% | 27.2% | 0.69x |
| GLM 4.6 | 75.6% | 19.2% | 0.57x |
| Kimi K2 | 66.8% | 22.8% | 0.66x |
| Gemini 3 Pro | 91.2% | 69.6% | 1.42x |
| Claude Opus 4.5 | 95.2% | 66.4% | 1.46x |
| **CUDA Agent** | **98.8%** | **96.8%** | **2.11x** |

**Ablations:**

| Variant | Pass Rate | Faster Rate vs Compile | Speedup vs Compile |
| --- | --- | --- | --- |
| No agent loop (single-turn) | 77.1% | 14.1% | 0.69x |
| No robust reward (raw speedup) | 96.8% | 60.4% | 1.25x |
| No RFT | 95.6% | 49.8% | 1.05x |
| No Value Pretraining | 98.6% | 50.9% | 1.00x |
| **Full CUDA Agent** | **98.8%** | **96.8%** | **2.11x** |

Every component matters: without the agent loop, both correctness and optimization drop (no execution feedback); without the robust reward, correctness holds but optimization collapses; without RFT or Value Pretraining, training becomes unstable (entropy explosion or trajectory-length explosion).

Five optimization patterns recur across the agent's trajectories: algebraic simplification (73.31x on a diagonal-matrix case), kernel fusion (24.04x), coalesced memory access, TF32 activation, and calling fused cuDNN APIs rather than reimplementing by hand. The ResNet BasicBlock case (3.59x) combines several of these at once.

Acknowledged limit: no comparison against frameworks like TVM (too heavy for a large-scale RL loop), and reliance on a 128-GPU H20 pool that limits the approach's accessibility.
