# AURA (working name)

Jon's personal, local-first music studio. A melody he hums, sings or plays on MIDI becomes an editable MelodySpec,
then two candidates he judges in a blind, level-matched audition, then a keeper he finishes in the Studio and exports
(WAV, stems, MIDI, ExportManifest) with full provenance, all rendered by open-weight engines on hardware he controls.
The control service and web UI are portable across macOS, Windows and Linux; the Mac (compute tier 4) comes first.

## Read first

- `docs/research/OWNER-DECISIONS-2026-11-07.md`: the current build. The repository is public for the build phase, so
  hosted CI stays free, and returns to private at production level. What may never appear on a public surface is hard
  rule 10. Merges into `integration` need green three-OS CI, enforced by rulesets, plus an independent review bound to
  the PR's patch. The continuation report's expansion trials are now in the plan.
- `docs/research/OWNER-DECISIONS-2026-11-06.md`: the merge policy: green current-head CI and independent review,
  integration only. November 7 supersedes its visibility: the repository is public during the build and returns to
  private at production level. November 7 also adds the server-side rulesets in place of its "procedural only" note.
  It relaxes the "changed base invalidates the review" clause for clean integration-only updates: the reviewed patch
  must equal the merged patch (`git patch-id --stable`), with fresh three-OS CI on the new head. Every other rule in it
  stays.
- `docs/research/OWNER-DECISIONS-2026-10-29.md`: Jon's continuation instruction and O-03 amendment to Extreme SSD.
  Then read `docs/research/OWNER-DECISIONS-2026-10-09.md` for binding O-01…O-11 and owner-pending defaults.
  The November 7, November 6 and October 29 amendments win where they change earlier decisions; all other owner decisions and owner-act gates remain.
- `docs/research/RECONCILIATION.md`: the verified evidence base. §4 is the component register, §6 the decisions
  D-01…D-24 behind the ADRs, §7 the owner's open questions, §8 what remains unverified. `evidence-register.json` is
  its machine-readable form, and `feature-inventory.md` lists every feature with its scope.
- `docs/spec/`: the v1 spec and its screens, `architecture.md` (modules, contracts, seams, tracer bullets and phase
  exits) and the ticket DAG.
- `GLOSSARY.md`: the domain language. Use its terms exactly in code, tests, tickets and copy, and never a listed
  _Avoid_ word for that concept.
- `docs/adr/` (0001–0037): decisions you must not silently undo. If your work contradicts one, say so in the PR.
- `contracts/`: the language-neutral source of truth: JSON Schemas, registry, golden fixtures, the stdlib reference
  and `product.json` (exists; changed only through contract tickets).
- `docs/DEVELOPING.md`: toolchain, the studio volume, environment, disk preflight, commands and evidence.
- `docs/agents/`: issue tracker, triage labels and domain-doc conventions.

## Hard rules

1. **Evidence, not claims.** Nothing is done until a check that could have failed has passed, and the PR carries its
   output. Report five kinds of evidence separately, each under its own PR heading, and never let one stand in for
   another: **CI on fakes** (FakeEngine, NeutralVoice, FakeBurstProvider: synthetic), **hardware** (per profile revision
   and host class), **listening** (Jon's verdicts), **paid** (quotes, approvals, ledger) and **per-OS** (a real host per
   operating system). Profile and capability status is computed from evidence records, never set by hand.
   Unverified work is labelled unverified, and an OS stays unverified until it passes on a real host, not only in CI.
2. **Never fabricate quality.** Quality is judged only by Jon's blind, level-matched auditions against his reference
   standards. No vendor figure, leaderboard, automatic scorer or Suno output counts toward "Suno v6-class". Diagnostic
   scores never select, rank or filter. Candidates are badged, never hidden. Before the reveal nothing leaks a
   candidate's route, profile, seed or file name: not the API, the DOM, logs or the jobs drawer.
3. **Honest figures and provenance.** Every number carries its figure label (MEASURED-LOCAL, VENDOR, COMMUNITY,
   COMPETITOR-RUN, OWNER-REPORTED, INFERRED, or UNVERIFIED where no check has been made). A VENDOR or COMMUNITY number
   is never shown, stored or written up as measured, and `claims_published` never holds MEASURED-LOCAL. Speed and
   memory numbers come from the worker SDK's own timings. An artifact without complete provenance is not stored.
   Synthetic output always reads "Synthetic test output".
