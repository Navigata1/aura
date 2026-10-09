# AURA screen specification (v1)

Status: implementation-ready draft, 2026-10-09. Author: product design, for the lead. Scope: every screen and shared
surface of the v1 web app (`apps/web`): the v1-core flow first, then the v1-studio screens (Studio, DSP finishing).
v2 surfaces are named only where a v1 screen must leave room for them. Nothing here has been built, run or listened
to. Every number drawn on a screen below is an **example** to fix layout and copy, not a measurement.

**Sources, in precedence order.** Owner decisions O-01…O-11 (`docs/research/OWNER-DECISIONS-2026-10-09.md`, binding)
→ the hard rules in `CLAUDE.md` (architecture §2) → ADR-0001…0037 → `docs/spec/architecture.md` (cited "arch §n") →
`GLOSSARY.md` (its terms, exactly) → `docs/research/RECONCILIATION.md` (§4 component register, §6, §7, §8) and
`docs/research/feature-inventory.md` (feature IDs A1…L11 and their scopes). Where this spec needs something those
sources do not settle, it proposes a default and lists it in §6 rather than inventing a contract silently.

**Names.** Domain words are the glossary's. UI component names (React, PascalCase) are defined in §5; a component is
**bold** the first time a screen section uses it. API resources are arch §4.1's. Screens are `S00`–`S15`; shared
surfaces (drawers, sheets, dialogs) are `O1`–`O12`.

**Figure labels** are the glossary's: MEASURED-LOCAL, VENDOR, COMMUNITY, COMPETITOR-RUN, OWNER-REPORTED, INFERRED, UNVERIFIED.

**The brief's headings, in glossary words.** The brief that commissioned this spec used a few words the glossary tells
us to avoid. The screens use the glossary word:

| Brief said | This spec says | Why (GLOSSARY) |
|---|---|---|
| take lanes | replacement tracks | Track: _Avoid_ take lane, version lane; "lane" always means operator lane |
| listening sessions | eval auditions | Audition: _Avoid_ listening session |
| results (with uncertainty) | evidence (with uncertainty) | Evidence record: _Avoid_ result, report |
| render routes | routes | Route: _Avoid_ render route |
| voice-memo import | import a recording | Hum: _Avoid_ voice memo (one way a hum can arrive) |
| rented burst | burst | Burst: _Avoid_ rental (alone) |

---

## 0. Conventions that apply to every screen

### 0.1 Visual direction: Manuscript

**The idea.** AURA is a private atelier for one composer, so it looks like his working manuscript: warm vellum paper,
engraved ink, a **red pencil** for marks and corrections, a **brass seal** on anything only he can do, and **verdigris**
for what evidence has proven. It is listening-first: when audio is the point, the page clears around it and the
largest thing on screen is a play control. It is light by default because a score is read on paper. The dark theme,
**Lamplight**, is the same desk at night, designed rather than inverted.

**What it refuses.**

1. **No template look.** No uniform card grids, no centred hero with a gradient blob, no unmodified component-library
   defaults, no one-radius-one-shadow-everywhere.
2. **No imitation of Suno's branding or look.** No dark gradient canvas, no cover-art grid, no prompt box as the home
   page, no "Create" as the main verb, none of Suno's colours, type or layout. Standard verbs (Cover, Extend, Replace)
   are used where they help muscle memory (ADR-0012, ADR-0021).
3. **No dashboard by numbers.** A number appears where a decision needs it, and every number carries its figure label.

#### Palette tokens

CSS custom properties on `:root`. Vellum is the default; `prefers-color-scheme: dark` selects Lamplight unless the user
chose a theme in Settings (`:root[data-theme]`); `prefers-contrast: more` (or Settings) applies the increased-contrast
overrides. Ratios are WCAG 2 contrast against `--paper`, computed for this spec (Vellum / Lamplight); CI's contrast
test re-checks every text role at ≥ 4.5:1 and every graphic role at ≥ 3:1 on all three grounds in both themes and in
increased contrast.

| Token | Role | Vellum | Lamplight | Ratio on `--paper` |
|---|---|---|---|---|
| `--paper` | page ground | `#F4EFE6` | `#15120E` | — |
| `--paper-raised` | sheets, dialogs, the margin column, the player bar | `#FBF8F2` | `#1F1B16` | — |
| `--paper-sunk` | wells where audio and notes are drawn: piano roll, timeline, meters, time ruler | `#EAE3D6` | `#0F0D0A` | — |
| `--ink` | primary text, primary buttons (filled), focus ring | `#1D1A16` | `#EFE8DA` | 15.1 / 15.3 |
| `--ink-2` | secondary text | `#4A443B` | `#C9BFAD` | 8.4 / 10.3 |
| `--ink-3` | captions (never below 14 px) | `#655D51` | `#A39885` | 5.7 / 6.6 |
| `--rule` | hairlines and staff lines (decorative only) | `#D9D0C1` | `#3B342A` | n/a |
| `--rule-strong` | edges that carry meaning: inputs, clip edges, bar lines | `#837968` | `#7A705F` | 3.7 / 3.8 |
| `--red-pencil` | marks: the record button, playheads, corrections, failure badges | `#A8241C` | `#F07A6E` | 6.3 / 6.9 |
| `--brass` | owner acts (the seal) and money | `#735614` | `#DDB55E` | 6.0 / 9.6 |
| `--verdigris` | evidence that passed; verified | `#2B6457` | `#72C4AC` | 6.0 / 9.1 |
| `--graphite` | unmeasured, unverified, synthetic, declared | `#525C66` | `#AAB3BD` | 6.0 / 8.8 |
| `--red-wash`, `--brass-wash`, `--verdigris-wash`, `--graphite-wash` | badge and banner grounds | `#F2DAD4`, `#EEE2C3`, `#D5E5DE`, `#E0E3E5` | `#3A1F1B`, `#3A3020`, `#1C342D`, `#262B30` | role colour on its own wash ≥ 5.2 |
| `--selection` | selected-row ground (never alone; see §0.7) | `#E8D7A6` | `#3B321F` | `--ink` on it 12.1 / 10.4 |
| `--on-ink` | text on filled ink buttons | `#F4EFE6` | `#15120E` | 15.1 / 15.3 |
| `--on-red-pencil` | glyph on the record disc | `#FFFFFF` | `#15120E` | 7.2 / 6.9 |

Increased contrast: `--ink-3` becomes `--ink-2`; `--rule` becomes `--rule-strong`; every wash gains a 1 px border in its
role colour; paper grain is removed; translucent surfaces become opaque. `body` always sets an explicit background.

#### Type

| Family | License | Used for |
|---|---|---|
| **Newsreader** (variable, optical sizes) | OFL 1.1 | display and headings only: song titles, screen titles, movement numerals, the reveal. Never in a control. |
| **IBM Plex Sans** | OFL 1.1 | all interface text, controls and body copy |
| **IBM Plex Mono** | OFL 1.1 | tabular figures: timecode, hashes, LUFS, dBTP, cents, money, sizes |
| **Bravura Text** (SMuFL) | OFL 1.1 | music glyphs only (♩, ♭, ♯, time signatures), subset to the glyphs used |

Plex Sans and Plex Mono are one superfamily, so the pairing is Newsreader (an editorial serif with optical sizes, for
the voice of the page) against Plex (an engineered sans, for the honesty of controls and figures). Bravura Text is the
one exception to the two-family budget, because notation needs real notation glyphs. Every font is self-hosted from the
control service's origin (a localhost tool makes no third-party font request), subset, `font-display: swap`, and is a
row in the component register before adoption (§6 Q13). Only Plex Sans 400 is preloaded.

| Token | Face | Size / line height | Use |
|---|---|---|---|
| `--type-display` | Newsreader 400 | `clamp(2.5rem, 1.6rem + 3vw, 4rem)` / 1.05 | song title, the reveal |
| `--type-title` | Newsreader 500 | `clamp(1.75rem, 1.4rem + 1.2vw, 2.5rem)` / 1.15 | screen title (the one `h1`) |
| `--type-heading` | Newsreader 500 | 1.5rem / 1.25 | section headings |
| `--type-subheading` | Plex Sans 600 | 1.125rem / 1.35 | group headings, card titles |
| `--type-body` | Plex Sans 400 | 1rem / 1.5 | body and controls |
| `--type-small` | Plex Sans 400 | 0.875rem / 1.45 | helper text, table cells |
| `--type-label` | Plex Sans 600, tracking 0.06em, uppercase by style | 0.75rem / 1.3 | figure labels and kickers (stored in sentence case so screen readers read words) |
| `--type-figure` | Plex Mono 500, tabular | 0.9375rem; large 1.75rem | every figure |
| `--type-glyph` | Bravura Text | 1.2em of the surrounding text | ♩ = 92, E♭, 6/8 |

The wordmark is `productName` from `contracts/product.json`, set in Newsreader small caps with 0.08em tracking. It is
live text, so a rename (O-10, ADR-0035) changes one constant and no asset.

#### Layout grammar

- **The staff rule.** A major break inside a page is five 1 px hairlines 3 px apart in `--rule`, hidden from assistive
  technology. It separates movements of a page, never items inside a card.
- **The margin.** At ≥ 1200 px every content screen has a 296 px right-hand column, like marginalia on a score: the
  operator lane, compute placement, provenance and figure labels of whatever is selected. Below 1200 px it folds into a
  "Details" disclosure at the end of the main column.
- **Movements.** A project's path is numbered like the movements of a piece: **I Seed · II Melody · III Song intent ·
  IV Render · V Listen · VI Finish**, roman numerals in Newsreader with the plain word beside them. The spine shows
  store state; it is never a wizard that locks a step.
- **Grid.** 12 columns at ≥ 1200 px (32 px gutters), 8 columns at 768–1199 px (24 px), 4 columns below 768 px with a
  16 px side gutter. No horizontal page scroll at any width from 320 px; the piano roll, the timeline and wide tables
  scroll inside their own wells.
- **Spacing scale** 4, 8, 12, 16, 24, 32, 48, 72 px. Rhythm, not uniform padding: 72 between movements of a page, 48
  after a staff rule, 24 between groups, 12–16 inside a group.
- **Radius** 2 px on controls (engraved and crisp), 6 px on sheets and dialogs, a full pill only on chips.
- **Depth** comes from paper layers, not drop shadows on everything: raised paper has a 1 px `--rule` edge and
  `0 1px 0 rgb(29 26 22 / 6%)`; drawers, sheets and dialogs cast `0 12px 32px rgb(29 26 22 / 14%)` (Lamplight
  `rgb(0 0 0 / 50%)`).
- **Texture.** A 3 % paper grain (inline SVG noise, never an image request) on `--paper` in Vellum and 2 % in
  Lamplight; none in wells where audio or notes are drawn, and none in increased contrast.

#### Motion rules

