# GPT-6 Astra, Looped Transformers, and Hidden Reasoning

## References

Full title: "GPT-6 Astra, Looped Transformers, and Hidden Reasoning"   

Link: <https://magazine.sebastianraschka.com/p/gpt-6-astra-looped-transformers-and>     

Date: 09/09/2026     

Author: Sebastian Raschka   

## Abstract

Following the release of GPT-6 Astra, The Information reported that the model uses a "recurrent depth" mechanism (looped transformers), raising concerns about hidden reasoning (chain-of-thought). Raschka explains the looping mechanism through several reference papers, then argues that the link between looping and hidden reasoning is largely unfounded: the drop in visible token count is mostly explained by increased model capability, not by hidden computation.

## Content

### Context: Astra and looping

Astra beats GPT-5.6 Sol across nearly every category (99.9% on ARC-AGI-3 versus 7.8%), especially on 3D rendering and computer-use. A looped transformer passes representations through the same blocks multiple times (shared weights), instead of stacking distinct blocks. Examples: Nanbeige4.2-3B (22 blocks applied twice), Ouro (48 blocks x4), Mixture-of-Recursions (loop count decided per token via a learned router). Actual effect: reduced weight memory, but compute and KV cache stay nearly identical to a conventional model of the same effective depth. Measured benefit (SMELT, 09/2026): 6.8 to 18% less training compute for the same loss, at matched parameter/KV cache budget.

No official confirmation that Astra uses this mechanism, only The Information's reporting. Jakub Pachocki (OpenAI chief scientist) clarified that "the depth of the computation graph for our present frontier models, including Astra, is within a factor of two of GPT-4," which is compatible with looping without confirming it. Raschka believes Astra's success mainly comes from the training recipe and data, with looping only a marginal contribution.

### The real debate: does looping hide reasoning

OpenAI has already been hiding most reasoning traces since o1, so nothing changes for the end user. The concern is mainly for interpretability researchers and model development teams.

At matched accuracy, Astra uses fewer tokens than Sol. Raschka argues this isn't necessarily a sign of opacity: a more capable model makes fewer mistakes and backtracks less. Illustrative comparison: Luna already uses 80% more tokens than Sol at similar performance, without anyone treating that as an interpretability problem for Sol. A reasoning trace is in any case never guaranteed to faithfully reflect what actually happens inside the model. The only valid concern would be if looping pushed the model to present fake traces more often than a conventional transformer, for which there is no evidence.

Astra's system card acknowledges reduced monitorability compared to Sol, tied to shorter and less informative traces, without establishing looping as the cause rather than the shorter length in general.

**Pachocki's quote**, published as clarification after the controversy: "I want to prevent a race into unmonitorability kicked off by confused reporting [...] OpenAI has worked to preserve chain-of-thought monitoring since our very first reasoning models [...] I do think it is fragile and unfortunately trending in a negative direction, for reasons not contingent on architecture changes, which I will write about soon. But there are things we can do to strengthen it, and it's a core goal of our current research program."

### Author's conclusion

Looping delivers better performance at a fixed compute budget, which likely explains part of its use in Astra. Shorter traces are a side effect of more capable models, not a new trend: it already existed between differently-sized models within the same family. Analogy: a brilliant student needs less scratch paper during an exam, without that meaning they're cheating.
