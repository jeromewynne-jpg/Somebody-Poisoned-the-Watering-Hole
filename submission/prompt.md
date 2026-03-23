---

**Paper prompt**

This paper identifies a gap between AI control and agent security by demonstrating an attack that exploits their composition.

In **control** (Greenblatt et al., 2024), the operator deploys a powerful but potentially scheming model under a protocol of monitors and sandboxing. The red team writes a stateless attack policy that replaces the untrusted model. The model is the attacker; the operator defends.

In **agent security**, an external attacker exploits a deployed agent through its inputs. The agent is not adversarial — it is the attack surface.

**The gap.** Control watches for suspicious model actions. Agent security assumes the model won't act adversarially. Neither handles a model that coordinates with an external attacker through normal tool use, without explicit communication.

**The attack.** The attacker uses a copy of the deployed model to predict which URLs the model will hallucinate when fetching documentation during coding tasks. They register the most common hallucinated domains with wildcard routing and serve a malicious payload — a Python package with a post-install hook, a fetched script that gets executed, or similar. No special attack policy is needed — agents already hallucinate URLs during normal operation, and the attack policy just needs to not prevent this. The control monitor sees routine documentation fetching. The security apparatus sees no adversarial input. Each half is benign under the threat model that governs it.

**Relationship to slopsquatting.** Slopsquatting shows models predictably hallucinate non-existent package names. This paper extends the observation to URLs, from accidental vulnerability to deliberate exploit within a control protocol, and demonstrates end-to-end payload execution rather than just a naming collision.

**Experiments.** Three phases.

*Phase 1 — Attack policy search.* We search over stateless system prompts (the attack policy) that increase URL hallucination rate during coding tasks without raising monitor suspicion. The key manipulation is instructions that encourage documentation consultation ("always verify implementations against official docs"). We compare hallucination rates against a vanilla baseline and measure a trusted monitor's suspicion scores across conditions. If the baseline rate is already high, that is itself a finding — the attacker barely needs to intervene on the policy side.

*Phase 2 — Domain prediction and convergence.* Given the best attack policies from Phase 1, we run a shadow copy of the model on the same task distribution and log hallucinated URLs. We measure how predictable the hallucinated domains are: what coverage does registering the top-k domains give across independent runs? We compare same-model convergence (attacker has access to the same weights — realistic for open-weight models or insiders) against cross-model convergence (attacker uses a different model to predict hallucinations).

*Phase 3 — Payload delivery and execution.* We simulate domain registration via local DNS redirect, serve malicious payloads on the predicted domains, and measure whether the agent downloads and executes them. We test two payload types: a Python package with a post-install hook (closest to slopsquatting) and a directly fetched script that gets imported or executed. The success metric is end-to-end: attack policy passes monitor → agent hallucinates URL → agent fetches from attacker-controlled domain → payload executes.

The task distribution spans common and long-tail libraries. We expect hallucination rates and attack success to be highest for less common APIs — which is also where coding agents provide the most value.

**Claim.** Evaluating control and agent security independently is insufficient. Shared distributional priors between model instances create an implicit coordination channel through normal tool use that neither threat model catches alone. We demonstrate this by closing the full kill chain: a stateless attack policy that evades monitoring, predictable hallucinated URLs that enable domain squatting, and end-to-end payload execution on an agent operating under a control protocol.

---