# C04 standards review: PR #136 (issue #132)

- **Head:** `1e0e1254a4b09faa5b1e0532ccfbf09f0a45dd5e` (`ticket/C04-pattern-anchoring`, one commit)
- **Base:** `dee28e2fd2b7a79ca2773e639a4a714af5c356b8` (the PR's integration base and the merge-base of head and base)
- **Diff:** `git diff dee28e2fd2b7a79ca2773e639a4a714af5c356b8...1e0e1254a4b09faa5b1e0532ccfbf09f0a45dd5e`
  (2 files, +78/-3: `scripts/spec/jsonschema_subset.py`, `scripts/spec/validate.py`). Saved as `C04-review-pr136.diff`
  (sha256 `c1e1552c9229e69245b4cbcc71f24e136de740eef9a18794c13bbf901e064a50`). `git patch-id --stable`:
  `332880565f3263269b30caeceaf4d0f1c01ee79b`.
- **Reviewer:** independent. I did not write or edit the implementation. Reviewed 2026-11-08 (UTC) in the disposable
  copy `/Volumes/STUDIO/scratch/review-C04-1e0e125/` (a clone at head, a worktree at base, and `git archive` copies
  for every mutant and plant).
- **Method:** `.claude/skills/code-review/SKILL.md` from the base tree. The Standards axis ran as its own pass, a
  sub-agent given only the diff, the standards sources and the smell baseline. Appendix A gives its report. I
  re-checked every claim it made with the probes below.

## Verdict: pass

There is no blocking finding. The `$` translation is exact for ECMA-262 end anchors:

- **Edge cases.** Every edge case agrees with V8 under no flag and under `u`.
- **Shipped regexes.** It agrees with V8 on all 512,024 pairs of shipped regex and contract value, where the base checker disagreed on 28,687.
- **Loosening.** It loosens no shipped pattern and no shipped schema.
- **Refusal.** The checker still refuses unsupported keywords.
- **Self-tests.** The self-tests are not vacuous. Removing the translation, two of the implementer's mutants and five of my own all fail the gate, and the sweep's guard fires.

Eight non-blocking findings follow: four on wording or docstrings, two latent self-test defects, one confirmed follow-up and some low-weight smells. A merge note closes the review.

## Non-blocking findings

**S-N1. Docstrings and PR text overclaim the class-boundary refusal.**
- **Where.** `validate.py:7-9` says a character class "that ECMA-262 and Python end in different places is refused". The same claim appears in `anchor_self_tests` (`validate.py:184-187`), the commit message and the PR body ("A pattern that Python reads differently, such as `[]$]` … the meta-check refuses it").
- **What actually happens.** The refusal happens only when a `$` falls in the stretch that Python still reads as inside the class.
- **Counterexamples** (R05, R16):
  - `^[]a]$` and `^[]]$` accept `"]"`.
  - `^[^]a]$` and `^[^]]$` accept `"x"` and `"a"`.
  - All four compile and run with Python's reading. Without flags, ECMA-262 reads `[]` as an empty class and `[^]` as any character, so the patterns match different strings: `^[]a]$` and `^[]]$` match nothing, and `^[^]a]$` matches `"xa]"`. With `u`, all four are SyntaxErrors.
- **Impact.** Behaviour is unchanged from base, and no shipped schema uses `[]` or `[^]`.
- **Fix.** Narrow the wording ("…is refused when a `$` falls inside it, such as `[]$]`"), or refuse `[]` and `[^]` outright (see S-N7).

**S-N2. `check_all` never compiles `patternProperties` keys.**
- **The claim.** The `_ecma_anchors` docstring (`jsonschema_subset.py:71-72`) says "`check_all` refuses it". That holds for `pattern` only: `_check` compiles `pattern` at lines 126-130 and only recurses into the values of `patternProperties` at lines 131-133.
- **What happens** (R10), with `[]$]` planted into the schemas:
  - As a `pattern` in an unused `$defs` entry, head refuses it with `bad pattern (bad escape \Z …)`.
  - As a `patternProperties` key in an unused `$defs` entry, the gate passes.
  - As a key on a schema that fixtures exercise, the gate dies with an uncaught `re.error: bad escape \Z` traceback. It exits 1, so it fails closed, but it is a crash rather than a refusal.
- **Impact.** The gap is pre-existing: base never compiled keys either. The only shipped key is `^[A-Z]$`.
- **Fix.** Compile each `patternProperties` key through `self._pattern` in `_check`, report `bad pattern`, and add a self-test with a `[]$]` key.

**S-N3. The sweep's oracle is wrong for a pattern whose body can match a newline (latent).**
- **The assumption.** `anchor_self_tests` (`validate.py:190-199`) requires every anchored pattern that accepts `"verse"` or `"id"` to reject that seed plus `"\n"`. ECMA-262 does not require this when the body can consume the newline.
- **Demonstration** (R11). An unused `$defs` entry `^[^/]+$` is a plausible future path-segment pattern. It makes the gate fail twice with "ECMA-262 $ matches only at the end of input", yet V8 accepts `"verse\n"` for it with no flag and with `u`.
- **Impact.** The failure is fail-closed: a false failure, never a false pass. No shipped regex triggers it, at base (58) or at integration `910910a` (60, see R14). It would still block a correct future schema behind a misleading ECMA claim.
- **Fix.** Skip a pattern whose body, between `^` and `$`, fully matches the planted value, or plant only values the body cannot consume.

**S-N4. The sweep filter skips a real anchor after an escaped backslash (latent).**
- **The defect.** The filter `not p.endswith("\\$")` (`validate.py:188-189`) also drops a pattern ending in an escaped backslash followed by a real anchor, such as `^a\\$`.
- **Impact.** No shipped pattern ends that way (R05 B), and the targeted case `^a\\$` still covers the translation itself.

**S-N5. Wording of what the self-test exercises.**
- **The claim.** `validate.py:7-8` says "every anchored contract pattern rejects a planted trailing newline". That reads as a description of what the self-test exercises.
- **Actual coverage.**
  - The sweep reaches 19 of the 58 shipped regexes.
  - The targeted cases add two more: `$defs/id` via `melody_id`, and the `^[A-Z]$` key.
  - That leaves 37 regexes that no self-test exercises.
- **The property itself holds for all 58** (R05 B). At head, each one rejects every contract value it accepts once `"\n"` is appended: 28,687 pairs, all of which base accepted.
- **Fix.** Say "every anchored contract pattern that accepts the planted value", as `anchor_self_tests`' own docstring already does.

**S-N6. Docstring wording on flags.**
- **The issue.** `jsonschema_subset.py:8` says patterns are "ECMA-262 regular expressions with no flags". JSON Schema 2020-12 core §6.4 recommends building patterns with the `u` flag (checked against the published spec).
- **Impact.** The anchor rule is unaffected, because only `m` changes `$`. Head agrees with V8 under both no flag and `u` on all 512,024 pairs (R05 C). This is wording only: "without the `m` flag".

**S-N7. Follow-up candidate: other dialect differences are neither bridged nor refused.** These are confirmed, pre-existing and outside #132.
- **`\s` differs by code point** (R05 D, every code point checked):
  - Python's `\s` includes U+001C–U+001F and U+0085, which ECMA-262's does not.
  - Python's `\s` lacks U+FEFF, which ECMA-262's includes.
  - So the shipped `uri` pattern `^https://[^\s]+$` accepts `"https://a﻿"`, which ECMA-262 rejects, and rejects `"https://a\x1c"` and `"https://a\x85"`, which ECMA-262 accepts. This confirms the implementer's report.
- **Other differences:**
  - `[]` and `[^]` classes (S-N1).
  - An authored `\Z`: without flags ECMA-262 reads it as the letter Z, and with `u` it is a SyntaxError.
  - Python-only syntax compiles untouched. Examples are `(?#…)` comments and inline flags such as `(?m)`.
  - The class scan runs to the end of an unterminated `[`, so `(?#[)^a$` hides its `$` from the translator and accepts `"a\n"`, exactly as base did.
- **Impact.** None of these appears in a shipped schema, at base or at `910910a`.
- **Suggestion.** One contract-fix that makes `check_all` refuse (or bridge) `\s`/`\S`, `[]`, `[^]`, `\Z` and the `(?` forms ECMA-262 lacks.

**S-N8. Judgement calls** (baseline smells, low weight):
- **Duplicated Code.** The bare-`SchemaSet` probe set-up (`__new__` plus writes to private attributes, `validate.py:172-174` and `200-201`) is repeated. One small helper would serve both sites.
- **Mysterious Name.** `_ecma_anchors` returns a rewritten pattern, but its name reads like a lookup. A name such as `_python_regex` would say what it returns.
- **Function length.** `checker_self_tests` is now 55 lines because its case table grew. This is data, not logic, and the PR discloses it.

**Merge note.**
- **State of the branch.** Integration has moved to `910910a594f131a8082c355412aefed2b9348e41` (S01 #127, then T02c #131), and GitHub reports the PR as `BEHIND`. Hosted checks at the reviewed head pass on all three OS (R12).
- **Merge preview** (an uncommitted `git merge --no-commit` of this head into `910910a`, R13 and R14):
  - The contract gate passes.
  - Every count matches integration alone except the checker self-tests (53 to 101).
  - T02c's two new regexes are plain `^…$`.
  - No contract value ends in a newline.
  - At `910910a`, 30,335 planted-newline pairs are newly rejected.
- **For the merger.** After the branch is updated, confirm the patch-id `332880565f3263269b30caeceaf4d0f1c01ee79b` and green three-OS checks on the new head.

## What was checked and passed

**CLAUDE.md hard rules and boundaries:**
- **Rule 1, evidence not claims.**
  - The PR body has the five evidence headings in the required order, and it labels everything CI on fakes or synthetic.
  - My own probes reproduce its numbers: 43 red, 101 self-tests, 310 identical fixture files.
  - The only overclaims are the wording issues in S-N1, S-N2 and S-N5.
- **Rules 5, 10, 11 and 12** (no weights, audio, secrets, addresses or product name):
  - The diff holds none of them.
  - At head, the policy scan covers 612 tracked files with 0 violations, and the Rule 07 and product-name lint covers 398 files (R01).
  - The commit uses the account's GitHub noreply identity and ends with the Co-Authored-By trailer.
- **Lanes and owner acts.** Untouched.
- **Contract-change path.** Nothing under `contracts/` changed: the `contracts/` tree hash is identical at base and head (R04). The change reaches `scripts/spec/` through the C04 contract-fix issue (#132, `area:contracts`), as `tickets.json`'s conflict-avoidance notes provide for edits after T02.
- **GLOSSARY.** No _Avoid_ word is used. "Anchor" appears only in its regex sense; GLOSSARY uses "anchor" descriptively for an evaluation anchor, not as a defined term, so there is no collision.
- **Standard library only.**
  - `jsonschema_subset.py` parses as Python 3.10 grammar, matching the docstring's bundling promise, and `validate.py` parses as 3.11 (R15).
  - This is a grammar check only: no 3.10 or 3.11 runtime is on STUDIO, and none was installed.
  - The code uses `re` behaviour (`\Z`, and the bad-escape error inside a class) that predates 3.10.
- **Tests through the seams.**
  - The new self-tests stay in the contract gate and call the checker as the existing self-tests do, through `_validate` and a bare `SchemaSet` probe.
  - Nothing is mocked.

**Is `_ecma_anchors` correct?** Yes (R05 A):
- **Edge cases agree with V8** under no flag and under `u`:
  - escapes: an escaped `\$`, an escaped backslash before the anchor, and an escaped backslash then an escaped dollar then the anchor;
  - classes: a `$` inside a class, and an escaped `]` with a `$` inside a class;
  - alternation: `^a$|^b$` and `^(a|b)$`;
  - anchors: end-only, start-only, and none at all;
  - newlines: `$` followed by a literal `\n`, and `\n?$`;
  - `$` inside a lookahead and inside a negative lookahead.
- **`[]$]` and `[^]$]`.** Base accepted them with Python's reading. Head refuses them in `check_all`. V8 reads an empty or `[^]` class without flags and raises a SyntaxError with `u`, so refusing them is the fail-closed choice.
- **Whole shipped corpus** (R05 C). I paired the 58 shipped regexes with 4,414 distinct contract strings and keys, each plain and with `"\n"`, for 512,024 pairs:
  - head disagrees with V8 on 0 pairs, under either flag;
  - base disagrees on 28,687, every one a planted newline.

**Can it loosen a pattern or a schema?** No, for every shipped pattern and schema:
- **Pattern level** (R05 B):
  - Each shipped regex changes only at its final `$`.
  - None has a lookaround, a backreference, `[]` or `[^]`.
  - Where a `$` sits in a negative lookahead (`^a(?!$)`, `^(?!a$)`), head now accepts `"a\n"` where base rejected it. V8 agrees: that is the ECMA-262 result, so the checker is never looser than ECMA-262.
- **Schema level** (R06, R07):
  - No pattern is reachable under `not` or in an `if` condition.
  - Both `patternProperties` keys sit beside `additionalProperties: false`.
  - Every pattern-bearing `oneOf` (91 of the 116 `oneOf` nodes) has pairwise-disjoint branches. Of the 95 branch pairs, 91 are proven by rule and 4 by reading. None of the proofs depends on an end anchor. R07's header line printed 116 as if every node bore a pattern; R07b corrects the count.
  - So a stricter `$` can only reject more.
- **Current integration tip.** The same holds at `910910a` (R14).

**Is the keyword refusal kept?** Yes (R09):
- An unsupported keyword is refused (`unevaluatedProperties`).
- A `$id` is refused twice, as an unsupported keyword and by the "carry no $id" rule.
- A dangling `$ref` is refused.
- The existing keyword and dangling-ref self-test still counts.

**Are the self-tests non-vacuous?** Yes (R08). Each mutant ran in a fresh `git archive` copy of the head with an exact, asserted source edit.

| Mutant | Result |
|---|---|
| X0 control | PASS |
| X1 translation removed | 43 FAIL (5 targeted cases, 37 sweep checks, the `[]$]` refusal) |
| X2 implementer's `trailing-only`, verbatim | 2 FAIL |
| X3 implementer's `python-leading-bracket`, verbatim | 1 FAIL |
| X4 an escape read as one character | 1 FAIL |
| X5 the class scan ignores escapes | uncaught `re.error`, exit 1 |
| X6 `patternProperties` keys bypass the translation | 1 FAIL |
| X7 `check_all` bypasses the translation | 1 FAIL |
| X8 string validation bypasses the translation | 41 FAIL |
| X9b the sweep's guard, given seeds that match no regex | both guard failures fire |

My first X9 design was invalid, and its log keeps it with a note. `"VERSE"` and `"ID"` match four mixed-case shipped regexes, so the guard rightly stayed silent.

## Probe index

All probes live at `/Volumes/STUDIO/evidence/C04/C04-review-*`, and their sums are in
`/Volumes/STUDIO/evidence/C04/C04-review-SHA256SUMS`.

| Probe | What it shows |
|---|---|
| R00, R01 | Install, then the full local gate at head (`scripts/ci/run.py --base dee28e2…`): pass |
| R02, R03 | `validate.py -v` at base and at head: both pass; counts identical except self-tests 53 to 101 |
| R04 | All 310 fixture files byte-identical; `contracts/` tree hash identical; matches the implementer's base inventory |
| R05 | Edge-case battery, shipped-regex sweep, the 512,024-pair V8 matrix and the `\s` code-point sets |
| R06, R07, R07b | Polarity contexts of every pattern; `oneOf` disjointness; corrected node count |
| R08 | The mutants listed above |
| R09 | Gate-level plants (`verse\n`, an id with `\n`, at base and head) and the keyword refusals |
| R10 | `pattern` against `patternProperties` keys in `check_all` |
| R11 | The latent oracle defect |
| R12 | Implementer sums verify (27 files); PR head unchanged; hosted checks pass |
| R13, R14 | Merge preview against integration `910910a` |
| R15 | Patch-id and grammar check |
| R16 | The sub-agents' exact examples, checked against V8 |
| Scripts | `dialect_probe.py`, `v8_oracle.mjs`, `polarity_probe.py`, `oneof_disjoint_probe.py`, `mutants_probe.py` |

## Appendix A: Standards-axis pass (sub-agent, independent), lightly cleaned

> **The `$` translation is correct and adds no fail-open path, but three docstrings claim more than the code does.**
>
> Python's `\Z` matches exactly where ECMA-262's `$` does without the `m` flag, so the swap is exact everywhere,
> lookarounds included. Classes end at the first unescaped `]`, as in ECMA. Python's class can only run longer, after
> a leading `]` or `^]`; a `$` in that extra stretch becomes `\Z` inside a Python class, which does not compile, so it
> is refused.
>
> **Docstrings overclaim** (the accuracy standard; CLAUDE.md hard rule 1):
> 1. `validate.py:7-9`, repeated at `:185-187` and `:203`:
>    - "Patterns follow ECMA-262" holds only for `$`.
>    - "Every anchored contract pattern rejects a planted trailing newline" holds only for the 19 of 58 regexes that accept "verse" or "id".
>    - Classes are refused only when a `$` falls in the extra stretch. `^[]]$` compiles and accepts "]", and `^[^]]$` accepts "a". ECMA rejects both, and both are SyntaxErrors under `u`. The behaviour is old; the claim is new.
> 2. `jsonschema_subset.py:71-72`, "`check_all` refuses it", is false for `patternProperties` keys. `_check` compiles `pattern` values only. With the key `[]$]`, `check_all()` returns `[]`, `_validate({})` passes, and `_validate({"x":1})` raises an uncaught `re.error`. Fix: compile the keys in `_check`.
> 3. Minor, `:8`: "with no flags" should say "without the `m` flag"; 2020-12 core §6.4 recommends `u`.
> 4. Minor, `validate.py:185/189`: the filter also drops `^a\\$`, whose final `$` is a real anchor. No contract pattern ends that way today.
>
> **Older gaps this diff does not fix:** Python-only syntax is not refused. The class scan runs to the end of the pattern when there is no closing `]`, which can hide a `$`: `(?#[)^a$` accepts "a\n", as the old code did.
>
> **Judgement calls:**
> - Duplicated Code: the probe set-up at `validate.py:200-201` repeats `:172-174`.
> - Mysterious Name: `_ecma_anchors`.
> - Brittle planting: a future negated-class pattern such as `^[^/]+$` would rightly accept "verse\n" under ECMA, yet would fail the self-test.
>
> **No breach found:** rules 11 and 12 hold, and the commit uses the noreply identity. The code is standard library only, and `contracts/` is untouched. No GLOSSARY _Avoid_ word is used.

**My verification of Appendix A:**
- Point 1 is confirmed by R05 B, R05 A and R16; it appears above as S-N1 and S-N5.
- Point 2 is confirmed at gate level by R10 (S-N2).
- Point 3 is checked against the published spec (S-N6).
- Point 4 is confirmed by reading and by R05 B (S-N4).
- The older gaps are confirmed by R05 A (S-N7).
- The brittle-planting judgement is demonstrated by R11 (S-N3).
- The "no breach" items are confirmed by R01 and R04.

The sub-agent made no writes.
