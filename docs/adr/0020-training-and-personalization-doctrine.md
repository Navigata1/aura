# No training from scratch; personalization starts as non-ML taste memory, and adapters wait for the harness and owned data

Status: accepted (2026-10-09). From D-20.

Every source rules out foundation training. ACE v1 took about 46K A100-hours; v1.5's compute is not stated.
MTG-Jamendo is about 70% non-commercial with no CC0 tracks and is now limited to non-commercial research; FMA is "meant
for research purposes". Suno's terms forbid using its output to train other models, and ElevenLabs' policy forbids
using its renders as ML input. ACE LoRA memory needs are CONTESTED (12 GB against 16–20 GB), and a Mac MPS NaN report
is open.

**Decision.**

- **No foundation training from scratch.**
- Personalization begins as a **non-ML taste memory**: preferences, keepers and verdict reasons (v2).
- **Adapters** (ACE LoRA or LoKr; plan for 16–20 GB; Mac MPS unproven) come only after the listening harness exists,
  and only on data Jon owns or has consent for, with a license record per track. They run in the research lane until a
  preregistered benchmark promotes them.
- **MTG-Jamendo and FMA are excluded** for anything shareable. **Suno outputs and ElevenLabs renders are never training
  data.**
- **Preference tuning (DPO)** runs only with held-out human preference and an evaluator separate from the reward.
- Escalation follows a cost-bounded ladder and stops as soon as the harness says the gap is closed: post-chain, then
  selection, then adapters, then preference tuning, then continued fine-tuning.

**Why.** Scratch training is unaffordable and unnecessary (A28, C45). Most public music data is non-commercial (C36).
Automatic rewards get hacked (X-14). Personalization only makes sense after selection and evaluation exist (A32).

## Consequences

v1 has no training job type. The codec ceiling study (ADR-0019) comes before any training claim.

**Reverse if:** nothing reverses the doctrine. Adapter timing moves with the harness.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §1 A28, A32; §2 C7, C36, C45; §4.8; §5 (Kimi 1);
§6 D-20. [evidence-register.json](../research/evidence-register.json) V-ace-7, V-cost-5, V-qe-6, V-qe-7, X-14, X-43.
[feature-inventory.md](../research/feature-inventory.md) K1–K5.
