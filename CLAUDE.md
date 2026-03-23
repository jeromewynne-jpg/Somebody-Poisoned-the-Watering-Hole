# ControlArena Hackathon

## Project

**Title**: Relating and Integrating AI Control and Agent Security

**Aim**: Write a 4-page NeurIPS workshop paper (with Apart Research) presenting a unified threat model that subsumes AI control and agent security.

**Thesis**: AI control and agent security locate the adversary differently (the agent vs. an external actor), but an operator in practice may face both. The unified threat model is the worst-case safety scenario. It reveals new risks where an adversarial agent and an external adversary coordinate against the operator.

**Contributions**:
1. Unified threat model subsuming control and agent security as special cases
2. Empirical data on hallucinated-URL predictability (Schelling-point mechanism)
3. Proof-of-concept Schelling-URL attack in ControlArena (LinuxArena task)

**Key framing decisions**:
- The operator is the explicit subject in both problem formulations
- Control: operator's adversary is the agent; a control protocol mediates access to the operator's system
- Agent security: operator's adversary is an external actor who exploits the agent across its lifecycle; agent is benign but exploitable
- "Operator's system" = the operator's assets (tools, data, infrastructure). External actors are outside this.
- "Control protocol" is used broadly (any procedure mediating agent access), not restricted to Greenblatt et al.'s three-component formulation. Footnote notes this divergence.
- The unified threat model is motivated as a worst-case safety scenario
- Use "I" not "we" (single author)
- Tone is direct and precise, not promotional

## Key references
- Greenblatt et al. (2024) — AI control (original paper)
- Deng et al. (2025) — agent security survey (ACM Computing Surveys)
- Dziemian et al. (2026) — indirect prompt injection competition
- Debenedetti et al. (2024) — AgentDojo (ported to ControlArena)
- OpenAI (2026) — monitoring coding agents for misalignment
- Anthropic (2026) — Claude Opus 4.6 system card (Sections 5.2 and 6)
- Greenblatt (2025) — overview of areas of control work (Redwood blog)
- Clymer (2025) — extending control evaluations to non-scheming threats

## Compiling the paper

```sh
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
cd submission
pdflatex -interaction=nonstopmode neurips_2026.tex
bibtex neurips_2026
pdflatex -interaction=nonstopmode neurips_2026.tex
pdflatex -interaction=nonstopmode neurips_2026.tex
```

Run all four steps when references change. For text-only edits, a single `pdflatex` pass is sufficient.

Font generation and `tlmgr install` require sandbox disabled.

## Figures

SVG source in `submission/figures/`. Convert to PDF before compiling:
```sh
rsvg-convert -f pdf -o figures/threat-models.pdf figures/threat-models.svg
```
This also requires sandbox disabled.

## Workflow
- Recompile after every edit the user wants to see
- Paragraph stubs are in [square brackets] describing purpose
- Iterate on stubs before writing prose
- Jerome prefers short, tightened text. Propose variations when drafting.
