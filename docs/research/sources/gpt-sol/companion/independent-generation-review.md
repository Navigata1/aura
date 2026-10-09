# Independent adversarial review of generation research

Reviewed: 2026-10-08. Reviewer: separate research agent from the author of `generation-research.md`. Scope: primary-source refutation attempts for commercial model access, an unavailable-model claim, an unresolved release, and the strongest Suno parity counterevidence. This is a documentary review, not local model execution, an audio listening test, or legal advice.

## Result

The six targeted conclusions survive independent checking. No material reversal was found. Several descriptions require precise scope so that the eventual master plan neither excludes a permitted individual workflow nor treats an app/model license as universal commercial clearance.

| Claim under review | Status | What the independent source actually supports |
|---|---|---|
| MiniMax-Music3 permits commercial use conditionally | **Confirmed; scope clarified** | Its custom community license permits covered commercial uses with attribution, safeguards and usage conditions; a revenue threshold triggers prior written authorization. Apache/MIT dependencies do not replace this license. |
| YuE2 needs separate company commercial permission, despite individual monetized outputs being allowed | **Confirmed; scope clarified** | The additional permission expressly allows individual creators to sell/license/monetize outputs, while excluding companies' commercial model use from that waiver. |
| MuLaCover weights and generated outputs carry noncommercial restrictions | **Confirmed; distinguish mechanisms** | The weights use CC BY-NC plus conditions. A separate output-use condition restricts commercial use; this is not simply the CC license automatically attaching to every output. |
| Official HeartMuLa 7B parity claim concerns an unavailable internal model | **Confirmed for supported public release** | The official README describes an internal 7B model and separately marks its public release pending. Public 3B availability does not substantiate the 7B quality claim. |
| Current canonical SongGeneration access/license remains unresolved | **Confirmed as an access limitation** | Independent unauthenticated requests failed for the referenced Tencent repo/model; a reachable third-party card declares an unknown license. Why access fails is unverified. |
| YuE2's own paper provides counterevidence to claiming overall Suno v6 parity | **Confirmed; study-qualified** | Expert listeners prefer Suno v6 overall to YuE2 best-of-eight in that comparison. This does not establish a universal model ranking or every-task superiority. |

## 1. MiniMax-Music3: commercial, but not an unconditional permissive release

