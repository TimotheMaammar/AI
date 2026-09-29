# Scalable watermarking for identifying large language model outputs

## About

Title: Scalable watermarking for identifying large language model outputs     

Company: Google DeepMind

Links: 
- <https://www.nature.com/articles/s41586-024-08025-4>
- <https://github.com/google-deepmind/synthid-text>   

Date: 23/10/2024     

## Synthesis

LLMs increasingly generate text that is hard to distinguish from human writing, making it difficult to trace a piece of content back to its source. This paper presents SynthID-Text, a watermarking scheme that slightly changes how the LLM samples tokens during generation, encoding a statistically detectable signal without degrading perceived text quality. The scheme was deployed live on Gemini, with a test on roughly 20 million responses showing a statistically insignificant difference in user satisfaction between watermarked and non-watermarked text.

The core mechanism is Tournament sampling: instead of drawing a single token from the model's distribution, the method draws 2^m candidate tokens, generates a pseudorandom seed from the last H tokens (H=4 typically) combined with a watermarking key, then has the candidates compete across m rounds in a knockout bracket, each match decided by a pseudorandom scoring function g. The winning token is the one produced. With exactly two competitors per match, the scheme is mathematically non-distortionary at the token level, meaning it does not change the model's probability distribution, so there is no measurable quality loss. A repeated-context masking mechanism prevents re-watermarking a token window that has already appeared, extending the guarantee to longer sequences.

Detection requires no access to the model, only the text and the watermarking key: a mean-scoring detector averages the g-values across all tokens and tournament rounds, and a stronger Bayesian detector is trained on watermarked/non-watermarked text to compute the posterior probability that the text came from the watermarked model. In the non-distortionary configuration, with selective prediction (the detector abstains on uncertain cases), the scheme reaches 95% true positive rate at 1% false positive rate.

**Latency cost** (Gemma 7B-IT, 30-round tournament): 15.527ms to 15.615ms per token, a 0.57% increase, versus 0.26% for standard Gumbel sampling and 0.28% for Soft Red List. Complexity stays constant as model size grows.

**Production test on Gemini**: about 20 million watermarked and non-watermarked responses, measured on user thumbs-up/thumbs-down rate. Thumbs-up rate gap: 0.01% (favoring the watermarked model); thumbs-down rate gap: 0.02%. Neither gap is statistically significant at 95% confidence. A separate controlled human evaluation on 3,000 ELI5-style questions found no significant preference difference across 5 dimensions (grammaticality, relevance, correctness, helpfulness, overall quality).

Acknowledged limitations: the watermark weakens under text modification, notably paraphrasing by another LLM (though this usually changes the text significantly enough to limit the appeal of that attack). The method requires coordination from whoever runs the text-generation service, which is a problem for open-source models deployed in a decentralized way, where enforcing watermarking is difficult. The authors acknowledge vulnerability to stealing, spoofing, and scrubbing attacks, an area of ongoing research. They frame the scheme explicitly as complementary to other approaches rather than a complete solution, since it cannot detect text from a model that does not implement this watermarking in the first place.
