# vec2vec: translating embeddings without paired data, with real security implications

## About

Title: "Harnessing the Universal Geometry of Embeddings"

Links : 
- <https://arxiv.org/pdf/2505.12540>
- <https://vec2vec.github.io/>
- <https://github.com/rjha18/vec2vec>

Date: 26/01/2026

Researchers: Rishi Jha, Collin Zhang, Vitaly Shmatikov, John X. Morris

## Synthesis

Different text embedding models encode the same semantic content into completely different, geometrically incompatible vector spaces, depending on architecture, training data, and initialization. vec2vec is the first method that translates embeddings from one such space to another with no paired data, no access to the original encoder, and no predefined set of candidate matches. The method rests on a strengthened version of the Platonic Representation Hypothesis: rather than just conjecturing that models converge toward a universal latent structure, the authors show that structure can be learned and actively exploited to translate between spaces.

The architecture is a modular five-part network: input adapters project each encoder's embeddings into a shared universal latent space, a shared backbone processes that latent representation, and output adapters project back into each target encoder's space. Training combines an adversarial (GAN) objective with three additional constraints, reconstruction, cycle-consistency, and vector space preservation, all shown by ablation to be individually necessary; removing any one collapses performance toward random.

Results are striking. In-distribution (trained and evaluated on Natural Questions), vec2vec reaches cosine similarities up to 0.96 and perfect matching on over 8,000 shuffled embeddings with no prior knowledge of the candidate set. On same-backbone model pairs it roughly matches strong baselines, but on cross-backbone pairs (say, a T5-based encoder versus a BERT-based one) it vastly outperforms both a naive baseline and an oracle-assisted optimal transport baseline, which both collapse to near-random performance. Critically, this holds out-of-distribution too: translators trained only on Wikipedia-style questions still translate tweets full of emojis and medical records full of specialized jargon with high fidelity, evidence that the learned structure is a genuine property of language rather than an artifact of the training corpus. A preliminary CLIP experiment shows the approach even extends, with degraded but above-baseline performance, across modalities.

The security implication is the paper's second major contribution. A vector database leak, embeddings only, no encoder, no original documents, is not as safe as it looks. By translating stolen embeddings into the space of a known, queryable model, an attacker can apply existing off-the-shelf inversion and attribute-inference tools built for that known model. The paper demonstrates this concretely: zero-shot attribute inference on translated embeddings often beats even the "ideal" same-space baseline, correctly identifying ultra-specific medical concepts (like "alveolar periostitis") that never appeared in vec2vec's own training data, which is itself evidence the learned space is genuinely universal. Zero-shot inversion on translated embeddings recovers meaningful content, names, dates, financial details, even lunch orders, for up to 80% of emails from the Enron corpus and 67% of tweets, judged by GPT-4o comparing reconstructions to ground truth.

Training remains GAN-typical unstable: on same-backbone pairs 14 of 15 random seeds converge to at least 80% top-1 accuracy, but on cross-backbone pairs only 3 of 15 seeds converge. Data efficiency is favorable, though: performance with just 50,000 training embeddings nearly matches performance with 1 million, and even 10,000 embeddings beat chance by a wide margin. The authors frame the result as strong empirical support for what they call the Strong Platonic Representation Hypothesis, and note plainly that better translation methods will only make extraction more accurate, reinforcing that embeddings leak nearly as much as the text itself.

The paper opened a distinct research subfield on embedding-translation attacks, now cited routinely across follow-up work on vector database security. Its direct successor, mini-vec2vec (Guy Dar, 2025-2026), replaced the GAN with a simple linear transformation while keeping the attack's effectiveness, making it far cheaper to carry out. OWASP has since codified embedding weaknesses as a standalone risk category (LLM08:2025), and several defenses have emerged (calibrated noise, learned projections) though none is yet recognized as robust.