1. Motion explains a change of state. Nothing moves for decoration, and nothing loops except one mark on a running job.
2. Only `transform` and `opacity` animate. `--dur-quick: 120ms` (hover, press, focus), `--dur-settle: 200ms`
   (drawer, sheet, disclosure), `--dur-turn: 280ms` (a screen change: an 8 px horizontal shift plus a fade, like
   turning a page; also the reveal's card turn). Easing `--ease-out: cubic-bezier(0.25, 1, 0.5, 1)`. Exits use
   `--dur-quick`.
3. Audio-coupled visuals (level meters, playheads, the audition position) are drawn from the audio clock
   (`AudioContext.currentTime`) in `requestAnimationFrame`, never with CSS animation, and they stop when audio stops.
4. Figures never count up, tween or roll. They change in place.
5. A running job shows exactly one moving mark: a small metronome tick that steps once a second beside its state.
6. **Reduced motion** (`prefers-reduced-motion: reduce`, or Settings): screen changes and the card turn are instant;
   drawers appear without sliding; the metronome tick becomes a static "Running" glyph with elapsed time updated as
   text; meters keep updating because they carry information, but without ballistic smoothing and with the numeric
   peak always shown; playheads keep moving, and views page-jump instead of smooth-scrolling.

#### Data display as part of the system

Every chart is drawn in the same hand: hairline axes in `--rule-strong`, figures in Plex Mono with their figure label,
patterns as well as colour (solid, hatched, dotted), and a "Show as table" toggle. The instruments are the
**LevelMeter** (S05), **ConfidenceShading** (S06), **LoudnessReport** (S11), **UncertaintyPlot** (S12), **StatusLadder**
(S13) and **CapGauge** (S14), defined in §5.

#### Iconography

Generic actions use Lucide (ISC, 1.5 px stroke; a component-register row before adoption). Meaning uses AURA's own
glyphs (§0.5), always beside words. Every icon-only control has an accessible name and a tooltip.

### 0.2 Global shell and navigation

#### Regions

| Region | Landmark | Content |
|---|---|---|
| **Masthead** | `header` | Wordmark · when inside a project, its title and **LaneTab** · **ComputeChip** · **StoreChip** · **CapChip** · **NeedsYou** · jobs toggle |
| **NavRail** | `nav` "Main" | Global: Library · Evaluation · Engines & licenses · Burst & monthly cap · Settings. Project (under the project title, when one is open): Song page, then the movements I Seed (Capture) · II Melody · III Song intent · IV Render (Generation) · V Listen (Audition) · VI Finish (Studio, Finishing). Each project item shows a state glyph with text on focus: done, current, needs you, unavailable (with the reason). |
| **Main** | `main` | The screen. One `h1`, the screen title. |
| **Margin** | `aside` "Details" | Context for the selection (§0.1). |
| **PlayerBar** | `region` "Player" | Sticky, 64 px. Plays captures, guides, keepers, imported mixes, references and exports. Hidden during a blind audition and in the Studio, which has its own transport. |
| **Footer** | `footer` | `{productName}` · build · `hello@islanddevcrew.com` as selectable text from `publicContactText`, never a link · "Serving on 127.0.0.1:{port}" (or "on 127.0.0.1 and the tailnet" when that opt-in is on) |
| Overlays | — | **JobsDrawer** (O1, right, 400 px), **ProvenanceDrawer** (O3, right, 480 px), sheets (centred, ≤ 720 px), dialogs (≤ 560 px), **CommandPalette** (O11) |

At 768–1199 px the NavRail becomes a 64 px icon rail whose labels show on focus and hover. Below 768 px the masthead
keeps the wordmark, the LaneTab and NeedsYou; a "Menu" button opens the navigation and the chips as a sheet.

#### Routes

| Route | Screen | Presentation |
|---|---|---|
| `/unlock` | S00 Unlock | pre-shell, no navigation |
| `/setup/:step` | S01 First run (browser part) | pre-shell until finished once |
| `/session` | S02 Session start | full page at session start; the same content as a dialog when switching |
| `/library` | S03 Library | shell home |
| `/p/:projectId` | S04 Song page | project home |
| `/p/:projectId/capture` | S05 Capture | |
| `/p/:projectId/melody` | S06 Melody | |
| `/p/:projectId/song` | S07 Song intent | |
| `/p/:projectId/requests/:requestId` | S08 Generation | |
| `/p/:projectId/auditions/:auditionId` | S09 Audition | focused: NavRail collapses to a back link, PlayerBar hidden, margin replaced |
| `/p/:projectId/studio` | S10 Studio | focused workspace, ≥ 1024 px |
| `/p/:projectId/finish` | S11 Finishing | |
| `/eval/:tab` | S12 Evaluation | |
| `/engines/:tab` | S13 Engines & licenses | |
| `/burst` | S14 Burst & monthly cap | |
| `/settings/:section` | S15 Settings | |

Routes use real history entries, so browser Back works everywhere, including inside S01's steps. A URL never carries a
candidate id, route, profile or seed while an audition is open, never a secret or token (the launch token arrives in
the fragment and is removed before anything renders, S00), and never personal data.

#### Masthead chips (exact formats)

| Chip | Normal | Attention | Opens |
|---|---|---|---|
| ComputeChip | "Tier 4 · Mac (MLX) · burst on approval" | "Tier 1 · CUDA host unreachable" (◇) ; "Switching…" | S02 as a dialog |
| StoreChip | "STUDIO · 812 GB free" | "STUDIO · 18 GB free · low" when effective free is under twice the margin; "STUDIO not mounted" (✕) | S15 Storage; O10 when missing |
| CapChip | "$3.12 of $25.00 · Oct" | "Burst blocked · overrun" (✕) | S14 |
| NeedsYou | "2 need you" with the seal glyph | — | a popover listing pending owner acts and auditions (§0.6) |
| Jobs toggle | "Jobs · 2 running" (text, never an icon alone) | "Jobs · 1 failed" | O1 |

When `STUDIO_ENV` is `dev` or `test`, a full-width dashed graphite band sits under the masthead: **"Test environment ·
fake engines · every output is Synthetic test output"** (ADR-0027, T-15).

The document title is "{screen} · {project} · {productName}", prefixed "(2) " while two things need Jon.

#### Responsiveness and browsers

- Every screen works from 320 px to 1920 px without horizontal page scroll. The two 2-D editors (the piano roll in S06
  and the timeline in S10) need a window at least 1024 px wide; below that each shows its editable list alternative.
- A Chromium-based browser is required for the Studio (Q10 default, ADR-0012). In another browser only S10 shows a
  notice; the rest of the app works. Live MIDI input needs Web MIDI, which is Chromium-only (S05 says so).

#### One blinding rule for the whole app

**A candidate can be heard only inside its audition until the verdict is recorded.** No other screen offers a play
control, waveform, duration, loudness or badge for an unrevealed candidate, and the PlayerBar refuses one. This keeps
what Jon saw in a plan (routes and profiles) from turning into a guess about which label is which.

### 0.3 Copy rules

1. **Glossary words, exactly.** In particular: *candidate* (never take, version, variant, output), *keeper* (never
   winner, final, master), *audition* (never listening test, comparison, A/B alone), *verdict* (never vote, rating),
   *capture* (never upload, take), *correction* (never fix, tweak), *revision* (never version, save, draft), *track*
   (never lane; "lane" always means operator lane), *compute tier* (never plan, mode), *quote*, *ceiling*, *monthly cap*
   (never estimate, price, budget alone), *approval* (never consent, OK), *DSP finishing* (never mastering,
   enhancement), *Isolate original* / *Re-perform* / *Create a new part* (never extract, split, clean up), *evidence
   record* (never result, log, proof).
2. Sentence case. Plain, second person ("your hum"). No exclamation marks. Never "magic", "instantly", "perfect",
   "studio-quality", "AI-powered" or "as good as Suno". "Suno" appears only where the Suno boundary applies (imports,
   risk acceptances) and in the quality-target sentence on S12.
3. **Every number carries its figure label**, inline or once in a table header. A VENDOR, COMMUNITY or COMPETITOR-RUN
   figure is never in a column headed as measured and is set in italic Plex with its label, so it never looks like
   AURA's own measurement.
4. **Honest progress.** Only real steps. "Step n of m" only when the engine reports counters. Downloads and transfers
   show bytes. Elapsed time is always shown. Remaining time appears only from MEASURED-LOCAL history, written "Usually
   1–2 min on this Mac (6 runs, MEASURED-LOCAL)". No percentage that a worker did not report as a counter.
5. **Failure copy** says what failed, what is safe, and what Jon can do, in that order: "The worker stopped before
   finishing. Nothing partial was kept. Try again."
6. **Money**: US dollars, two decimals, Plex Mono, in brass. A figure is always named: "Ceiling $0.37", "Settled $0.29
   (provider billing)", "Settled at ceiling $0.37 (no billing data)". Never "about" or "≈" for money counted against
   the cap.
7. **Sizes**: GB (10⁹ bytes), as the model repos and Finder count. Exact bytes in the accessible description and in
   provenance. Margins configured in GiB show both: "10 GiB (10.74 GB)".
8. **Time**: durations `m:ss` (`h:mm:ss` past an hour); edit positions `m:ss.mmm`; musical positions "bar 12 · beat 3";
   clock times in local time, with the UTC instant in provenance. The cap's month is the UTC calendar month shown in
   local time: "October (UTC) · resets Oct 31, 7:00 pm CDT".
9. **Hashes**: Plex Mono, first four and last four hex digits ("4f2a…c41f"), the full hash on focus and hover, one
   Copy action; screen readers hear "hash beginning 4 f 2 a".
10. **Public contact**: `hello@islanddevcrew.com` only, as selectable text, never a `mailto:` link, only in the footer
    and Settings → About. No personal address anywhere (ADR-0037).
11. The product name is only ever `{productName}`. Copy below writes "AURA" for readability; the string catalog uses the
    constant.
12. Every string lives in one message catalog from the first ticket. No string is assembled from fragments in a way
    that blocks translation. Numbers, dates and durations use `Intl` formatters.

### 0.4 State vocabulary

Every screen section lists its states with these names.

| State | Meaning | Default treatment |
|---|---|---|
| **Empty** | Nothing stored yet | **StateBlock**: one sentence, one primary action, at most one secondary |
| **Loading** | Reading local data | Nothing for 300 ms, then staff-line skeletons. Never placeholder numbers |
| **Working** | A job, download or check with real steps | **StepTrail** with the real states, elapsed time and the metronome tick |
| **Error** | A request or job failed | **Banner** or StateBlock: what failed, what is safe, what to do; the failure code in the margin |
| **Partial capability** | The registry, a capability gate, the lane or a missing verified component does not allow something here | The control is replaced by a one-line reason and, where one exists, the remedy ("needs smoke", "not in the LLC lane", "unverified on Windows"). Never an error colour for something not built. Never hidden silently where Jon would expect it |
| **Offline worker** | A worker this screen needs is not running or not reachable | **WorkerBanner** naming the worker and host, what waits, and what still works |
| **Store unavailable** | The STUDIO volume disappeared | O10 takes over; nothing can be kept or recorded |
| **Offline** | No internet | Only downloads, live-rate reads and burst runs change. Everything local is unaffected |
| **Needs you** | An owner act or an audition is waiting for Jon | Seal glyph + "Needs you" + the NeedsYou count |
| **Synthetic** | Output of a `test_only` profile, or synthetic evidence | Dashed graphite badge "Synthetic test output" wherever the artifact appears (except per arm in a blind audition, §0.5), plus the test band |
| **Stale revision** | Another window or an agent moved a revision head | Banner "This changed in another window (revision 8). Your last change wasn't applied." + "Load revision 8" |
| **Blind** | An audition is open for this request | Identities hidden everywhere; jobs shown as ordinals (§0.2 blinding rule) |

### 0.5 Badges, figure labels, lanes, placement and money

**Badges** are plain labels from a hard constraint or a measurement (ADR-0005). They never rank, sort, filter or hide
a candidate; candidate lists keep plan order. The stored value is the `candidate/1` enum value ("duration off",
"unbenchmarked route", …); the UI renders it in sentence case, which is the exact text below.

| Badge (exact text) | Glyph | Ink | Source | Before the reveal |
|---|---|---|---|---|
| Unplayable | ✕ in a hatched square | red pencil | decode failed | **shown** (the only one) |
| Silent | ✕ | red pencil | non-silence check | hidden |
| Duration off | ✕ | red pencil | duration tolerance from the gate record | hidden |
| Clipping | ✕ | red pencil | sample clipping | hidden |
| True-peak over (+0.4 dBTP) | ✕ | red pencil | AURA's ≥ 4× oversampled meter | hidden |
| Lyric errors high (PER 31 %) | ✕ | red pencil | lyric PER above the gate | hidden |
| Melody not kept | ✕ | red pencil | adherence outside the thresholds of the committed adherence gate record, on a real candidate only while `adherence.real-separator` is smoke-passed | hidden |
| Adherence unmeasured (no LLC separator yet) | ◌ dotted circle | graphite | LLC lane, ADR-0029 | hidden |
| Lyric errors unmeasured | ◌ | graphite | no verified G2P yet (TB8) | hidden |
| Synthetic test output | ⬚ dashed square | graphite | `synthetic_test` | per arm hidden; an audition-level notice shows instead |
| Unverified on real hums | ◇ open diamond | graphite | transcriber status | — |
| Needs smoke | ◇ | graphite | profile below smoke-passed on this host class | — |
| Unbenchmarked route | ◇ | graphite | a candidate whose route has no benchmark record (the plan itself carries the label "Unbenchmarked routes") | — |
| Separated · unreviewed | ◇ | graphite | an isolated stem before Jon's listening verdict on that separator revision | — |
| Not for release (research lane) | ◇ | graphite | an export in a research project, or with an uncovered release blocker | — |
| Diagnostic only | ⓘ | graphite | audiobox-aesthetics or CLAP (v1-studio) | hidden |

Passing checks are not badges. They appear as measurements in the margin and the ProvenanceDrawer ("Melody adherence:
median 41 cents · onset F1 0.78 · MEASURED-LOCAL").

**FigureLabel** renders the label in `--type-label` inside a hairline box: MEASURED-LOCAL in verdigris; VENDOR,
COMMUNITY and COMPETITOR-RUN in graphite beside an italic figure; OWNER-REPORTED in ink-2; INFERRED in graphite with a
dotted underline on its figure; UNVERIFIED in graphite beside the ◇ glyph, where no check has been made.

**LaneTab**: "◯ Individual", "▢ LLC", "△ Research". Glyph and word always together, in ink; lanes are never
colour-coded. Eligible lanes read "Eligible: ◯ Individual · △ Research".

**Placement chips**: "This Mac · MLX", "Worker host · linux-4090 · CUDA", "Burst · RunPod · 24 GB class · paid" (with
the coin glyph, brass). Host class appears in provenance ("mlx/m5pro").

**Other glyphs**: the seal (octagon with a centre dot, brass) marks owner acts; ✓ in a square (verdigris) marks evidence
that passed; a lock marks irreplaceable artifacts; the coin marks paid placements.

### 0.6 Owner acts in the interface: the seal

The owner acts (ADR-0031) are: approving a quote, changing the monthly cap, acknowledging an overrun or a
reconciliation adjustment, changing a project's operator lane, recording a verdict, accepting a risk, accepting a model
license, recording a reference permission and attesting an import. This spec also treats
Jon's "not garbled" smoke check as one (§6 Q2).

- Every owner act is a **SealButton**: 2 px brass outline, the seal glyph, and a label that names the act and its
  object ("Approve and reserve $0.37", "Record verdict", "Accept the MIT license for ACE-Step 1.5 weights").
- A SealButton is never the default button. Enter never triggers it unless it has focus. It is the last control in its
  dialog's tab order and never sits where a double-click on the previous control could land.
- Its accessible description is "Owner act. Only you can do this, from this browser."
- After the act, a receipt line appears in the margin: "Recorded 14:21 · verdict 9c1e…77a0".
- If this browser has lost the owner-ui scope, every SealButton is disabled with "Unlock this browser to do this"
  (→ S00).
- A 403 from the API reads: "Only you can do this, from the AURA window you unlocked. Scripts and agents can prepare
  it but can't do it."
- **NeedsYou popover** lists what is waiting, newest first, each with who prepared it: "Approve a paid run · Morning
  Light · ceiling $0.37 · expires 14:32 · quote prepared by the eval harness 14:02"; "Audition ready · Morning Light ·
  2 candidates"; "Listen to the smoke render · ace-2b-sft-mlx"; "Acknowledge an overrun · $0.15 over".

### 0.7 Accessibility baseline

- WCAG 2.2 AA as the floor. Text ≥ 4.5:1 and graphics ≥ 3:1 in both themes and in increased contrast (§0.1).
- Everything is operable from the keyboard. The focus indicator is a 2 px `--ink` outline with a 2 px `--paper`
  offset and is never removed. Focus order follows reading order. Drawers, sheets and dialogs trap focus and return it
  to the control that opened them.
- Targets are at least 24 × 24 CSS px everywhere, at least 44 × 44 for primary actions and transport, and 72 × 72 for
  the record button and the audition arms.
- A "Skip to main content" link, landmarks as in §0.2, one `h1` per screen, headings nested without gaps.
- Screen readers: every icon-only control is named; every glyph has its words; one shared live region announces job
  changes `polite` (at most one announcement per job every 2 s); `assertive` only for things that need action now
  (STUDIO unmounted, a recording stopped by an error, an approval expiring while its dialog is open).
- **Meaning never by colour alone.** Badges are glyph + text; lanes glyph + text; selection is `--selection` + a 3 px
  brass left rule + a check glyph + `aria-selected`; piano-roll confidence is opacity + a dotted outline + a "?" glyph
  + text in the list view; section markers carry their names.
- Reduced motion and increased contrast as in §0.1. Settings can force either.
- Audio never plays on load. Every audio has a visible play control. The level meter and the loudness report have
  numeric text equivalents. Lyrics are shown as text wherever a vocal plays.
- Every chart has "Show as table" and a one-sentence summary.
- The 2-D canvases (piano roll, timeline, time ruler) are `role="application"` with an `aria-roledescription`, a
  documented keyboard model, and a fully editable list or table alternative (**NoteList**, **TrackList**). WCAG 1.4.10
  exempts 2-D content from reflow; the alternatives make the exemption unnecessary in practice.
- Text zooms to 200 % without loss and reflows at 320 px on every screen. Browser zoom shortcuts are never captured.
- Time limits: the 15-minute approval expiry is part of what an approval means (WCAG 2.2.1's essential exception). The
  dialog warns at 2 minutes, and getting a new quote is one action.
- Single-key shortcuts can be turned off in Settings (WCAG 2.1.4).
- Playwright runs an automated accessibility audit on every screen and every state listed in this spec (arch §6.1).

### 0.8 Keyboard model (global)

Modifiers display per OS: ⌘ and ⌥ on macOS, Ctrl and Alt on Windows and Linux. "Mod" below means ⌘ or Ctrl.

| Keys | Action | Notes |
|---|---|---|
| `?` | Keyboard map (O11) | outside text fields |
| Mod+K | Command palette (O11) | never performs an owner act; it can open the dialog |
| `G` then a letter | Go to: `L` Library, `S` Song page, `C` Capture, `M` Melody, `I` Song intent, `R` latest generation request, `A` open audition, `T` Studio, `F` Finishing, `E` Evaluation, `X` Engines & licenses, `B` Burst & monthly cap, `,` Settings | outside text fields; a two-key sequence within 1 s |
| Shift+J | Jobs drawer | |
| Shift+P | Provenance drawer for the focused artifact | refused for an unrevealed candidate |
| Space | Play or pause the screen's player | when focus is on the page or a non-button element; on a focused button Space activates the button |
| Esc | Close the topmost drawer, sheet or dialog; cancel a gesture in progress | never cancels a request already sent |
| Mod+Z, Shift+Mod+Z | Undo, redo | where the screen has undo (S06, S07 fields, S10) |
| F6, Shift+F6 | Next, previous landmark | masthead → nav → main → details → player |

### 0.9 User-story groups

The product spec's user stories are grouped under these names. If the product spec names a group differently, rename
here; do not fork. Each screen section ends with the groups it serves; §4 maps each group back to feature IDs, ADRs and
tracer bullets.

| Group | Covers |
|---|---|
| **G01 Install, studio volume and disk preflight** | `studioctl setup`, the STUDIO sparse bundle on Backup Plus, probes, preflight, stray caches, first downloads |
| **G02 Compute tiers and sessions** | detection, recommendation, choosing and switching a tier, placement per profile, worker hosts |
| **G03 Library and projects** | the library, new songs, the Song page as project home, autosave and crash safety |
| **G04 Melody capture** | hum or sing, import a recording, MIDI file, live MIDI |
| **G05 Transcription and correction** | transcription with confidence, piano-roll corrections, tempo map, key, meter, phrases, revisions |
| **G06 Song intent** | SongSpec: style, exclusions, vocal mode, approved lyrics and language, SongForm, references, candidate count, routes per lane and compute profile, intent vs actual |
| **G07 Generation, routes and jobs** | the plan with reasons, explicit choice, honest job states, cancel, failure, re-roll |
| **G08 Audition, verdict, reveal and keeper** | blind level-matched A/B, verdict with reasons, reveal, failure badges, keep, "kept n of m" |
| **G09 Provenance, keeper cost and export** | how an artifact was made, the license chain, keeper cost, the export bundle and manifest |
| **G10 Studio timeline and edits** | timeline, transport, sections, replacement tracks, Copy to main track, edit operations and the preservation check |
| **G11 Stems** | Isolate original with its residual, the three stem operations, aligned stem export |
| **G12 Evaluation** | reference standards, the hum benchmark, briefs and preregistration, runs, eval auditions, evidence with uncertainty |
| **G13 Engines, registry and licenses** | profiles and their computed status, capabilities, the component register, downloads and license acceptance |
| **G14 Imports and the Suno boundary** | references with permission records, imported mixes, DSP finishing of a Suno download, risk acceptances |
| **G15 Paid runs and the monthly cap** | quotes, approval, reservation, settlement, the ledger, overruns, the cap |
| **G16 Owner acts and local security** | unlock, owner-ui vs automation scope, NeedsYou, secrets never in the client |
| **G17 Operator lanes** | lane per project, lane-aware routes and separators, lane change, export lane checks |
| **G18 Platforms and capabilities** | per-OS gates (`studio.playback`, `capture.mic`), Chromium requirement, portable copy |
| **G19 Accessibility** | §0.7 on every screen |
| **G20 Honest labels and progress** | figure labels, badges, honest job states, nothing called done without evidence |
| **G21 Failure and recovery** | store loss, worker loss, restart reconciliation, stale revisions, backup reminders |

### 0.10 Modules and resources the screens use

Every screen reads and writes only through the generated typed Studio API client (ADR-0025). Screens never compute
lane eligibility, profile status, plans, quotes or gains themselves; they show what the modules returned.

| Module (arch §4) | Screens |
|---|---|
| ProjectStore (`/system`, projects, captures, artifacts, exports, events) | all |
| Conductor (jobs, SSE `GET /api/v1/events`) | S05–S13, O1 |
| Registry (`/registry`, admission refusals, `/evidence`, `/licenses/{c}/accept`) | S07, S08, S13, O7 |
| Placement (`/compute/*`, `/sessions`, quotes, `/budget`) | S01, S02, S08, S14, O2 |
| Score (revisions, `as/midi\|abc\|guide`, `song`, plans) | S06, S07, S08 |
| Audition (`audition/1`, audio by label, verdict, reveal, keepers) | S09 |

### 0.11 Narration must not be precluded

The narration service gets its own spec (ADR-0008), but these surfaces render whatever the shared contracts carry and
must not assume music: the JobsDrawer (any job kind), the ProvenanceDrawer (every `Artifact.origin`, `tts_render`
included), the Export sheet's manifest view, Engines & licenses, Burst & monthly cap, and Settings → Storage. The
Library groups by `Project.kind` and hides the kind column while only songs exist.

---

## 1. Screens

Each section gives: Purpose · Scope and phase · Route and entry · Layout · Components · Key copy · States · Keyboard ·
Accessibility · Story groups. "Key copy" lists strings not already quoted in Layout. Braces mark values filled at run
time; every concrete number shown is an example.

---

### S00 Unlock (`/unlock`)

**Purpose.** Give this browser the owner-ui scope (ADR-0031) so Jon can perform owner acts here and nowhere else.

**Scope and phase.** v1-core · P0 (TB0).

**Route and entry.** Shown whenever the browser has no valid owner-ui cookie. `studioctl serve` prints a link of the
form `http://127.0.0.1:{port}/unlock#launch={token}`. The page reads the fragment, exchanges the token for the
`SameSite=Strict` cookie, and removes the fragment with `history.replaceState` before anything renders. The token is
never in a query string, never logged and never stored by the page. Pasting the code is the fallback.

**Layout.** One raised sheet, 480 px, centred on vellum: wordmark; title "Open your studio"; body text; a code field
with a show/hide toggle; the primary button; a small note; the footer.

**Components.** **Wordmark**, **CodeField**, **Button** (ink), **Banner**.

**Key copy.**
- Body: "Use the link `studioctl serve` printed in your terminal. If you opened AURA another way, paste the launch code
  here."
- Field label "Launch code"; button "Unlock this browser".
- Note: "The code works once. It becomes a cookie that only this browser keeps, for AURA only."
- Success (no screen; redirects): to S01 if first run is unfinished, else S02 if a session must start, else the page
  that sent Jon here.

**States.**
| State | Treatment |
|---|---|
| Exchanging | Button shows "Unlocking…" (no spinner under 300 ms) |
| Error: used or invalid code | Banner: "That code has been used or isn't valid. Stop `studioctl serve` and start it again for a new one." |
| Error: wrong origin | Banner: "This page must be opened at the address `studioctl serve` printed (127.0.0.1)." |
| Store unavailable | O10 (the service refuses new work without STUDIO) |
| Offline worker, partial capability | Not applicable: unlocking needs only the control service |

**Keyboard.** Tab order: field → show/hide → Unlock. Enter in the field submits.

**Accessibility.** The field has a visible label and `autocomplete="off"`. Errors are announced `assertive` and linked
with `aria-describedby`. The sheet is the page's `main`.

**Story groups.** G16, G19.

---

### S01 First run: install in the terminal, then in the browser

**Purpose.** Put AURA's store on the Backup Plus drive without reformatting it, prove the volume works, show what the
hardware can do and recommend a compute tier, make sure no write can fill a disk, and install the first engine.

**Scope and phase.** v1-core · P0 (TB0); the engine step is P2 (TB3).

**Why two parts.** The control service refuses to start without a mounted, matching, unlocked store (arch §3.1). So
the volume is created by `studioctl setup` in the terminal, and the browser part (`/setup/:step`) begins the first time
`serve` runs. Both parts are specified here as screens; the terminal output is copy too.

#### S01a `studioctl setup` (terminal)

Plain text, no colour codes that carry meaning, no emoji, one step per block, every command AURA runs shown before it
runs. It never runs `sudo`; anything that needs admin rights is printed for Jon to run (arch §8.1).

```
AURA setup · macOS {version} · this Mac: Apple M5 Pro, 48 GiB unified memory

1  Where the studio lives
   Found: /Volumes/Backup Plus  (exFAT · USB · 1.1 TiB free)
   AURA keeps everything in one APFS disk image on this drive, called STUDIO.
   Nothing on the drive is reformatted or moved.
   Image:         /Volumes/Backup Plus/STUDIO.sparsebundle
   Logical size:  900g   (a cap, not space used now; press Enter, or type another size)

2  Creating and attaching STUDIO
   $ hdiutil create -type SPARSEBUNDLE -fs APFS -volname STUDIO -size 900g \
       -imagekey sparse-band-size={band} "/Volumes/Backup Plus/STUDIO.sparsebundle"     done
   $ hdiutil attach -nobrowse -owners on -mountpoint /Volumes/STUDIO \
       "/Volumes/Backup Plus/STUDIO.sparsebundle"                                      done

3  Checking the volume (each check could fail; results are kept as evidence {hash})
   owners on   pass    symlinks   pass    chmod   pass    hardlinks   pass    clonefile   pass

4  Pointing caches and environments at STUDIO
   Wrote ~/.config/studio/env (HF_HOME, UV_*, PIP_CACHE_DIR, TORCH_HOME, XDG_CACHE_HOME, TMPDIR,
   PLAYWRIGHT_BROWSERS_PATH, the MLX cache limit, the pnpm store).

5  Keeping the volume quiet
   Spotlight: wrote .metadata_never_index at the root.
   Owner action (needs admin rights, run it yourself):   mdutil -i off /Volumes/STUDIO
   Time Machine: excluded (sticky). Your real backup of irreplaceable work is `studioctl store backup`.

6  This machine
   Recommended compute tier: 4 (Apple Silicon: ACE runs here; YuE2 runs as a burst, with your approval each time).
   Wrote the default compute profile. You can choose any tier when a session starts.

Next: studioctl serve
```

On Windows and Linux step 1 reads "Choose a folder on a native filesystem (NTFS or ext4) for the studio" and steps 2
and 5 are replaced by "Using {path} as the studio root (a plain folder with the same layout)." A failed probe prints
"fail", the consequence ("hardlinks fail, so caches will copy instead of linking and use more space"), and "Run
`studioctl doctor` for details." If no drive is found: "No external drive found at /Volumes/Backup Plus. Connect it, or
pass a path with --root."

#### S01b First run in the browser (`/setup/:step`)

**Route and entry.** The first UI load after setup, straight after S00, until step 6 is finished once. A **StepRail**
across the top reads "Step 3 of 6 · Studio volume". Each step is a real route, so Back works.

**Layout.** One column, max 840 px, with the margin column at ≥ 1200 px holding "What AURA has checked so far" (a list
of evidence records created during setup, each with ✓ and its hash). A footer bar holds "Back" (quiet) and the step's
primary action (ink).

**Step 1 · Welcome.** Title "A studio that runs on your machines". A short colophon, four lines with a staff rule
above and below:
1. "Your melody becomes a melody you own and can correct, before any engine hears it."
2. "Nothing is called done until a check that could fail has passed."
3. "You approve every paid run. Rented GPUs are capped at $25 a month."
4. "Engines run on hardware you control, and every result says how it was made."
Primary "Begin".

**Step 2 · This machine.** Title "What this machine can do".
- **HardwareSnapshotCard** for each reachable host: "Apple M5 Pro · 48 GiB unified memory · Metal working set 37.44 GiB
  (MEASURED-LOCAL)". "Show the raw output" disclosure holds the recorded `sysctl` and `system_profiler` text.
- Recommendation block: "Recommended: tier 4. Apple Silicon runs ACE-Step here with MLX. YuE2 needs an NVIDIA GPU, so
  in tier 4 it runs as a rented burst, and each run needs your approval." Warnings, if any, as a list with ◇ glyphs.
- Four **TierCards** as a radio group (S02 defines them). Tier 4 is preselected from the profile setup wrote.
- "Linux and Windows machines: not reachable. Add one later with `studioctl worker add <url>`."
- Primary "Use tier 4" (label follows the selection: "Use tier 2").

**Step 3 · Studio volume.** Title "Where your work lives".
- **VolumeCard**: "STUDIO · APFS disk image on Backup Plus · 900 GB cap · {free} GB free". "Backup Plus is a spinning
  hard drive on USB. Models load more slowly from it; AURA keeps one model loaded to make up for it."
- Probe rows with ✓ and their evidence hash: owners, symlinks, chmod, hardlinks, clonefile.
- Speed rows: "Sequential read {n} MB/s · write {n} MB/s · random 4K {n} IOPS (MEASURED-LOCAL, {date})", or when not yet
  measured: "Not measured yet" with "Measure now" (a `doctor` job that reads and writes 1 GiB; progress in bytes). The
  band size row reads "Band size 8 MiB (default, unmeasured)" until P0's 8-vs-64 MiB record exists.
- **CommandBlock**: `mdutil -i off /Volumes/STUDIO` with Copy and the label "Owner action · needs admin rights".
- Backup row (attention, not error): "No second copy yet. Backup Plus is one physical drive, so until you choose a
  backup device, irreplaceable work has no backup. Choose one in Settings → Storage." Choosing is owner-pending, so
  this step never blocks on it.
- Primary "Continue".

**Step 4 · Room to work.** Title "Making sure nothing fills a disk".
- **PreflightRows**, one per volume:
  - "This Mac's internal disk · 9.5 GB free (MEASURED-LOCAL, now). AURA writes nothing here. Heavy jobs pause while
    it has under 2 GiB free, because macOS swaps to it."
  - "STUDIO · {effective} GB usable · the smaller of the disk image's free space and Backup Plus's free space, minus
    band overhead. AURA always keeps 10 GiB (10.74 GB) spare."
- "Old caches on the internal disk" table: path, size (MEASURED-LOCAL), Copy path. Copy above it: "From now on these
  caches go to STUDIO. The old ones are still on your internal disk. Deleting them is your call; AURA never deletes
  them."
- Primary "Continue".

**Step 5 · First engine.** Title "Install your first engine".
- **DownloadRow** for `ace-2b-turbo-mlx` (draft): "ACE-Step 1.5 · 2B turbo, with its text encoder and VAE ·
  {size} GB from the repo listing (about 6.34 GB, VENDOR)". Destination "STUDIO · models". Preflight result inline
  ("Fits: {free} GB usable, needs {size} GB, keeps 10 GiB spare").
- License line: "Code and weights: MIT · ungated · allowed in every lane".
- **SealButton** "Accept the MIT license and download" (owner act; O7 shows the detail first).
- After acceptance, a StepTrail with real steps: Download ({bytes} of {total}) → Verify every file's hash → Build the
  engine's environment → Conformance → Smoke render → Your listening check → Smoke-passed (computed). The listening
  check and the smoke steps continue in S13 if Jon leaves.
- Secondary "Skip for now". Skipping is honest: "Without an engine you can capture and correct melodies, but AURA can't
  make candidates yet."

**Step 6 · Ready.** Title "Your studio is set". Summary list: "Tier 4 on this Mac", "STUDIO on Backup Plus", "ACE-Step
1.5 2B turbo: {status}". Primary "Hum your first melody" (opens O5, then S05). Secondary "Open the library".

**Components.** StepRail, HardwareSnapshotCard, TierCard, VolumeCard, CommandBlock, PreflightRow, DownloadRow,
SealButton, StepTrail, Banner.

**States.**
| State | Treatment |
|---|---|
| Loading | Each card loads independently; skeletons after 300 ms |
| Working | Measuring the drive, downloading, verifying: StepTrail with bytes and elapsed time |
| Error: a probe failed | Row shows ✕ with the consequence and "Run `studioctl doctor` for details"; Continue stays enabled, because AURA still works |
| Error: download hash mismatch | "File {n} of {m} didn't match its hash. It was deleted, and nothing was installed. Try again." |
| Error: preflight refused | "Not enough room on STUDIO: {free} GB usable, this needs {size} GB, and AURA keeps 10 GiB (10.74 GB) spare. Free some space, or raise the image's size cap in Settings." |
| Partial capability | Engine step on a host with no smoke-passed profile yet: the StepTrail stops at "Your listening check" until Jon listens |
| Offline worker | Analysis worker did not start (needed for the probe and the measurement): "The analysis worker didn't start. Run `studioctl doctor`, then reload." |
| Offline | Engine step: "Downloads need the internet. You can finish setup and install later." |
| Store unavailable | O10 |

**Keyboard.** Tab moves through the step; Enter activates the focused control; the StepRail items are links (only for
steps already reached). Arrow keys move within the tier radio group.

**Accessibility.** StepRail is an ordered list with `aria-current="step"`. Each probe and preflight row is one list item
with its status in words. The CommandBlock's Copy button is named "Copy command: mdutil -i off /Volumes/STUDIO".

**Story groups.** G01, G02, G13, G16, G20.

---

### S02 Session start: the compute switcher (`/session`)

**Purpose.** At the start of every session, show what hardware is reachable, recommend a compute tier with reasons, show
all four tiers with the evidence each has, and let Jon keep or change the tier in one action. The same content, as a
dialog, switches the tier at any time (O-02, ADR-0003).

**Scope and phase.** v1-core · P0 (TB0); worker hosts appear in P6.

**Route and entry.** Full page on the first UI load after each `serve` start, and after an idle gap (default 4 hours,
one constant; §6 Q5). As a dialog from the ComputeChip at any time.

**Layout (full page).**
1. Title "Start a session". Subline: "Last session: tier 4 · Oct 8, 9:40 pm".
2. "Since last time" list: "Nothing changed." or items such as "linux-4090 is now reachable on the tailnet" and "Driver
   570.12 on linux-4090 is older than YuE2 needs (570.26)".
3. Hosts: one HardwareSnapshotCard per reachable host, with "Show the raw output".
4. Recommendation block (as in S01 step 2), with reasons and warnings.
5. Four **TierCards** in a radio group (2 × 2 at ≥ 1200 px, one column below). Each card:
   - Newsreader numeral and name: "1 · NVIDIA 24–32 GB", "2 · NVIDIA 24 GB", "3 · NVIDIA 12–16 GB, with offload or
     burst", "4 · Apple Silicon, plus a rented burst".
   - "Where things run" rows for ACE, YuE2 (individual lane), burst, analysis and separation, read from
     `compute-tiers.v1.json` and the resolved placements.
   - "Evidence on matching hardware": each profile with ✓ (status computed on that host class) or ◇ "needs smoke".
   - When the hardware cannot satisfy the tier, the card says so before anything is chosen: "No CUDA host is reachable.
     In this tier ACE would be unavailable here and YuE2 would run only as a burst." Each placement shows `burst` or
     "Unavailable: {reason}. {remedy}".
6. "Advanced: placement per engine profile" disclosure: a table of profile × {This Mac, a worker host, Burst} with the
   current choice; changing one shows the same consequences inline.
7. Footer bar: primary "Keep tier 4" (or "Start on tier 2" when the selection differs); secondary "Hosts and workers"
   (S15 Compute).

**Switching during a session (dialog).** Same cards, then an impact summary computed by Placement before confirming:
- "2 jobs not yet dispatched will be re-planned."
- "1 job waiting for approval will be re-quoted. Its approval is void."
- "1 running job finishes where it is." with "Cancel it" per job.
- "Projects never change when you switch. The switch is logged in this session's record."
Primary "Switch to tier 2"; secondary "Keep tier 4".

**Components.** HardwareSnapshotCard, TierCard, PlacementTable, ImpactSummary, Banner, WorkerBanner.

**Key copy.** Already given above. A tier chosen against the recommendation adds, without blocking: "You chose tier 2.
AURA recommended tier 4 for this hardware. Anything the hardware can't run will be placed as shown on the card."

**States.**
| State | Treatment |
|---|---|
| Loading | "Checking this machine…" StepTrail of the real probes (sysctl, system_profiler, Metal working set, each reachable host's describe) |
| Empty | Never empty: the studio host always has a snapshot. Other hosts: "Linux and Windows machines: not reachable. Add one with `studioctl worker add <url>`." |
| Error: a probe failed | "This host wasn't probed, so it can't qualify for a tier." on that host's card |
| Partial capability | No accelerator: "No GPU found. Tier 4, burst only: every candidate would need a paid burst run." |
| Offline worker | A registered worker host is unreachable: its card is outlined dashed with "Unreachable since 14:02. Jobs placed there will wait or be re-planned when you switch." |
| Offline | Burst rows read "Burst runs need the internet" |
| Store unavailable | O10 |

**Keyboard.** Arrow keys move among tier cards (radio group); Enter confirms the primary action; Esc (dialog only)
keeps the current tier. Within the advanced table, arrows move between cells and Space selects a placement.

**Accessibility.** The radio group is named "Compute tier". Each card's accessible name is its numeral and name; its
description summarises placements and evidence ("ACE here; YuE2 as a burst; 2 profiles have evidence, 1 needs
smoke"). The impact summary is announced when it changes.

**Story groups.** G02, G15, G18, G20.

---

### S03 Library (`/library`)

**Purpose.** Every song and imported mix in one ruled ledger, with what needs Jon at the top.

**Scope and phase.** v1-core · P1 (TB1).

**Route and entry.** Shell home; `G L`; the wordmark.

**Layout.**
1. Title "Library".
2. **WaitingForYou** strip, only when something is waiting: rows such as "Audition ready · Morning Light · 2
   candidates" [Open], "Approve a paid run · Morning Light · ceiling $0.37 · expires 14:32" [Review], "Listen to the
   smoke render · ace-2b-sft-mlx" [Listen], "Acknowledge an overrun · $0.15 over" [Review]. Each row carries the seal
   glyph when it is an owner act.
3. Toolbar: **SearchField** "Search songs"; filter chips for lane (◯ Individual, ▢ LLC, △ Research) and state (Has a
   keeper, In progress, Imported mixes); sort menu (Last touched (default), Title, Created); primary "New song" (ink).
4. **SongLedger**: a ruled table at ≥ 768 px; stacked rows below. Columns: Title (Newsreader 1.25rem) with its LaneTab ·
   Where it is (movement numeral and words, for example "V Listen · audition ready") · Keeper (duration and a play
   button, or "—") · Last touched. Rows are never cover-art tiles.
5. "Imported mixes" section, the same ledger: Title · Source ("Suno · your download", "Your own DAW mix") · Allowed uses
   ("Listen · measure loudness · DSP finishing") · Imported.

**Components.** WaitingForYou, SearchField, FilterChips, SortMenu, SongLedger, LaneTab, PlayButton, StateBlock, Banner.

**Key copy.**
- Empty: title "Your first song starts with a melody." Body "Hum it, sing it or play it. AURA turns it into a melody you
  can correct, then into two candidate songs you judge blind." Primary "Hum a melody". Secondary "Import a MIDI file".
- No match: "No songs match "{query}"." [Clear search].

**States.**
| State | Treatment |
|---|---|
| Empty | StateBlock above |
| Loading | Ledger skeleton (staff lines) after 300 ms |
| Error | "AURA couldn't read the library. Your work is safe in the store. Run `studioctl store fsck`, then reload." |
| Partial capability | No profile is smoke-passed on this host class: Banner "No engine has passed its smoke gate on this Mac yet. You can capture and correct melodies; candidates need an engine." [Engines & licenses] |
| Offline worker | Not used by this screen; waiting rows say when they depend on one ("waiting for linux-4090") |
| Store unavailable | O10 |
| Synthetic | Rows whose keeper is synthetic carry the badge |

**Keyboard.** `/` focuses search; ↑/↓ move between rows; Enter opens the song; Space plays the focused row's keeper;
`N` opens the new-song sheet (O5).

**Accessibility.** The ledger is a table with column headers and a caption ("Songs, newest first"); each row's title is
a link; the play button is named "Play the keeper of {title}, {duration}". Filter chips are toggle buttons with
`aria-pressed`. The waiting strip is a list with a heading "Waiting for you".

**Story groups.** G03, G15, G16, G17, G19.

---

### S04 Song page (`/p/:projectId`)

**Purpose.** The project's home: where the song stands, its keeper, how it was made, what it cost, and its exports.

**Scope and phase.** v1-core · P1 (TB1b); keeper revisions from edits are v1-studio (P5).

**Route and entry.** From the Library, `G S`, the project title in the masthead and NavRail.

**Layout.**
1. Kicker "Song" · title `--type-display`, editable in place (the project name) · LaneTab with "Change lane" (O6).
2. **MovementSpine**: "I Seed ✓ · II Melody ✓ revision 7 · III Song intent ✓ revision 3 · IV Render ✓ · V Listen ✓ ·
   VI Finish —". Each item links to its screen; the current one is marked in words ("You are here" for screen readers
   and the visible underline).
3. **KeeperCard** (when a keeper exists): a 72 px play button, a single waveform (display only), duration, native media
   facts ("48 kHz · stereo · float32"), keeper revision ("Keeper revision 2 · from 'Replace section: Chorus 2'"), the
   route, profile and seed (revealed), and every badge. Actions: "Export…" (O4), "Open in the Studio" (S10), "Finish"
   (S11), "How this was made" (O3).
   Without a keeper: a StateBlock naming the next step from the spine ("Your melody is ready. Next: song intent.").
4. "Approved lyrics": read-only, section tags in small caps; "Edit in song intent".
5. "Generation requests", newest first, each a disclosure: "Request 3 · SongSpec revision 3 · Oct 9 · 2 candidates ·
   Prefer B · kept B". Opened: both candidates with route, profile, seed and every badge, and the per-route record
   ("R2-synth kept 3 of 5"). A request whose audition is still open reads only "Audition open" (§0.2 blinding rule).
6. **KeeperCost**: "This keeper took 6 candidates (2 re-rolls) · compute $0.29 settled · cold load 3:12, warm 1:04
   (MEASURED-LOCAL) · listening 11:40". Cost is never shown per candidate (ADR-0023).
7. "Exports": rows "Export 2 · Oct 9, 3:41 pm · verified · 5 files · individual lane" with "Save as .zip", "Copy folder
   path", "Manifest".
8. "Inputs": "2 captures · MelodySpec revision 7" with links.

Margin: the keeper's eligible lanes, placement and host class, license chain ("ACE-Step 1.5 (MIT) · NeutralVoice
(AURA) · pYIN+HMM (ISC)"), human contributions ("Melody, lyrics, 27 corrections, choices"), AI-disclosure flag and its
reasons, retention class ("Irreplaceable · in the backup closure").

**Components.** LaneTab, MovementSpine, KeeperCard, Waveform, Badge, ApprovedLyrics, RequestHistory, KeeperCost,
ExportRow, StateBlock, ProvenanceDrawer (O3), ExportSheet (O4).

**Key copy.** Title placeholder "Untitled song {n}". Lane note for LLC projects in the margin: "LLC lane: YuE2, Demucs
and every non-commercial component stay out of this song."

**States.**
| State | Treatment |
|---|---|
| Empty (new song) | Spine all pending; StateBlock "Start with a melody." [Capture] |
| Loading | Skeletons after 300 ms |
| Error | "This song didn't load. Your work is safe in the store." [Try again] |
| Partial capability | No engine smoke-passed: the spine's IV shows ◇ "needs an engine" |
| Offline worker | Export job waiting: "Export is waiting for the analysis worker." |
| Store unavailable | O10 |
| Blind | Requests with an open audition show only "Audition open" |
| Synthetic | KeeperCard and the requests carry "Synthetic test output" |

**Keyboard.** Space plays the keeper; `E` opens the export sheet; Shift+P opens provenance; ↑/↓ move between requests
and Enter expands one.

**Accessibility.** The spine is an ordered list named "Where this song is", with each item's state in words. The
KeeperCard's play button is named "Play the keeper, {duration}". The waveform is decorative (aria-hidden); the
duration and media facts are text.

**Story groups.** G03, G08, G09, G17, G20.

---

### S05 Capture (`/p/:projectId/capture`)

**Purpose.** Take Jon's melody into the project exactly as he performs it: hummed or sung into a microphone, an
existing recording, a MIDI file, or a live MIDI performance (O-04, ADR-0004).

**Scope and phase.** v1-core. MIDI file P1 (TB1a); microphone and recording P1 (TB1c); live MIDI P2 (TB4).

**Route and entry.** `G C`; the spine's "I Seed"; "Hum your first melody" (S01) after O5.

**Layout.** Kicker "I · Seed", title "Capture". An ARIA tab list: "Hum or sing" · "Import a recording" · "MIDI".
Below the tabs, "Captures in this song".

**Hum or sing** (default tab).
- Centre: the **RecordButton** (72 px red-pencil disc with a white dot; "Record", then a square and "Stop"), and beside
  it a 240 px tall **LevelMeter** in a sunk well: dBFS scale from −60 to 0 with marks at −18, −12, −6, −3 and 0; the
  live bar; a numeric "Peak −7.2 dBFS"; on clipping, a hatched cap and the text "Clipped at 0:12", kept until Jon
  presses "Reset".
- An elapsed timer in Plex Mono.
- Input select: "Input: {device name}".
- **InputChecks**, read from the track's `getSettings()` after the stream opens: "Echo cancellation: off ✓", "Noise
  suppression: off ✓", "Auto gain: off ✓", "Sample rate: 48,000 Hz (device)".
- Guidance (`--type-small`): "Hum or sing the melody once through. Words are optional. Tempo and key are worked out
  later, and you can correct every note." and "Aim for peaks around −12 dBFS. If the meter reaches 0, move back from
  the microphone."
- After Stop, **CaptureReview** replaces the centre: a waveform, play, duration, "Keep this capture" (ink) and "Record
  again" (quiet; nothing is stored).
- Keeping: hashing in the browser → sending it (bytes shown) → the store verifies the hash → "Kept · sha256 7c1d…9e02 ·
  verified by the store" → the transcribe job starts → link "Watch it become a melody" (S06).

**Import a recording.**
- A drop zone: "Drop a WAV file, or choose one".
- Helper: "A phone voice memo works once it's saved as WAV. AURA can't open .m4a yet: its decoder's license is still
  being checked." (ADR-0004; RECONCILIATION §4.9.)
- After a file is chosen: rate, channels and duration, then "Keep this capture".

**MIDI.** Two cards side by side (stacked below 768 px):
- "MIDI file": drop zone for `.mid` or `.midi`. A multi-track file asks "This file has 3 tracks. Which one is the
  melody?" with a track list showing note counts and ranges. Then "Keep this MIDI".
- "Play it live" (Web MIDI): device select, the same RecordButton, and a small live roll that draws notes as they
  arrive. After Stop: "Keep this performance".
- Shared note: "MIDI becomes your melody as played, with no transcription. You can quantize it later."

**Captures in this song.** Rows: lock glyph · kind ("Hum · 0:41 · 48 kHz mono", "MIDI file · 64 notes", "Live MIDI ·
52 notes") · time · hash · "Used by MelodySpec revisions 1–7". Captures are never edited or deleted here; "Irreplaceable"
is their retention class.

**Components.** Tabs, RecordButton, LevelMeter, InputChecks, CaptureReview, DropZone, TrackPicker, LiveMidiRoll,
CaptureRow, Banner, WorkerBanner.

**Key copy.**
- Recording announcements: "Recording", "Recorded 41 seconds".
- Silent recording (browser-side RMS check before keeping): "Nothing was heard above −60 dBFS. Check the input and try
  again." Keeping stays allowed.
- Hash mismatch: "The store's hash didn't match this browser's (7c1d… against 7c1e…). Nothing was kept. Try again."

**States.**
| State | Treatment |
|---|---|
| Empty | No captures: the list reads "No captures yet." |
| Loading | Device list "Finding inputs…" |
| Working | Hashing, sending (bytes), verifying: StepTrail |
| Error: permission denied | "AURA can't hear your microphone. Allow it in this browser's site settings for 127.0.0.1, then try again." No imitation of a system dialog. |
| Error: no input | "No microphone found. Plug one in, or import a recording." |
| Error: hash mismatch | as above |
| Partial capability: processing not honoured | Banner (attention): "This browser kept noise suppression on. Your capture is still kept exactly as recorded, and the setting is written into its provenance. Transcription may find it harder." |
| Partial capability: `capture.mic` not passed on this OS | The RecordButton is replaced by "Check this microphone": "Microphone capture hasn't passed its check on {OS} yet. Record a 5-second test take; AURA checks that processing is off, that it decodes and that it isn't silent, and records the result." A passing check opens Record; a failing one names the check that failed and offers "Import a recording or use MIDI." |
| Partial capability: no Web MIDI | "Play it live" card: "Live MIDI needs a Chromium-based browser. MIDI files work here." |
| Partial capability: transcriber disabled | After keeping a hum: "Kept. The transcriber is off until it passes its floor, so draw the notes in the melody editor." |
| Offline worker | Kept, but transcription waits: "Kept. Transcription is waiting: the analysis worker didn't start. Run `studioctl doctor`." |
| Store unavailable | O10; the Keep buttons are disabled with "Captures can't be kept while STUDIO is missing." |

**Keyboard.**
| Keys | Action |
|---|---|
| ←/→ on the tab list | Switch tab |
| `R` | Start or stop recording (Hum or sing, Play it live) |
| Space | Play or pause the review |
| `K` | Keep this capture |
| Shift+R | Record again (discard the unkept recording) |
| `0` | Reset the clip indicator |

**Accessibility.** The record button is named "Record a hum" / "Stop recording" with `aria-pressed`. The meter is
`role="meter"` with `aria-valuemin="-60"`, `aria-valuemax="0"` and `aria-valuetext` ("peak minus 7 decibels full
scale"), updated for assistive technology at most 4 times a second while drawn at the display rate. Clipping is
announced once, politely. The timer is not a live region; the recorded length is announced on stop. The live MIDI roll
is decorative; a text line reads "52 notes recorded".

**Story groups.** G04, G18, G19, G21.

---

### S06 Melody: transcription review and piano-roll correction (`/p/:projectId/melody`)

**Purpose.** Turn the transcription's first guess into Jon's MelodySpec: see how sure the transcriber was about each
note, correct notes, tempo, meter and key, and mark the phrases the SongForm will use. Every change makes a new
immutable revision and is logged (ADR-0004, ADR-0033).

**Scope and phase.** v1-core · P1 (TB1d; MIDI-first in TB1a).

**Route and entry.** From S05 after keeping; `G M`; the spine's "II Melody".

**Layout (≥ 1024 px).**
1. Kicker "II · Melody", title "Melody".
2. **RevisionBar**: "MelodySpec revision 7 · 12 corrections · saved 14:02" and "History" (drawer).
3. **TranscriberLine**: "First guess by pYIN+HMM (v0) · ◇ unverified on real hums", or "From MIDI file 'melody.mid',
   track 2", or "Drawn by hand".
4. **TempoKeyBar**: "♩ = 92" [Set tempo] · "4/4" [Set meter] · "E♭ major" [Set key], plus tempo-map segments when
   there are several. A value the transcriber guessed carries "◇ transcriber's guess" until Jon sets it; then it gets a
   red-pencil tick.
5. **PhraseStrip** above the roll: named bars ("Phrase 1"…), click to select, double-click to rename.
6. **PianoRoll** in a sunk well:
   - Left: a keyboard with note names at every C ("C4").
   - Grid: bar lines in `--rule-strong`, beat lines in `--rule`, bar numbers above.
   - Notes as 2 px-radius bars. **ConfidenceShading**: high confidence is solid ink; medium is 60 % ink; low is 30 % ink
     with a dotted outline and a "?" glyph where the note is wide enough. Bands come from one constants file, tuned by
     the hum benchmark (TB6).
   - Corrected and added notes carry a small red-pencil tick at their start. Notes from MIDI carry none.
   - Selection: a 2 px brass outline with resize handles.
   - Playhead: a 2 px red-pencil line.
7. Under the roll, aligned to it: the capture strip (the hum's waveform) and, when the transcribe job stored its pitch
   track, a "Pitch trace" overlay toggle.
8. **ToolBar** (above the roll): Select · Draw · Split · Merge · Transpose · Quantize ("Quantize to 1/16 · reversible: the
   played timing stays underneath") · Mark phrase · Delete · grid menu · zoom.
9. Play controls: "Play melody" (an oscillator preview drawn from the TS TimeModel, no job), "Play hum", "Play both",
   and "Hear the guide" (a NeutralVoice `guide` job; when ready it plays in the PlayerBar as "Guide · NeutralVoice · not
   a candidate").
10. Footer bar: "Edit as a list" (toggle) and primary "Continue to song intent".

Margin: **NoteInspector** for the selection: pitch ("E♭4 · MIDI 63"), start ("bar 3 · beat 2 · tick 480"), length,
confidence ("0.42 · low · from the transcriber"), origin (transcribed, corrected, added, from MIDI), phrase. Below it,
"Correction effort: 12 corrections over 6 min (MEASURED-LOCAL)", because the log is the benchmark's effort metric.

**History drawer.** Revisions newest first: "Revision 7 · 14:02 · 3 corrections (move ×2, transpose)". "Use revision 4
again" creates a new revision equal to revision 4, with the note: "Nothing is deleted. This makes revision 8 from
revision 4."

**Narrow widths (< 1024 px).** The roll is replaced by the **NoteList** (below) and a small contour sparkline, with the
banner: "The piano roll needs a window at least 1024 px wide. The list edits the same melody."

**NoteList.** A grid: # · Start (bar · beat · tick) · Length · Pitch (name and MIDI number) · Confidence (number and
band in words) · Origin · Phrase. Cells are editable; every edit is a correction like any other.

**Components.** RevisionBar, TranscriberLine, TempoKeyBar, PhraseStrip, PianoRoll, ConfidenceShading, CaptureLane,
ToolBar, NoteInspector, NoteList, HistoryDrawer, Banner, WorkerBanner.

**Key copy.**
- Saving rule: each gesture (one drag, one key press) is one set of corrections posted against the current revision;
  the RevisionBar shows "Saving…" then "saved 14:02".
- Undo: "Undo makes a new revision that reverses your last correction. Nothing is deleted."
- Set tempo field: label "Tempo (quarter notes per minute)"; meter: "Time signature"; key: "Key".

**States.**
| State | Treatment |
|---|---|
| Empty | No capture and no MIDI: "No melody yet. Capture one, or draw it here." [Capture] [Start drawing] |
| Working: transcribing | The capture strip shows; the roll reads "Transcribing your hum · {elapsed}" with real steps if the worker reports them |
| Error: transcription failed | "Transcription failed ({code}). Your capture is safe. Try again, or draw the notes yourself." [Try again] [Draw the notes] |
| Error: correction refused | "That correction didn't apply. Revision 7 is unchanged." |
| Stale revision (409) | "This melody changed in another window (revision 8). Your last correction wasn't applied." [Load revision 8] |
| Partial capability | The transcriber is disabled (its synthetic floor missed): "The transcriber didn't pass its floor, so it's off. Draw the notes, or use MIDI." "Unverified on real hums" shows whenever the transcriber is on |
| Offline worker | "Hear the guide" waits: "The guide is waiting for the analysis worker." Corrections still work: they need only the control service |
| Store unavailable | O10 |

**Keyboard** (the roll or the list has focus).
| Keys | Action |
|---|---|
| ←/→ | Select the previous / next note |
| Shift+←/→ | Extend the selection |
| Alt+↑/↓ | Transpose by a semitone; Alt+Shift+↑/↓ by an octave |
| Alt+←/→ | Move by one grid step; Alt+Shift+←/→ by one beat |
| Mod+Alt+←/→ | Shorten / lengthen by one grid step |
| `V`, `D` | Select tool, draw tool |
| `S` | Split the selected note at the playhead (or in half) |
| `M` | Merge the selected adjacent notes |
| `N` | Add a note at the playhead (type a name such as "Eb4") |
| Delete, Backspace | Delete the selection |
| `Q` | Turn the quantize layer on or off |
| `P` | Mark a phrase from the selection |
| `T`, Shift+T, `K` | Set tempo, set meter, set key |
| `[`, `]` | Coarser / finer grid |
| `=`, `-` | Zoom in / out |
| Space; Shift+Space; Alt+Space | Play the melody; play the hum; play both |
| Home, End | Playhead to start / end |
| Mod+Z, Shift+Mod+Z | Undo, redo |
| `H`, `L` | History drawer; list view |

**Accessibility.** "Edit as a list" is the first control after the title, and it is the recommended mode with a
screen reader. The roll is `role="application"` with `aria-roledescription="piano roll"` and the label "Melody, 48 notes,
revision 7". A focused note reads "E flat 4, bar 3 beat 2, eighth note, low confidence, transcribed". Each correction
announces its result ("Moved to F 4"). Confidence is never shown by opacity alone (dotted outline, "?" glyph, and the
list's words). The playhead and the waveform are decorative; positions are text in the inspector.

**Story groups.** G05, G04, G19, G20, G21.

---

### S07 Song intent (`/p/:projectId/song`)

**Purpose.** Say what the song should be, as a SongSpec: style and exclusions, vocal mode, approved lyrics and their
language, the SongForm built from phrases, references with their permissions, and the candidate count. Show, honestly
and before anything runs, which routes can make this song in this project's lane under this compute profile, and what
each engine profile will actually receive (ADR-0018, ADR-0032).

**Scope and phase.** v1-core · P1 (TB1a). Reference timbre and larger candidate counts are v1-studio; the editable R1
score (A9) is v1-studio (chord symbols are edited in the S07 chords slot; note changes go through MelodySpec ops).

**Route and entry.** From S06 "Continue to song intent"; `G I`; the spine's "III Song intent".

**Layout.** Kicker "III · Song intent", title "What should this song be?", RevisionBar "SongSpec revision 3 · saved".
The main column holds five groups separated by staff rules; the margin holds **IntentLedger** (below). Every field
change is debounced and saved as a new SongSpec revision (`PUT /api/v1/projects/{id}/song`); the response's conflicts
and unsupported fields render inline.

1. **Style.**
   - "Style" (textarea). Placeholder: "e.g. slow worship ballad, warm piano, soft strings, male vocal".
   - "Leave out" (chip input). Placeholder: "e.g. drums, autotune".
   - "Vocal" radio: "Sung, with your lyrics" · "Instrumental".
   - Shown only where a smoke-passed profile in the plan maps them: any further control (for example a guidance
     control). Turbo profiles never show guidance.

2. **Approved lyrics.**
   - **LyricsEditor** (Plex Sans; section tags such as `[Verse 1]` and `[Chorus]` styled as small caps). Helper:
     "These are your words. Nothing AURA hears in a rendered vocal will ever change them."
   - "Language" select, default "English (en)" (owner-pending Q6). The list is BCP-47.
   - Tag binding: a tag with no matching SongForm section is underlined in red pencil with "No section called 'Bridge'
     in the form"; a vocal section with no lyrics reads "Chorus 2 has no lyrics".
   - Note: "Bracketed directions are hints to the engine, not commands."
   - **TranscriptPanel**, beside the editor once any revealed candidate has an ASR transcript (lyric PER, TB8):
     "What the vocal seems to sing · request 3, candidate B · ASR transcript, for checking only". Read-only, with
     differences from the approved lyrics underlined in red pencil and listed in words. It never edits the
     approved lyrics; copying a line across is Jon typing it (ADR-0017, feature B7).

3. **SongForm.**
   - **SongFormEditor**: an ordered list of sections. Each row: name (Intro, Verse 1, Chorus, Bridge, Outro or your
     own) · Vocal / Instrumental · phrases (chips chosen from the MelodySpec's phrases) · bars · repeats. Add, remove
     and reorder.
   - Default for a new song: one vocal section per phrase, in order (§6 Q14). Copy: "One section per phrase to start.
     Rearrange it as you like."
   - Computed: "Form length 3:28 at ♩ = 92 (from the tempo map)". This is exact arithmetic, so it carries no figure
     label.
   - "Target duration" (m:ss). A mismatch shows inline: "The form is 3:28; the target is 4:00."
   - "Hear the assembled guide": a NeutralVoice `guide` job over the assembled melody; plays in the PlayerBar as
     "Guide · not a candidate".

4. **References.**
   - **ReferenceList** with "Add a reference" (O8). Each row: title as typed · permission ("I own this recording" or
     "Licensed: {note}") · allowed use.
   - Allowed use is "Listening only" by default. "Global timbre/style reference" appears only where a smoke-passed
     profile implements reference timbre (v1-studio) and the permission allows engine input, with the line: "A global
     style and timbre hint. It is not voice cloning." (ADR-0007.) A reference standard is always listening only.

5. **Candidates and routes.**
   - "Each request makes 2 candidates." (Larger n is a priced v1-studio choice; it appears only when implemented.)
   - **RouteTable**: computed by the API's what-if admission for this project's lane and the session's compute
     profile. Above it, ◇ "Unbenchmarked routes: they are listed in a fixed default order, not by quality. No route is known to be better until a benchmark record says so."

     | Route | What it does | Engine profile | Where it runs | Status |
     |---|---|---|---|---|
     | R1 | YuE2 sings from a score of your melody | `yue2-3b-score` | Burst · paid · your approval each run | Eligible, or ◇ "needs smoke on the burst host class" |
     | R2-synth | ACE covers the NeutralVoice guide of your melody | `ace-2b-sft-mlx` | This Mac · MLX | Eligible |
     | R2-raw | ACE covers your hum itself | `ace-2b-sft-mlx` | This Mac · MLX | Eligible, or "Needs a hum capture; this melody came from MIDI." |
     | text | ACE from style and lyrics only, no melody seed | `ace-2b-sft-mlx` | This Mac · MLX | Eligible |

   - Typed reasons a route cannot run, exactly:
     - LLC lane: "Not in the LLC lane. YuE2's weights (CC BY-NC 4.0, with an individual-creator permission) don't
       cover LLC work."
     - Lyrics language: "R1 needs English or Chinese lyrics."
     - Length: "R1 handles songs up to about 6 minutes."
     - No profile on this host class: "No engine profile for this route has passed smoke on this Mac."
     - Burst blocked by an overrun: "Burst runs are blocked until you acknowledge an overrun." [Review]
   - R1 row disclosure "See the score R1 would send": the MelodySpec rendered as YuE2's ABC (`as/abc`), read-only, with
     the conversion notes ("Pickup in bar 1 padded with a rest. Triplet in bar 7 re-quantized to eighths."). Chord
     symbols are edited in the S07 chords slot (v1-studio, A9); with chords present R1 sends `cot='full'`.
   - Cap note when R1 is eligible and the month is nearly used: "This month's cap has $0.10 left. A burst quote larger
     than that will be refused." (A note, not a block: the quote decides.)

Footer bar: primary "Plan candidates" (Mod+Enter). Disabled with its reason when no route can run: "No route can make
this song yet: no engine profile has passed smoke on this Mac." [Engines & licenses]

**IntentLedger** (margin; "What the engines will get"). For the routes in the default plan, one row per SongSpec field:
Field · You asked · Supported by {profile} · Observed (after generation). Examples: "Vocal gender · — · not a control in
ace-2b-sft-mlx"; "Guidance · — · fixed at 1.0 by ace-2b-turbo-mlx". It turns ADR-0018's requested, supported and
observed into something Jon can read before he spends anything.

**Conflicts** (from `Validation`), inline at the field, each with two one-click resolutions:
- "Your style mentions 'female vocal', but the song is set to Instrumental. Which do you mean?" [Make it sung] [Remove
  the vocal words]
- "The style asks for drums, and 'Leave out' lists drums." [Keep drums] [Leave drums out]

**Components.** RevisionBar, StyleField, ChipInput, LyricsEditor, TranscriptPanel, LanguageSelect, SongFormEditor, ReferenceList,
RouteTable, AbcPreview, IntentLedger, ConflictNote, Banner, WorkerBanner.

**States.**
| State | Treatment |
|---|---|
| Empty | First visit: language English, vocal Sung, the default form from phrases; the RouteTable is already computed |
| Loading | Groups load in order; skeletons after 300 ms |
| Error: save failed | "Couldn't save that change. Revision 3 is intact." [Try again] |
| Stale revision (409) | "This song intent changed in another window (revision 4). Your last change wasn't applied." [Load revision 4] |
| Partial capability | Routes ineligible as listed; reference timbre hidden until implemented; the primary button disabled with its reason when nothing can run |
| Offline worker | The guide waits: "The guide is waiting for the analysis worker." Routes placed on an unreachable worker host read "Waiting for linux-4090 (unreachable). Switch tier to re-plan." |
| Offline | R1 reads "Burst runs need the internet." |
| Store unavailable | O10 |

**Keyboard.** Standard form navigation. In the SongForm list: ↑/↓ move between sections; Alt+↑/↓ move the focused
section; `A` adds a section after it; Delete removes it (with an UndoBar for 8 s); Enter edits its name. Mod+Enter plans
candidates.

**Accessibility.** Every field has a visible label. On "Plan candidates" with problems, an error summary at the top
lists each with a link to its field. Conflicts are tied to their fields with `aria-describedby`. Reordering announces
"Chorus moved to position 3 of 6". The RouteTable is a table with a caption ("Routes for this song in the individual
lane on tier 4").

**Story groups.** G06, G07, G15, G17, G20.

---

### S08 Generation: plan and progress (`/p/:projectId/requests/:requestId`)

**Purpose.** Show the plan for one generation request (routes, profiles, seeds and placements, each with a reason, and
the routes declined and why), take the paid-run decision where one is needed, then follow every job through its real
states until both candidates are ready for the audition (ADR-0004, ADR-0012, ADR-0030).

**Scope and phase.** v1-core · P1 (TB1a fakes, TB2 paid gate on the fake provider); P2 (TB3 ACE); P3 (TB7 YuE2 burst).

**Route and entry.** "Plan candidates" in S07 creates the request and lands here. `G R` opens the latest request. A
re-roll from a "Neither" verdict creates a new request and lands here, labelled "Re-roll of request 3".

**Layout.** Kicker "IV · Render", title "Request 3". Subline: "From SongSpec revision 3 · MelodySpec revision 7 · ◯
Individual · tier 4".

**Phase A: the plan** (before the jobs start).
1. Mode: "Let AURA plan (the first two eligible routes in the default order)" · "Choose routes myself". In auto mode
   R1 is planned only when it runs without a burst, or when Jon ticks "Include a paid R1 candidate" for this request.
2. **PlanTable**, one row per candidate, in plan order:

   | | Route | Engine profile | Where | Seed | Why |
   |---|---|---|---|---|---|
   | Candidate 1 | R1 | `yue2-3b-score` · rev 7a10…be52 | Burst · RunPod · 24 GB class · paid | 18227 | "First in the default order (unbenchmarked); you asked for a paid R1 candidate." |
   | Candidate 2 | R2-synth | `ace-2b-sft-mlx` · rev 9b03…e1d4 | This Mac · MLX | 50311 | "Next in the default order (unbenchmarked); runs here for free." |

3. "Not in this request" list: "R2-raw: the plan takes two routes, and R2-raw is third in the default order
   (unbenchmarked)." · "text: this song has a melody seed."
4. "Choose routes myself" turns each row into two pickers (route, then an eligible profile). Draft and render profiles
   are offered side by side where both are smoke-passed: "`ace-2b-turbo-mlx` · draft" and "`ace-2b-sft-mlx` · render".
   The same route may fill both slots; it then gets two seeds.
5. **QuoteCard**, only when a row is placed on burst: "Candidate 1 runs on a rented GPU. Ceiling $0.37 · this month
   $3.12 of $25.00 · quote expires 14:32." Buttons: "Review and approve" (opens O2) and "Decline the burst".
   Declining relabels the plan "ACE-only: burst declined" and refills the row from the next eligible ACE route; the
   change is shown, never silent.
6. Footer: primary "Start 2 candidates", or "Start 2 candidates (1 waits for your approval)". Free jobs start at once;
   a paid job waits in `awaiting_approval` until O2 writes the reservation.

**Phase B: progress** (after Start). Two **JobCards** in plan order (never arrival order). Each card:
- Header: "Candidate 1" · route · profile · placement chip.
- **StepTrail** with the real states: Queued → Waiting for your approval (paid only) → Preparing → Loading →
  Generating → Checking → Ready.
- The current state's line (exact copy in the table below), elapsed time, and the metronome tick.
- "Usually 1–2 min on this Mac (6 runs, MEASURED-LOCAL)" only when history exists for this profile and host class.
- Child jobs listed under the card: "measure", and "adherence" where the lane allows it, or "Adherence: unmeasured (no
  LLC separator yet)".
- "Cancel candidate 1" (quiet; confirmation: "Cancel candidate 1? Nothing partial is kept. A paid run is terminated
  and settles at what it has cost.").
- **No output facts.** A ready card shows "Ready" and nothing about duration, loudness or badges (§0.2 blinding rule).

When both are ready, a Banner: "Both candidates are ready. Labels are drawn when you open the audition." with primary
"Open the audition" (large, ink). Once the audition is open, both cards lose their route, profile and placement and
read "Candidate 1 · hidden until your verdict"; the PlanTable collapses to "Plan hidden until your verdict".

Footer in phase B: "Cancel request" (quiet, with confirmation).

**Job state copy** (shared with O1).
| State | Line |
|---|---|
| `queued` | "Queued · waiting for this Mac's GPU. One heavy model runs at a time." (or "Queued") |
| `awaiting_approval` | "Waiting for your approval · the quote expires at 14:32" |
| `preparing` | "Preparing · sending inputs by hash (2 of 3 already there)" |
| `loading` | "Loading `ace-2b-sft-mlx` · cold, from STUDIO" or "· warm" |
| `generating` | "Generating · step 23 of 50" when the engine reports counters, else "Generating" |
| `analyzing` | "Checking · decodes, loudness, true peak, melody adherence" (adherence omitted where the lane forbids it) |
| `ready` | "Ready" |
| `cancelled` | "Cancelled. Nothing partial was kept." |

**Failure copy** (what failed · what is safe · what to do).
| Code | Line | Action |
|---|---|---|
| `profile_not_promoted` (409 at submit) | "This engine profile hasn't passed its smoke gate on this host, so nothing was started." | [Engines & licenses] |
| `lane_forbidden` | "This lane doesn't allow {profile}. Nothing was loaded." | [Change routes] |
| `use_forbidden` | "{input} isn't allowed as engine input (it's listening only). Nothing was loaded." | [Change references] |
| `insufficient_space` | "Not enough room on {volume}: {free} GB usable, needs {n} GB, keeps 10 GiB (10.74 GB) spare. Nothing was started." | [Storage] |
| `worker_refused` (`unsupported_task`, `over_limit`, `language_unsupported`, `weights_missing`, `insufficient_memory`, `insufficient_disk`, `busy`) | "The worker refused before loading anything: {reason in words}." | per reason |
| `worker_lost` | "The worker stopped before finishing. Nothing partial was kept." | [Try again] (free) / [Get a new quote] (paid) |
| `hash_mismatch` | "An output didn't match its hash, so it was discarded. Nothing partial was kept." | [Try again] |
| `decode_failed`, `media_mismatch` | "The output didn't decode as declared, so it was discarded." | [Try again] |
| `timeout` | "The job ran past its deadline and was stopped. Nothing partial was kept." | [Try again] |
| `disk_low` | "Free space on {volume} fell below half the margin, so the job stopped. Nothing partial was kept." | [Storage] |
| `store_unavailable` | "STUDIO disappeared while this job ran. Nothing partial was kept." | O10 |
| `budget_refused` | "This run would take the month past the $25.00 cap, so it can't start." | [Decline the burst] [Burst & monthly cap] |
| `quote_expired` | "The quote expired before you approved it. Nothing was spent." | [Get a new quote] |
| `cancelled_by_owner` | "You cancelled this. Nothing partial was kept." | — |
| `internal` | "Something inside AURA failed. Nothing partial was kept. The details are in the margin." | [Try again] |

Retries: a retryable failure on a free placement retries on its own up to its bounded count, shown as "Retrying (1 of
2)". "Try again" makes a new job for the same plan row with the same seed. A paid job never retries on its own: "Trying
again needs a new quote and your approval."

An audition needs both candidates. While one has failed, the Banner reads: "The audition needs both candidates.
Candidate 2 failed; try it again, or cancel the request."

**Components.** PlanTable, RoutePicker, QuoteCard, JobCard, StepTrail, PlacementChip, Banner, WorkerBanner,
ApprovalDialog (O2), UndoBar.

**States.**
| State | Treatment |
|---|---|
| Empty | Not reachable: a request always has a plan |
| Loading | Plan skeleton after 300 ms |
| Working | Phase B |
| Error | Per the failure table |
| Partial capability | Only one eligible route: "Both candidates come from R2-synth with different seeds, because it is the only eligible route here." LLC: "In the LLC lane only ACE has a melody route today, so both candidates are ACE." |
| Offline worker | Local worker not running: "Starting the ACE worker…" (a real step). Worker host unreachable: the card's line reads "Waiting for linux-4090 (unreachable since 14:02)" with "Switch tier to re-plan". Burst pod lost: "The rented GPU was lost. The run settled at its ceiling ($0.37, no billing data)." |
| Offline | Paid rows: "Burst runs need the internet." |
| Store unavailable | O10 |
| Blind | After the audition opens, as above |
| Synthetic | Fake profiles' rows carry "Synthetic test output" (dev and test only) |

**Keyboard.** Mod+Enter starts the candidates; `O` opens the audition when it is ready; ↑/↓ move between job cards;
Enter on a card opens its detail in the margin. Cancel is a button only, with its confirmation.

**Accessibility.** Each StepTrail is an ordered list with `aria-current="step"`. State changes are announced politely
("Candidate 1: generating"), failures politely with their line, and "Both candidates are ready" once. The metronome tick
is decorative. Elapsed time is not a live region.

**Story groups.** G07, G02, G15, G17, G20, G21.

---

### S09 Audition (`/p/:projectId/auditions/:auditionId`)

**Purpose.** AURA's acceptance gate: a blind, level-matched A/B of two ready candidates, ending in Jon's verdict, the
reveal, and the keeper. Nothing but the sound decides (ADR-0005, ADR-0010).

**Scope and phase.** v1-core · P1 (TB1b); adherence numbers at the reveal P2 (TB5); lyric errors P4 (TB8). Eval mode
P4.

**Route and entry.** "Open the audition" in S08; the NeedsYou popover; `G A`. Opening draws the labels on the server
(`POST /generations/{id}/auditions`), only when every arm is ready.

**Layout (focused).** The NavRail collapses to a back link ("Request 3"), the PlayerBar is hidden, and the margin is
replaced by an "About this audition" disclosure.
1. Kicker "V · Listen", title "Audition". Subline: "Blind · level-matched · labels sealed ({commitment 3e9b…c41f})".
2. **AuditionDeck**: two **ArmButtons**, at least 160 × 160 px, side by side at ≥ 768 px and stacked below, each a
   Newsreader capital at 6rem ("A", "B"). The playing arm has a 4 px red-pencil bar under its letter, the word
   "Playing", and `aria-pressed="true"`. Under each arm, room for one badge: only "Unplayable" can appear.
3. **Transport**: Play/Pause (72 px), "−5 s", "+5 s", the position ("1:12 / 3:41", the active arm's), and the
   **TimeRuler**: a full-width sunk bar with minute ticks, the playhead, the loop region, and problem-interval brackets
   lettered by arm. **No waveform**: a waveform would show each arm's envelope and invite guessing.
4. "Listened: A 2:41 · B 2:12" (seconds listened per label, recorded with the verdict).
5. **VerdictPanel** (right of the deck at ≥ 1200 px, below it otherwise): heading "Your verdict"; a segmented control
   "Prefer A" · "Prefer B" · "Tie" · "Neither"; a disclosure "Say why (optional)" holding:
   - Axes, each A / Same / B / Skip: "Keeps my melody" · "Vocal" · "Lyrics clarity" · "Arrangement" · "Sound".
   - Reason chips per arm: "Melody drifted" · "Lyrics unclear" · "Wrong feel" · "Muddy mix" · "Glitches" · "Structure"
     (the contract field is §6 Q1).
   - "Problem intervals": rows like "A · 1:02–1:10" with an optional note; edit and remove.
   - A note field.
   - **SealButton** "Record verdict", disabled until a choice is made. Pressing it shows an inline confirmation, not a
     modal: "Record 'Prefer A'? A verdict can't be changed." [Record] (seal) [Back].
6. "About this audition" disclosure: "Both arms are 48 kHz, 24-bit previews. The louder one is turned down (never up)
   to the quieter one's loudness, matched within 0.1 LU. Labels were drawn at random when you opened this audition, and
   only a sealed commitment to them is shown. Duration and sound can't be hidden; everything else is."

**Switching.** A and B play in sync: switching keeps the position (clamped at the shorter arm's end) and crossfades in
25 ms, equal power (a default constant; §6 Q6). Past the end of the shorter arm: "B ended at 3:12."

**Reveal.** Recording the verdict posts it, then posts the reveal. The **RevealCards** turn over (the 280 ms card turn;
instant under reduced motion):
- "A · R2-synth · `ace-2b-sft-mlx` · rev 9b03…e1d4 · seed 50311 · This Mac (mlx/m5pro)"
- Every badge, now visible, and the measurements: "Melody adherence: median 41 cents · octave errors 2 % · onset F1
  0.78 · contour 0.91 (MEASURED-LOCAL)" or "Melody not kept"; "Lyric errors unmeasured"; "True peak −0.8 dBTP".
- The route's everyday record: "R2-synth kept 3 of 5". It never changes a profile's status (ADR-0027).
- Commitment check: "✓ Commitment verified: the labels match what was sealed (3e9b…c41f)." A mismatch, which should
  never happen, is shown plainly: "✕ The reveal doesn't match what was sealed. The verdict is kept and flagged."
- Diagnostic scores (v1-studio) under a ⓘ "Diagnostic only · never used to choose".
- "How this was made" on each card opens O3 for that candidate: intent and actual, timings, placement, license chain.

**After the reveal.**
- Prefer A / Prefer B: "Keep A" (ink, primary on the preferred arm) and "Keep B" (quiet). Keeping makes the keeper and
  returns to S04 with the toast "Kept A as this song's keeper."
- Tie: "Keep A" and "Keep B", equal weight; and "Re-roll with new seeds".
- Neither: "Re-roll with new seeds" (a new request; a paid row needs a new quote) and "Back to song intent". The re-roll
  counts toward keeper cost.

**Eval mode** (from S12). Arms A, B, C… as the brief requires. A reference standard used as an anchor is shown with its
title and "Anchor · reference standard · not blind" (honest: it is recognizable). The subline reads "Eval audition
14 of 36 · preregistration 77c0…1a2b". About 10 % of eval auditions are hidden repeats: "Some auditions repeat an
earlier pair. You won't be told which." The verdict is the same owner act. The reveal shows only "✓ Commitment
verified" and keeps identities until the preregistered set of auditions concludes (§6 Q3).

**Components.** AuditionDeck, ArmButton, Transport, TimeRuler, IntervalBracket, VerdictPanel, AxisRow, ReasonChips,
SealButton, RevealCard, CommitmentCheck, Badge, Toast.

**Key copy.** Opening: "Opening the audition · drawing labels". Arm failed to load: "B didn't load. Try again." Audition-level
synthetic notice (test environments): "One or more arms is Synthetic test output." (§0.5; per-arm badges are withheld.)

**States.**
| State | Treatment |
|---|---|
| Empty | Not reachable: an audition opens only over ready arms |
| Loading | "Opening the audition · drawing labels", then fetching both previews (bytes) |
| Error: an arm didn't load | Inline under that arm, with "Try again"; the other arm still plays |
| Unplayable arm | "B is unplayable: it didn't decode. You can still prefer A, or choose Neither." |
| Error: verdict refused | "Your verdict wasn't recorded ({reason}). Nothing changed." |
| Partial capability | Fewer than two playable arms: the deck explains and offers "Neither" only |
| Offline worker | Not used: previews already exist |
| Store unavailable | O10; Record verdict is disabled: "Verdicts can't be recorded while STUDIO is missing." |
| Blind | The whole screen until the reveal |

**Keyboard.**
| Keys | Action |
|---|---|
| Space | Play / pause |
| `A`, `B` (`C`, `D`… in eval mode) | Switch to that label, in sync |
| ←/→; Shift+←/→ | Seek 5 s; seek 1 s |
| Home | Back to the start |
| `[`, `]`, `\`, Shift+`\` | Loop start at the playhead, loop end, loop on/off, clear loop |
| `I` | Start, then end, a problem interval on the playing arm |
| `1`, `2`, `3`, `4` | Choose Prefer A, Prefer B, Tie, Neither (choice only, never a record) |
| Mod+Enter | Move focus to "Record verdict" and open its confirmation; Enter on the focused Record button records |
| `K` | After the reveal: keep the preferred arm |

**Accessibility.** The arms are toggle buttons named "Label A" and "Label B". The DOM, ARIA attributes, element ids,
titles and network URLs carry only labels (`/api/v1/auditions/{sid}/audio/A`), and audio is decoded into buffers rather
than exposed as media elements with sources. Switching announces "Playing A at 1 minute 12" (polite, debounced to one
announcement a second). Problem intervals are a list. The reveal is announced as a sentence per arm. The TimeRuler is a
slider ("Position, 1 minute 12 of 3 minutes 41") operable with the arrow keys.

**Story groups.** G08, G12, G16, G19, G20.

---

### S10 Studio (`/p/:projectId/studio`)

**Purpose.** Arrange, edit and finish a keeper on a timeline: hear it in context, replace a section or a line without
touching anything else, extend it, isolate its original stems with an honest residual, and commit a replacement by
copying it to the main track, which rebuilds the mix (ADR-0006, ADR-0013, ADR-0017).

**Scope and phase.** v1-studio · P5 (TB9). Isolate original is v1-studio; Re-perform and Create a new part are v2 and
appear only as explanations. The brief's "take lanes" are **replacement tracks** here (see the table of the brief's
headings at the top).

**Route and entry.** "Open in the Studio" on the Song page; `G T`; the spine's "VI Finish". Requires a keeper.

**Layout (focused workspace, ≥ 1024 px).**
1. **TransportBar** (top, 56 px): Play/Stop · Return to start · Loop · position ("bar 12 · beat 3" and "0:42.512") ·
   "♩ = 92 · 4/4" (the tempo map; edits happen in S06 and make a new revision) · the keeper chip "Keeper revision 2" ·
   the gate line "Playback gate passed on macOS ✓ (8 tracks × 30 min, 0 underruns, UI p95 under 100 ms while generating;
   MEASURED-LOCAL, {date})".
2. **SectionRuler**: named section markers across the top (Intro, Verse 1, Chorus…), each a button with its name in text;
   the selected section has a brass outline.
3. **LyricsStrip** (when an alignment exists): words placed in time; "Fix alignment" lets Jon drag word boundaries. Without
   an alignment: "No lyric alignment yet. Line and word replacement need one." (D9; alignment on singing is unverified.)
4. Tracks. **TrackHeader** (240 px) per track: name · part ("Mix", "Vocals", "Drums", "Bass", "Other", "Residual") ·
   **OriginBadge** ("Generated mix", "Isolated original", "Residual", "Replacement · proposal 1") · "M" and "S"
   toggles · fader with its dB value · pan · meter. **ClipView**s show a single waveform each, gain and fade handles,
   and their name.
   - The **main track group** is the keeper's mix, or, after Isolate original, its stems plus the residual summed.
   - **Replacement tracks** sit under the main group, one per edit operation, labelled "Replacement · Chorus 2 ·
     proposal 1 (preferred in its audition)" and "· proposal 2". They appear only after that edit's verdict (§0.2
     blinding rule). Each header has "Copy to main track".
5. **Inspector** (right, 320 px) with tabs Section · Clip · Track, and the **EditOperationPanel**:
   - "Replace section": the selected section's mask ("1:02.400–1:31.900"), crossfades, locked context, and the plan
     ("2 candidates · ACE repaint · `ace-2b-sft-mlx` · This Mac"). Primary "Plan 2 candidates".
   - "Replace line" and "Replace word": shown only when a lyric alignment exists and a smoke-passed profile does masked
     repaint; otherwise one line: "Needs a lyric alignment."
   - "Extend": at the start or the end; the per-pass length range is the profile's declared limit (VENDOR until
     measured).
   - DSP clip edits (deterministic, no model): gain, fades, trim, remove section. They change the timeline, never the
     keeper's audio; an export renders the timeline offline.
6. **StemsDrawer** (bottom, collapsed; "Stems"). Three cards, always in this order, so the difference is learned:
   1. **"Isolate original"** — "Splits the mix into stems with a separator. The residual (the mix minus the stems) is
      always kept and can always be heard. Nothing is performed anew." Button "Isolate original · Demucs htdemucs ·
      this Mac" (individual and research lanes). In an LLC project: "No LLC-eligible separator yet. Demucs weights are
      for research or personal use only." Afterwards: the stems and the residual as tracks, and the checks: "Rebuild
      check: stems plus residual equal the mix ✓", the bleed figure, and "Listen: stem · residual · rebuilt mix".
      "Transcribe this stem to MIDI" appears on a stem only where a transcriber is smoke-passed, labelled "◇ unverified
      on separated stems".
   2. **"Re-perform this part"** — "Generates a new performance of a part, guided by its stem. Always labelled a new
      performance. Arrives in v2." No control.
   3. **"Create a new part"** — "Generates a part the song didn't have, fitted to the mix. Arrives in v2." No control.

**The edit flow.** Select a section → "Plan 2 candidates" → the request runs (S08's JobCards in a drawer) → "Open the
audition" (S09 over two full-length candidates that differ only inside the mask) → verdict and reveal → both proposals
appear on a replacement track → "Copy to main track" on the chosen one.

**Copy to main track** opens a sheet:
- "Copy proposal 1 to the main track?"
- "AURA rebuilds the mix from its sources with Chorus 2 replaced. Nothing is layered over the old part. Then it checks
  that every sample outside 1:02.400–1:31.900 and its crossfades is identical to keeper revision 2."
- Primary "Copy and rebuild"; secondary "Not now".
- Working: "Rendering offline · checking preservation" (real steps).
- Passed: "Preservation check passed. Keeper revision 3 is now the song's keeper." with an UndoBar: "Undo · restores
  keeper revision 2 by its hash; nothing regenerates."
- Failed: "Preservation check failed: 3 samples differ outside the mask, first at 0:12.004. The edit wasn't accepted;
  keeper revision 2 is unchanged."

A whole-song re-render is never offered as Replace section. If no smoke-passed profile can mask, the Replace actions are
absent and the Inspector says "No engine profile on this Mac can replace a section yet (repaint with a chunk mask)."

**Narrow widths and other browsers.** Under 1024 px: "The Studio needs a window at least 1024 px wide. The song page,
auditions and exports work at any width." with a read-only **TrackList** (tracks, clips and play buttons). In a
non-Chromium browser: "The Studio needs a Chromium-based browser. Everything else in AURA works here."

**Components.** TransportBar, SectionRuler, LyricsStrip, TrackHeader, ClipView, OriginBadge, Fader, Meter, Inspector,
EditOperationPanel, StemsDrawer, StemOperationCard, CopyToMainSheet, PreservationResult, UndoBar, TrackList, Banner,
WorkerBanner.

**States.**
| State | Treatment |
|---|---|
| Empty | No keeper: "The Studio opens on a keeper. Keep a candidate first." [Song page] |
| Loading | "Opening the timeline · reading the clips" with bytes for each clip's decode |
| Working | Isolate original, rebuild, preservation check, an edit's request: StepTrails in the Inspector or the drawer |
| Error | "The timeline didn't open. The keeper is unchanged." [Try again] |
| Partial capability: playback gate not passed on this OS | Banner: "Studio playback hasn't passed its gate on {OS} yet. Edits and exports still work, and auditions play normally; timeline playback stays off until the gate passes." [Run the playback gate] (a 30-minute evidence job: "Running · 12:40 of 30:00 · 0 underruns so far") |
| Partial capability: imported mix | "This is an imported mix from Suno. AURA may only listen to it, measure it and DSP-finish it." Edit operations and stems are absent |
| Partial capability: LLC lane | Isolate original card as above |
| Offline worker | The repaint or separator worker: "The ACE worker isn't running. AURA starts it when a job needs it." or "linux-4090 is unreachable; jobs placed there will wait." |
| Store unavailable | O10 |
| Blind | An edit's proposals stay off the timeline until its verdict |

**Keyboard** (the timeline has focus).
| Keys | Action |
|---|---|
| Space | Play / stop |
| `J`, `K`, `L` | Play backwards / stop / play forwards (press `L` twice for double speed) |
| Home, End | Start / end |
| ←/→; Shift+←/→ | Move the playhead by a beat; by a bar |
| `[`, `]` | Previous / next section marker |
| ↑/↓ | Select the previous / next track |
| `M`, `S` | Mute / solo the selected track |
| `I`, `O` | Set the mask in / out at the playhead |
| `R` | Replace the selected section (opens the panel) |
| `E` | Extend (opens the panel) |
| `C` | Copy to main track (on a replacement track; opens the sheet) |
| Shift+S | Stems drawer |
| `=`, `-` | Zoom in / out |
| Mod+Z, Shift+Mod+Z | Undo (restores by hash), redo |

**Accessibility.** The timeline is `role="application"` with `aria-roledescription="timeline"` and the label "Timeline,
6 tracks, keeper revision 2". Tracks are rows; a focused clip reads "Mix, clip from 0 to 3 minutes 41, gain 0 decibels".
Faders are sliders with `aria-valuetext` ("minus 3 decibels"); meters are `role="meter"`. Section markers are buttons.
The Copy to main track sheet states exactly what changes before the act, and the preservation result is announced. The
TrackList is the alternative for narrow windows and screen readers.

**Story groups.** G10, G11, G17, G18, G19, G20.

---

### S11 Finishing (`/p/:projectId/finish`)

**Purpose.** Measure before anything else: show the keeper's (or an imported mix's) integrated loudness and true peak
with the standard and meter named, keep a dry export always, and apply only deterministic DSP finishing (ADR-0019,
ADR-0021).

**Scope and phase.** The loudness report is v1-core (P1: `measure` feeds the manifest). The DSP chain and finishing of
an imported Suno download are v1-studio (P5). In a v1-core build the chain is absent and the screen holds the report
and the dry export.

**Route and entry.** "Finish" on the Song page; `G F`; the spine's "VI Finish"; an imported mix's row in the Library.

**Layout.** Kicker "VI · Finish", title "Finishing". A **SourcePicker**: "Keeper revision 2" or an imported mix.
Two columns at ≥ 1200 px, stacked below.

Left: **LoudnessReport**.
- "Integrated −16.2 LUFS · BS.1770-4 (pyloudnorm {version})"
- "Loudness range 6.3 LU"
- "True peak −0.8 dBTP · AURA meter {version}, 4× oversampling"
- "Sample peak −1.1 dBFS"
- All MEASURED-LOCAL, with the measured time. A horizontal LUFS scale with the measured mark; the optional target as a
  dotted line.
- Note: "BS.1770-5 hasn't been compared with -4 for stereo yet, so this report names the revision it used."
- "Loudness target (optional)": "Integrated __ LUFS" and "True-peak ceiling __ dBTP". With a target: "Gain needed −2.3
  dB → predicted −18.5 LUFS, true peak −3.1 dBTP (INFERRED until measured)". Copy: "Targets depend on where the song is
  going. AURA never applies one by itself."

Right: **DspChain** (v1-studio), non-generative mixing and mastering (O-08's DSP finishing), deterministic steps in a fixed order, each with its parameters and an on/off switch:
"Gain" · "Fades" (in, out) · "EQ" · "Loudness to target" (gain only) · "Trim" · "Format and rate" (48 kHz, 24-bit with
TPDF dither seeded from the export id). Loudness to target refuses rather than limits: "At −10 LUFS the true peak would
reach +1.8 dBTP. AURA doesn't limit in v1; choose a lower target."

Below both: **DryFinishedCompare**: "Dry" and "Finished" toggle buttons, level-matched by default ("Level-matched, so
you hear the change, not the volume"), with Space and `D`. Then "Apply DSP finishing" (ink; an offline render job that
makes a new artifact derived from the source, then measures it) and "Export…" (O4). Line: "AURA always keeps a dry
export beside a finished one."

For an imported mix, a Banner (neutral) at the top: "Imported mix · Suno (your download) · allowed: listening, loudness
measurement, DSP finishing (mixing, mastering, format). Suno's embedded provenance stays intact." A set of Jon's own Suno
stems is mixed here the same way. Nothing generative is offered anywhere for it, and placing it on a Studio timeline
beside AURA audio is refused: "A Suno import can't share a timeline with AURA's own audio unless you sign a risk
acceptance for edit input."

**Components.** SourcePicker, LoudnessReport, FigureLabel, TargetFields, DspChain, DryFinishedCompare, Banner,
WorkerBanner, ExportSheet (O4).

**States.**
| State | Treatment |
|---|---|
| Empty | No keeper and no imported mix: "Nothing to finish yet. Keep a candidate, or import a mix." |
| Loading | Skeleton report after 300 ms |
| Working | "Measuring loudness and true peak" / "Rendering offline · measuring the result" |
| Error | "Measurement failed ({code}). The audio is safe." [Try again] |
| Partial capability | v1-core build: DSP chain absent; the report and "Export…" remain. True-peak target refused as above |
| Offline worker | "Measuring is waiting for the analysis worker." |
| Store unavailable | O10 |
| Synthetic | The source's badge shows beside the picker |

**Keyboard.** Space plays; `D` toggles dry and finished; Mod+Enter applies DSP finishing; Tab through the chain, with
arrow keys on sliders.

**Accessibility.** The report is a definition list; the scale has "Show as table". Number fields carry units in their
labels ("Integrated loudness target, LUFS"). The dry/finished toggle is a pair of toggle buttons with `aria-pressed`.

**Story groups.** G09, G14, G20.

---

### S12 Evaluation (`/eval/:tab`)

**Purpose.** The only place the quality target is measured: Jon's reference standards, the hum benchmark, preregistered
briefs and their runs, the eval auditions he listens to, and the evidence with its uncertainty. No button here promotes
anything; status changes only through evidence records (ADR-0010, ADR-0027).

**Scope and phase.** v1-core. Hum benchmark P2 (TB6, parallel track); reference standards, preregistration, smoke-12 and
eval auditions P4 (TB8); running the 48-brief benchmark to completion is post-v1.

**Route and entry.** Global nav "Evaluation"; `G E`; NeedsYou ("6 eval auditions ready").

**Layout.** Title "Evaluation". Tabs: Overview · Reference standards · Hum benchmark · Briefs and preregistration · Runs ·
Eval auditions · Evidence. The evaluation ticket's container declares the tabs: it builds Overview, Hum benchmark (a
read-only view of hum-benchmark evidence records), Briefs and preregistration and Runs; the eval-auditions ticket fills
Reference standards, Eval auditions and Evidence.

**Overview.**
- The target, verbatim from the glossary's sense: "The quality target is 'Suno v6-class', measured only by your blind,
  level-matched auditions of AURA keepers against your reference standards, on preregistered briefs, with thresholds
  fixed before anything is rendered. No vendor figure, leaderboard or Suno output counts toward it."
- Status: "No preregistered evaluation has concluded yet." (or the latest conclusion with its evidence hash).
- "External context only" box: "Published benchmark numbers (VENDOR or COMPETITOR-RUN) are context and never enter a
  gate." No numbers are shown here.

**Reference standards.** Four **FeelSlots**, one per O-05 feel: "Worship or acoustic ballad" · "Cinematic or orchestral"
· "R&B, soul or pop ballad" · "Broad mix".
- Empty slot: "Add your reference standard" (O8, reference mode).
- Filled slot: title and artist as Jon typed them · duration · integrated loudness (MEASURED-LOCAL) · permission ("I own
  this recording" or "Licensed: {note}") · "Listening only · never engine input" · "In eval auditions it is an anchor,
  and it isn't blind."

**Hum benchmark** (TB6).
- Explanation: "Which transcriber should make the first guess? Your hums decide, and drawing the notes yourself is
  allowed to win."
- Preregistration line: "Preregistration {hash} committed {time}, before any scoring ✓" or "Not committed yet."
- Pairs: "Hum it, then play it" rows, N set at preregistration: each pair is a hum (S05's recorder) and the same melody
  played on MIDI as ground truth, with ✓ when both exist.
- Blind correction tasks: "Correct transcription X" (each transcriber's output, anonymised as X, Y, Z), opened in the S06
  editor. Correction effort is logged as usual.
- Scoring: "COn, COnP and COnPOff via mir_eval." Partial until its license check closes: "Scoring waits for mir_eval's
  license check."
- Outcome: "Default transcriber: pYIN+HMM (decided by evidence 5d1a…)" or "Outcome: manual entry wins".

**Briefs and preregistration.**
- "Smoke set · 12 briefs" and "Benchmark set · 48 briefs (8 categories × 6)": rows with name, feel, lane (LaneTab), seed
  kind (hum, MIDI, lyrics), and the routes and profiles under test.
- **PreregCard**: hash · committed at · what it fixes (briefs, asset hashes, pins, budgets including paid ceilings,
  listening quotas, thresholds) · "Committed before the first run ✓ (CI checks the commit order)". Read-only: the eval
  harness prepares and commits it; the UI shows it.

**Runs.** A table: brief × route × profile → job state (S08's copy), placement and lane, with equal candidate counts per
route. Paid rows awaiting approval show "Review and approve" (O2). An LLC brief never lists YuE2; preregistration
validation refuses it.

**Eval auditions.** "Ready to listen: 6" with primary "Start the next audition" (S09, eval mode). Progress: "14 of 36
auditions (the preregistered quota)". Note: "Some auditions repeat an earlier pair, to measure your consistency. You won't
be told which. Identities stay hidden until the set concludes."

**Evidence.** One row per comparison:
- "R1 vs R2-synth · R1 preferred in {k} of {n} auditions over {b} briefs · {p} % (95 % interval {lo}–{hi} %, clustered
  by brief) · MEASURED-LOCAL", with an **UncertaintyPlot** (a dot and its interval against a 50 % line).
- "Consistency on repeat pairs: {c} of {r} agreed."
- The gate: "Gate (fixed at preregistration): {rule} → passed / failed / inconclusive (quota short)".
- Status changes the records caused: "`yue2-3b-score` on cuda/runpod-24gb: smoke-passed → benchmarked (evidence
  8c2f…)". Line under the table: "Status changes only through evidence records."

**Components.** Tabs, FeelSlot, PreregCard, BriefTable, RunTable, QueueCard, UncertaintyPlot, EvidenceRow, StatusChange,
Banner, WorkerBanner.

**States.**
| State | Treatment |
|---|---|
| Empty | Reference standards: four empty slots. Briefs: "No preregistration yet. The eval harness prepares one; nothing runs before its hash is committed." |
| Loading | Per tab, skeletons after 300 ms |
| Working | Runs in progress per S08 |
| Error | Per tab: "Couldn't read the evaluation records. They are safe in the store." |
| Partial capability | mir_eval unverified (hum benchmark scoring); G2P unverified ("Lyric errors unmeasured" in evidence); a quota short at the end: "Inconclusive · the quota wasn't met, so nothing is promoted" |
| Offline worker | Runs waiting on a worker show its name and since when |
| Offline | Paid runs wait: "Burst runs need the internet." |
| Store unavailable | O10 |
| Synthetic | Synthetic evidence rows carry the badge and "can't satisfy a benchmark gate" |

**Keyboard.** ←/→ on the tab list; Enter on "Start the next audition"; tables are navigable with the arrow keys when
focused; Enter expands a row.

**Accessibility.** Each UncertaintyPlot has the same sentence as text and "Show as table". Feel slots are a list with
their state in words. Evidence rows are a table with a caption.

**Story groups.** G12, G14, G15, G17, G20.

---

### S13 Engines & licenses (`/engines/:tab`)

**Purpose.** What AURA may run, where, in which lane, and at what evidenced status; every component's terms; and every
download with its size, license acceptance and verification (ADR-0001, ADR-0011, ADR-0016, ADR-0027).

**Scope and phase.** v1-core · P0 (register, profiles declared) and P2 (ACE install, conformance, smoke).

**Route and entry.** Global nav; `G X`; links from partial-capability notes everywhere.

**Layout.** Title "Engines & licenses". A switch at the top right: "Show: everything · what the product sees" (the
second is `audience=product`, which omits anything below smoke-passed). Tabs: Engine profiles · Capabilities ·
Component register · Downloads.

**Engine profiles.** One **ProfileCard** per profile, grouped by engine:
- Header: "`ace-2b-sft-mlx`" · "ACE-Step 1.5 · 2B SFT" · role "render".
- Tasks as chips ("cover", "text to song"); limits (duration, lyric languages, channels); lanes ("◯ Individual · ▢ LLC
  · △ Research"); components (links to register rows).
- Pins: code commit, weights manifest, environment lock or image digest, SDK version → "Profile revision 9b03…e1d4".
- **StatusLadder**, one per host class: "mlx/m5pro: declared ✓ → installed ✓ (evidence a1b2…, Oct 9) → smoke-passed ✓
  (evidence c3d4…) → benchmarked ◇ (needs a preregistered benchmark)". `disabled` is drawn as a red-pencil strike
  through the ladder with its reason and evidence. Each step's evidence opens in the margin.
- Two columns, never merged: "Published claims" (italic, each with VENDOR, COMMUNITY or COMPETITOR-RUN and its source)
  and "Measured here" (each MEASURED-LOCAL with its evidence id): for example "Cold load 51 s · warm 9 s".
- Actions, only those that apply: "Install" · "Run conformance" · "Run the smoke render" · "Listen to the smoke render"
  · "Unload".
- **NotGarbledCheck** after a smoke render: the render plays in the PlayerBar, then two SealButtons: "Not garbled" and
  "Garbled", recorded as evidence (§6 Q2).
- After a pin change: "A pin changed (environment lock), so this is a new revision. Its status starts again at
  installed."
- YuE2 in tier 4: host class "cuda/runpod-24gb (burst)"; install is the pinned image digest; conformance and smoke run
  as approved burst runs.
- XL: "Offered as diffusers bf16 (about 11.1–11.5 GB, VENDOR) once its loader check passes. The 19.95 GB F32 files are
  never offered."

**Capabilities.** Rows per capability and OS: "`studio.playback` · macOS: smoke-passed ✓ · Windows: unverified ◇ ·
Linux: unverified ◇" and "`capture.mic`" likewise. Line: "AURA is never called ready on an operating system until that
system passes its own gate."

**Component register.** A read-only table generated from the evidence register: Component · Role · Code license ·
Weights license · Output terms · Obligations · Allowed lanes · Process boundary · Verification · Release blocker.
Filters: "What an LLC song may use", "Unverified or contested", "Release blockers only". Line above it: "Generated from
the research evidence register. To change a row, change the research, not this table." A row expands to its sources
(plain links to primary sources).

**Downloads.** One **DownloadRow** per profile or component:
- Files and sizes from the repo listing ("{n} files · 6.34 GB", VENDOR until the bytes arrive), destination ("STUDIO ·
  models/hf"), the preflight result per volume, and the license ("MIT · not accepted yet").
- **SealButton** "Accept the {license} license and download" (O7 shows the detail first).
- Progress in bytes, then "Verifying every file's hash ({i} of {n})", then "Installed · {bytes} bytes (MEASURED-LOCAL)".
- YuE2: "Downloads onto the burst pod at boot (7.30 + 0.53 GB, VENDOR). Nothing is stored on this Mac."
- Nothing is ever bundled with AURA; every weight downloads at runtime from a pinned revision.

**Components.** ProfileCard, StatusLadder, ClaimsColumns, NotGarbledCheck, CapabilityRow, ComponentTable, FilterChips,
DownloadRow, SealButton, LicenseDialog (O7), Banner, WorkerBanner.

**States.**
| State | Treatment |
|---|---|
| Empty | No profile installed: "No engine is installed yet. ACE-Step 1.5 2B turbo is the first, on this Mac, in every lane." [Install] |
| Loading | Skeletons after 300 ms |
| Working | Downloads, environment builds, conformance and smoke as StepTrails with real steps |
| Error: hash mismatch | "File {n} of {m} didn't match its hash. It was deleted, and nothing was installed." [Try again] |
| Error: conformance failed | "Conformance failed: {test}. The profile stays at declared on this host." with the evidence link |
| Error: preflight refused | §S01 copy |
| Partial capability | "Needs smoke" on every profile below smoke-passed on the session's host class; release blockers flagged |
| Offline worker | "Conformance can't run: the worker didn't start." / "linux-4090 is unreachable." |
| Offline | "Downloads need the internet." |
| Store unavailable | O10 |
| Synthetic | `test_only` profiles appear only in dev and test, with "Synthetic test output" |

**Keyboard.** ←/→ on tabs; in tables, arrow keys move between cells and Enter expands a row; Space toggles a filter
chip.

**Accessibility.** Each StatusLadder is an ordered list ("Status on mlx/m5pro: smoke-passed; next step benchmarked,
needs a preregistered benchmark"). The two claim columns have headers that say "Published by others" and "Measured
here". Tables have captions and sortable headers announced with `aria-sort`.

**Story groups.** G13, G01, G17, G18, G20.

---

### S14 Burst & monthly cap (`/burst`)

**Purpose.** Every paid run and every cent counted against the $25 monthly cap, in the open: what is waiting for
approval, what is running, what settled and on what basis, and what has not been verified about the provider (O-09,
ADR-0030, ADR-0023).

**Scope and phase.** v1-core · P1 (TB2 on the fake provider) and P3 (TB7, RunPod).

**Route and entry.** Global nav "Burst & monthly cap"; the CapChip; `G B`.

**Layout.**
1. Title "Burst and monthly cap".
2. **CapGauge**: "This month (October, UTC): $3.12 counted of $25.00 · $21.88 left". A stacked bar: settled $2.75
   (solid brass), reserved $0.37 (hatched), fixed lines $0.00 (dotted), remaining (paper). "Resets Oct 31, 7:00 pm CDT
   (Nov 1, 00:00 UTC)." "Show as table".
3. Needs you: pending quotes ("Morning Light · request 3 · ceiling $0.37 · expires 14:32" [Review]); an overrun block
   (Banner, attention: "A burst run cost more than it reserved: $0.52 against a $0.37 reservation. New burst runs are
   blocked until you acknowledge it." with the SealButton "Acknowledge the overrun").
4. **BurstRunTable**: Run · Request or brief · Provider · GPU class · State · Ceiling · Settled · Basis · Egress. A row
   expands to its timeline: "quoted 14:17 · approved 14:19 · reserved 14:19:02 · provisioned 14:19:40 · conformance ping
   ✓ · job ready 14:26 · terminated 14:26:30 (confirmed by the provider) · settled 14:40 (provider billing)"; the
   egress list by hash ("ABC score 4f2a…, lyrics plan 9c1e…, job parameters"); and the pod tag ("studio-burst ·
   run 31").
5. **LedgerTable** (append-only): Time · Entry (reserve, settle, release, overrun, fixed line, cap change) · Run · Amount
   · Month-to-date after.
6. "What isn't verified yet": "The in-image shutdown deadline is a second lock. Whether it stops billing is UNVERIFIED
   (spike open)." · "The provider spend limit is set by you at RunPod. AURA can't read it (UNVERIFIED)." · "Monthly
   reconciliation against the invoice: last done {date}" or "not done yet" · "The reaper last ran at 14:35 · 0 orphan
   pods."
7. Line: "Only you can change the cap, in Settings." [Settings → Monthly cap]

**Components.** CapGauge, QuoteRow, Banner, SealButton, BurstRunTable, RunTimeline, LedgerTable, UnverifiedList.

**States.**
| State | Treatment |
|---|---|
| Empty | "No burst runs yet. In tier 4, YuE2 runs here only after you approve each run." |
| Loading | Skeletons after 300 ms |
| Working | Running pods: "Running · 6:12 elapsed · ceiling $0.37" with the metronome tick |
| Error | "Couldn't read the ledger. Nothing was charged by reading it." [Try again] |
| Partial capability | No RunPod key in the OS keychain: "Burst runs need a RunPod API key in the OS keychain. AURA never shows or stores it anywhere else." |
| Offline worker | A lost pod: the row reads "Pod lost · settled at ceiling $0.37 (no billing data)" |
| Offline | "Live rates and burst runs need the internet. Quotes made now use the dated price snapshot, labelled with its date." |
| Store unavailable | O10 |
| Synthetic | FakeBurstProvider runs in dev and test carry "Synthetic test output" and "$0 · fake provider" |

**Keyboard.** Tables navigable with the arrow keys; Enter expands a row or opens a quote's review.

**Accessibility.** The gauge has its sentence as text and a table. Hatched and dotted patterns repeat the colours'
meaning. The ledger table has a caption ("Ledger, newest first, append-only").

**Story groups.** G15, G16, G20, G21.

---

### S15 Settings (`/settings/:section`)

**Purpose.** Everything configurable, every owner record, and the facts about storage and security, in one place.

**Scope and phase.** v1-core from P0; sections fill in with their tracer bullets.

**Route and entry.** Global nav; `G ,`; links from chips and banners.

**Layout.** Title "Settings". A left sub-navigation (a list of links; a select below 768 px): Compute · Storage ·
Monthly cap · Lanes · Audio · Accessibility · Owner records · Security · About.

**Compute.** The default compute profile (tier and the placement table from S02). Worker hosts: name, host class,
reachability ("reachable" or "unreachable since 14:02"), conformance evidence, "Added with `studioctl worker add`";
tokens are never shown. "Start a new session after {4 hours} idle" (one constant; §6 Q5).

**Storage.**
- STUDIO: location, logical size cap ("900 GB · raise it with" a CommandBlock for `hdiutil resize`), band size (measured
  or default), free space as in S01 step 4, and the margin "10 GiB (10.74 GB)", editable.
- Fixed facts: "Heavy jobs pause while the internal disk has under 2 GiB free."
- Roots: project store, environments and the uv cache ("Environments and the uv cache always move together: `studioctl
  setup --envs-root`").
- Hygiene: Spotlight status, Time Machine exclusion, last clean detach, "Reclaimable inside the image: {n} GB · reclaim
  it offline with" a CommandBlock for `studioctl store compact`.
- Backup: destination ("Not chosen" is owner-pending), last backup, last `fsck`, "Remind me weekly" (on by default),
  CommandBlocks for `studioctl store backup <dest>` and `studioctl store fsck`. Copy: "Backup Plus is one physical drive.
  The backup is the only second copy of your irreplaceable work."
- Old caches on the internal disk (the S01 table).

**Monthly cap.** "$25.00 a month" and a SealButton "Change the monthly cap" opening a dialog: new amount, an optional
note, "This is recorded in the ledger." and the SealButton "Set the cap to ${n}". Lowering below the month-to-date is
allowed; new quotes are then refused until the month resets.

**Lanes.** "New songs start in: ◯ Individual" (the default, editable). The three lane definitions in plain words.
"A song's lane is changed on its Song page; that is an owner act and re-checks everything in the song."

**Audio.** Output device (Chromium's `setSinkId`; elsewhere "follows the system output"); input device; the capture
processing check ("Echo cancellation, noise suppression and auto gain are turned off for captures, and this browser
honours it ✓"); "Audition switch crossfade: 25 ms". Line: "Auditions play 48 kHz, 24-bit previews."

**Accessibility.** Theme (System · Vellum · Lamplight); Contrast (System · More); Motion (System · Reduce); Single-key
shortcuts (On · Off); "Announce job changes" (All · Only when something needs me · Off).

**Owner records.** Read-only lists with time and hash: license acceptances (component, license, revision, sha256);
risk acceptances (the named risk and the one use it allows); lane changes; cap changes; overrun acknowledgements;
verdicts (count, with a link to each song). "Accept a risk…" opens O9.

**Security.** "This browser is unlocked (since Oct 9, 9:02 am)." [Lock this browser] (drops the cookie; S00 next time).
"Automation token: in ~/.config/studio/. It's never shown here. Scripts and agents that use it can do everything except
owner acts." "Serving on 127.0.0.1 only" (or "and on the tailnet, with a token"). OS keychain: "RunPod API key: present"
or "absent"; "Hugging Face token: absent (not needed for ACE)". Values are never shown (§6 Q8 for how they are set).

**About.** `{productName}` · build · contracts version · "AURA's own code: all rights reserved (license choice pending)"
· link to the component register · "Contact: `hello@islanddevcrew.com`" as selectable text, never a link · "Copy a
diagnostics summary" (versions, OS, tier, store facts; no personal data, no secrets).

**Components.** SubNav, PlacementTable, HostRow, CommandBlock, FieldRow, SealButton, CapDialog, RecordList, Banner.

**States.**
| State | Treatment |
|---|---|
| Empty | Records lists: "No license acceptances yet." etc. |
| Loading | Per section |
| Error: save failed | "Couldn't save that setting. The previous value is still in force." |
| Partial capability | `setSinkId` unsupported: output follows the system; tailnet binding not configured: shown as off |
| Offline worker | Worker hosts unreachable as above |
| Store unavailable | O10 (Settings still opens read-only for Storage facts) |

**Keyboard.** ↑/↓ in the sub-navigation; Tab through fields; Enter or Space to toggle.

**Accessibility.** Each section is a `form` region with a heading; settings that take effect at once announce "Saved".
Theme, contrast and motion apply immediately and persist per browser.

**Story groups.** G01, G02, G15, G16, G17, G18, G19, G21.

---

## 2. Shared surfaces

### O1 Jobs drawer

**Purpose.** Every job in the studio, live from the event stream, with honest states and the one action a job allows
(cancel).

**Layout.** A right drawer, 400 px (full width below 768 px). Heading "Jobs". A scope switch "This song · All". Groups:
"Needs you" · "Running" · "Queued" · "Finished in the last 24 hours" · "Failed". A **JobRow**: kind and subject
("Generate · Morning Light · candidate 1", "Transcribe · hum 0:41", "Export · Morning Light"), placement chip, the state
line from S08's table, elapsed time, the metronome tick when running, and "Cancel" or "Open".

**Blinding.** Rows belonging to a request whose audition is open read "Candidate 1 · hidden until your verdict", with no
route, profile or placement.

**States.** Empty: "Nothing is running." Error: "Lost the job stream. Reconnecting…" (the stream resumes from the last
event id; nothing is lost). Store unavailable: rows show `failed(store_unavailable)`.

**Keyboard.** Shift+J toggles; ↑/↓ move; Enter opens; Delete asks to cancel the focused job (confirmation required);
Esc closes.

**Accessibility.** `aside` with the heading "Jobs"; group headings; job changes go to the shared polite live region,
throttled as in §0.7.

**Story groups.** G07, G20, G21.

### O2 Paid-run approval dialog (owner act)

**Purpose.** Jon's single-use yes to one quote, with everything he needs to decide in front of him (ADR-0030).

**Entry.** "Review and approve" on a QuoteCard (S08), a quote row (S14, S12 Runs) or the NeedsYou popover. Opening it
fetches the challenge nonce (`POST /quotes/{id}/challenge`).

**Layout.** A dialog, 560 px. Title "Approve this paid run?". A summary sentence: "Candidate 1 of Morning Light runs on a
rented GPU. It can cost at most $0.37." Then a definition list:
- "Provider · RunPod · secure cloud"
- "GPU class · 24 GB class (RTX 4090; fallbacks A5000, RTX 3090)"
- "Rate · $1.10 an hour · read live at 14:17" or "· price snapshot from Oct 9 (the live rate couldn't be read)"
- "Jobs · 1: score to song (R1) with `yue2-3b-score`"
- "Time allowed · up to 20 min, including boot and the weights download (job estimates: unmeasured, VENDOR × 3)"
- "Ceiling · $0.37 (20 min at the highest rate in the GPU list)"
- "This month · $2.75 settled + $0.37 reserved + $0.00 fixed = $3.12 of $25.00"
- "After this run · at most $3.49 counted · $21.51 left"
- "What leaves this Mac · the ABC score (4f2a…c41f), the lyrics plan (9c1e…77a0), the job parameters"
- "What never leaves · your hum, your reference standards, any Suno audio"
- "Lane · ◯ Individual · YuE2 is allowed here (CC BY-NC 4.0, individual-creator permission)"
- "Expires · 14:32 (in 14 min)"

Every value above is an example (the $1.10 rate and the $0.37 ceiling are the architecture's INFERRED illustration;
the GPU names are placeholders). Every real field comes from the quote, and pod rates stay UNVERIFIED until P3's spike.

Buttons, in tab order: "Not now" (quiet) · "Decline the burst" (quiet) · **SealButton** "Approve and reserve $0.37"
(last; never the default).

After approval: "Approved. $0.37 is reserved against this month's cap (ledger entry 2c4d…9a10). Starting the pod." The
dialog closes and the JobCard moves to Preparing.

**Refusals** (the SealButton is absent; the reason and the way forward replace it):
| Case | Copy | Actions |
|---|---|---|
| Over the cap | "This run's ceiling ($0.37) would take October past the $25.00 cap ($24.80 already counted). It can't be approved." | "Decline the burst" · "Change the cap in Settings" |
| Overrun not acknowledged | "Burst runs are blocked until you acknowledge an overrun from Oct 8." | "Review the overrun" |
| Expired | "This quote expired at 14:32. Rates may have moved. Nothing was spent." | "Get a new quote" |
| Job list changed | "The job list changed after this quote was made, so it no longer applies." | "Get a new quote" |
| Compute profile switched | "You switched compute tier, so this quote is void." | "See the new quote" |
| Offline | "Burst runs need the internet. Nothing was spent." | "Not now" |
| No owner scope | "Unlock this browser to approve paid runs." | "Unlock" |

**Keyboard.** Focus starts on the title. Tab moves through the details (each row is focusable read-only text only when
it has a Copy action) and then the buttons. Esc is "Not now" (the quote stays pending until it expires). Enter does
nothing unless a button has focus.

**Accessibility.** `role="dialog"`, `aria-modal="true"`, labelled by the title and described by the summary sentence.
The expiry is announced at 5 minutes, 2 minutes, 1 minute and on expiry, not every second.

**Story groups.** G15, G16, G17, G20.

### O3 Provenance drawer ("How this was made")

**Purpose.** Everything needed to say how an artifact came to be, readable by a person (ADR-0009, ADR-0029).

**Layout.** A right drawer, 480 px. Heading "How this was made". Sections:
1. "What it is": origin ("Generated mix", "Separated source", "Human recording", "Rendered guide", "Imported mix"…, and
   `tts_render` when narration arrives), media facts, hash, retention class, `synthetic_test`.
2. "What made it": producing job, engine profile and revision, weights revision and hash, code commit, environment lock
   or image digest, seed.
3. "Intent and actual": a two-column table, one row per parameter. A row where the profile changed the intent carries ≠
   and words: "Guidance: you set — · the engine used 1.0 (fixed by turbo)".
4. "Where and when": host, host class, compute profile, placement, cold or warm, load and run times (MEASURED-LOCAL).
5. "Lanes and licenses": the operator lane, eligible lanes, the license chain with obligations, allowed uses.
6. "Made from": an indented **ParentTree** with typed edges: "derived from" · "converted from" · "analyzed by". Analyzed-by
   edges carry the note "doesn't pass on its lane or license".

**Blinding.** For a candidate in an open audition: "Hidden until your verdict."

**Keyboard.** Shift+P opens it for the focused artifact; ↑/↓/←/→ move through the tree; Mod+C on a hash copies it; Esc
closes.

**Accessibility.** A `tree` with `aria-level`; tables with headers; hashes read as described in §0.3.

**Story groups.** G09, G17, G20.

### O4 Export sheet

**Purpose.** Produce a verified export bundle from a keeper, with nothing capped and nothing hidden (ADR-0019,
ADR-0029).

**Layout.** A sheet, 720 px. Title "Export {song title}". Formats, as a checklist showing only what is implemented:
- "Mix at its native rate · 48 kHz · stereo · float32 WAV, bit-exact" (always included; not a checkbox).
- "48 kHz, 24-bit deliverable · TPDF dither seeded from this export" (only when the native rate differs; otherwise the
  line "The native rate is already 48 kHz, so no conversion is needed").
- "MIDI · with the tempo map and section markers".
- "MelodySpec and SongSpec (JSON)".
- "Aligned stems · zero start, equal length" (v1-studio; only when stems exist).
- "ExportManifest" (always included).
Then a summary of what the manifest will say:
- Loudness: "−16.2 LUFS integrated · −0.8 dBTP · BS.1770-4 (pyloudnorm) · AURA meter v1".
- Lanes: "Eligible: ◯ Individual · △ Research. This song's lane: ◯ Individual ✓".
- AI disclosure: "Yes · generated vocal and accompaniment (`ace-2b-sft-mlx`)".
- "Converted vocal · No".
- Human contributions: "Melody, lyrics, 27 corrections, your choices".
- License chain with obligations, for example "YuE2 weights: CC BY-NC 4.0 under an individual-creator permission.
  Whether and how to release is your decision."
- Imported terms, when the source is an imported mix.
- Preflight: "Needs 0.2 GB on STUDIO (exports clone stored audio where they can)".
Primary "Export". Working: "Rendering offline" → "Verifying: decoding and hashing every file again (3 of 5)" →
"Verified · 5 files · 3:41 pm" with "Save as .zip" and "Copy folder path".

**Refusals and failures.**
- Lane: "This keeper can't be exported in the LLC lane: its closure includes YuE2 audio (individual and research lanes
  only)."
- Verification: "Verification failed: the 48 kHz deliverable didn't decode to the expected length. The export wasn't
  offered."
- Store unavailable: O10. Preflight: §S01's copy.

**Keyboard.** Tab through the checklist; Space toggles; Mod+Enter exports; Esc closes (an export in progress continues
in the jobs drawer).

**Accessibility.** The checklist is a fieldset with a legend; locked items are plain text, not disabled checkboxes; the
verification count is announced on completion only.

**Story groups.** G09, G11, G17, G20.

### O5 New song sheet

**Layout.** Title "New song". "Title" (optional; default "Untitled song {n}"). "Who is this song for?" radio:
- "◯ Individual · You, personally. The default."
- "▢ LLC · Island Development Crew ventures, Sabbath Echo included. No non-commercial components: no YuE2, no Demucs."
- "△ Research · Private experiments. Never released."
Note: "Changing the lane later is an owner act, and AURA re-checks everything in the song when you do." Primary "Create
song" → S05.

**Keyboard.** Arrows in the radio group; Enter creates. **Story groups.** G03, G17.

### O6 Lane change dialog (owner act)

**Layout.** Title "Change this song's lane?". Current lane and the radio group from O5. Copy: "AURA re-checks every
artifact in the song. If any of them can't enter the new lane, nothing changes." SealButton "Change the lane to LLC".

**Outcomes.**
- Changed: "Lane changed to ▢ LLC. 37 artifacts re-checked; all are eligible."
- Refused: "Not changed. 4 artifacts here can't enter the LLC lane:" then a list ("Candidate 1 of request 2 · YuE2 ·
  CC BY-NC 4.0"; "Vocal separation for request 2 · Demucs · research or personal use only") and "To make this song in
  the LLC lane, start a new LLC song and bring the same hum or MIDI file into it."

**Story groups.** G17, G16.

### O7 License acceptance dialog (owner act)

**Layout.** Title "Accept this license?". Shown before any weights download, gated or not, whether the weights come from
Hugging Face, a pinned URL or a file inside a pinned package. Component and role; each license document with a plain link
to its text, its pinned commit or revision and its hash (YuE2 shows two: the Hugging Face LICENSE, CC BY-NC 4.0, and the
GitHub MODEL_LICENSE that carries the individual-creator permission); the weights source; weights manifest hash; obligations ("Show 'MiniMax-Music3' in commercial interfaces…" where
applicable); allowed lanes; "AURA records your acceptance under models/licenses/ and downloads from this revision only."
SealButton "Accept the {license} license for {component}". Then the download starts (S13). If a document's hash
changes later, the acceptance is void and the component is refused until Jon accepts again: "The license text for
{component} changed since you accepted it. Review it again before AURA uses it."

**Story groups.** G13, G16.

### O8 Import sheet: references and imported mixes

**Layout.** Title "Import". A choice: "A reference (to listen to beside your work)" · "An imported mix (a finished song
from outside AURA)".

**Reference.** A WAV file; "Title" and "Artist" as text; for the evaluation, "Feel" (the four O-05 feels); "Permission":
"I own this recording" · "I hold a license" (with a note). "Allowed use": "Listening only" (the default, and the only
choice for a reference standard) or "Global timbre/style reference" (only where a profile implements it and the
permission allows conditioning). Recording the permission is an owner act: a **SealButton** "Record this permission". If Jon marks the source as Suno: "A Suno song can't be a reference in AURA (the Suno
boundary). Import it as a mix to listen to it, measure it and DSP-finish it." The reference option is then disabled.

**Imported mix.** A WAV file, or a set of Suno stems from one download; "Where it's from": "Suno · my own download" ·
"My own mix from a DAW" · "A recording I bought" · "A recording I licensed" (with its license document). For Suno: "Plan
when downloaded" (Pro or Premier; free-plan output can't be imported because it isn't commercially usable), "Downloaded
on", and "Whose Suno account" (mine, or the LLC's; an LLC project needs the LLC's account or a written license). For a DAW
mix: "Which AURA exports does it contain?" (a picker of this store's export bundles) and "Does it contain anyone else's
audio, or Suno audio?" (yes turns it into a Suno or licensed import). AURA checks the file on import: a Suno provenance
mark makes it a Suno import, and an AURA export tag must match an export Jon picked. A DAW mix inherits the lanes of the
exports it contains, so a mix of an individual-only export can't enter an LLC song. Copy for Suno: "AURA can listen to
it, measure its loudness and DSP-finish it (mixing, mastering and format, never generation). It will never use it in an
audition, as a reference, as engine input, for separation, for training or as test material. Suno's embedded provenance
stays intact." A purchased recording is for listening, measuring and evaluation anchors only. Decoder limit: "AURA reads
WAV only for now."

Primary **SealButton** "Import as mine" (attesting an import is an owner act; an agent can prepare the sheet but not
press it). Every kind is irreplaceable and carries its permission or terms record.

**Story groups.** G14, G12, G06.

### O9 Risk acceptance dialog (owner act)

**Layout.** Title "Accept a named risk?". Copy: "This widens what AURA may do with one import, for one named use. The
Suno boundary keeps Suno audio out of auditions, references, evaluation, training and testing always; engine input,
conditioning, separation, edit input and conversion input are the only uses you can sign for here, one at a time. This is
not legal advice." Fields: the import; the one use (engine input, conditioning, separation input, edit source or
conversion input); a note.
Uses that need an ADR change first are listed but not selectable: "An audition arm or an evaluation reference needs
ADR-0010 amended first. This dialog can't grant it." SealButton "Sign this risk acceptance". Signed acceptances appear in
Settings → Owner records.

**Story groups.** G14, G16.

### O10 Store unavailable

**Purpose.** Say plainly that STUDIO has gone, what that stopped, and how to get it back (arch §4.2 mount watch).

**Layout.** A full-page takeover over the shell (the masthead's StoreChip stays). Title "STUDIO isn't mounted". Copy:
"Your work lives on the STUDIO volume on the Backup Plus drive. AURA can't keep or record anything until it's back.
Jobs that were running stopped, and nothing partial was kept." Steps: "1 · Connect the Backup Plus drive." "2 · Run
`studioctl store attach`." "If the drive was unplugged without detaching, AURA checks the volume before reopening it."
Live line: "AURA will notice when STUDIO is back." When it returns: "STUDIO is back. Its checks passed. Reopening…" then
the page Jon was on.

**Accessibility.** The title is announced `assertive` once. **Story groups.** G21, G01.

### O11 Keyboard map and command palette

**Keyboard map** (`?`): a sheet listing the global keys (§0.8) and this screen's keys, grouped, with the OS's modifiers,
and a link to Settings → Accessibility → "Single-key shortcuts".

**Command palette** (Mod+K): a search field over screens, songs and this screen's actions ("Go to Melody", "Open the
audition", "Export…"). It opens dialogs for owner acts but never performs one. ↑/↓ move, Enter runs, Esc closes.

**Story groups.** G19.

### O12 PlayerBar

**Purpose.** Play anything that may be heard outside an audition: captures, guides, keepers, imported mixes,
references, smoke renders and exports.

**Layout.** A 64 px bar on `--paper-raised`: play/pause (44 px), title, an origin chip ("Keeper", "Capture · hum",
"Guide · not a candidate", "Imported mix · Suno", "Smoke render"), the position and duration, a TimeRuler (no waveform at
this size), "How this was made" (O3), close.

**Rules.** It refuses an unrevealed candidate (§0.2) and hides during an audition and in the Studio.

**Keyboard.** Space (when the page has focus); ←/→ seek 5 s when the bar has focus. **Story groups.** G03, G08.

---

## 3. State coverage map

✓ = specified in that section; — = not applicable; O10 = handled by the takeover.

| Screen | Empty | Loading | Working | Error | Partial capability | Offline worker | Offline | Store unavailable | Blind | Synthetic | Stale revision |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S00 Unlock | — | ✓ | — | ✓ | — | — | — | O10 | — | — | — |
| S01 First run | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | O10 | — | — | — |
| S02 Session | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | O10 | — | — | — |
| S03 Library | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | O10 | ✓ | ✓ | — |
| S04 Song page | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | O10 | ✓ | ✓ | — |
| S05 Capture | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | O10 | — | — | — |
| S06 Melody | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | O10 | — | — | ✓ |
| S07 Song intent | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | O10 | — | — | ✓ |
| S08 Generation | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | O10 | ✓ | ✓ | — |
| S09 Audition | — | ✓ | — | ✓ | ✓ | — | — | O10 | ✓ | ✓ | — |
| S10 Studio | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | O10 | ✓ | — | — |
| S11 Finishing | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | O10 | — | ✓ | — |
| S12 Evaluation | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | O10 | ✓ | ✓ | — |
| S13 Engines & licenses | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | O10 | — | ✓ | — |
| S14 Burst & monthly cap | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | O10 | — | ✓ | — |
| S15 Settings | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | O10 | — | — | — |

---

## 4. Story-group traceability

| Group | Screens and surfaces | Feature IDs (feature-inventory) | ADRs | Tracer bullets / phases |
|---|---|---|---|---|
| G01 Install, studio volume, preflight | S01, S13 Downloads, S15 Storage, O10 | J4, J9 | 0015, 0016, 0034 | TB0 (P0), TB3 (P2) |
| G02 Compute tiers and sessions | S01 step 2, S02, ComputeChip, S15 Compute | J8 | 0003, 0024 | TB0, P6 |
| G03 Library and projects | S03, S04, O5, O12 | J1, J2, J3, F14 | 0009, 0028 | TB1 (P1) |
| G04 Melody capture | S05 | A1, A2, A3 | 0004 | TB1a, TB1c, TB4 |
| G05 Transcription and correction | S06 | A4, A5 | 0004, 0033 | TB1d, TB6 |
| G06 Song intent | S07, O8 | B1, B3, B4, B5, B7, B8, C5, G2; A9 (v1-studio) | 0018, 0032, 0007 | TB1a |
| G07 Generation, routes, jobs | S08, O1 | A6, C1, C3, C4, C7, J7 | 0001, 0002, 0004, 0012 | TB1a, TB3, TB7 |
| G08 Audition, verdict, reveal, keeper | S09, S04, O12 | J10, C1, C2, A7, C9 | 0005, 0010 | TB1b, TB5 |
| G09 Provenance, keeper cost, export | S04, S11, O3, O4 | I1, I2, I3, J5, C9, J12 | 0009, 0019, 0023, 0029 | TB1b |
| G10 Studio timeline and edits | S10 | F1, F2, F3, F5, D1, D2, D3, D4, D5, D6, D8, D9, C10 | 0013, 0017 | TB9 (P5) |
| G11 Stems | S10 stems drawer, O4 | E1, E2, E3, E4; E5, E6 named only | 0006 | P5 |
| G12 Evaluation | S12, S09 eval mode, O8 | J10, J11, A4 (hum benchmark) | 0010, 0027 | TB6 (P2), TB8 (P4) |
| G13 Engines, registry, licenses | S13, O7, S01 step 5 | J6 | 0001, 0011, 0016, 0027 | TB0, TB3 |
| G14 Imports and the Suno boundary | O8, O9, S11 | A12 | 0021, 0036 | P5 |
| G15 Paid runs and the cap | S08, O2, S14, S15 | (O-09) | 0030, 0023 | TB2 (P1), TB7 (P3) |
| G16 Owner acts and local security | S00, §0.6, NeedsYou, S15 Security | (O-09) | 0031, 0025, 0037 | TB0, TB2 |
| G17 Operator lanes | LaneTab, O5, O6, S07, O4 | (O-06) | 0011, 0029 | TB1, TB7 |
| G18 Platforms and capabilities | S05, S10, S13 Capabilities | J19, J20 | 0024, 0012, 0014 | P0, P5, P6 |
| G19 Accessibility | §0.7, every screen | — | 0012 | every phase |
| G20 Honest labels and progress | §0.3–§0.5, every screen | C2, C8 | 0005, 0027 | every phase |
| G21 Failure and recovery | O10, S08 failure table, S06/S07 stale revision, S15 Storage | F14 | 0028, 0034 | P1 |

Features deliberately without a v1 surface: B2, B6 (an LLM lyric writer appears only once an LLM profile exists; B6 is
v1-core optional), B9–B14, C6 (v1-studio priced n; added to S07 when implemented), C11–C13, E5–E10 (beyond the named
cards), F4, F6–F13, G1, G3–G7 (v2 voice registry), H1–H8 (narration spec), I5 beyond O4's MIDI line, I6–I11, J13–J18,
K1–K5, L1–L11. Their absence follows the owner rule that controls appear only where a backend implements them.

---

## 5. Component and token inventory

### 5.1 Chrome and states

| Component | Purpose | Notes | Used by |
|---|---|---|---|
| **AppShell** | Masthead, NavRail, main, margin, PlayerBar, footer | landmarks as §0.2 | all |
| **Wordmark** | `productName` in Newsreader small caps | live text | all |
| **LaneTab** | Operator lane, glyph + word | never colour-coded | masthead, S03, S04, S07, S12 |
| **ComputeChip**, **StoreChip**, **CapChip** | Masthead facts | exact formats §0.2 | all |
| **NeedsYou** | Count and popover of pending owner acts and auditions | lists who prepared each | all |
| **NavRail** | Global and project navigation with state glyphs | icon rail at 768–1199 px | all |
| **MovementSpine** | I–VI with state | not a wizard | S04, NavRail |
| **StateBlock** | Empty, error and partial blocks | one primary action | most |
| **Banner** | Inline info, attention or error with up to two actions | | most |
| **WorkerBanner** | Names a worker and host, what waits, what works | | S05–S14 |
| **Toast**, **UndoBar** | Transient confirmation; with Undo for 8 s | never the only record | S04, S06, S07, S10 |
| **StepRail**, **StepTrail** | Steps of a flow; real states of a job | `aria-current="step"` | S01, S08, S10, S13 |
| **CommandBlock** | A command to copy, labelled "Owner action" when it needs admin rights | | S01, S15, O10 |
| **SealButton** | The owner-act control | §0.6 | O2, O6, O7, O9, S09, S13, S14, S15 |
| **CommandPalette**, **KeyboardMap** | O11 | | all |

### 5.2 Figures and badges

| Component | Purpose | Used by |
|---|---|---|
| **FigureLabel** | MEASURED-LOCAL and the other labels | everywhere |
| **Badge** | §0.5 table | S04, S08, S09, S10 |
| **OriginBadge** | Artifact origin on tracks and the player | S10, O12 |
| **PlacementChip** | Where a job runs | S07, S08, O1 |
| **StatusLadder** | Computed profile status per host class | S13, S02 |
| **CapGauge** | Month-to-date against the cap, with patterns | S14 |
| **UncertaintyPlot** | A preference with its interval, clustered by brief | S12 |
| **LoudnessReport** | LUFS, LRA, true peak, sample peak, standard and meter | S11, O4 |
| **KeeperCost** | Candidates, compute, timings and listening per keeper | S04 |

### 5.3 Audio, notes and listening

| Component | Purpose | Notes | Used by |
|---|---|---|---|
| **RecordButton** | 72 px red-pencil disc | `aria-pressed` | S05 |
| **LevelMeter** | dBFS meter with peak text and clip memory | `role="meter"` | S05, S10 |
| **InputChecks** | `getSettings()` results | | S05, S15 |
| **CaptureReview** | Play, keep or discard a recording | | S05 |
| **LiveMidiRoll** | Notes as they arrive | decorative + count | S05 |
| **PianoRoll** + **ConfidenceShading** | The MelodySpec editor | `role="application"` | S06 |
| **NoteList** | The editable list alternative | `role="grid"` | S06 |
| **TempoKeyBar**, **PhraseStrip**, **NoteInspector**, **RevisionBar**, **HistoryDrawer** | Melody editing | | S06, S07 |
| **LyricsEditor**, **TranscriptPanel**, **SongFormEditor**, **RouteTable**, **AbcPreview**, **IntentLedger**, **ConflictNote** | Song intent | | S07 |
| **PlanTable**, **RoutePicker**, **QuoteCard**, **JobCard** | Generation | | S08 |
| **AuditionDeck**, **ArmButton**, **Transport**, **TimeRuler**, **IntervalBracket**, **VerdictPanel**, **RevealCard**, **CommitmentCheck** | The audition | labels only in the DOM | S09 |
| **KeeperCard**, **Waveform** | The keeper | waveform is display only (wavesurfer.js core may draw it) | S04, S10 |
| **TransportBar**, **SectionRuler**, **LyricsStrip**, **TrackHeader**, **ClipView**, **Fader**, **Inspector**, **EditOperationPanel**, **StemsDrawer**, **StemOperationCard**, **CopyToMainSheet**, **PreservationResult**, **TrackList** | The Studio | never wavesurfer-multitrack (ADR-0013) | S10 |
| **DspChain**, **DryFinishedCompare**, **TargetFields** | Finishing | | S11 |
| **PlayerBar** | O12 | | shell |

### 5.4 Setup, registry, money and records

| Component | Purpose | Used by |
|---|---|---|
| **HardwareSnapshotCard**, **TierCard**, **PlacementTable**, **ImpactSummary** | Compute | S01, S02, S15 |
| **VolumeCard**, **PreflightRow**, **DownloadRow** | Storage and downloads | S01, S13, S15 |
| **ProfileCard**, **ClaimsColumns**, **NotGarbledCheck**, **CapabilityRow**, **ComponentTable** | The registry | S13 |
| **FeelSlot**, **PreregCard**, **BriefTable**, **RunTable**, **EvidenceRow** | Evaluation | S12 |
| **BurstRunTable**, **RunTimeline**, **LedgerTable**, **QuoteRow**, **UnverifiedList** | Money | S14 |
| **ApprovalDialog** | O2 | S08, S12, S14 |
| **ParentTree** | Typed provenance edges | O3 |
| **RecordList** | Owner records | S15 |

### 5.5 Token summary

Colour roles, type and motion are in §0.1. The rest:

| Token | Value |
|---|---|
| `--space-1` … `--space-8` | 4, 8, 12, 16, 24, 32, 48, 72 px |
| `--radius-control` / `--radius-sheet` / `--radius-pill` | 2 px / 6 px / 999 px |
| `--shadow-raised` | `0 1px 0 rgb(29 26 22 / 6%)` |
| `--shadow-overlay` | `0 12px 32px rgb(29 26 22 / 14%)` (Lamplight `rgb(0 0 0 / 50%)`) |
| `--focus-ring` | `2px solid var(--ink)`, offset `2px` on `--paper` |
| `--target-min` / `--target-primary` / `--target-hero` | 24 / 44 / 72 px |
| `--margin-col` / `--nav-rail` / `--nav-rail-compact` | 296 / 220 / 64 px |
| `--player-height` / `--transport-height` | 64 / 56 px |
| `--bp-narrow` / `--bp-editor` / `--bp-wide` | 768 / 1024 / 1200 px |
| `--grain-opacity` | 0.03 Vellum, 0.02 Lamplight, 0 in increased contrast |
| `--ab-crossfade` | 25 ms (audio constant, §6 Q6) |

---

## 6. Open questions for the lead

1. **Verdict reason codes.** `verdict/1` holds optional axes, problem intervals and seconds listened per label. The
   reason chips on S09 need either a field (an additive minor version) or to be dropped in favour of axes and interval
   notes. Recommendation: add `reasons[]` per label, because a later taste memory (K1, v2) will want them.
2. **The smoke "not garbled" check as an owner act.** ADR-0031's list does not name it, but `Registry.record` rejects a
   listening gate without owner verdicts, and an agent must not be able to record "not garbled". Recommendation: add it
   to the owner-act list; this spec already draws it with the seal.
3. **Deferring identities in eval mode.** Revealing each eval audition's identities would teach Jon the routes' sound and
   weaken later blind auditions and the hidden repeat pairs. This spec checks the commitment per audition but shows
   identities only when the preregistered set concludes. It needs a line in ADR-0010 or the eval contract.
4. **Launch-token transport.** S00 reads the token from the URL fragment and removes it at once, with a paste fallback;
   it never uses a query string. Confirm before the TB0 ticket.
5. **Session idle gap.** S02 appears after each `serve` start and after "an idle gap"; this spec proposes 4 hours, as one
   constant.
6. **A/B switch crossfade.** 25 ms equal power is a design default, not a measured value; tune it by ear.
7. **MP3 export.** Feature I1 lists WAV and MP3; the architecture's export task produces WAV, MIDI, specs and the
   manifest, and an MP3 encoder's license is unverified. v1 offers no MP3 (controls appear only where implemented).
8. **Setting keychain secrets.** The control service reads the RunPod key and the Hugging Face token from the OS
   keychain, but no `studioctl` command for setting them is listed. Settings shows only presence or absence.
9. **Backup from the UI.** `backup`, `fsck` and `compact` are CLI-only, so the weekly reminder can only show commands.
   Should the Studio API expose `backup` and `fsck` (not owner acts) so the reminder can run them?
10. **The default route order before a benchmark.** Applied default (ticket set note (f); confirm with Jon): the plan-rules
   contract fixes R1 (only without a burst, or with Jon's per-request opt-in), then R2-synth, R2-raw, text, with no quality
   claim; route-standing records from concluded preregistered sets adjust it; the route comparison decides ADR-0004's
   reverse-if. The original question: the plan needs a stated default order (formerly "two best eligible routes")
    until a benchmark record ranks routes.
11. **Where gate values live.** Resolved in the design review: the badges "Duration off", "Lyric errors high" and
    "Melody not kept" read their thresholds from gate records in `contracts/registry/gates/`, committed before any real
    evidence (the adherence thresholds by the adherence ticket); a test fails on a hard-coded threshold.
12. **Moving work between lanes.** O6's refusal tells Jon to start a new LLC song and bring the same hum or MIDI in by
    re-importing it; there is no API resource for copying a capture across projects. Confirm that is enough.
13. **Interface components in the register.** Newsreader, IBM Plex Sans and Mono, Bravura Text (all OFL 1.1) and
    Lucide (ISC) need component-register rows before adoption, like any other component (ADR-0011).
14. **The default SongForm.** S07 starts a new song with one vocal section per phrase, in order. Confirm, or start
    empty.
15. **Synthetic labels inside a blind audition.** The glossary says only "Unplayable" shows during a blind audition;
    the architecture says synthetic output is labelled on every surface. This spec withholds the per-arm badge and shows
    an audition-level notice ("One or more arms is Synthetic test output") plus the test band. Confirm.
16. **Owner-pending defaults used here.** Chromium for the Studio (Q10), Jon as the only voter and gate owner (Q8),
    English lyrics by default (Q6), the backup destination (ADR-0034), Linux and Windows hardware (Q1). Each appears in
    copy only as a default that can change.

---

## Section list

S00 Unlock · S01 First run (S01a `studioctl setup`, S01b in the browser) · S02 Session start · S03 Library · S04 Song
page · S05 Capture · S06 Melody · S07 Song intent · S08 Generation · S09 Audition · S10 Studio · S11 Finishing · S12
Evaluation · S13 Engines & licenses · S14 Burst & monthly cap · S15 Settings · O1 Jobs drawer · O2 Paid-run approval
dialog · O3 Provenance drawer · O4 Export sheet · O5 New song sheet · O6 Lane change dialog · O7 License acceptance
dialog · O8 Import sheet · O9 Risk acceptance dialog · O10 Store unavailable · O11 Keyboard map and command palette · O12
PlayerBar.

Contact for the project, as text only: `hello@islanddevcrew.com`
