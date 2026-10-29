# Local Smoothing, Kakeya and the Exponential Time Hypothesis

## About

Title : Working with academic communities to build scientific understanding

Links : 
- https://openai.com/index/building-scientific-understanding-with-academic-communities/
- https://github.com/openai/math/blob/main/preprints/Local-smoothing-for-the-Euclidean-wave-equation-October-25-2026/paper.pdf
- https://github.com/openai/math/blob/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf


Date : 26/10/2026

## Synthesis

### Article

- OpenAI announces three results from its internal models: local smoothing and Kakeya (analysis), the Exponential Time Hypothesis is false (complexity), and existence of 4D Yang-Mills and QCD (physics, no public manuscript yet)
- The manuscripts are presented as "raw research data", handed to external expert groups ("shepherds") who explain them to the community
- Math: AI output released directly (obtained 18/10/2026, Lean-formalized the next day)
- CS: group led by Impagliazzo, Paturi and Williams, proof and Lean formalization public (found 16/10/2026, Lean 17/10/2026), conference on the implications funded by OpenAI
- Physics: group led by David Gross, AI artifacts withheld while they write it up
- OpenAI claims no academic credit, no NDAs, and gives $5 million to the Simons Foundation for programs on understanding AI-produced results

### Paper 1: Local smoothing for the wave equation

**The problem**

When a wave focuses (like ripples converging to a point), its amplitude can spike far above its starting size. Local smoothing (Sogge, 1991) says these spikes are very short-lived: averaged over time, the wave is much tamer than the worst instant. Proved before only in 2D (Guth-Wang-Zhang, 2019) and partially in higher dimensions.

**What is proved**

The conjecture in every dimension, with the best possible amount of smoothing. The key step is a single estimate at the critical exponent, which loses only a logarithm.

**How, in short**

- The authors build a conserved quantity from the wave itself, a kind of "flow" that tracks the waves heading in each direction
- They then solve an auxiliary PDE (a determinant equation of Monge-Ampère type) whose solution measures how concentrated the wave can get
- A comparison argument turns this into the estimate, the log loss coming from how solutions of the Laplace equation behave in the plane

**What follows**

| Consequence | In plain terms |
|---|---|
| Kakeya conjecture | A set containing a unit segment in every direction has full dimension n (needle-turning sets cannot be "thin") |
| Nikodym | Same idea for segments through a point |
| Bochner-Riesz | Sharp convergence of Fourier series partial sums in all dimensions |
| Stein square function, Fourier restriction, Schrödinger smoothing | Sharp ranges across the conjectured interior |

A separate manuscript (24/09/2026) treats the 3D critical case alone.

### Paper 2: The Exponential Time Hypothesis is false

**The problem**

ETH says that solving 3-SAT (can a logical formula be satisfied?) with n variables essentially requires trying exponentially many assignments, about 2^n. It underlies hundreds of "conditional hardness" results across graphs, databases and geometry.

**What is proved**

A deterministic algorithm that does better than any fixed exponential: it runs in time 2^(n / (log n)^(1/2)) up to lower-order terms, uses little memory, and even counts the solutions exactly, not just decides if one exists. That is subexponential, so ETH is false.

**How, in short**

- Splitting the variables into independent blocks would make counting cheap, but real formulas link the blocks
- The trick: rewrite the counting problem as a polynomial, deform it so that blocks interact only through a small number of shared "measurements", count block by block, then recover the true answer by interpolation
- Reductions then extend this from restricted formulas to arbitrary ones

**What follows**

- Subexponential counting of independent sets, graph colorings and perfect matchings
- Accurate subexponential approximation of Max-k-SAT
- A superlinear circuit lower bound for a class tied to NP

### Reading notes

- Both results come with Lean proofs but have not yet been examined by the shepherd groups
- This fiche rests on the abstracts, introductions and technique overviews, not a line-by-line check
