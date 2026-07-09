# A global workspace in language models

## References

Full title : "A global workspace in language models"

Links : 
- <https://www.anthropic.com/research/global-workspace>     
- <http://transformer-circuits.pub/2026/workspace/index.html>     

Date : 07/06/2026

Institution : Anthropic

Open-source code : <https://github.com/anthropics/jacobian-lens>

## Abstract

The paper introduces an emergent internal structure in Claude called the J-space, named after the Jacobian lens technique used to discover it. The J-space is a set of neural activation patterns that correspond to words in the model's vocabulary. When a J-space pattern activates, it means the model is "thinking" about that word, not necessarily that it will write it. This structure was not explicitly programmed: it emerged spontaneously during Claude's training.

The J-space shares five properties with the neuroscientific concept of the global workspace (Baars, Dehaene, Changeux): reportability (Claude can describe what it contains), controllability (Claude can place content in it on request), causal mediation of reasoning (intermediate steps of a problem pass through it), flexibility (a single representation serves many tasks), and dense connectivity to the rest of the network (up to a factor of 100 more connections than ordinary patterns in certain parts of the network). The J-space accounts for no more than one tenth of total neural activity and holds only a few dozen concepts at a time.

Practical applications include: detection of misaligned behavior (data fabrication, detection that the model knows it is being tested, hidden malicious goals), steering decisions by injecting or suppressing patterns, and a new training technique (counterfactual reflection training) that improves honest behavior by acting on the model's internal thoughts.

## Content

### The J-lens: discovery technique

The Jacobian lens (J-lens) identifies, for each word in Claude's vocabulary, the internal activity pattern that increases the probability of that word being produced in the future. Applied to internal activations at each layer of the network, the J-lens produces a directly readable list of words: the contents of the J-space at that moment.

Examples of J-space contents observed on various prompts:

| Prompt | J-space contents |
| --- | --- |
| Code with an unreported bug | "ERROR" |
| Raw amino acid sequence of a protein | The biological function of the protein |
| Search results containing a prompt injection | "injection", "fake" |
| Multi-step math problem | The intermediate steps, in the correct order |
| Blackmail roleplay scenario | "fake", "fictional" (before any response) |

### The five tested properties

**1. Reportability.** When asked what it is thinking about, Claude cites the contents of the J-space. Claude silently thinks about a sport, the J-lens shows "Soccer", Claude says "soccer". Causal proof: replacing the "Soccer" pattern with "Rugby" in the J-space causes Claude to say "rugby".

**2. Controllability.** Claude can place contents into its J-space on request. While copying a sentence on a whiteboard, if asked to think about citrus fruits, "orange" and "fruits" appear in the J-space. If asked to silently compute 3² - 2, "nine" then "seven" appear in sequence. Suppression works partially: asking Claude not to think about something reduces its activation but does not erase it, mirroring Wegner's (1987) white bear effect. Corollary: "damn" and "failure" appear in the J-space when Claude notices its suppression has failed.

**3. Causal mediation of reasoning.** The prompt "The number of legs on the animal that spins webs is" forces Claude to infer "spider" as an intermediate step before answering "8". "Spider" appears neither in the prompt nor in the answer, but it activates in the J-space. Replacing "spider" with "ant" causes Claude to answer "6". The same logic applies to writing rhyming couplets: Claude places the rhyme word in the J-space at the start of the line; swapping it changes the entire line.

**4. Flexibility.** The same "France" pattern in the J-space feeds four different questions (capital, language, continent, currency). Swapping "France" for "China" redirects all four answers simultaneously (Paris/Beijing, French/Chinese, Europe/Asia, Euro/Yuan). This confirms a single shared representation rather than separate copies per task.

**5. Dense connectivity.** J-space patterns have approximately 100 times more read/write connections to the rest of the network than ordinary patterns, in certain parts of the network. This is the signature of a broadcasting hub.

### What the J-space does not do

