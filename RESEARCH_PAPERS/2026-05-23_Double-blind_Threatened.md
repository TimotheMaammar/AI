# Abstracts can reveal their authors

## About

Title : Large Language Models Threaten Double-blind Review

Link : <https://arxiv.org/abs/2608.05157>

Authors : Bulambo Mwendelwa Gloire, Prasenjit Mitra

Date : 05/23/2026

Code : <https://github.com/anonymous-authorship-collapse/unmask-double-blind-anonymisation>

## Synthesis

Double-blind review assumes that an anonymized manuscript does not let reviewers reliably recover its authors. This paper tests that assumption using only titles and abstracts, with names, affiliations, citations, and stylistic or bibliographic features excluded. The task is deliberately constrained: one true author is placed among four plausible candidates, all domain experts, and the model ranks the five candidates. The authors use a corpus of more than 12,000 papers published in 2024-2025, after the stated training cutoffs of the evaluated models, and compare LLMs against 20 graduate researchers.

**Human baseline and Qwen2.5-72B (five domain-expert candidates):**

| Measure | Human researchers | Qwen2.5-72B, Semantic Scholar experts |
| --- | ---: | ---: |
| Top-1 accuracy | 11.00% | 42.34% |
| Top-2 accuracy | 23.00% | 61.72% |
| Top-3 accuracy | 41.00% | 76.44% |
| Top-4 accuracy | 61.00% | 88.24% |
| MRR | 0.36, 95% CI [0.31, 0.41] | 0.623, 95% CI [0.617, 0.629] |
| Expected Calibration Error | 0.37 | 0.30 |

Qwen2.5-72B therefore reaches nearly four times the human top-1 rate. The MRR difference is significant (Wilcoxon p < 0.001, Cliff's delta = 0.52); ranking distributions also differ under a KS test (p < 0.0001). At confidence threshold tau = 0.5, humans retain the true author in a suspect set in 22.0% of trials, with an average set size of 1.94 candidates. Qwen2.5-72B retains the true author in 61.6% of trials with an almost identical 1.95-candidate set. The paper's claim is not that models identify every author, but that they narrow the plausible set much more effectively at comparable uncertainty.

**Candidate construction determines the strength of the leak (tau = 0.5):**

| Setting | Recall of true author in suspect set | Average suspect-set size | Top-1 accuracy |
| --- | ---: | ---: | ---: |
| Human researchers | 0.220 | 1.94 | 11.00% |
| LLaMA3-70B, OpenAlex experts | 0.515 | 1.78 | 36.97% |
| LLaMA3-70B, Semantic Scholar experts | 0.577 | 1.83 | 40.41% |
| Qwen2.5-72B, Semantic Scholar experts | 0.616 | 1.95 | 42.34% |
| Qwen2.5-72B, random candidates | 0.841 | 1.82 | 68.53% |

The random candidate pool is the easy case: Qwen2.5-72B reaches 68.53% top-1 accuracy and 0.841 recall. OpenAlex produces more confusable domain-expert pools than Semantic Scholar: at tau = 0.5, LLaMA3 recall falls to 0.515 versus 0.577 and its ECE rises to about 0.082 versus 0.057. Nevertheless, even the harder expert pools remain above the human 0.220 recall baseline. Qwen2.5-72B and LLaMA3-70B have similar top-1 accuracy, about 42% and 40%, and AUC-ROC, about 0.67 and 0.68; bootstrap confidence intervals find no significant difference (p > 0.1).

**Robustness and boundaries:**

- Removing confidence scoring and asking only for a ranked list leaves LLaMA3 top-1 accuracy near 40%.
- Shuffling candidate order and increasing decoding temperature from 0.0 to 0.3 do not significantly change performance.
- Aggregating Qwen2.5-72B and LLaMA3-70B does not improve on Qwen2.5-72B alone: top-1 accuracy is 41.84% versus 42.34%.
- Multi-round model debate lowers recall by 7.5% relative to the single-model setting at tau = 0.5, from 0.616 to 0.541, while expanding the average suspect set from 1.95 to 2.22.
- Medicine shows an 8% stronger authorship signal than computer science in the paper's disciplinary comparison. Senior and junior author settings show similar performance, which the authors interpret as evidence that the effect is not driven only by visibility or reputation.

The proposed mechanism is a latent conceptual signature: problem framing, methodological choices, and research focus remain in the title and abstract after conventional anonymization has removed explicit identifiers. The authors frame double-blind review as a probabilistic safeguard, not an absolute guarantee. Their stated limits are that only two open-weight models were evaluated, candidate pools always contain five names, and the 20 human evaluators were graduate researchers rather than senior specialists. Whether this degree of anonymity reduction changes real peer-review outcomes remains unmeasured.
