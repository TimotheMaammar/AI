# On the Navier–Stokes Millennium Prize Problem

## About

Title : On the Navier–Stokes Millennium Prize Problem

Links : 
- https://openai.com/index/navier-stokes-solution/
- https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf

Company : OpenAI

Date : 08/09/2026

## Synthesis

### Article 

- Navier-Stokes equations describe how fluids move, used for aircraft design, weather forecasting, and blood flow modeling
- The question of whether smooth 3D fluid motion can break down (develop infinite speed in finite time) has been open for about 90 years
- OpenAI states this result resolves the Millennium Prize problem by establishing statement "C" (and "D") of the official Clay formulation
- The proof was produced by an internal OpenAI model described as significantly more capable than GPT-6 Astra, still in training at the time
- The effort started September 1, 2026 after hearing rumors that two Millennium Prize problems had been solved (later traced to Levent Alpoge at Anthropic and NYU professor Tristan Buckmaster)
- OpenAI deployed a multi-agent system: around 10,000 concurrent agents for the Navier-Stokes group, with access to a cached internet snapshot and code execution
- Different agent groups were assigned different variants of the problem (A/B aiming for a proof of regularity, C/D aiming for a disproof via blowup)
- Before tackling Navier-Stokes, the same system surprised researchers by resolving the unforced Euler regularity problem (a simpler limiting case with zero viscosity), using about 100 agents over roughly 50 hours
- Following that Euler result, OpenAI redirected resources from other Millennium Problems entirely onto Navier-Stokes
- The agents reached the Navier-Stokes resolution about 88 hours after launch (Saturday, September 5); Lean formalization and verification took an additional 17 hours via GPT-6 Astra
- Total effort across all attempted problems: 4.9 million messages, about 300 billion output tokens; the Navier-Stokes resolution alone used 2.7 million messages and about 130 billion output tokens
- OpenAI reached out to Alpoge and Buckmaster once they realized the rumor concerned a different result (forced Euler, not Navier-Stokes) and explicitly recognizes priority on that separate work
- OpenAI states it does not intend to claim the Millennium Prize money for this result and frames the announcement as a progress report on AI capability rather than a final achievement

### Paper

**The core problem**

Navier-Stokes equations describe fluid motion (water, air, etc.). It's one of the 7 Millennium Prize Problems (1 million dollars, Clay Institute). The question: can a fluid that starts perfectly smooth suddenly "explode," reaching infinite speed in finite time, while total energy stays finite? Nobody had answered this since 1934.

**What the paper claims to demonstrate**

They construct a concrete example where this happens. A fluid starts at rest, a smooth external force (which turns off after some time) sets it in motion, and its speed becomes infinite at one precise point in space at one precise instant, while total kinetic energy stays bounded the entire time.

**Important nuance not to miss**

The result applies to the "with external force" case (alternative C and D in Fefferman's official problem statement), not the "no force" case, which is the harder and more emblematic version of the Millennium problem. Fefferman had listed 4 possible ways to resolve the problem, and proving blowup with a force is officially one of them. So this is a genuine partial resolution of the official problem, but it is not "explosion with no outside help," which remains open.

**The physical mechanism (in a picture)**

They build a vortex that contracts faster and faster toward a central point, like a sink drain that would shrink infinitely in finite time. The technical problem is that this vortex, on its own, would require an infinite external force to exist, which the theorem forbids. Their trick: they add small, precisely calibrated oscillating ripples that, through their own motion, supply exactly the missing momentum, letting the actual external force stay perfectly smooth right up to the moment of blowup.

**How it is demonstrated**

It is a construction, not an abstract proof. The paper literally builds, step by step, the exact mathematical shape of the fluid (150 pages), adding successive finer corrections to cancel all residual errors, until reaching a mathematical object that satisfies every required property. The method extends prior work (Tao 2016, Buckmaster-Vicol, Cordoba et al.) but pushes the technical difficulty further.
