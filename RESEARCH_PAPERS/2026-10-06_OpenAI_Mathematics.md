# 722 research-level math manuscripts from an internal OpenAI model

## About

Title : Sharing AI progress in mathematics

Links : 
- <https://openai.com/index/sharing-ai-progress-in-mathematics/>
- <https://github.com/openai/math>

Date : 06/10/2026

## Synthesis

OpenAI released a catalogue of 722 mathematical manuscripts organized into 372 families, produced by an unreleased internal model. A family groups a principal result with companion arguments, consequences or alternative proofs, and each family is classified by discipline. The evaluation on open research problems was expanded after the model's existing math evaluations saturated.

**Production procedure**

- ~4,000 problems posed to the model over the evaluation
- ~3 hours of ChatGPT Pro thinking compute per result on average
- Output aggregated into families and manuscripts, then filtered on an "appropriate level of significance"
- Exceptions to the fixed procedure: the zero-free region for the Riemann zeta function and the Hodge conjecture for CM abelian varieties; the Re(s) > 11/12 writeup was human-edited for readability
- Abridged reasoning summaries released for 10 families: 007 (two-point correlations of multiplicative functions), 017 (irrationality exponent of pi), 087 (Mahler conjectures), 102 (SDP-threshold NP-hardness), 159 (quasipolynomial bounds for arithmetic progressions), 197 (Kaplansky direct-finiteness, characteristic two), 221 (Mézard-Parisi formula), 271 (quantum Heisenberg ferromagnet), 287 (free group factors), 362 (relativistic Vlasov-Maxwell)

**Families by discipline**

| Discipline | Families |
|---|---|
| Theoretical computer science | 40 |
| Combinatorics | 37 |
| Algebraic and complex geometry | 36 |
| Number theory | 31 |
| Probability and statistical mechanics | 29 |
| Differential geometry | 29 |
| Mathematical physics | 25 |
| Operator algebras | 19 |
| Algebra | 18 |
| Topology | 18 |
| Real and complex analysis | 16 |
| PDE | 16 |
| Convex and metric geometry | 15 |
| Group theory | 14 |
| Dynamical systems and ergodic theory | 12 |
| Functional analysis | 11 |
| Mathematical logic | 6 |

**Headline results by field (as stated in the catalogue)**

| Field | Results |
|---|---|
| Number theory | Zero-free half-plane Re s > 7/8 for zeta (003, alternate proof at 11/12), irrationality of Catalan's constant (005), irrationality exponent of pi equal to 2 (017), Hilbert's tenth problem over Q resolved negatively (004), Artin's primitive root conjecture for every base (029), Gaussian moat (028) |
| Algebraic geometry | BSD full formula for Selmer corank 0 or 1 (002), with Goldfeld (006) giving full BSD for a density-one set of twists; rational Hodge for CM abelian varieties and products of K3 (032); irrational cubic fourfolds (054) |
| Theoretical CS | Unique Games Conjecture (102), 2-to-1 Games (105), L = RL = BPL (103), matrix multiplication exponent ω ≤ 9/4 (107), permanent vs determinant bound Ω(m^3) (108), Subset Sum in O(2^0.49n) (138), exact matching in almost-linear time (120), factor-2 shortest common superstring (128), exact quantum factoring over a fixed finite gate set (279) |
| Combinatorics and geometry | Borsuk's conjecture fails in dimension 9 (156), every 5-coloring of the plane has a monochromatic unit pair (158), counterexamples to Sidorenko (161) and Hadwiger (157), Seymour second neighborhood (173), combinatorial invariance of Kazhdan-Lusztig (168), universal optimality of the triangular lattice (090), Kakeya in dimensions 3 and 4 (074), Falconer (073) |
| Algebra, groups, operator algebras | Counterexamples to Kaplansky's zero-divisor conjecture (196) and Kurosh's problem (201), Saxl (205), Cannon (246), Thompson's group F nonamenable (248), all nonabelian free group factors isomorphic (287), Kadison's similarity conjecture (288), counterexample to hyperinvariant subspace problem (293), Baum-Connes and Kadison-Kaplansky counterexamples (285) |
| Probability and physics | Benjamini-Schramm pc < pu (214), Mézard-Parisi formula (221), Bloch's T^(3/2) law (271), spin-one Haldane gap (268), N(6) = 3 mutually unbiased bases in dimension 6 (266), optimal logarithmic mixing of the Thorp shuffle (238) |
| Topology, differential geometry, PDE | Hilbert-Smith conjecture in every dimension (304), Kervaire invariant at the prime 3 (309), Grothendieck homotopy hypothesis (312), Yau's uniformization conjecture (338), counterexample to nearby Lagrangian conjecture (340), De Giorgi's conjecture in dimension 8 (375), hot spots conjecture for simply connected planar domains (369), universal computation in forced Navier-Stokes flows (376) |

**Verification status**

- `lean/formalization.yaml` (v0.4) lists 162 formalized manuscripts out of 722, with a Lean library and Comparator instructions in the repository
- Formalizations are being added as they are obtained; individual manuscripts ship PDFs, sources and BibTeX
- Results sit at different stages of verification. OpenAI's own caveat: "Some of the unformalized results could have issues", with fixes promised quickly and corrections recorded as new versions

Figures above come from the repository README, overview and manuscript map (OpenAI's own descriptions); the proofs themselves were not independently checked here. With ~3 compute-hours per result and a significance filter applied downstream, the bottleneck in this release shifts from generating candidate proofs to verifying them.
