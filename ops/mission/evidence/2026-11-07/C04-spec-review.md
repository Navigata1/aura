# C04 spec review: PR #136 against issue #132

- **Head:** `1e0e1254a4b09faa5b1e0532ccfbf09f0a45dd5e` (`ticket/C04-pattern-anchoring`, one commit)
- **Base:** `dee28e2fd2b7a79ca2773e639a4a714af5c356b8` (the PR's integration base and the merge-base of head and base)
- **Diff:** `git diff dee28e2fd2b7a79ca2773e639a4a714af5c356b8...1e0e1254a4b09faa5b1e0532ccfbf09f0a45dd5e`
  (2 files, +78/-3). Saved as `C04-review-pr136.diff` (sha256
  `c1e1552c9229e69245b4cbcc71f24e136de740eef9a18794c13bbf901e064a50`). Patch-id:
  `332880565f3263269b30caeceaf4d0f1c01ee79b`.
- **Spec sources:**
  - Issue #132 (open; labels `ready-for-agent`, `stream:shared`, `area:contracts`; no comments). A snapshot is saved as `C04-review-issue-132.json`.
  - `docs/spec/tickets.json` has no C04 row; C-numbered items are contract-fix tickets. The closest original acceptance is T02's: "validate.py passes on every existing fixture and no existing byte under contracts/fixtures changes".
  - `contracts/README.md`: the checker "refuses every keyword it does not implement".
- **Reviewer:** independent; I did not write or edit the implementation. Reviewed 2026-11-08 (UTC) in the disposable copy `/Volumes/STUDIO/scratch/review-C04-1e0e125/`.
- **Method:** `.claude/skills/code-review/SKILL.md` from the base tree. The Spec axis ran as its own pass, a sub-agent given only the diff and the spec; Appendix A gives its report. I re-checked every claim it made with my own probes. The probe logs and their sums are in `/Volumes/STUDIO/evidence/C04/C04-review-*` and `C04-review-SHA256SUMS`.

## Verdict: pass

All three acceptance criteria are satisfied, and so is the "What to build" requirement that the fix must not loosen any existing pattern. Nothing is claimed as done that is not done. What stays open is stated honestly in the PR: only `$` is bridged, and `\s` and Python-only syntax remain. I confirm those items and record them as follow-ups. They are not unmet acceptance.

## Acceptance criteria

### AC1: satisfied

> A planted `"verse\n"` (and `"id\n"` for an id pattern) is rejected by every anchored pattern; the self-test fails
> before the fix and passes after.

**Every anchored pattern rejects the planted seeds** (R05 B):
- All 58 shipped regexes are anchored, written exactly as `^…$`.
- At head, `"verse\n"` is accepted by 0 of the 58; base accepted it for 18.
- At head, `"id\n"` is accepted by 0 of the 58; base accepted it for 19.

**The id pattern** (`$defs/id`):
- It requires an underscore, so the literal `"id"` is not a record id.
- The PR plants `melody_id\n` for it instead, which is the faithful reading of "for an id pattern". Head rejects it and base accepted it.

**The fix reaches beyond the two seeds** (R05 B, C):
- For each of the 58 regexes, I took every contract value it accepts and appended `"\n"`. Head rejects every such value: 28,687 pairs, all of which base accepted.
- Across 512,024 pairs of shipped regex and contract value (plain and with `"\n"`), head agrees with V8 on all of them, with no flag and with `u`.

**Gate-level plants** (R09), each in a fresh copy:
- **`"verse\n"` as the `tl_hymn` marker name** (the T02d probe-G case). The base checker's schema check accepts it, and only the fixture's byte regeneration fails. The head checker rejects it with `$.markers[0].name: 'verse\n' does not match '^[a-z][a-z0-9-]{0,31}$'`.
- **`"tl_hymn\n"` as the timeline id.** Head rejects it at `$.id`, against the record id pattern. Base's schema check accepts it.

**Fails before the fix, passes after** (R08):
- With the translation removed (X1), the same self-tests give 43 FAIL lines: 5 targeted cases, 37 sweep checks and the `[]$]` refusal.
- Unmodified (X0), they pass.
- This matches the implementer's `C04-red-at-head.log`, which also shows 43.

**Caveat on wording only** (standards S-N5):
- The self-test sweep exercises the anchor for the 19 regexes that accept a seed, and the targeted cases add `$defs/id` and the `^[A-Z]$` key.
- The validate.py docstring reads as if every anchored pattern were exercised.
- The behaviour itself holds for all 58.

### AC2: satisfied

> `validate.py` passes; no existing fixture byte changes. Any existing fixture that only passed because of the bug is
> reported, not silently rewritten.

**`validate.py` passes:**
- `validate.py -v` passes at head (R03) and at base (R02).
- The full local gate passes at head: `scripts/ci/run.py --base dee28e2…` (R01). It covers contracts, tickets and registry, pytest (54 passed plus 12 subtests), Vitest, the node test, the build, the policy scan and licenses.
- Every gate count is identical at base and head except the checker self-tests (53 to 101). That includes 316 files valid by kind, 93 invalid records rejected for the named reason, 94 scenarios plus 8 valid scenarios, 59 rules and every vector family.

**No fixture byte changes** (R04):
- All 310 files under `contracts/fixtures/` are byte-identical: the per-file SHA-256 lists at base and head are identical.
- The git tree `8544bfb4f7a9adc868ae9dff131155633e176d2c` is the same at both, and the whole `contracts/` tree (`61674c5a75456bbd82c58e689d6182dc61c1fdf1`) is unchanged.
- My base list is identical to the implementer's `C04-fixture-inventory-base.sha256`.

**No fixture passed only because of the bug:**
- No string or object key anywhere in `contracts/` or `docs/evidence/` ends in `"\n"`. I checked 366 files, holding 4,414 distinct strings and keys (R05 B).
- The PR body reports the same result in its own terms (3,780 distinct strings in 316 contract files), so the criterion's "reported" clause is met.
- The only values containing a newline anywhere are lyric texts. Their schema field, `song-spec` `approved_lyrics.text`, carries only length bounds and no pattern.
- Nothing was rewritten.

**This still holds after integration moved** (R13, R14). Integration is now `910910a`, with S01 #127 and T02c #131 merged.
- In the merge preview, which is not committed, the gate passes.
- Every count matches integration alone except the self-tests.
- No value among 4,753 in 384 files ends in a newline.

### AC3: satisfied

> The checker's docstring states the ECMA-262 anchor rule.

- **Module docstring.** `scripts/spec/jsonschema_subset.py:8-12` states the rule. Patterns are ECMA-262 regexes, so `$` matches only at the end of input. Python's `$` would let `^[a-z]+$` accept `"verse\n"`. So every unescaped `$` outside a class compiles as `\Z`, and no other dialect difference is bridged.
- **Function docstring.** `_ecma_anchors` (`:68-72`) restates the rule at the function.
- **Wording nit.** See standards S-N6: "with no flags" should say "without the `m` flag", since JSON Schema recommends `u`. The rule is unaffected.

### "What to build"

**"It must not loosen any existing pattern": satisfied.**
- **Pattern level** (R05 B): for every shipped regex, the only change is that its final `$` becomes `\Z`, and no shipped regex has a lookaround, a backreference, `[]` or `[^]`.
- **Schema level** (R06, R07, R07b):
  - No pattern is reachable under `not` or in an `if` condition.
  - Both `patternProperties` keys sit beside `additionalProperties: false`.
  - All 91 pattern-bearing `oneOf` nodes have pairwise-disjoint branches, by rule or by reading, never by an end anchor.
  - So the change only rejects more; it never accepts more.
- **The only case where head accepts more than base.** That is a `$` inside a negative lookahead, such as `^a(?!$)` or `^(?!a$)` on `"a\n"`. There, head now gives the ECMA-262 result that V8 gives (R05 A, R16). No shipped pattern has one.

**"Self-tests: a known-bad value with a trailing newline fails for an anchored pattern, and a known-good one passes": satisfied.** The pairs include:
- `beef` and `beef\n`;
- `melody_id` and `melody_id\n`;
- the key `A` and the key `A\n` under `^[A-Z]$`;
- the escaped and class cases, alternation, and a pattern with no end anchor (`^a` still accepts `"a\n"`).

### Other spec sources

- **T02's fixture-byte acceptance: satisfied.** It is the same evidence as AC2.
- **`contracts/README.md`, "refuses every keyword it does not implement": still true** (R09). Head refuses:
  - `unevaluatedProperties`;
  - `$id`, both as unsupported and by the no-`$id` rule;
  - a dangling `$ref`.
- **"Evidence kinds: CI on fakes only": satisfied.**
  - The PR body has a summary followed by the six evidence headings, in the required order.
  - All evidence sits under CI on fakes and is labelled synthetic or software-only.
  - Hardware, Listening and Paid all say "None".
  - Per-OS correctly says that the hosted checks are CI, not real per-OS hosts.
  - The hosted three-OS checks pass at the reviewed head (R12).

### Scope

- **Confined to the gate.** The change touches only the checker and its gate in `scripts/spec/`, and no `contracts/` path.
- **The `[]$]` refusal is within scope.** It is how the translation stays fail-closed when it cannot tell whether a `$` is an anchor.
- **Its supporting text claims too much.** The broader wording ("a class that ECMA-262 and Python end in different places is refused") goes further than the code. So does the docstring line "`check_all` refuses it" for `patternProperties` keys. See standards S-N1 and S-N2; both are non-blocking.

### Still open (honestly stated in the PR, confirmed here)

**`\s` differs between the dialects** (R05 D). I confirmed the implementer's report:
- Python's `\s` includes U+001C–U+001F and U+0085, and lacks U+FEFF.
- The shipped `uri` pattern `^https://[^\s]+$` therefore accepts a trailing U+FEFF, which ECMA-262 rejects.
- It also rejects U+001C and U+0085, which ECMA-262 accepts.

**Python-only syntax compiles untouched** (R05 A):
- Examples are `(?#…)` comments and inline flags such as `(?m)`.
- Further unbridged differences: `[]` and `[^]` classes, and an authored `\Z`.
- None of these is in a shipped schema.

**Suggested follow-up:** one contract-fix ticket that makes `check_all` refuse (or bridge) these forms. See standards S-N7.

### Merge note

- **Branch is behind.** The PR is `BEHIND` integration `910910a`.
- **Preview.** A merge preview passes the gate (R13, R14).
- **Before merging.** Per the protocol, the merger updates the branch and confirms the patch-id `332880565f3263269b30caeceaf4d0f1c01ee79b`. The merger also needs green three-OS checks on the new head.
- **Issue closure.** The merger closes #132 by hand. Merges into `integration` do not auto-close issues.

## Appendix A: Spec-axis pass (sub-agent, independent), lightly cleaned

> **All three acceptance criteria hold on what I could compute; no Critical or High findings.**
>
> - **validate.py passes.** At head: 0 failures. Every count except the self-tests matches base, and the self-tests go from 53 to 101.
> - **Fails before, passes after.** Head's self-tests against base's checker give 43 failures (5 targeted cases, 37 sweep checks, the `[]$]` probe). Against head's checker they give 0.
>
> **(a) Missing or partial**
> 1. "Rejected by every anchored pattern": the sweep only tests patterns that accept "verse" or "id", 19 of the 58 distinct shipped regexes. The targeted cases add `$defs/id` and `^[A-Z]$`, so 37 shipped patterns never get a trailing-newline test. The fix itself is complete: each of the 58 rejects a real fixture value plus "\n" at head, and base accepted every one. The docstring line "every anchored contract pattern rejects a planted trailing newline" overstates the test. The literal "id\n" never reaches the record-id pattern, which requires a `_`; the `melody_id\n` case covers it.
> 2. The sweep filter skips nothing today, because all 58 are written exactly as `^…$`. It would skip three kinds of pattern: one ending in an escaped backslash before a real anchor, end-only anchors, and `^a$|^b`.
> 3. "Any existing fixture that only passed because of the bug is reported": there is nothing to report, since no string or key under `contracts/` or `docs/evidence` ends in "\n". The commit doesn't say this was checked.
>
> **(b) Not asked for:** the `[]$]` meta-check refusal and its self-test. The claim is broader than the code: `^[]a]$` and `^[^]a]$` pass `check_all` with Python's reading. `_check` never compiles `patternProperties` keys, so a `[]$]` key passes the meta-check and then raises an uncaught `re.error` in `_validate`. No shipped schema is affected.
>
> **(c) Looks implemented; one caveat.** "Must not loosen any existing pattern" holds for every shipped schema:
> - For all 58, the only change is the final `$` becoming `\Z`.
> - No shipped pattern uses lookarounds or `[]`/`[^]` classes, and none can be reached under `not` or `if`.
> - Every `oneOf` that contains a pattern has branches that cannot both match.
> - The only `patternProperties` key sits beside `additionalProperties: false`.
>
> The caveat: this guarantee comes from today's patterns, not from the translator. A `$` inside a negative lookahead would loosen: `^(?!a$)` accepts "a\n" at head but not at base, which is the correct ECMA-262 result. The docstring states the rule at `jsonschema_subset.py:8-12`.

**My verification of Appendix A:**
- The counts, the 43 red failures and the 37/19/58 split are confirmed by R02, R03, R05 B and R08.
- Point (a)1 is confirmed (R05 B).
- Point (a)2 is confirmed by reading and by R05 B.
- Point (a)3 needs one correction. The commit message does not mention the check, but the PR body reports it explicitly ("none of the 3,780 distinct strings in the 316 contract files ends in a newline"), so the "reported" clause is met. My scan, which also covers keys, `contracts/schemas` and `docs/evidence`, agrees (R05 B).
- Point (b) is confirmed by R05 A, R10 and R16. I read the `[]$]` refusal as within scope, not as scope creep: it is the translation's fail-closed case. The overclaim is a standards finding.
- Point (c) is confirmed by R05 B, R06, R07 and R07b, and the negative-lookahead behaviour by R05 A and R16.

The sub-agent made no writes.