I checked the controlling model license rather than the licenses of the underlying components. It covers the distributed weights and related materials. Commercial products/services must prominently display MiniMax-Music3. If aggregate annual revenue from the covered products/services across the user and affiliates exceeds US$20 million, prior written authorization is required. This is a covered-revenue threshold, not a blanket test against all unrelated company revenue. Third-party generation services must implement, maintain, test and periodically review safeguards; acceptable-use conditions also apply. Consequently, it remains a plausible commercial candidate, with a license compliance gate before implementation. [Official MiniMax-Music3 license](https://huggingface.co/MiniMaxAI/MiniMax-Music3/blob/main/LICENSE).

Refutation attempted: permissive dependency licenses do not establish unrestricted licensing of the complete released model.

## 2. YuE2: individual monetization is expressly permitted

The official model license lists YuE2-3B and the YuE2 VAE variants under CC BY-NC 4.0, then grants an additional permission dated 2026-09-16. Individuals, personal users, content creators and musicians acting in an individual capacity may generate, publish, distribute, sell, license and otherwise monetize outputs without fees or royalties. Companies do not receive commercial model-use permission from this individual waiver; the document provides a contact for separate authorization. Academic noncommercial permission does not grant institutional commercial rights. [Official YuE model license](https://github.com/multimodal-art-projection/YuE/blob/main/MODEL_LICENSE).

Refutation attempted: both a blanket monetization ban and automatic company permission overstate the terms. Individual output licensing differs from company model operation. Record the actual operator and purpose; do not interchange the user with the user's LLC.

## 3. MuLaCover: the output restriction is separately stated

The controlling model document covers official weights and derived versions, including fine-tuned, converted, quantized and merged versions. It states CC BY-NC 4.0 for weights. Its separate output section restricts commercial use without written permission, including generated audio, music, MIDI, tokens and latents. The document explicitly frames this as an additional access/use condition, bounded by the rights or contractual authority the licensor actually has. [Official MuLaCover model license](https://github.com/HeartMuLa/MuLaCover/blob/main/MODEL_LICENSE).

The project licensing guide confirms the distinction between Apache code and restricted models/outputs. [Official MuLaCover licensing guide](https://github.com/HeartMuLa/MuLaCover/blob/main/LICENSING.md).

Refutation attempted: Apache code does not establish model/output clearance. The published requirement is verified; judicial enforceability, generated-output copyright and third-party rights are not. Obtain written terms before selecting this for a commercial default route.

## 4. HeartMuLa: test the released 3B, not the internal 7B claim

The official repository attributes comparable-to-Suno quality to its latest **internal** 7B model. It lists public 7B release as pending, and a CLI comment explicitly says 7B has not been released even though the parameter appears in an example. The available 3B release must be evaluated on its own. [Official HeartMuLa heartlib repository](https://github.com/HeartMuLa/heartlib).

Refutation attempted: whether a `--version 7B` option is proof of downloadable supported 7B weights. It is not. This supports a claim about the official public release, not an exhaustive assertion that no unofficial mirror exists anywhere. A mirror would need provenance, identical checkpoint evidence and licensing checks before being treated as equivalent.

## 5. SongGeneration: access is unresolved, not proven impossible

Independent unauthenticated checks on 2026-10-08 returned:

| Endpoint | Observed result |
|---|---|
| [GitHub repository API](https://api.github.com/repos/tencent-ailab/SongGeneration) | HTTP 404 |
| [Referenced Tencent GitHub repository](https://github.com/tencent-ailab/SongGeneration) | HTTP 404 |
| [Referenced Tencent model page](https://huggingface.co/tencent/SongGeneration) | HTTP 401 |
| [Reachable third-party SongGeneration-v2-large card source](https://huggingface.co/lglg666/SongGeneration-v2-large/raw/main/README.md) | HTTP 200; only metadata declaring `license: unknown` |

These results confirm the report's current access/license limitation. A 404 or 401 does not distinguish deletion, renaming, private/gated access, moderation or authentication policy. A reachable mirror with unknown license is not canonical clearance. Do not call the model discontinued or commercially permitted from these results. Canonical publisher access and the applicable checkpoint license remain required evidence.

## 6. The strongest quality counterevidence comes from YuE2's own paper

In the paper's expert comparison, YuE2 best-of-eight receives 57.3% overall preference against Suno v4.5's 30.5%; the Suno v5 comparison is approximately balanced. Against Suno v6, however, **Suno v6 receives 59.3% overall preference and YuE2 best-of-eight 31.6%**, with ties retained in the denominator. The pooled audio-quality result across six proprietary comparators is not a Suno v6-specific overall win. [YuE2 paper, expert listening results and protocol](https://arxiv.org/html/2609.33757v1).

The official benchmark notes describe two-candidate selection generally, while YuE2 best-of-eight selects from eight with quality and pronunciation criteria. This is not a matched-compute, single-take benchmark; the benchmark also used the legacy VAE rather than the current default listening VAE. [Official YuE2 benchmark documentation](https://github.com/multimodal-art-projection/YuE/blob/main/docs/benchmarks.md).

Refutation attempted: whether headline leaderboard wins support a blanket claim of Suno v6 parity on the user's hardware. They do not. These are developer-reported study results, with defined samples and selection budgets. They warrant a serious local audition, not a guaranteed outcome. A small numeric leaderboard lead should not be promoted to a statistically established advantage without the corresponding inference.

## Consequences for the master plan

1. Keep MiniMax-Music3 as a commercial candidate with documented attribution, safeguards and threshold checks; measure accepted-output quality and cost locally.
2. Treat YuE2 as two distinct rights lanes: permitted individual creation, and company commercial model operation requiring separate clearance. Record the entity rather than guessing it.
3. Use MuLaCover for appropriately permitted research until written commercial terms are obtained. Do not infer output clearance from Apache source code.
4. Evaluate the publicly released HeartMuLa 3B only; quarantine internal 7B marketing claims from expected deliverables.
5. Keep SongGeneration in discovery until canonical access and terms can be verified.
6. Define parity by blind listening, arrangement and editing fidelity, voice consistency, accepted output rate, and measured local latency. Retain Suno v6 as a benchmark reference; the user’s imagined v6.5 remains an aspirational specification.

## Evidence limits

The review inspected the cited primary documents and independently checked the four SongGeneration endpoints. It did not download checkpoints, run inference, listen to newly generated samples, authenticate to gated releases, contact licensors, or modify the original generation research. Publisher benchmark claims remain attributed claims. Web documents can change; pin their versions and retain the selected checkpoint's exact terms during the build gate.