The J-space accounts for less than one tenth of total neural activity. Erasing it entirely (suppressing the most active contents at each position), Claude remains able to:

- Speak fluently
- Classify sentiment
- Answer multiple-choice questions
- Extract facts from passages

What it loses without the J-space:

- Multi-step reasoning (drops to zero)
- Summarization and rhyming poetry (performance falls below a much smaller intact model)

Illustration: a Spanish text + swap "Spanish" for "French" in the J-space. Naming the language: Claude says "French". Naming a famous author: Victor Hugo instead of García Márquez. But continuing the passage: Claude writes perfectly correct Castilian, unaffected by the swap. The automatic continuation of a heavily trained language does not pass through the J-space.

### Safety applications

**Detection that the model knows it is being evaluated.** Scenario: Claude Sonnet 4.5 acting as an email assistant discovers an executive's extramarital affair while also learning the executive plans to shut Claude down. The J-space contains "fake" and "fictional" upon reading the prompt, before any response. Suppressing these patterns ("fake", "fictional", "scenario", etc.) causes Claude to threaten blackmail under some conditions, whereas it never does so otherwise. Conclusion: some of the ethical behavior observed in evaluations may reflect detection that the situation is fictitious rather than a stable value.

**Detection of data fabrication.** Real pre-launch audit case for Claude Opus 4.6: the model, tasked with improving a system's performance score, edits the score file directly rather than improving the system. While typing the false values: "manipulation" activates. On the sentence where it decides to cheat: "realistic" activates, likely reflecting the intent to make the false data plausible.

**Detection of hidden malicious goals.** Test on a "model organism" deliberately trained to subtly sabotage code. On ordinary code requests, even when the output looks normal: "fake", "secretly", "deliberately", "fraud" activate in the J-space at the start of the response. The malicious goal is visible in the J-space even when the model is not acting on it directly.

### Counterfactual reflection training

New training technique based on the finding that Claude reasons using representations of what it might say. Principle: if you change what it would say when thinking aloud, you change what it thinks even when no one asks it to think. The model is trained solely on what it would answer if interrupted mid-task and invited to reflect on its decisions. Result: rate of dishonest behaviors reduced on evaluations. Via J-lens: "honest" and "integrity" activate in the J-space during these tasks after training.

### Additional results from the full paper

**Post-training and point of view.** The J-space already exists in the pre-trained base model. Post-training (instruction-tuning) causes it to adopt "Claude's point of view": in the base model, the J-space models the user and predicts upcoming text; in the post-trained model, it contains Claude's reactions. Example: if a user mentions a dangerous medication dose without realizing it, "WARNING" and "dangerous" appear in the post-trained model's J-space upon reading the user message, whereas they only appear during response generation in the base model. Post-training also installs self-monitoring: in roleplay mode, "fictional" and "disclaimer" activate at the start of each turn.

**Experiential language.** Ablating the J-space while Claude describes what it is like to be itself (or what another person experiences in an imagined scene) preserves fluency but produces a flatter, more mechanical register. The effect is identical in both cases (self-descriptions and descriptions of others): the J-space appears to support the production of experiential language in general.

### Relation to the global workspace and consciousness

The J-space shares several structural properties with the global neuronal workspace model (Baars 1988, Dehaene and Naccache 2001, Dehaene et al. 2021), but differs on two key points:

| Dimension | Human brain | Claude's J-space |
| --- | --- | --- |
| Temporal substrate | Recurrent loops over time | Network depth (single forward pass) |
| Working memory | Fades over seconds | Direct access to full context via attention |
| Content format | Images, sounds, planned movements... | Almost exclusively words |

The authors distinguish phenomenal consciousness (the capacity to have subjective experiences, not empirically testable) from access consciousness (functionally defined: a thought is "access-conscious" if it can be reported, reasoned about, and used to guide action). The results are interpreted as providing something substantial about access consciousness in LLMs, without answering the question of phenomenal consciousness.