4. **Operator lanes are enforced, never bypassed.** Every project has a lane: `individual` (Jon personally, the
   default), `llc` (Sabbath Echo and every Island Development Crew venture) or `research`. YuE2, Demucs and
   demucs-mlx, SwiftF0 and Basic Pitch (until their provenance review), Kim Mel-Band-RoFormer (until its training-data
   review) and every non-commercial scorer run only in `individual` and `research` (SongBench in `research` only); a
   component whose license is still UNVERIFIED runs only in `research`. A melody drafted by a lane-restricted
   transcriber carries that transcriber's lanes, and an import's lanes come from its attested terms. Lanes are checked
   at the seven points of ADR-0029. Only `derived_from` and `converted_from` edges carry a lane; `analyzed_by` never
   does. No code path, flag or fixture skips a lane check.
5. **Licensing doctrine.** Never commit, vendor or redistribute weights: they download at runtime from a pinned source
   (a Hugging Face revision, a pinned URL with sha256, or a file in a pinned package) only after Jon accepts the license
   (`license-acceptance/1`), gated or not. Non-commercial and copyleft components run only inside a separate worker
   process, never in the control service or the web bundle (CI runs a license allowlist there: anything unknown fails,
   and LGPL, GPL, AGPL, NC, CC-BY-SA, SSPL and BUSL are denied). Never copy AGPL code (ACE-Step-DAW, openDAW,
   VoiceStudio, Ruach Studio). A component whose license is UNVERIFIED in the
   register is not adopted until its license ticket closes. Never commit audio: fixtures are JSON, and NeutralVoice
   audio is generated at test time.
6. **The Suno boundary.** A Suno import may be listened to, loudness-measured and DSP-finished (mix, master, format),
   nothing more. It is never an audition arm, a reference, an evaluation reference or anchor, training data or test
   material (O-08, ADR-0010, ADR-0020), whatever is signed; a risk acceptance can add only engine, conditioning,
   separation, edit or conversion input, one named use at a time. Every import is an owner act whose uses follow its
   source. No third-party Suno API, and no imitation of Suno's branding or look.
7. **Storage.** Never write models, caches, interpreters, environments, `node_modules`, build output, worktrees or
   large temp files to the internal disk. They go on the studio volume (`/Volumes/STUDIO`, the APFS sparse bundle on
   Extreme SSD, per the October 29 owner amendment) through the env file. The canonical checkout at `~/Music Gen/aura` holds docs only, with nothing
   installed. Run the disk preflight before every download, install, environment build, job or export: refuse when the
   studio volume's effective free space minus the estimate is under 10 GiB, put no planned writes on the internal
   disk, and block heavy jobs while it is under 2 GiB free. Never run `sudo`; print the command for Jon. Never delete
   Jon's files or caches to make room; report sizes and let him decide.
8. **Paid runs.** Every burst run needs Jon's explicit yes for that run, given in the Studio UI, and must fit under the
   $25 monthly cap with its ceiling reserved before anything is provisioned. Agents, scripts, the CLI and the eval
   harness may request a quote and then wait. They never approve, raise the cap, retry a paid job, or start a pod or a
   `--paid` conformance run on their own. The self-hosted Mac runner never runs paid jobs.
9. **Owner acts belong to Jon.** Approving a quote, changing the cap, acknowledging an overrun or a reconciliation
   adjustment, changing a project's lane, giving a verdict, accepting a risk, accepting a model license, recording a
   reference permission and attesting an import happen only in the Studio UI under the owner-ui scope. A test-mode
   verdict is allowed only in a temporary `test_store`, and its records are labelled synthetic or "hardware,
   non-listening". Never forge, replay or script one (no launch token, cookie or nonce handling on his behalf), and
   never record a verdict for him.
10. **No secrets in the client.** The RunPod API key, the HF token and tailnet pairing secrets live in the OS keychain
    through `keyring`. They never appear in code, the web bundle, API responses, logs, fixtures, evidence or commits.
    Worker tokens and burst URLs never cross the Studio API. No `.env` with real values is ever committed. Because the
    repository is public during the build (November 7 decision), nothing sensitive goes onto any public surface:
    tracked files and commit messages, issues, PR bodies, comments and reviews, review and merge files committed under
    `ops/`, and CI logs. That means no secrets, personal addresses, audio, weights, or private paths beyond
    `/Volumes/STUDIO/...`. A private path is an absolute path that names a local account, such as one under a home
    directory. This is the one statement of the rule, and other documents point here.
11. **Public contact (IDC Rule 07).** The only contact address anywhere is `hello@islanddevcrew.com`, as text (in code
    formatting in Markdown), stored once in `contracts/product.json`. Never a `mailto:` link, never a personal address,
    in code, copy, contracts, manifests, package metadata, docs or commit metadata. Commits use the GitHub noreply
    identity.
12. **One name constant.** "AURA" reaches the product only through `productName` in `contracts/product.json`. Code
    uses neutral identifiers: `studio_*` packages, `STUDIO_*` variables, the `studioctl` CLI, the `/Volumes/STUDIO`
    volume and the `studio` store format. Never put the product name in a package, variable, path or on-disk format.
13. **Scope.** v1 has no voice cloning or conversion; own voice is v2, and the RVC and rmvpe weights stay out.
    Narration is a separate, later spec: build no narration UI, engine or worker, but keep the store, jobs, provenance
    and worker SDK domain-agnostic (`tts_render` origin, `narration` project kind reserved). No hosted music service in
    v1-core, and no training jobs.
14. **Accessibility is a feature.** Every screen, the audition included, works keyboard-only with a visible focus.
    Playwright audits every screen. Text contrast is at least 4.5:1 in light and dark. Meaning is never carried by
    colour alone (badges are words). Motion respects reduced-motion. Every control has an accessible name, and no
    accessible name leaks a blind identity.

## Parallel-work rules

- One ticket is one issue, one branch `ticket/<NN>-<slug>`, one worktree at `/Volumes/STUDIO/worktrees/<NN>-<slug>/`
  and one PR into `integration` (O-01; `main` advances only by Jon's release merge), squash-merged only after the
  required checks pass and an independent review of that patch finds no blocking issue (November 6 and 7 decisions).
  The `integration` ruleset enforces the three-OS checks, an up-to-date branch and squash merging. The merging agent
  confirms the checks with `gh pr checks --watch` and the review by its patch-id. Never build in the canonical checkout, and never use `.claude/worktrees/`
  (it sits on the internal disk).
- One feature per folder: a control-service module in `services/control/studio_control/<module>/`, a worker in
  `workers/<name>/`, a web screen in its own folder under `apps/web/src/`. A ticket changes its own folder and its
  tests; shared code changes through the ticket that owns it.
- Contracts change only through contract tickets. `contracts/` (schemas, registry, fixtures, reference,
  `product.json`) is the source of truth. Generated Pydantic and TypeScript types are regenerated, never hand-edited,
  and CI checks the drift. A feature ticket that needs a contract change stops and is blocked by a contract ticket.
  Frozen `contracts/fixtures/legacy/` fixtures are never edited.
- The control service carries no audio or ML dependencies. Each engine worker is a standalone uv project with its own
  lock, outside the workspace lock. Worker environments are keyed by lock hash on the studio volume and shared by every
  worktree.
- Tests go through the seams: StudioHarness through the Studio API, conformance through the worker protocol, golden
  fixtures for Score. Fakes exist only at real boundaries, nothing mocks an internal collaborator, and tests wait on
  event `seq`, never on sleeps. Build test-first (`tdd`).
- Name things with `GLOSSARY.md` terms. A missing term is a gap for `domain-modeling`, not a licence to invent one.
- After the merge, remove the worktree (`git worktree remove`). Leave nothing behind on the internal disk.

## Agent skills

### Issue tracker

GitHub Issues on `Navigata1/aura` via `gh`. The repository is public during the build phase and private again at
production level (`docs/research/OWNER-DECISIONS-2026-11-07.md`). Issues, PRs, comments, reviews and CI logs are public,
so hard rule 10 applies to all of them.
Run every `gh` command for this repo as `GH_TOKEN="$(gh auth token --user Navigata1)" gh …` so the machine's default
account is never switched. See `docs/agents/issue-tracker.md`.

### Triage labels

The default five roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), plus `spec`,
`gate:evidence`, `area:<name>` and the work-stream labels `stream:engine`, `stream:studio`, `stream:voice`,
`stream:eval` and `stream:shared` ("lane" alone always means operator lane). `ready-for-human` means a ticket needs Jon
for an owner act or an input only he can supply; an agent still prepares everything up to it. See
`docs/agents/triage-labels.md`.

### Domain docs

Single-context: root `GLOSSARY.md` plus `docs/adr/`. See `docs/agents/domain.md`.

### The method

`to-spec` → `to-tickets` → `implement-spec`, which builds each ticket with `tdd` in its own worktree and ends with
`code-review`. Use `codebase-design` (with `DEEPENING.md` and `DESIGN-IT-TWICE.md`) when shaping a module's interface,
and `domain-modeling` (with `GLOSSARY-FORMAT.md` and `ADR-FORMAT.md`) when a term or a decision changes. The vendored
Matt Pocock skills live in `.claude/skills/` (MIT, pinned commit `6fd94792` in `MATTPOCOCK-SKILLS-COMMIT`).
