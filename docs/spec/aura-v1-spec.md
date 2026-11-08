# AURA v1 product spec

Status: **proposed**, revised by the 2026-10-09 design review (architecture.md, "Design review log"); the ticket set is a draft until Jon accepts this spec and ADR-0025…0037 · Date: 2026-10-09 · Product: AURA (working name, held in
one constant, O-10) · Studio host: the Mac first; the control service and UI are portable to Windows and Linux, with Studio
playback gated per operating system (ADR-0024).

Sources this spec synthesizes:

- **Owner decisions** O-01…O-11 and the owner-pending defaults: `docs/research/OWNER-DECISIONS-2026-10-09.md` (binding).
- **The verified evidence base**: `docs/research/RECONCILIATION.md` (§0 verdict; §1 agreements A1–A32; §2 conflicts C1–C55
  and gap research GAP-01…08; §4 component register; §6 proposed decisions D-01…D-24; §7 owner questions Q1–Q14; §8 what
  remains unverified), and `docs/research/evidence-register.json` (claims V-* and X-*, 122 component rows; the component register adds 9 supplement rows, 131 in all).
- **The feature inventory**: `docs/research/feature-inventory.md`. Its ids (A1…L11) are cited in brackets.
  Unbracketed ids cite RECONCILIATION.md (agreements A1–A32, conflicts C1–C55, GAP-01…08, owner questions Q1–Q14,
  and its § numbers); V-* and X-* cite the evidence register; T-01…T-16, TB0–TB9 and P0–P6 (with exit checks such as
  P1-9) cite the architecture.
- **The measurement note** on the Backup Plus drive (MEASURED-LOCAL, 2026-10-09).
- **The v1 architecture**: `docs/spec/architecture.md` (modules, contracts, seams, compute, storage, lanes, tracer bullets
  TB0–TB9 and phases P0–P6 with exit evidence).
- **The ADRs**: `docs/adr/0001`–`0037`. ADR-0001…0024 accept D-01…D-24 as amended by the owner decisions; ADR-0025…0037
  record the architecture's own decisions.
- **The glossary**: `GLOSSARY.md`. This spec uses its terms exactly and avoids the words it lists to avoid.
- **House style and method**: the JOVRA iOS v1 spec and its `spec/` contract pattern, and the vendored `to-spec`,
  `to-tickets`, `implement-spec`, `codebase-design`, `domain-modeling` and `tdd` skills.

Nothing in this spec has been built, installed, generated or listened to. Every statement that AURA "does" something is a
design commitment, not a measurement. Figures carry the labels of RECONCILIATION.md: MEASURED-LOCAL, VENDOR, COMMUNITY,
COMPETITOR-RUN, OWNER-REPORTED, INFERRED, and UNVERIFIED where no check has been made.

## Problem Statement

Jon has a melody in his head. He can hum it, sing it with or without words, or play it on a keyboard, and he wants it to
become a finished, beautiful song that is still his: a melody he can correct note by note, lyrics he wrote, an honest
choice between candidates, a keeper he can finish in a studio, and files he can take anywhere. He wants the quality of the
best hosted service he has used, Suno v6, without the parts of that service that work against him.

The tools available to him today fail him in specific, documented ways:

- **Nothing starts from his melody.** None of the three research plans designed a path from a hum to a song
  (RECONCILIATION A12). Hosted "melody preservation" is a request, not a guarantee [A6]; practitioners report melodies
  regressing between model versions [A7, GSV-12]; ACE-Step's cover kept song identity poorly in a competitor's test
  (Hit@1 2.4%, COMPETITOR-RUN; C8); and no hum transcriber is both license-clean and benchmarked on humming (GAP-01). Jon's
  tune is exactly the thing most likely to be lost.
- **Lock-in.** The features that make a song finishable sit behind the top plan: Suno Studio 2.0, its 48 kHz stem export
  and Advanced Split are Premier-only (C52, §4.2), and Mureka's MIDI and WAV export is Premier-only (C37) [L4]. Models are
  retired underneath the user (every pre-v6 Suno model is gone, C30), a hosted `auto` model setting drifts (X-31), Suno
  has no public API (C37), and unofficial endpoints are off-limits (A21).
- **Caps and credit burn.** Since 2026-09-03 downloads are capped at 20 a month on Pro and 60 on Premier (A19, V-suno-6).
  Every generation spends credits (§4.2), and one practitioner needed four to five attempts per keeper [C9]. The real
  price of a song is every attempt behind it, and no hosted tool reports it that way (C44, ADR-0023).
- **Outputs he cannot edit, and edits that destroy songs.** Users report edits that ruin keepers [D4, D5] (ADR-0017). A
  lyric fix re-sings the section, an ASR transcript overwrites the author's words [B7], an "instrumental" request still
  sings because the style text named a voice [B5, GSV-14], and controls silently do nothing on some models [C5] (C4,
  ADR-0018).
- **Dirty stems.** Suno's stems are regenerated, not separated: "Suno listens to it and regenerates each stem from
  scratch" (C22, V-sep-7). A "stem" is a new performance presented as the original part. Open separators give four to six
  stems at best, and the strongest six-stem checkpoint has no clear license (C23) [E1, E5, E9].
- **No MIDI or DAW hand-off.** The melody he hummed never comes back as MIDI with its tempo map, and aligned stems for a
  DAW are a premium feature or missing [I4, I5, L4] (C52).
- **Ownership ambiguity.** Uploading his melody gives Suno a perpetual license to it, and Suno's output may not "power,
  enable or train" another AI or be used to compete with Suno (C35, X-07, GAP-07). Open weights are not automatically
  clean either: YuE2's permission covers an individual, not a company (C9, GAP-05); Demucs's weights are for research and
  personal use only (GAP-06); MiniMax output must be disclosed as machine-generated (X-12). Copyright needs human
  authorship, and stock libraries ban AI uploads (X-44, C34). Without a record of who made what with which components,
  Jon cannot tell what he may release, or under which of his entities.
- **Quality claims he cannot check.** Every quality figure behind the open engines comes from an interested party (§0);
  "Suno 6.5" does not exist (X-06, C29); no source ran anything (A31, X-45); and the strongest open engine still lost to
  v6 by 59.3% to 31.6% in its own authors' study (C11, VENDOR-run). Automatic scorers are biased, non-commercial, or deaf
  above 8–12 kHz (C14), and best-of-n does not close the gap (C13, refuted).
- **His hardware is real, not ideal.** The Mac's 48 GiB of unified memory is not 48 GB of VRAM (A6); the internal disk
  swings between about 2 and 11 GiB free (C47, X-02, MEASURED-LOCAL); the only large disk is a spinning USB HDD formatted
  exFAT (measurement note); and the Linux and Windows GPUs are unknown and unreachable (Q1). YuE2 and MiniMax need CUDA
  (C10, C16).

From Jon's side: the melody is his, the lyrics are his, the choices are his, and he wants to own everything that comes out
of the studio, with no caps, no credits, no lock-in, and no number he did not measure himself.

## Solution

AURA is Jon's personal, local-first music studio, running open-weight engines on hardware he controls:

- **Start from the melody.** Jon hums, sings or plays into the browser, or drops in a MIDI file. The capture is kept
  exactly as received. A first transcription becomes an editable MelodySpec in a piano roll, every correction makes a new
  revision, and the MelodySpec stays the source of truth on every route (ADR-0004, ADR-0033).
- **Say what the song is.** A SongSpec holds approved lyrics in a declared language, style and exclusions, vocal mode, a
  SongForm of sections built from phrases, references with permission records, target duration and candidate count. Each
  field records what was requested, what the engine profile supports and what was observed, and conflicts are flagged
  before anything runs (ADR-0018, ADR-0032).
- **Several engines, honestly gated.** Requests name engine profiles, never engines. ACE-Step 1.5 runs on the Mac in
  every lane. YuE2 renders from a score of the melody for individual-lane projects, on an approved and capped burst.
  HeartMuLa or MiniMax compete for LLC projects by smoke. Nothing reaches the product until evidence records say it passed
  (ADR-0001, ADR-0002, ADR-0027).
- **Two candidates, judged blind.** Each generation request yields two candidates, by default one from each of the two
  best routes eligible in the project's lane. Hard constraints badge candidates and never hide them. Jon listens in a
  blind, level-matched audition and gives a verdict; only then are route, profile and seed revealed (ADR-0005, ADR-0010).
- **Keep it, finish it, take it anywhere.** The keeper is the song's version of record. It exports as an export bundle:
  native-rate audio, a 48 kHz/24-bit deliverable, MIDI with its tempo map and section markers, the specs, and a
  self-describing ExportManifest, with no caps. In v1-studio Jon arranges the keeper on a timeline, replaces a section with
  an edit operation that leaves everything else sample-identical, isolates stems with their residual, and DSP-finishes
  imports (ADR-0009, ADR-0013, ADR-0017, ADR-0019).
- **Every byte accounted for.** Artifacts are content-addressed and immutable. Each carries complete provenance: the
  producing job, profile revision, weights, seed, intent and actual parameters, host, compute profile, operator lane,
  eligible lanes and license chain. The database can always be rebuilt from content-addressed records (ADR-0009,
  ADR-0028, ADR-0029).
- **Lanes that cannot leak.** Each project is `individual` (the default), `llc` or `research`. AURA enforces each lane's
  component eligibility at seven points, so non-commercial YuE2 or personal-use Demucs output never reaches LLC work
  (ADR-0011, ADR-0029).
- **Rented compute on Jon's terms.** In tier 4, YuE2 runs on rented GPU time only after a live-rate quote, Jon's approval
  in the Studio UI, and a reservation at the ceiling against a $25 monthly cap. Declining is always allowed and always
  labelled (ADR-0030, ADR-0031).
- **Choose the machine.** A compute profile is recommended from detected hardware, chosen at install and at every session
  start, and switchable at any time. The control service and UI run on macOS, Windows and Linux (ADR-0003, ADR-0024).
- **Measured, never claimed.** Quality is judged only by Jon's preregistered blind auditions against his four reference
  standards. Suno output never enters the harness. Every number carries a figure label, and a vendor number is never shown
  as measured (ADR-0010, ADR-0021, ADR-0036).
- **Durable on a fragile disk.** The store lives in an APFS sparse bundle on the Backup Plus drive, a disk preflight guards
  every write on every volume, and a hash-verified mirror of everything irreplaceable lives on a second device (ADR-0015,
  ADR-0034).

## User Stories

Actors:

- **Jon**: the owner and only user of v1. "Jon" is the default actor.
- **Jon the listener**: Jon in his role as the blind listener in auditions and the named owner of every listening gate
  (Q8 default: the only voter).
- **The maintainer agent**: a coding or workflow agent that works AURA's tickets. It holds an automation token, never the
  owner-ui scope, and can prepare an owner act but never perform one.
- **A future open-source user**: someone running AURA on their own hardware after Jon publishes it (Q5).

Story groups are for navigation; numbering is continuous. Each group names its scope (GLOSSARY: v1-core or v1-studio) and
the feature-inventory rows and ADRs it covers. What other tools call "take lanes" or "version lanes" are **tracks** here,
because "lane" always means operator lane.

### 1. Install and compute profile

_Scope: v1-core (stories 1–26). Covers ADR-0003, ADR-0012, ADR-0016, ADR-0031, ADR-0035; O-02, O-10, O-11; architecture §3, §7.1–§7.4._

1. As Jon, I want one `studioctl setup` command that creates and attaches the studio volume, writes the environment file and records a default compute profile from AURA's recommendation, so that a clean checkout becomes a working studio without hand-editing anything.
2. As Jon, I want setup to print every command that needs administrator rights for me to run myself, and never run `sudo`, so that nothing changes my system behind my back.
3. As Jon, I want `studioctl doctor` to detect my hardware (chip, unified memory, Metal working set, GPUs and their memory, driver versions, compute capability, total RAM, WSL2 and its memory setting) and keep the raw command output, so that every recommendation can be checked against what the machine actually reported.
4. As Jon, I want AURA to recommend a compute tier from the detected hardware, with its reasons, so that I start from a sensible choice, which on this M5 Pro is tier 4.
5. As Jon, I want the recommendation to warn me about host RAM under 24 GiB for YuE2, drivers too old for cu128, a Blackwell card paired with cu126, and WSL2 memory under 24 GB, so that I meet a CUDA trap on the Session screen rather than in the middle of a job.
6. As Jon, I want AURA never to qualify a tier from hardware it has not probed, so that an unreachable Linux or Windows box is never presented as available.
7. As Jon, I want the Session screen to show the hardware snapshot, the recommended tier, all four tiers, and for each tier which engine profiles have evidence on a matching host class and which still "need smoke", so that I choose knowing what has actually been proven.
8. As Jon, I want to keep my compute profile with one click, or pick any tier, host or operating system, at the start of every session, so that the recommendation never locks me in.
9. As Jon, I want a tier my hardware cannot satisfy to be allowed, with each affected engine profile shown as resolving to a burst or to "unavailable" with a reason and a remedy before I submit anything, so that nothing is ever substituted silently.
10. As Jon, I want to switch compute profile at any time, with the switch logged in the session, so that I can move work between machines whenever I need to.
11. As Jon, I want a switch to re-plan jobs not yet dispatched, re-quote jobs awaiting approval (voiding my earlier approval) and let running jobs finish where they are unless I cancel them, so that a switch never strands or silently re-routes paid work.
12. As Jon, I want every job and artifact to record the compute profile, placement and host class it ran under, so that I can always tell where a candidate came from.
13. As Jon, I want switching compute profile never to change any project, so that my songs do not depend on which machine I happened to use.
14. As Jon, I want the Session screen to point out what changed since my last session, such as a newly reachable worker host or a new GPU driver, so that new hardware is noticed without my hunting for it.
15. As Jon, I want a tier-preset table that says where ACE, YuE2, burst, analysis and separation run in each tier, so that I can read the consequence of a choice before I make it.
16. As Jon, I want `doctor` to list stray caches on the internal disk (Hugging Face, uv, pnpm and Playwright browsers) with their sizes, and leave every deletion to me, so that the internal disk stops filling without AURA deleting anything I did not approve.
17. As Jon, I want each engine environment created lazily, the first time a profile needs it, on the studio volume and keyed by its lock hash, so that nothing heavy installs before it is used and every worktree shares one copy.
18. As Jon, I want the control service to bind only to 127.0.0.1, with a Host allowlist and an Origin check on every state change, so that a web page I happen to visit cannot drive my studio, spend my money or cast a verdict.
19. As Jon, I want `studioctl serve` to print a one-time launch token that my browser exchanges for an owner-ui cookie, so that only my own browser can perform owner acts.
20. As Jon, I want binding the control service to the tailnet to be opt-in and token-gated, so that another machine reaches my studio only when I decide.
21. As Jon, I want the RunPod API key, any Hugging Face token and the tailnet pairing secrets kept in the OS keychain, never sent to the web app and never returned by any API, so that no secret can leak through the UI.
22. As Jon, I want the product name to come from one constant, and every code identifier, CLI name, environment variable and volume name to be neutral, so that renaming AURA later changes one value and no path (O-10).
23. As Jon, I want the CLI named `studioctl` and never `studio`, so that it cannot collide with Android Studio's launcher on the machine where I also build JOVRA.
24. As the maintainer agent, I want an automation token that can do everything except owner acts, so that I can drive setup, generation and evaluation while Jon keeps the decisions that spend money, set lanes or judge quality.
25. As the maintainer agent, I want a 403 "owner act required" problem on every owner act I attempt, so that I cannot cross Jon's line even by mistake, and I know to hand the step to him.
26. As a future open-source user, I want setup to depend only on documented commands and configured roots, with no hidden state elsewhere on the machine, so that I can reproduce the studio on my own hardware.

### 2. Store and disk

_Scope: v1-core (stories 27–54). Covers [J4, J9]; ADR-0015, ADR-0028, ADR-0034; O-03; architecture §4.2, §8._

27. As Jon, I want AURA's store to live in an APFS sparse bundle on the Backup Plus drive, mounted as STUDIO, so that symlinks, POSIX permissions, hardlinks and clones work without reformatting a drive that also holds my other backups (O-03).
28. As Jon, I want setup to probe ownership, symlinks, chmod, hardlinks and `clonefile` on the new volume and record the outcome as an evidence record, so that a broken filesystem assumption fails at setup, not in the middle of a song.
29. As Jon, I want model weights, engine environments, every package and model cache, worktrees, scratch space and the project store on the studio volume, so that the nearly full internal disk holds only the OS, the browser, the docs checkout, a few kilobytes of config and keychain entries.
30. As Jon, I want one environment file, sourced by every `studioctl` command and every worker spawn, that routes every cache and temp variable to the studio volume, so that nothing silently writes gigabytes to the internal disk.
31. As Jon, I want anything that hardlinks or clones to live on the same volume as its counterpart (the uv cache and the environments, the pnpm store and `node_modules`, the content-addressed store and exports), so that nothing silently degrades into full copies.
32. As Jon, I want a disk preflight before every download, install, environment build, job and export, from an estimate declared per volume, so that no write starts that would fill a disk.
33. As Jon, I want a preflight refusal to name the volume, its free space, the amount needed and the margin, so that I know exactly what to free and how much.
34. As Jon, I want the studio volume's effective free space to be the smaller of the space free inside the bundle and the space free on the exFAT host, minus band overhead, checked against a 10 GiB margin I can configure, so that the sparse bundle's over-reported free space never fools the preflight.
35. As Jon, I want no planned writes on the internal disk, and heavy jobs blocked while it has under 2 GiB free, so that swap never runs out under an MLX load.
36. As Jon, I want a running job to fail honestly with `disk_low` if free space falls below half the margin, so that a full disk ends one job cleanly instead of damaging the store.
37. As Jon, I want downloads to be selective (only the files a profile needs) after a size dry run whose estimate lands within 10% of the actual size, so that preflight numbers can be trusted.
38. As Jon, I want every downloaded byte verified against the profile's weights manifest and every LFS sha256, so that a truncated or tampered weight file never loads.
39. As Jon, I want the bundle's logical size to default to 900g, to be mine to change, and to be raisable later, so that AURA leaves room on a shared backup drive (T-11).
40. As Jon, I want `studioctl store compact` to reclaim host space offline, and the preflight to report reclaimable bands separately, so that deleting inside the bundle eventually frees real space.
41. As Jon, I want setup to turn Spotlight indexing off on the volume (printing the `mdutil` command as an owner action in case macOS ignores the marker) and add a sticky Time Machine exclusion, so that indexing and Time Machine do not thrash a spinning disk.
42. As Jon, I want P0 to measure the volume's sequential throughput, random 4K IOPS and the 8 MiB versus 64 MiB band size on this HDD, recorded as MEASURED-LOCAL evidence, so that the band size is chosen from measurement rather than guessed.
43. As Jon, I want `doctor` to tell an HDD from an SSD by measured IOPS, because `diskutil` reports "Info not available", so that my load-time expectations match the disk I actually have.
44. As Jon, I want `studioctl store attach` and `detach`, with an optional login item to attach at login and with `detach` stopping the control service and workers first, so that ejecting the drive never cuts a write in half.
45. As Jon, I want an unclean detach to leave a marker that makes the next attach verify the volume before AURA opens the store, so that an accidental unplug is checked before more data lands on it.
46. As Jon, I want `serve` to refuse to start unless the store is mounted, its identity file matches and its single-writer lock is free, so that I can never run two studios against one store, or a studio against the wrong drive.
47. As Jon, I want every artifact and record to carry a retention class (irreplaceable, derived or reproducible), and `doctor` to report the space used per class, so that I know what is precious and what can simply be downloaded or recomputed.
48. As Jon, I want `studioctl store backup <destination>` to copy the irreplaceable closure, in the same content-addressed layout, to a second device and re-hash every file there, adding derived data only when I ask, so that a single spinning HDD is never the only copy of my melodies, verdicts and keepers.
49. As Jon, I want `restore` to rebuild a fresh store from a backup and `fsck` to re-hash it, so that recovery is a drill I have run, not a hope.
50. As Jon, I want the store and environment roots to be configurable, with the environments and the uv cache always moving together, so that when I free internal space or buy an SSD I can move the hot parts without breaking the one-volume rule.
51. As Jon, I want `doctor` to check for a mount-point collision on STUDIO, so that another volume with the same name is never mistaken for my store.
52. As the maintainer agent, I want git worktrees for tickets, with their `node_modules` and virtual environments, on the studio volume, so that parallel ticket work never fills the internal disk.
53. As a future open-source user, I want a documented store layout (identity file, content-addressed blobs, provenance sidecars, canonical records and the database) that I can read without AURA's code, so that my songs outlive the software.
54. As a future open-source user on Windows or Linux, I want the store to be a plain directory with the same layout, short lowercase-hex paths and no symlinks or extended attributes, so that it works on any filesystem with atomic rename and fsync.

### 3. Melody capture: hum and MIDI

_Scope: v1-core (stories 55–72). Covers [A1, A2, A3]; ADR-0004; O-04; architecture §3.1 (browser), TB1c, TB4._

55. As Jon, I want to record a hum or a sung line, with or without words, on the Capture screen with a live level meter, so that the melody in my head gets in the moment I have it [A1].
56. As Jon, I want AURA to capture raw float32 PCM at the device's own rate through an AudioWorklet, with echo cancellation, noise suppression and auto gain turned off and the browser's settings checked, so that the browser never "improves" my voice in ways that bend its pitch.
57. As Jon, I want the Capture screen to tell me if the browser would not turn echo cancellation, noise suppression or auto gain off, and to label any capture made that way, so that a processed capture is never mistaken for a clean one.
58. As Jon, I want to choose the input device and see its sample rate before I record, so that I know which microphone AURA is listening to.
59. As Jon, I want to listen back and re-record before a capture is kept, so that a false start never becomes an irreplaceable artifact.
60. As Jon, I want the browser to hash each capture and the control service to verify that hash on ingest, refusing a mismatch, so that what I recorded is exactly what is stored.
61. As Jon, I want every capture kept exactly as received and never edited, as an irreplaceable human recording, so that everything AURA derives can be traced back to my own performance.
62. As Jon, I want a project to hold several captures, each named and timestamped, and to choose which one to transcribe, so that I can hum a verse and a chorus separately or try the tune again.
63. As Jon, I want an optional count-in and metronome at a tempo I set, heard only in my headphones and never mixed into the capture, whose tempo seeds the MelodySpec's tempo map, so that I can hum in time when I want to and freely when I do not.
64. As Jon, I want to drop a Standard MIDI File into a project and get a MelodySpec directly, with no transcription step, so that a melody I already played arrives losslessly [A3].
65. As Jon, I want to choose which track or channel of a multi-track MIDI file holds the melody, so that an arrangement file still gives me just the tune.
66. As Jon, I want to play the melody live on a Web MIDI keyboard and have it become a MelodySpec, so that I can play it instead of humming it (O-04).
67. As Jon, I want imported MIDI files and live MIDI event lists kept as irreplaceable captures exactly as received, so that a played melody is as protected as a hummed one.
68. As Jon, I want to import an existing recording of my hum as WAV, and to be told plainly that compressed phone memos (m4a/AAC) wait on the decoder license check, so that a voice memo has a path in today and none is silently mangled [A2].
69. As Jon, I want microphone permission requested only when I open Capture, with a short reason first and a clear way back if I denied it, so that a permission problem never dead-ends the screen.
70. As Jon, I want microphone capture treated as a capability with its own evidence on each operating system, so that "capture works" is only claimed where it was checked.
71. As Jon, I want ingesting a hum to start its transcription job automatically, with honest steps in the jobs drawer, so that the piano roll is ready as soon as it can be.
72. As the maintainer agent, I want Playwright to feed a NeutralVoice hum into Chromium as a fake microphone, so that the capture path is tested end to end with a melody whose true notes are known.

### 4. Transcription and piano-roll correction

_Scope: v1-core (stories 73–94). Covers [A4, A5]; ADR-0004, ADR-0032, ADR-0033; GAP-01; architecture §4.6, §4.9, TB1d, TB6._

73. As Jon, I want a transcription job to turn my hum into the first MelodySpec revision, with every note carrying a confidence, so that I start correcting from a guess instead of a blank page [A4].
74. As Jon, I want the default transcriber (pYIN with AURA's own HMM note segmentation, no weights, clean in every lane) labelled "unverified on real hums" until the hum benchmark says otherwise, so that I never over-trust the first guess.
75. As Jon, I want low-confidence notes marked by outline or pattern as well as colour, so that I go straight to the notes most likely to be wrong.
76. As Jon, I want the capture's pitch curve drawn behind the piano roll, so that I can see where the transcription departs from what I actually sang.
77. As Jon, I want to hear the MelodySpec through a simple oscillator, alone or against the capture, and to hear it sung by the NeutralVoice guide, so that I correct by ear as well as by eye.
78. As Jon, I want to move, resize, transpose, split, merge, add and delete notes in a piano roll, so that the melody becomes exactly what I meant [A5].
79. As Jon, I want a dragged note to respond immediately in the browser, using the same time model as the server, so that editing feels instant and the server never disagrees about where the note landed.
80. As Jon, I want to set the tempo map, meter and key, including tempo and meter changes, so that the melody sits on the right grid.
81. As Jon, I want quantize to be a reversible layer over my played timing, so that I can snap notes to the grid without losing the feel of the original.
82. As Jon, I want to mark phrases in the MelodySpec, so that the SongForm can place, repeat or leave them out.
83. As Jon, I want every set of corrections to make a new immutable revision on a named base, so that no earlier state of my melody is ever overwritten.
84. As Jon, I want a correction made against an out-of-date revision refused with a clear explanation, so that two browser tabs or an agent never silently overwrite each other's work.
85. As Jon, I want to step back to any earlier revision and continue from it, so that undoing a run of corrections is safe and nothing is lost.
86. As Jon, I want every correction logged with its time, so that AURA can measure how much correcting each transcriber really costs me.
87. As Jon, I want to start a MelodySpec from scratch and enter the notes by hand, so that I can skip transcription entirely when that is faster.
88. As Jon, I want every note to record its origin (transcribed, corrected, midi_file, midi_live, manual or assembled, as `melody-spec/1` names them) and every transcribed revision its transcription method and its transcriber's lanes, so that I can see how much of the melody the machine guessed.
89. As Jon, I want to re-transcribe a capture with another enabled transcriber as a new revision chain beside my corrected one, so that trying a better transcriber never discards my corrections.
90. As Jon, I want to get any MelodySpec revision as MIDI, as YuE2's ABC or as a NeutralVoice guide, so that the melody leaves AURA in whatever form I need.
91. As Jon, I want to record a set of hums together with the same melodies played on MIDI as ground truth, and run a preregistered hum benchmark that scores Basic Pitch, SwiftF0's note segmentation and pYIN with HMM on COn, COnP and COnPOff plus blind correction effort, so that the default transcriber is chosen on my own voice (TB6).
92. As Jon, I want the hum benchmark allowed to conclude that manual entry wins, so that AURA never forces a transcriber that costs me more time than it saves.
93. As the maintainer agent, I want the transcriber kept disabled until it meets its preregistered COnP F1 floor on NeutralVoice hums with drift, onset jitter, vibrato, breath noise and rubato, recorded as synthetic evidence that satisfies only its smoke gate, so that a broken transcriber never reaches Jon.
94. As a future open-source user, I want the MelodySpec to use 960 PPQ, integer microseconds per quarter note and one half-up rounding function shared by Python and TypeScript, so that MIDI round trips are exact and the two runtimes never drift apart.

### 5. SongSpec and lyrics

_Scope: v1-core (stories 95–113, 115); v1-studio (story 114). Covers [B1, B3, B4, B5, B7, B8, G2]; ADR-0004, ADR-0007, ADR-0018, ADR-0032; architecture §4.6 (validate, assemble)._

95. As Jon, I want lyrics and style in separate editors, so that lyric words never leak into the style and style words never get sung [B4].
96. As Jon, I want to declare the lyrics' language, English by default, so that any route that accepts only some languages can tell me before I submit (Q6 default).
97. As Jon, I want my approved lyrics stored apart from any transcript or alignment of a rendered vocal, and never overwritten by speech recognition, so that the words I wrote stay the words of record [B7].
98. As Jon, I want section tags in the lyrics to bind lines to SongForm sections, so that each verse and chorus gets the words meant for it.
99. As Jon, I want a SongForm editor that builds an ordered list of sections (intro, verse, chorus, bridge, instrumental, outro) from marked phrases with bars and repeats, so that a short hummed idea becomes a full-length song plan.
100. As Jon, I want both vocal and instrumental sections in the SongForm, so that the song can breathe with an intro, a solo or an outro.
101. As Jon, I want to hear the assembled melody sung by NeutralVoice along the whole SongForm before anything is generated, so that I catch a wrong repeat or a missing bar for free.
102. As Jon, I want section names to survive every step, from the SongSpec to the timeline to the markers in exported MIDI, so that "chorus 2" means the same thing everywhere.
103. As Jon, I want to describe the style and list exclusions, so that I can steer the sound without writing a prompt essay.
104. As Jon, I want to choose a vocal mode, sung or instrumental, and to see any other vocal control only where the chosen profile implements it, so that I never set a control that does nothing [B3].
105. As Jon, I want to set a target duration and see the candidate count, two by default, as part of the SongSpec, so that what I asked for is on record.
106. As Jon, I want each SongSpec field to record what I requested, what each engine profile supports and what was observed in the result, so that I can tell exactly what each engine consumed [B8].
107. As Jon, I want conflicts flagged inline before I submit, such as an instrumental vocal mode alongside style words that name a voice, so that a song never comes back singing when I asked for none [B5].
108. As Jon, I want the fields a selected profile does not support listed beside the form, so that I know which of my choices will be ignored and by which profile.
109. As Jon, I want the Song screen to show early when route R1 is ineligible for this SongSpec (lyrics in a language other than English or Chinese, a song longer than about six minutes, or a melody the YuE2 dialect cannot represent), with the reason, so that I am not surprised at submit time.
110. As Jon, I want to attach references to a song, each with a permission record that says how it may be used, so that a listening-only reference is never fed to an engine.
111. As Jon, I want every SongSpec edit to make a new immutable revision, refused against a stale base, so that a generation request always points at exactly the spec it was made from.
112. As Jon, I want a simple "describe the song" path with no melody seed, so that I can still sketch an idea from words alone when I do not have a tune yet [B1].
113. As Jon, I want R1's lyric syllable plan kept beside the ABC it was made for, and viewable, so that I can see which syllable lands on which note before I pay for a burst.
114. As Jon, I want a reference clip offered to ACE only as a "global timbre/style reference", labelled that way, so that nobody, me included, mistakes it for voice cloning [G2] (ADR-0007).
115. As the maintainer agent, I want SongSpec validation exposed through the Studio API, so that the UI, the CLI and the eval harness flag exactly the same conflicts.

### 6. Routes, generation requests and engines

_Scope: v1-core (stories 116–139, 143); v1-studio (stories 140–142). Covers [A6, A8, A9, B1, C3, C4, C5, C6, C7, C11]; ADR-0001, ADR-0002, ADR-0004, ADR-0016, ADR-0018, ADR-0032; architecture §4.6 (plan, to_abc), §4.10, TB1a, TB3, TB7._

116. As Jon, I want to submit a generation request in auto mode and get a plan that names its routes, engine profiles and seeds, each with a reason, so that I see why AURA chose what it chose.
117. As Jon, I want auto mode to pick, by default, one candidate from each of the first two eligible routes in this project's lane, in a default order fixed in the plan rules (R1 only where it runs without a burst or when I opt in for that request, then R2-synth, R2-raw, text) and adjusted only by concluded preregistered results, so that an individual-lane pair can be mixed-engine without a paid quote on every request and no route is called best before a record says so [C7].
118. As Jon, I want both candidates to come from one route with different seeds when only that route is eligible, so that I still get a real choice.
119. As Jon, I want an explicit mode in which I choose the routes and engine profiles myself, so that I can test a hunch without an auto-router overruling me [C4].
120. As Jon, I want every route the plan declined listed with its reason, so that "why didn't it use YuE2?" always has an answer.
121. As Jon, I want the plan labelled "unbenchmarked routes" until a benchmark record exists for its routes, so that I never read the default as proven.
122. As Jon, I want route R2-synth to cover the NeutralVoice guide of the assembled melody with ACE, sweeping cover strength from 0.8 to 1.0 and the cover noise strength, so that ACE hears a clean, in-tune version of my melody.
123. As Jon, I want route R2-raw to cover my own hum with ACE, with the hum's slices laid out along the SongForm, so that the character of my actual performance can carry into the song.
124. As Jon, I want route R1 to send YuE2 a two-voice ABC made from the assembled melody (fixed header, one integer tempo, full bars, pickups padded with rests, tuplets re-quantized) with the lyrics bound by section tags, so that the one engine with a documented score input is conditioned on exactly the notes I wrote (whether it sings them is measured by adherence, never assumed) (GAP-02).
125. As Jon, I want anything R1 cannot represent returned as a typed "ineligible" with reasons and never silently altered, so that the score YuE2 receives is never something I did not write.
126. As Jon, I want to view the exact ABC and syllable plan R1 will send before I approve its burst, so that I know what leaves my machine and what the engine will be conditioned on [A9].
127. As Jon, I want a text route that makes a song from the SongSpec alone, so that lyrics-only and style-only ideas have a path [B1].
128. As Jon, I want the ACE turbo profile for quick iterations and the ACE SFT profile for full-quality candidates, each chosen explicitly, so that I can sketch fast and commit carefully [C3].
129. As Jon, I want ACE XL to appear only after its own smoke run, preflight and loader check, so that a checkpoint known to have produced garbled output on Apple Silicon before a fix never reaches me unproven (C3).
130. As Jon, I want controls to appear only where the selected profile implements them (turbo hides guidance, for example), so that no control ever silently does nothing [C5].
131. As Jon, I want every candidate to record the intent I set and the actual parameters the engine received, so that I can compare candidates by intent and reproduce one from what it actually got.
132. As Jon, I want every candidate's seed recorded, and to reproduce a candidate from its seed and actual parameters on the same profile revision, so that a good result is never a one-off accident.
133. As Jon, I want a request that names a profile below smoke-passed refused with `profile_not_promoted` before anything loads, so that I never wait for, or pay for, an unproven engine.
134. As Jon, I want guides and assembled hum slices stored as content-addressed artifacts and reused across requests, so that AURA never renders again what it already has.
135. As Jon, I want to cancel any job and have it stop within five seconds with no partial output, so that a wrong request costs me seconds, not minutes.
136. As Jon, I want the plan labelled "ACE-only: burst declined" when I decline a burst, and the request to continue with what runs locally, so that saying no is always allowed and always visible.
137. As Jon, I want YuE2 refused for an LLC project at submit and again by its worker before it loads anything, so that a non-commercial engine cannot touch LLC work even through a bug in one layer.
138. As Jon, I want each lane's default candidate pair treated as provisional, so that the smoke set, hum fixtures included, can demote any engine, YuE2 included.
139. As Jon, in LLC projects, I want HeartMuLa and MiniMax to compete for the second slot by smoke once a CUDA host or an approved burst can run them, with MiniMax's disclosure obligation carried into every manifest that contains its output, so that LLC songs are not ACE-only forever (P6).
140. As Jon, I want an optional instrumental profile (Stable Audio 3 Medium on the Mac) available only after its gated download, my license registration and its smoke gate, with its attribution and no-training obligations recorded on every artifact it makes, so that I can make intros and beds without breaking its terms [C11].
141. As Jon, I want to ask for more than two candidates only as an explicit, priced choice with its budget logged, promoted to a default only if my blind auditions show a gain, so that best-of-n stays my choice rather than a hidden cost [C6].
142. As Jon, I want to hear a hum or a MIDI clip as a chosen instrument once a MIDI synth and soundfont have passed their license check, so that I can sketch an arrangement from the same melody [A8].
143. As the maintainer agent, I want every product feature to be a job spec submitted through the Conductor (transcribe, guide, assemble-audio, generate, measure, adherence, separate, export), so that every one of them shares one lifecycle, one admission check and one event stream.

### 7. Candidates and blind audition

_Scope: v1-core (stories 144–166, 168); v1-studio (story 167). Covers [A7, A11, C1, C2, C8, J10]; ADR-0005, ADR-0010; architecture §4.7, §4.9 (measure, adherence), TB1b, TB5._

144. As Jon, I want each generation request to yield two candidates, so that I always have a real choice and no hidden batch behind it [C1].
145. As Jon, I want every candidate checked against the hard constraints (it decodes, is not silent, fits its duration, has no clipping or true-peak overs, keeps an acceptable lyric error rate, and keeps the melody when it was seeded), computed before the audition and shown after the reveal, with only "unplayable" visible before it, so that objective failures are on record without biasing my blind listening.
146. As Jon, I want a candidate that fails a hard constraint badged, never hidden or deleted, so that I can still hear it and decide for myself.
147. As Jon, I want every seeded candidate measured for melody adherence (median cents error, octave-error rate, onset F1 and contour correlation), so that "it sounds great but lost my tune" is caught by a number [A7].
148. As Jon, I want a candidate that loses my melody to carry the badge "melody not kept", so that a beautiful wrong song is never mistaken for my song.
149. As Jon, in an LLC project, I want adherence to read "adherence unmeasured (no LLC separator yet)" rather than be skipped silently, so that a missing measurement is never read as a pass [A11].
150. As Jon, I want adherence and lyric error rate shown on real candidates only after each has been validated within thresholds fixed in advance: adherence on NeutralVoice ground truth and then through the real separator under a NeutralVoice bed and an ACE bed (the `adherence.real-separator` capability), and lyric error rate on sung vocals whose words I verified, so that a broken metric never misleads me.
151. As Jon the listener, I want an audition to open only when every candidate in it is ready, so that arrival order cannot tell me which is which.
152. As Jon the listener, I want blind labels drawn at random when the audition opens, with only a sealed commitment to them shown, so that neither I nor the software can bias the mapping.
153. As Jon the listener, I want every arm played from a 48 kHz, 24-bit preview while each candidate keeps its native rate, so that sample rate cannot give a candidate away.
154. As Jon the listener, I want louder arms lowered to the quietest arm's integrated loudness and never raised, with the remaining mismatch at most 0.1 LU and true-peak headroom checked by AURA's own meter, so that loudness cannot decide my verdict and nothing clips.
155. As Jon the listener, I want to switch instantly between arms at the same position with a short crossfade, loop a span, and control everything from the keyboard, so that I compare the same musical moment.
156. As Jon the listener, I want no route, profile, seed or file name in the page, in its accessible names or in any network response before my verdict, with audio served by label under identical headers, so that the audition is blind in fact and not just in layout.
157. As Jon the listener, I want the jobs drawer to show candidates only by ordinal while an audition is open, and only the "unplayable" badge before the reveal, so that progress and badges cannot unblind me.
158. As Jon the listener, I want a candidate that cannot be played to show "unplayable" even during a blind audition, so that I am never left listening to silence wondering why.
159. As Jon the listener, I want to give a verdict of A, B, tie or neither, with optional axes and marked problem intervals, and with the seconds I listened to each label recorded automatically, so that my judgment is captured with its context.
160. As Jon the listener, I want my verdict to be an immutable owner act that only my own browser can submit, so that no script or agent can vote for me.
161. As Jon the listener, I want the reveal checked against the commitment made when the audition opened, and a mismatch reported loudly, so that I can trust the reveal.
162. As Jon, after the reveal, I want to see each candidate's route, profile revision, seed, badges, adherence numbers and any diagnostic scores, so that I learn what produced the candidate I preferred.
163. As Jon, I want "neither" to re-roll new candidates with new seeds and count toward the keeper's cost, so that rejecting both is cheap to do and honest to account for.
164. As Jon, I want everyday verdicts shown per route as "kept n of m" and never used to change a profile's status, so that casual listening informs me without quietly promoting an engine.
165. As Jon, I want to open an audition over any two or more ready candidates in a project, including earlier candidates against new ones, so that a re-roll can be compared with what I already had.
166. As Jon the listener, I want the audition screen to state plainly that duration and sonic character cannot be hidden, so that I know the one leak that remains.
167. As Jon, after the reveal, I want diagnostic scores (audiobox-aesthetics, LAION-CLAP) shown for information only and never used to select, rank or filter, so that a scorer that cannot hear above 8–12 kHz never chooses for me [C8] (C14).
168. As the maintainer agent, I want audition gains computed by the control service and applied by the browser only as attenuation, so that the level-matching rule is enforced in one place and can be tested.

### 8. Keepers and projects

_Scope: v1-core (stories 169–181, 183); v1-studio (story 182). Covers [C9, D8, F14, J1, J2, J3]; ADR-0009, ADR-0023; O-06; architecture §4.2, §4.7 (keep)._

169. As Jon, I want to create a project with a name and an operator lane, `individual` by default, so that every song starts with clear ownership (O-06).
170. As Jon, I want to keep the candidate I preferred, making it the song's keeper, so that the project has one version of record that I can edit, finish and export.
171. As Jon, I want later keepers, from re-rolls or accepted edit operations, to become new keeper revisions while the earlier ones remain, so that I can always go back to the keeper I loved yesterday.
172. As Jon, I want a projects list with search, filters (operator lane, feel, has a keeper, awaiting approval) and newest first, so that I find a song quickly [J1].
173. As Jon, I want a project page with the title, approved lyrics, SongForm, melody revisions, generation requests, candidates, keepers and export bundles, so that the whole song is in one place [J2].
174. As Jon, I want a persistent player bar that keeps playing a keeper or a capture while I move between screens, so that I can listen while I work [J3].
175. As Jon, I want the projects list and each project page to surface the next useful action (correct a new transcription, approve a waiting quote, audition ready candidates, export a new keeper), so that nothing is forgotten mid-song.
176. As Jon, I want every change committed as it happens, with no "save" button and nothing lost if the browser closes, so that I never lose work to a crash [F14].
177. As Jon, I want every candidate kept, rejected ones included, so that I can return to an idea I passed over and so that keeper cost stays honest [C9].
178. As Jon, I want each keeper to show its keeper cost (candidates rendered including re-rolls, compute cost, cold and warm time, and listening time), so that I see what the song really took (ADR-0023).
179. As Jon, I want to rename a project or a keeper's title without changing any identifier or hash, so that names can evolve without breaking provenance.
180. As Jon, I want to follow a keeper back through its candidate, generation request and SongSpec and MelodySpec revisions to my original capture, so that I can see how the song grew from my melody.
181. As Jon, I want projects to be songs, with narration reserved as a future project kind, so that the narration service can later share the same store without a migration.
182. As Jon, I want to start a new project from a keeper revision, carrying its closure and checked against the new project's lane, so that I can branch a song without disturbing the original [D8].
183. As the maintainer agent, I want project state observable only through the Studio API and its event stream, so that the UI, the CLI and my tools all see the same truth.

### 9. Provenance and export

_Scope: v1-core (stories 184–199, 202–203); v1-studio (stories 200–201). Covers [I1, I2, I4, I5, J5, L4, L9]; ADR-0009, ADR-0019, ADR-0028, ADR-0029; architecture §4.6 (manifest), §4.9 (export), §5, TB1b, TB4._

184. As Jon, I want to export a keeper as an export bundle holding the mix at its native rate (bit-exact), a 48 kHz, 24-bit deliverable only when the native rate differs, MIDI with its tempo map and section markers, the MelodySpec and SongSpec records, and an ExportManifest, so that I can take the whole song anywhere [I1, I5].
185. As Jon, I want every file in an export bundle decoded and hashed again before the bundle is offered, so that what I download is exactly what the manifest describes.
186. As Jon, I want exports to be deterministic, with the 48 kHz deliverable dithered by TPDF seeded from the export id, so that exporting the same keeper twice gives the same bytes.
187. As Jon, I want to download the bundle as a zip and see each file's role, rate, frame count and hash first, so that I know exactly what I am getting.
188. As Jon, I want no caps on exports, no credits, no forced watermark and no account, so that I own the output outright (A29) [J15, J16].
189. As Jon, I want the ExportManifest to list the files with hashes, roles, rates and frames; my human contributions; the model and license chain; the operator lane and eligible lanes; the AI-disclosure flag with its reasons; `converted_vocal: false`; any imported-source terms; a loudness report naming its standard and meter version; the closure hash; the synthetic flag; and the verification time, so that rights and disclosure questions can be answered from the bundle alone [I2].
190. As Jon, I want my human contributions recorded (the melody I captured, the lyrics I wrote, my corrections, my verdicts and choices, and my edits), so that authorship and disclosure questions have evidence behind them (X-44).
191. As Jon, I want every export to carry an AI-disclosure-ready manifest even though my default release plan is personal, so that I can release later without reconstructing anything (Q4 default).
192. As Jon, I want an export refused when the project's lane is not among the closure's eligible lanes, with the reason naming the responsible component, so that I never release something my lane does not allow.
193. As Jon, I want a provenance panel on any artifact showing the producing job, profile revision, weights, code commit, environment lock or image digest, intent and actual parameters, seed, host and host class, compute profile, timings, operator lane, eligible lanes, license chain and typed parents, so that I can answer "how did this come to exist?" for any sound in AURA [J5].
194. As Jon, I want to see a keeper's closure (every ancestor reachable through derived-from and converted-from edges), with analysis edges shown apart, so that I understand which components a song really contains.
195. As Jon, I want any artifact without complete provenance refused at the store's write path, so that no sound can exist in AURA without being accounted for.
196. As Jon, I want exported MIDI to open in a DAW with the same notes and ticks as the MelodySpec, so that the melody I corrected arrives intact.
197. As Jon, I want exported files to be zero-copy clones of the stored blobs where the filesystem allows, so that exporting a long song does not double its disk use.
198. As Jon, I want any export made from fake-engine output marked "Synthetic test output" in its manifest and on screen, so that a test export can never be mistaken for a song.
199. As Jon, I want export renders treated as reproducible and manifests as irreplaceable, so that backups hold what matters and any export can be rebuilt from its closure.
200. As Jon, I want to export aligned stems and tracks at a common rate, all starting at zero with equal frame counts, so that a DAW can take the song over cleanly [I4].
201. As Jon, I want a DAW import of the aligned stems checked (zero start, equal frame counts) with screenshots kept as evidence, so that "DAW-ready" is a checked claim and not a hope.
202. As a future open-source user, I want the ExportManifest to be self-describing JSON with a published schema, so that I can read an AURA export without AURA [L9].
203. As the maintainer agent, I want the ExportManifest assembled by a pure function from the closure, the license chain and the file list, never by hand, so that every manifest is computed the same way and can be golden-tested.

### 10. Studio timeline and transport

_Scope: v1-studio (stories 204–219). Covers [D1, E2, F1, F2, F3, F5, F6, J20]: sections come from the SongForm (no automatic sectionizer in v1), each section name keeps one colour, always beside its name as text, across the Editor, the Studio and exported MIDI markers, and a text-route keeper takes its sections from its SongSpec's SongForm; ADR-0013, ADR-0024, ADR-0033; architecture §4.11 (StudioEngine), TB9, P5._

204. As Jon, I want to open a keeper in the Studio as a timeline of tracks and clips, so that I can arrange and finish the song [F1].
205. As Jon, I want clips to refer to artifacts at their native rate, MIDI clips to sit in musical time, the tempo map to be shared with the MelodySpec, and SongForm sections to appear as markers, so that the timeline and the melody never disagree [F5].
206. As Jon, I want transport controls (play, pause, stop, return to start, loop a span) with keyboard shortcuts, so that moving around the song is fast.
207. As Jon, I want solo, mute, a fader, pan and a level meter on every track, so that I can balance the song.
208. As Jon, I want per-clip gain and fades, so that I can smooth an entrance or an exit without a generative edit operation [F3].
209. As Jon, I want each clip's waveform drawn and the timeline zoomable in bars and beats or in time, so that I can place an edit precisely.
210. As Jon, I want Studio playback to run on an AudioWorklet engine with a ring buffer per track, fed by a separate decoding worker, so that generation, disk or network work never causes a dropout.
211. As Jon, I want every export to use a separate, deterministic offline render and never what the browser played, so that a playback glitch can never end up in an export bundle.
212. As Jon, I want the Studio marked ready on an operating system only after 8 tracks have played for 30 minutes with no underruns and the UI stayed under 100 ms at the 95th percentile while a generation ran, so that "the Studio works here" is a measured claim [J20].
213. As Jon, I want the Studio to show the output latency the browser reports, so that I know how far the sound trails the playhead on this machine.
214. As Jon, I want the Studio to require a Chromium-based browser and say so plainly in any other browser, so that I never debug Safari's audio stack by accident (Q10 default).
215. As Jon, I want timeline changes saved as immutable revisions as I make them, so that every arrangement step can be undone.
216. As Jon, I want to edit MIDI clips in the same piano roll I use for the melody, so that I learn one editor [F6].
217. As Jon, I want a replacement part to arrive on its own track and the mix to be rebuilt when I copy it to the main track, never layered over a mix that still holds the old part, so that I never hear a part twice [E2, F2].
218. As Jon, I want a 16-track stretch gate measured and reported beside the 8-track gate, so that I know how far the Studio can go on this Mac before I rely on it.
219. As the maintainer agent, I want the StudioEngine to be the only module replaced if a playback gate fails (by a native CPAL engine behind the same timeline contract), so that a browser audio problem never forces a rewrite of the timeline.

### 11. Edit operations and replacement tracks

_Scope: v1-studio (stories 220–237). Covers [C10, D2, D3, D4, D5, D6, D7, D8, D9, F2, L1]; ADR-0006 (rebuild), ADR-0017, ADR-0021; architecture §5 (`edit-operation/1`), TB9, P5._

220. As Jon, I want to select a section of a keeper and replace it, with the mask set from the section markers and adjustable by hand along with its crossfades, so that I can change one part without touching the rest [D2].
221. As Jon, I want a section replacement to run ACE repaint with the chunk mask and return two candidates for a blind audition, so that an edit operation is judged the same way as a song.
222. As Jon, I want an edit operation to stay a proposal until I accept one of its candidates, so that trying an edit never changes my keeper [D4].
223. As Jon, I want every accepted edit operation to pass a preservation check (the working audio outside the mask and crossfades is identical, sample for sample, in a declared rate, channel and sample-type domain), so that "local edit" is a check that can fail, not a promise [D5].
224. As Jon, I want an edit operation that fails the preservation check refused, with the first differing sample position reported, so that a destructive edit never reaches my keeper.
225. As Jon, I want an accepted edit operation to make a new keeper revision, so that every edit is a step I can see and reverse.
226. As Jon, I want undo to restore the previous keeper revision by hash, with no generation job run, so that undo is instant and exact.
227. As Jon, I want a whole-song re-render never labelled a local edit, so that "edit" always means the rest of the song is untouched.
228. As Jon, I want to extend the song at its start or end with repaint, one pass at a time, so that I can add an intro or an outro [C10].
229. As Jon, I want to replace a single line or word, scoped by aligned lyrics, offered only once the alignment and the scoped repaint have passed their checks, so that a one-word change does not re-sing the verse [D3].
230. As Jon, I want lyric alignment shown with a way to correct word timings by hand, kept as its own asset apart from my approved lyrics, so that word edits hit the right syllables and my words are never rewritten [D9].
231. As Jon, I want deterministic DSP edits (crop, remove a section, reverse, fade in and out) that need no model, so that simple changes are instant and exact [D6].
232. As Jon, I want speed changes offered only after the time-stretch library passes its quality evaluation, so that a stretching artefact never ships as a feature.
233. As Jon, I want an edit history for each keeper that lists every edit operation, its candidates and which one I accepted, so that I can see how the song got here [D8].
234. As Jon, I want a restyle (cover) of a keeper labelled a new performance, with its melody adherence measured, so that a restyle never pretends to be the same performance [D7].
235. As Jon, I want edit candidates placed on their own tracks so I can compare them in context, with "copy to main track" rebuilding the mix, so that alternatives never overwrite the original until I choose one [F2].
236. As Jon, I want any edit operation on an imported Suno mix refused, so that a Suno download is never the source of a generative edit (ADR-0021).
237. As the maintainer agent, I want a planted one-sample change outside the mask to fail the preservation check in CI, so that the check is proven not to be vacuous.

### 12. Stems: isolate original, re-perform, create a new part

_Scope: v1-core (stories 248, 252); v1-studio (stories 238–247, 249–251). Covers [E1, E2, E3, E4, E5, E6, A11]; ADR-0006, ADR-0029; GAP-06; architecture §3.1 (separator worker), §10, P5._

238. As Jon, I want to isolate original stems from a keeper with a separator that keeps the residual, so that the stems plus the residual always rebuild the mix [E1].
239. As Jon, I want to listen to each stem, to the residual and to the rebuilt mix, so that I can judge a separation by ear.
240. As Jon, I want each separation checked by its sum-to-mixture residual and measured for bleed, so that separation quality is a number as well as an impression.
241. As Jon, I want the residual always kept and always audible, so that nothing a separator dropped disappears silently.
242. As Jon, I want stems labelled isolated only when a separator produced them, and any regenerated part labelled a new performance, so that AURA never calls a regenerated part the original (C22).
243. As Jon, I want ACE's "extract" task treated as a re-perform and never as isolation, so that a generative output never passes as a separated original [E5].
244. As Jon, in LLC projects, I want isolation refused until a separator whose weights and training data have passed review is allow-listed, with the reason shown, so that Demucs's personal-use weights never touch LLC work (GAP-06).
245. As Jon, I want to insert one stem onto a track, insert all stems at once, or download a stem, so that stems are useful immediately [E3].
246. As Jon, I want stem-to-MIDI transcription, with per-note confidence, offered on any stem, so that I can recover a bass line or a riff as notes [E4].
247. As Jon, I want replacing a part always to rebuild the mix from retained sources and never to lay a new part over a mix that still holds the old one, so that the old part never ghosts underneath [E2].
248. As Jon, I want the internal separation AURA runs for adherence and lyric checks never offered or exported as a stem, so that an analysis by-product never becomes part of a song [A11].
249. As Jon, I want a Suno import never separated by a machine-learning model, with a pointer to Suno's own stems instead, so that the Suno boundary holds.
250. As Jon, I want separation output budgeted in the disk preflight at its real size (about 87.9 MiB per four-minute stereo float32 stem), so that a separation never fills the disk halfway through.
251. As the maintainer agent, I want RoFormer checkpoints loaded only from an allow-list keyed on verified licenses, so that an unlicensed community checkpoint can never slip in (C23).
252. As a future open-source user, I want "regenerated part" and "new part" already among the artifact origins, so that Re-perform and Create a new part can arrive in v2 without a schema change [E5, E6].

### 13. DSP finishing and loudness

_Scope: v1-core (stories 253–259, 268); v1-studio (stories 260–267). Covers [A12, D6, F9 (gain and EQ only), I3]; ADR-0019, ADR-0021, ADR-0036; X-47; architecture §4.9 (measure, export), §10 (use policy), P5-6._

253. As Jon, I want every candidate and keeper measured for integrated loudness, labelled "BS.1770-4 (pyloudnorm)" until the BS.1770-4 versus -5 comparison closes, so that every loudness figure says which standard produced it [I3] (X-47).
254. As Jon, I want true peak measured by AURA's own meter oversampling at least four times, so that inter-sample overs are caught even though pyloudnorm has no true-peak meter.
255. As Jon, I want clipping and true-peak overs treated as hard constraints with badges, so that a clipped candidate is known before I listen.
256. As Jon, I want every loudness report in a manifest to name its standard and its meter version, so that a figure is only ever compared with figures made the same way.
257. As Jon, I want a dry export always kept beside any loudness-processed one, and no loudness target ever applied silently, so that processing is always my choice and always reversible.
258. As Jon, I want audition previews and loudness reports to come from the same measurement job, so that level matching and the loudness I am shown never disagree.
259. As Jon, I want no generative enhancement or super-resolution applied to my audio by default, so that nothing invents detail my song never had (ADR-0019).
260. As Jon, I want to choose a loudness target for a destination explicitly at export time, with the dry export still included, so that I can deliver at -14 LUFS, or anything else, without losing the original.
261. As Jon, I want gain, fades, EQ, trimming, and format or rate conversion as deterministic DSP finishing, so that finishing never changes what was performed.
262. As Jon, I want a loudness and true-peak meter in the Studio with numeric readouts, so that I finish by measurement rather than by guess.
263. As Jon, I want to import my own permitted Suno download as an imported mix that records Suno as its source service together with its terms, so that I can finish my first version of the song in AURA [A12] (O-08).
264. As Jon, I want a Suno import's allowed uses fixed at listening, loudness measurement and DSP finishing, unless I sign a risk acceptance naming a further use, so that Suno's terms are enforced by data and not by memory.
265. As Jon, I want a DSP-finished Suno import exported with its embedded provenance marks preserved and its imported terms in the manifest, so that the finished file stays honest about where it came from.
266. As Jon, I want a Suno import refused as cover, repaint, extend, conversion or separation input, as an audition arm and as an evaluation reference, with the reason shown, so that I cannot cross the Suno boundary by accident.
267. As Jon, I want to import a mix of my own work exported from a DAW as an imported mix whose source is my own, without the Suno limits but inheriting the lanes and license chains of any studio exports it contains (and refused as my own if it contains Suno or third-party audio), so that material I made elsewhere can be finished in AURA too without laundering a lane.
268. As the maintainer agent, I want a ticket that compares BS.1770-4 with BS.1770-5 integrated loudness on stereo programme and records the result as evidence, so that the "-4" label is kept or dropped on evidence (X-47).

### 14. Evaluation harness, reference standards and smoke set

_Scope: v1-core (stories 269–292). Covers [C2, J10, J11]; ADR-0005, ADR-0010, ADR-0027; O-05, O-08; architecture §4.4, §4.7 (eval mode), TB8, P4._

269. As Jon the listener, I want to import my four reference standards (worship or acoustic ballad; cinematic or orchestral; R&B, soul or pop ballad; and a broad mix) as listening-only references with permission records, so that AURA is judged against the songs I hold up as the standard (O-05).
270. As Jon, I want a listening-only reference refused as engine or conditioning input before any job loads, so that my reference standards never leak into a generation.
271. As Jon the listener, I want a reference standard to appear only as an evaluation anchor, acknowledged as recognizable, and never as an arm in a product audition, so that product auditions stay blind.
272. As Jon, I want every evaluation preregistered (briefs, asset hashes, pins, candidate and compute budgets, paid-run ceilings, listening quotas and gates), with its hash committed before anything is rendered for it, so that results can never be reinterpreted after the fact.
273. As the maintainer agent, I want CI to check that each preregistration's hash was committed before its first evidence record, so that preregistration order is enforced rather than trusted.
274. As Jon the listener, I want the 12-brief smoke set run first (hummed melody, MIDI chord seed, guide vocal with corrected lyrics, explicit no-vocal instrumental, three-reference role task, one-word replace, chorus-only replace with protected verses, a piece over four minutes, sparse acoustic worship, dense pop, rhythm-heavy, cinematic instrumental bed), so that every route and engine profile faces my kinds of song before any claim is made.
275. As Jon the listener, I want only a preregistered benchmark gate to make a profile benchmarked (the 48-brief benchmark set, 6 briefs in each of 8 categories mapped to my four feels, for engine profiles; the hum benchmark for transcribers), so that a route earns its default on a real sample.
276. As Jon, I want each brief run in its own operator lane, so that LLC briefs never touch YuE2, Demucs or a non-commercial scorer.
277. As Jon, I want an LLC brief whose plan names YuE2 to fail preregistration validation, so that a lane mistake is caught before anything runs.
278. As Jon the listener, I want equal-candidate and equal-compute tracks, so that no route is favoured just because it got more tries or more GPU time.
279. As Jon the listener, I want about 10% hidden repeat pairs in evaluation auditions, so that my own consistency as a listener is measured.
280. As Jon, I want evaluation results reported with uncertainty clustered by brief, so that one lucky brief cannot carry a route.
281. As Jon, I want an evaluation that falls short of its preregistered listening quota to conclude "inconclusive" and promote nothing, so that a half-finished study never changes a default.
282. As Jon, I want every rejected candidate retained in evaluation records, so that results can be re-examined later.
283. As Jon, I want any route, YuE2 included, allowed to lose and to be demoted by the records, so that the preferred choice is tested rather than protected.
284. As Jon, I want the "unbenchmarked routes" label dropped only for routes that have a benchmark record, so that the label tells the truth route by route.
285. As Jon, I want operational gates (melody adherence, lyric error rate, edit preservation, export alignment and playback stability) recorded beside the listening results, so that a song that sounds good but breaks a measurable promise is still visible.
286. As Jon, I want the quality target "Suno v6-class" claimed only from my preregistered blind auditions against my reference standards, with gates fixed at preregistration, and never from a vendor figure, a leaderboard or a scorer, so that the ambition is allowed to fail honestly (ADR-0010).
287. As Jon, I want WildSongBench, Artificial Analysis and vendor numbers shown only as labelled external context and never in a measured column, so that a VENDOR number is never presented as measured.
288. As Jon, I want Suno output excluded from the harness entirely (never an arm, a reference, an input or test material), so that AURA is never built or tested on Suno audio (O-08).
289. As Jon the listener, I want to be the named gate owner and the only voter, with my listening minutes recorded with every verdict, so that the scarcest input in the studio is visible (Q8 default).
290. As the maintainer agent, I want the eval harness to be a Studio API client with no private path to the store, able to request quotes for paid briefs but never to approve them, so that evaluation runs through the same checks as the product.
291. As Jon, I want the smoke runs to compare whole-form rendering with per-section rendering, so that my verdicts decide whether SongForm assembly sounds repetitive.
292. As Jon, I want lyric phoneme error rate to join the badges only after its G2P's license is verified and it is validated on NeutralVoice and fixture vocals, so that a GPL phonemizer or a broken metric never ships [C2].

### 15. Operator lanes and licensing

_Scope: v1-core (stories 293–314). Covers [J6, L9]; ADR-0011, ADR-0022, ADR-0029, ADR-0036, ADR-0037; O-06; GAP-05, GAP-06; architecture §4.4, §10._

293. As Jon, I want each project's operator lane set when it is created (`individual` by default; `llc` for Sabbath Echo and every Island Development Crew venture; `research` for private experiments that are never released), so that "who is this work for?" is answered before anything runs (O-06).
294. As Jon, I want changing a project's lane to be an owner act that re-checks every artifact already in the project and is refused with the list of artifacts that block it, so that an individual project holding YuE2 or Demucs output can never quietly become LLC work.
295. As Jon, I want every artifact and candidate to show its eligible lanes (the lanes every component in its license chain allows, intersected with its audio parents' eligible lanes), so that I can see at a glance where a sound may go.
296. As Jon, I want lanes enforced at seven points (lane change, admission, the worker before loading, the store's write path, export, evaluation preregistration and burst egress), each refusing with a reason before anything loads or is spent, so that a lane leak would take seven bugs, not one.
297. As Jon, I want analysis never to narrow the lanes of the audio it measured (only derived-from and converted-from edges carry lanes and license obligations), while analysis jobs are still admitted in the project's lane, so that measuring a keeper cannot taint it and an LLC project still never runs a personal-use separator.
298. As Jon, I want each input's allowed uses checked against the task before any job runs, so that a reference or an import is only ever used the way its permission record allows.
299. As Jon, I want a risk acceptance to be an owner act recorded with the exact use it allows, so that any widening of an input's allowed uses is deliberate and on record.
300. As Jon, I want accepting a model's license to be an owner act, recorded with each license document's URL, revision and sha256 and the time, before any weights download starts, gated or not and whether from Hugging Face, a pinned URL or a package, so that every weight file on my disk has a recorded acceptance.
301. As Jon, I want weights downloaded at runtime from a pinned repository and revision and never vendored into the repository, with CI rejecting weight files by size and extension, so that AURA never redistributes weights it has no right to redistribute.
302. As Jon, I want copyleft and non-commercial code and weights to run only inside separate worker processes, with CI running a GPL, AGPL and non-commercial deny-list over the control service's environment and the web bundle, so that AURA's own code stays clean enough to open-source later.
303. As Jon, I want any release blocker in a keeper's closure (YuE2's non-commercial weights, for example) badged on the keeper and listed in its manifest, so that I know before releasing what stands in the way.
304. As Jon, I want a YuE2 song made in an individual project to state in its manifest that it is eligible for the individual and research lanes only, so that I never license it through my LLC by accident (GAP-05).
305. As Jon, I want the component register (terms, obligations, allowed lanes, redistribution status and verification status for every component) regenerated byte for byte from the evidence register and checked in CI, so that license facts have one source.
306. As Jon, I want every legal reading in AURA labelled as an interpretation and not legal advice, so that I know when to ask a lawyer.
307. As Jon, I want SwiftF0 limited to the individual and research lanes until its training-data provenance is reviewed, so that LLC adherence never rests on a non-commercial dataset.
308. As Jon, I want MiniMax's machine-generated disclosure obligation carried into the manifest of any closure that contains its output, so that publishing such a song cannot skip the disclosure (X-12).
309. As Jon, I want AURA to hold no hosted music-service API keys in v1, so that none can leak and no hosted service can become a silent fallback (ADR-0022).
310. As Jon, I want the only contact address anywhere in AURA (UI, docs, contracts, schemas, manifests, package metadata) to be `hello@islanddevcrew.com`, shown as text, never a mailto link and never a personal address, so that a personal inbox never becomes a public target (ADR-0037).
311. As the maintainer agent, I want every commit made with a noreply identity, and a CI lint that fails on any mailto link, any address other than the public contact and any non-noreply author, with planted violations proving that it fails, so that Rule 07 is enforced rather than remembered.
312. As the maintainer agent, I want CI to scan the built web bundle for secrets, so that no key ever ships to the browser.
313. As a future open-source user, I want every component to pass the open-source-readiness register before the repository goes public, so that publishing AURA is a license choice and not a cleanup (Q5 default).
314. As a future open-source user, I want lane semantics published as data (forbidden component classes per lane and the propagation rule), so that I can audit and adapt the policy without reading code.

### 16. Rented burst and cost

_Scope: v1-core (stories 315–339), except that the cost and economics log [J12] behind keeper cost is v1-studio in the inventory. Covers [C9, J12]; ADR-0023, ADR-0030, ADR-0031; O-02, O-09; architecture §4.5, §7.5, §7.6, TB2, TB7, P3._

315. As Jon, I want a job placed on a burst to get a quote showing the provider, GPU class, the live rate and when it was read, the job list, the ceiling, month-to-date spend, the monthly cap, the remainder and exactly which assets would leave my machine, so that I approve with everything I need on one card.
316. As Jon, I want a quote to use the provider's live rate, falling back to a dated price snapshot only when the live rate is unavailable and labelled with that date, so that I am never quoted from a stale price without knowing it.
317. As Jon, I want the ceiling computed from boot, weights download, the job estimates and a teardown margin at the highest rate in the GPU-class fallback list, with each estimate either measured history on that GPU class or the vendor figure times three labelled "unmeasured", so that the ceiling is conservative and says how it was made.
318. As Jon, I want a quote refused, with no override in the flow, when month-to-date spend (settled runs, open reservations at their ceilings and fixed monthly lines) plus its ceiling would exceed the $25 monthly cap, so that the cap is a wall, not a warning (O-09).
319. As Jon, I want to approve a quote only in the Studio UI, through a dialog that fetches a single-use challenge, with an approval bound to the quote's hash that expires 15 minutes after the quote, so that only I, in person, can say yes to spending money.
320. As Jon, I want one approval to cover one generation request's burst jobs, and any change to the job list or a compute-profile switch to need a new quote and a new yes, so that I always approve exactly what will run.
321. As Jon, I want the reservation at the ceiling written and synced to disk in the same transaction as the cap check, before anything is provisioned, so that a crash can never leave spend unaccounted for.
322. As Jon, I want every burst run to use the provider's secure cloud, start from a pinned image digest with no weights inside, carry a one-run bearer token of which only the hash is stored, and have a hard maximum duration and an in-image shutdown deadline, so that my unreleased melody and lyrics only ever reach a locked-down, short-lived machine.
323. As Jon, I want burst weights downloaded at boot from the pinned revision under my recorded license acceptance, with the download time included in the quote, so that the quote reflects the real cold start.
324. As Jon, I want the burst worker to pass a conformance ping before its first job, so that a broken image fails cheaply.
325. As Jon, I want every burst run settled from the provider's reported cost, or at the ceiling and labelled `settled_at_ceiling` when billing is missing, with monthly reconciliation able to raise the total (invoice charges the ledger never saw count toward the cap and block new runs until I acknowledge them) and to lower only an amount settled at the ceiling, so that the ledger never understates what I spent.
326. As Jon, I want a cost above the reservation to write an overrun that blocks new burst runs until I acknowledge it as an owner act, so that one surprise is never followed by another.
327. As Jon, I want a reaper, at startup and every 5 minutes, that terminates any tagged machine without an open burst run and any burst run past its hard maximum, and then settles it, so that an orphan never bills me through the night.
328. As Jon, I want every termination confirmed through the provider's API, so that "terminated" means the provider agrees.
329. As Jon, I want no paid job ever retried automatically, so that a failure never spends money twice without my yes.
330. As Jon, I want a Budget screen showing, for the UTC calendar month in my local time, month-to-date spend, open reservations, settled runs, fixed lines, the cap and every ledger entry, so that I always know where the $25 stands.
331. As Jon, I want changing the monthly cap to be an owner act in Settings, recorded in the ledger, so that the cap only moves when I move it.
332. As Jon, I want a reminder to set the provider-side spend limit by hand and to reconcile each month against the provider's invoice, so that the provider's own limit backs up AURA's.
333. As Jon, I want each burst run's cold and warm timings shown beside its ceiling and its actual cost, so that I learn what a YuE2 candidate really costs.
334. As Jon, I want every job to record its compute cost (zero for local work, the settled amount for a burst) and its cold and warm wall time as measured by the worker SDK, so that keeper cost is built from real numbers (ADR-0023).
335. As Jon, I want the egress list of an R1 burst to hold only the ABC, the lyrics plan and the job parameters, never Suno audio or reference standards, and every job that leaves the studio host to record the hashes it sent and where they went, so that I know exactly what left my machine.
336. As Jon, I want a network volume for burst weights adopted only when settled runs show it is cheaper, with its monthly fee then counted as a fixed line, so that a storage fee never sneaks under the cap.
337. As Jon, I want each unverified provider behaviour (HTTPS proxy reachability and limits, the live-rate API, whether an in-container shutdown stops billing, the provider spend limit and private-registry pulls) recorded as its own pass-or-fail spike before AURA relies on it, so that the burst path rests on evidence.
338. As the maintainer agent, I want every step of the paid flow exercised for $0 against a fake burst provider in CI, so that the money path is tested on every pull request.
339. As the maintainer agent, I want paid conformance on a real burst to go through the same quote, UI approval and reservation as any other job, so that even testing never spends money without Jon's yes.

### 17. Engine registry and health

_Scope: v1-core (stories 340–360). Covers [C3, J6, J8]; ADR-0001, ADR-0016, ADR-0026, ADR-0027; architecture §4.4, §4.8, §4.10, §6.2, TB3._

340. As Jon, I want the product view of the registry to list only engine profiles at smoke-passed or better on this session's host class, and to show unproven routes as "needs smoke", so that nothing appears to work until it has passed a check.
341. As Jon, I want published claims and AURA's own results in separate columns, each figure carrying its label (MEASURED-LOCAL, VENDOR, COMMUNITY, COMPETITOR-RUN, OWNER-REPORTED or INFERRED), so that I can see at a glance which numbers AURA measured.
342. As Jon, I want profile status (declared, installed, smoke-passed, benchmarked or disabled) computed from evidence records for each profile revision and host class, and never set by hand, so that no status can be raised without proof.
343. As Jon, I want each profile revision identified by the hash of its code commit, weights manifest, environment lock or image digest and worker SDK version, and shown in the registry, so that I know exactly which build produced a candidate.
344. As Jon, I want any pin change to make a new profile revision that computes to declared until its own install and conformance records exist, so that an upgrade never inherits a stale smoke-passed.
345. As Jon, I want installing a profile to go environment, preflight, license acceptance, selective download, verification, conformance and smoke, each step recorded as evidence and smoke-passed computed only at the end, so that the install path is itself the proof.
346. As Jon the listener, I want my "not garbled" check on a profile's smoke candidates recorded as an owner verdict within its smoke gate, so that an engine that decodes but sounds broken never reaches the product.
347. As Jon, I want any later failing evidence record on the same revision and host class to disable the profile, so that a regression takes an engine out immediately.
348. As Jon, I want upgrades admitted only after the new revision passes its smoke gate on that host class, so that a new release never silently replaces a working engine.
349. As Jon, I want each worker's health (idle, loading or busy, its resident profile and memory) visible, so that I can see why a job is waiting.
350. As Jon, I want one heavy model resident per device, unloaded when idle or when another heavy profile needs the device, with cold and warm times reported separately, so that the Mac never thrashes and model-load time on the HDD stays visible.
351. As Jon, I want workers to refuse an unsupported task, a forbidden lane, an over-limit duration, an unsupported language, missing weights, too little memory or disk, or a busy device before loading anything, with a code I can read, so that a bad request fails in milliseconds rather than minutes.
352. As Jon, I want each profile's limits (maximum duration, lyric languages, channels and sample rate) shown in the registry, so that I know what an engine can do before I ask it.
353. As Jon, I want ACE pinned at or after the commit that fixed its Apple Silicon output, and every engine in its own pinned environment, so that conflicting torch pins never break one another (ADR-0016).
354. As Jon, I want each worker host on the tailnet registered once with a pairing token and admitted for a profile only when that profile's revision has an installed record on its host class, so that a new machine earns trust profile by profile [J8].
355. As Jon, I want non-engine capabilities (Studio playback on each operating system, and microphone capture) gated by the same evidence fold as engine profiles, so that "works on Windows" is never claimed without a record.
356. As Jon, I want workers to fetch nothing from the network except their profile's pinned weights, and never an arbitrary URL, so that a worker can never be turned into a downloader.
357. As the maintainer agent, I want a lab view of the registry showing every profile at every status (declared, installed and disabled included) with the evidence behind each, so that I can see what to work on next.
358. As the maintainer agent, I want test-only fake profiles visible only in dev and test, with every output labelled "Synthetic test output", so that a fake can never reach Jon's product view.
359. As the maintainer agent, I want a registry schema rule that rejects MEASURED-LOCAL inside published claims and requires every local result to cite an evidence record, so that a vendor number cannot be laundered into a measurement.
360. As a future open-source user, I want adding an engine to mean writing a worker adapter (describe, prepare, run, unload) and a registry declaration, with no UI branch, so that new engines plug in without touching the product.

### 18. Cross-platform

_Scope: v1-core (stories 361–364, 366–371, 374–375); P6 (stories 365, 372, 373: the cross-machine CUDA worker [J8], per interpretation 7); the per-OS Studio playback gate [J20] is v1-studio. Covers [J8, J19, J20]; ADR-0003, ADR-0024; O-11; X-46, X-49; architecture §3.2, §8.7, P6._

361. As Jon, I want the control service and the localhost UI to run on macOS, Windows and Linux, so that I can choose the studio host whenever I need to (O-11) [J19].
362. As Jon, I want the control service to carry no macOS-only dependency (no `afconvert`, for example), with macOS-only code confined to the sparse-bundle volume adapter and the store's helper scripts, so that porting is configuration, not a rewrite.
363. As Jon, I want the control service's tests to run on Linux, macOS and Windows for every pull request (since PR #12, 2026-11-06) and for every integration push and nightly build, from the first ticket, so that a portability break is caught the day it happens.
364. As Jon, I want an operating system labelled "unverified" until the harness and the playback gate pass on a real host running it, not only in CI, so that AURA is never called three-platform ready from one machine.
365. As Jon, I want a Linux or WSL2 CUDA box on my tailnet to become a worker host that passes conformance on its own host class, with tier 1–3 recommendations made from its real snapshot, so that the second engine can run at home once the hardware is reachable (P6).
366. As Jon, I want a Linux machine to be able to act as the studio host, with the store as a plain directory, Chromium and local workers, so that I am not tied to the Mac.
367. As Jon, I want the control service to run natively on Windows with CUDA workers in WSL2, and WSL2's localhost forwarding checked before it is relied on, so that the Windows box can be a studio host too.
368. As Jon, I want workers placed by capability, MLX profiles on the Mac and CUDA profiles on Linux or WSL2, so that each engine runs where it actually works.
369. As Jon, I want projects moved between hosts only by backup and restore in v1, so that every move is hash-verified.
370. As Jon, I want the same `studioctl` commands on every operating system, so that I do not have to learn three tools.
371. As Jon, I want the DAW round trip and the recovery test run on each operating system once a host running it is reachable, so that finishing and recovery on each one are evidenced rather than assumed.
372. As Jon, I want a Metal port of YuE2 or HeartMuLa to become placeable only after a Metal-against-reference parity check and the same smoke gate, as another host class, so that a community port never replaces a burst on faith (GAP-04).
373. As Jon, I want a 16 GB NVIDIA card to get YuE2 only after its own smoke record, so that an open hardware question is answered by measurement (A4).
374. As the maintainer agent, I want the control service's paths, process calls and decoders to work on all three systems, with Windows path cases covered by store fixtures, so that a Windows host never fails on a path the Mac accepted.
375. As a future open-source user on Linux or Windows, I want the walking skeleton (MIDI to a verified export on the fake engine) to pass on my system in CI, so that I can try AURA without Apple hardware.

### 19. Accessibility

_Scope: v1-core (stories 376–391). Covers ADR-0012 (UX direction); architecture §6.1 (Playwright accessibility audit and keyboard-only operation)._

376. As Jon, I want every screen operable by keyboard alone, including Capture, the piano roll, the audition, the approval dialog and Export, so that I can work quickly without a mouse.
377. As Jon, I want to select, move, resize, split and transpose notes in the piano roll from the keyboard, with the selected note's pitch, start and length readable as text, so that the melody can be edited without dragging.
378. As Jon, I want a list view of the MelodySpec's notes with numeric pitch, start, length and confidence, so that the melody is readable without the piano roll.
379. As Jon the listener, I want keyboard controls for switching arms, playing, pausing and looping in an audition, and a verdict that needs a deliberate confirmation, so that a stray key can never cast a verdict.
380. As Jon the listener using a screen reader, I want arms announced only by their blind labels, with no route, profile or file name in any accessible name or description, so that accessibility support never unblinds an audition.
381. As Jon, I want badges, statuses and lanes conveyed by text and shape as well as colour, so that meaning never depends on colour.
382. As Jon, I want job state changes and approval requests announced politely to assistive technology, so that I know when candidates are ready without watching the screen.
383. As Jon, I want focus moved into the approval dialog and returned afterwards, with every figure (rate, ceiling, month-to-date, cap and egress list) readable as text in a logical order, so that I can approve spending by keyboard and screen reader with full information.
384. As Jon, I want text to scale to 200% without losing content or function, so that the Studio is usable at any zoom.
385. As Jon, I want colour contrast to meet WCAG 2.2 AA in both the light and the dark theme, so that the Studio stays readable in a dark room or a bright one.
386. As Jon, I want animation reduced whenever my system asks for reduced motion, so that the interface never distracts or unsettles.
387. As Jon, I want level meters and loudness readouts to show numbers as well as bars, so that levels are readable without judging a graphic.
388. As Jon, I want auditions only ever to attenuate and never to boost, and a master output level in the player bar that AURA remembers, so that a loud candidate never startles my ears.
389. As Jon, I want every control to be at least 24 by 24 CSS pixels, so that small controls never cause a wrong click on a trackpad or touchscreen.
390. As Jon, I want each error message to say what happened, what is safe and what I can do next, so that every refusal is actionable.
391. As the maintainer agent, I want an automated accessibility audit and a keyboard-only pass in Playwright on every screen, failing CI on any violation, so that accessibility regressions are caught at the pull request.

### 20. Recovery and reliability

_Scope: v1-core (stories 392–413). Covers [F14, J7]; ADR-0012, ADR-0028, ADR-0034; architecture §4.2, §4.3, §9.1, P1-4, P1-9._

392. As Jon, I want every artifact, record and event committed in one unit of work (the blob, then its sidecar or record, then the database rows and events), so that outputs appear only together and a crash leaves at most unreferenced blobs.
393. As Jon, I want a crash or kill during a job to leave the job failed as `worker_lost`, with no partial artifact visible and never marked ready, so that anything marked ready is complete [J7].
394. As Jon, I want local workers to exit when the control service dies, and remote or burst jobs to be re-queried on restart (resuming if still running, failed otherwise), so that a restart reconciles honestly.
395. As Jon, I want submitting the same job twice to be harmless, with the job id as the idempotency key, so that a retry after a network hiccup never duplicates work or spend.
396. As Jon, I want automatic retries only for retryable errors on free placements, and only a bounded number of times, so that transient faults heal without risking a loop.
397. As Jon, I want jobs to report only real steps, with an index and total only when the engine reports real counters, and never a fabricated percentage, so that progress is never a lie.
398. As Jon, I want every failure to carry a typed code (worker lost, worker refused, hash mismatch, decode failed, media mismatch, timeout, disk low, store unavailable, budget refused, quote expired, cancelled by owner, internal) and a plain explanation, so that I always know what went wrong.
399. As Jon, I want the UI's event stream to resume from the last event it saw after a disconnect or a reload, so that no state change is ever missed.
400. As Jon, I want new jobs refused and running jobs failed as `store_unavailable` if the studio volume disappears, and integrity checks run again on reattach before the store reopens, so that a pulled cable never damages my store.
401. As Jon, I want a recovery scan at startup that removes stale temporary files, quarantines blobs without rows, flags rows without blobs and runs the database integrity check, so that every start begins from a known-good state.
402. As Jon, I want one bad record or blob quarantined and reported without stopping the service or hiding other projects, so that a single corruption never takes my studio down.
403. As Jon, I want the database rebuildable with `reindex` from the content-addressed records and provenance sidecars, so that losing the database never loses a song.
404. As Jon, I want a database snapshot taken nightly and after every keeper, so that the most precious moments are always captured.
405. As Jon, I want the database written with full synchronous writes and full fsync on macOS, so that a power cut never loses a verdict that was already committed.
406. As Jon, I want AURA to hold an idle-sleep assertion while it is writing or downloading, so that the Mac never sleeps in the middle of a write to a USB disk.
407. As Jon, I want a weekly reminder to run `fsck` and a backup, so that the second copy stays current.
408. As Jon, I want `fsck` to detect even a single flipped byte, so that silent corruption on a spinning disk is caught.
409. As Jon, I want stored records never rewritten by an upgrade, with older schema versions upcast on read, so that an AURA update can never damage my songs.
410. As Jon, I want a cancel that has not taken effect within five seconds to kill a local worker or terminate a burst machine, ending the job cancelled with no partial output, so that cancel always means stopped.
411. As Jon, I want everything except burst runs and weight downloads to work with no network connection, so that a dead connection never stops me working on a song.
412. As the maintainer agent, I want frozen legacy fixtures from the first release to load at HEAD forever, so that a format break is caught in CI before it reaches Jon's store.
413. As the maintainer agent, I want the harness to wait on event sequence numbers, never on sleeps, and to use an injectable clock, so that reliability tests are deterministic and fast.

### 21. Supply-chain pins and expansion trials (added 2026-11-07)

_Scope: v1-core (stories 414–416: the lock advisory check and YuE2's exact pins); research (stories 417–422: the transcription, decoder and instrument trials, run only in research projects). Touches [A4] and [J13] (the decoder trial is one slice of the codec round-trip study), and [A8, C11] without building them. Covers ADR-0002, ADR-0005, ADR-0010, ADR-0011, ADR-0016, ADR-0027; O-06; `docs/research/OWNER-DECISIONS-2026-11-07.md`, which cites each item's pinned primary sources._

414. As Jon, I want an engine environment refused before it is built when its lock resolves a package version that a recorded security advisory lists as vulnerable (the first is GHSA-4prv-5hj7-c2xr: Diffusers 0.42.0 and earlier, patched in 0.42.1), and the versions it did resolve recorded in the environment's evidence, so that a known-vulnerable model loader never runs on my machine and the patched loader is on record.
415. As the maintainer agent, I want CI to fail when a committed worker lock pins a version inside a recorded advisory's vulnerable range, naming the lock, the package and the advisory, so that a vulnerable loader is caught at the pull request rather than at install.
416. As Jon, I want YuE2 pinned by an exact source commit, never by a version label or tag, with its code license, its individual-creator permission, its weights license and its VAE license each recorded at its own pinned revision and hashed into my license acceptance, so that I know exactly which terms cover the code and weights behind my R1 candidates (the label 0.1.6 names Apache-2.0 code on main and CC BY-NC 4.0 code at the 0.1.6 tag).
417. As Jon, I want four hard hum kinds (a one-note phrase with a single duration, adjacent fixed word boundaries, a long melisma, and a noisy vocal standing in for a separated one) generated with known notes and scored for onsets and offsets in a research project, so that I learn where each transcriber breaks before I rely on one.
418. As Jon, I want GAME and SheetSage2 runnable only as pinned, research-only transcribers behind the process boundary, after I accept their non-commercial terms, with their scores kept out of the default-transcriber decision and out of every register row, so that a research result never widens what my songs may use.
419. As Jon the listener, I want the same saved ACE latents decoded by the official decoder and by a compatible alternate decoder (ScragVAE first) and auditioned as two blind, level-matched candidates, with problem intervals whose notes name transients, sibilance, stereo image or quiet tails, so that a fidelity claim is decided by my ears and not by a card's spectral figures.
420. As Jon, I want an alternate decoder used only after its terms are in the component register and I have accepted them, loaded only from its verified, pinned download on the studio volume (never through an engine's own downloader or mirror), and only in research projects until a review widens its lanes, so that a decoder swap never brings unreviewed rights into my songs.
421. As Jon, I want Magenta RealTime 2 tried on my Mac as a playable instrument worker in a research project, with its code and weights terms recorded at pinned revisions and accepted by me before any download, and with no Studio control, so that I can judge a playable instrument without it touching my v1 songs.
422. As Jon, I want that trial to pass a smoke gate measured on my own Mac with the worker's own timings on the official Python MLX runtime, not the C++ runner the vendor's figures describe (faster than real time with no underruns over a fixed duration, and a control latency from a MIDI change to the changed audio under a threshold committed before the first measurement, the small checkpoint first) plus my "not garbled" check, with every model and cache file on the studio volume rather than the runtime's default folder in my home directory, so that a vendor's real-time claim becomes a measured fact or an honest failure.

## Implementation Decisions

The v1 architecture and ADR-0001…0037 hold the full reasoning. This section records the decisions the tickets build
against: modules, interfaces, contracts, API shapes, the worker protocol, job states, compute behaviour, storage and lanes.
It names no source paths. The few type shapes below are trimmed from the architecture's contracts because they encode
decisions more precisely than prose; they are shapes, not code.

### Shape and seams

- **Five parts.** One control service (Python 3.12, FastAPI, one uvicorn process, stdlib `sqlite3` in WAL mode, **no
  audio or ML dependencies**); one worker SDK (stdlib-only, Python ≥3.10); a small set of worker processes that do all DSP
  and inference; a thin Vite + React + TypeScript web app served by the control service from its own origin with COOP/COEP
  headers; and a content-addressed store on the studio volume (ADR-0012, ADR-0025).
- **Two behaviour seams, both as high as they can be.** (1) The **Studio API** (HTTP + SSE) is the only product seam:
  the browser, `studioctl`, StudioHarness, the eval harness and agents are all clients of it, and the eval harness has
  no private path to the store. (2) The **worker protocol** (HTTP, with the control service always the client) is the
  process-boundary seam that a localhost Mac worker, a tailnet CUDA box and a rented burst machine behind NAT all speak
  unchanged (ADR-0026).
- **Six deep modules behind the Studio API**, all in-process: ProjectStore, Conductor, Registry, Placement, Score and
  Audition. Only the Studio API and the worker protocol are external seams.
- **Contracts, not shared code.** JSON Schema 2020-12 is the language-neutral source of truth. Pydantic models (control
  service) and TypeScript record types plus a typed Studio API client (web app) are generated from it, with a drift check
  in CI. The stdlib worker SDK validates the same schemas with a bundled subset checker that refuses keywords it does not
  implement (the JOVRA `spec/` pattern). Pure rules (tick↔frame, SongForm assembly, MelodySpec→ABC, tier recommendation,
  ledger arithmetic, lane closure, audition gains) have stdlib reference implementations that regenerate the golden
  fixtures deterministically.
- **Neutral identifiers** (ADR-0035). The product name and the public contact text live in one product record. Python
  packages are `studio_*`, environment variables `STUDIO_*`, the CLI is `studioctl`, the volume is STUDIO, and the store
  format says `studio`.
- **Stack departures from D-12, each deliberate:** JSON Schema as the source of truth; one HTTP worker protocol; the
  control service serves the built app (no CORS, no Node at runtime, SharedArrayBuffer available from P0); pnpm with its
  store on the studio volume; YuE2 as an OCI image; engine workers as standalone uv projects outside the workspace lock;
  `awaiting_approval` as a job state. No Next.js and no SSR.

### Studio API (the one product seam; thin by design)

It validates contracts at the edge, maps module errors to typed problem responses, serves the built web app and
range-served audio, and holds no music logic.

| Area | Resources |
|---|---|
| System and compute | `GET /api/v1/system` (store mount, free space per volume against its margin, versions, product name) · `GET /api/v1/compute/detect` → HardwareSnapshot + Recommendation · `POST /api/v1/compute/recommend` (pure what-if) · `POST /api/v1/sessions {tier \| ComputeProfile}` · `PATCH /api/v1/sessions/{id}` (switch) |
| Projects and capture | `POST /api/v1/projects {name, operator_lane}` · `GET /api/v1/projects/{id}` → ProjectView · `POST /api/v1/projects/{id}/captures` (PCM WAV with the client's sha256 → Artifact + transcribe Job; or a `.mid` file, or a live-MIDI event list → MelodySpec) · `POST /api/v1/projects/{id}/lane` (**owner act**; re-checks every artifact) |
| Melody and song | `POST /api/v1/melodies/{id}/revisions {base_rev, ops[]}` (409 on a stale base; every op timestamped into the correction log) · `GET /api/v1/melodies/{id}/{rev}/as/{midi\|abc\|guide}` → bytes, a Job, or `Ineligible{reasons}` · `PUT /api/v1/projects/{id}/song` → SongSpec revision + `Validation{conflicts, unsupported_by_profile}` |
| Generation and jobs | `POST /api/v1/projects/{id}/generations {song_rev, mode: auto\|explicit, routes?}` → GenerationRequest {plan with reasons, declined routes with reasons, jobs, quotes} (409 `profile_not_promoted` before any load) · `POST /api/v1/jobs/{id}/cancel` · `GET /api/v1/events?after=seq` (SSE, resumable with `Last-Event-ID`) |
| Paid runs | `GET /api/v1/quotes/{id}` · `POST /api/v1/quotes/{id}/challenge` → `{nonce, expires_at}` (owner-ui session only) · `POST /api/v1/quotes/{id}/approve {nonce, quote_sha256}` (**owner act**) · `GET /api/v1/budget` · `POST /api/v1/budget/overruns/{id}/acknowledge` (**owner act**) · cap change (**owner act**, Settings) |
| Audition and keepers | `POST /api/v1/generations/{id}/auditions` and `POST /api/v1/projects/{id}/auditions {candidate_ids}` (candidates from several requests, a re-roll beside an earlier one) → audition (labels and commitment only; opens only when every arm is ready and every arm's audio allows `audition_arm`) · `GET /api/v1/auditions/{id}/audio/{label}` · `POST /api/v1/auditions/{id}/verdict` (**owner act**) · `POST /api/v1/auditions/{id}/reveal` · `POST /api/v1/projects/{id}/keepers {candidate_id, verdict_id}` |
| Export | `POST /api/v1/keepers/{id}/exports {formats}` → export Job · `GET /api/v1/exports/{id}` (bundle listing and zip) |
| References and imports | `POST /api/v1/references` (audio + permission record; **owner act**) · `POST /api/v1/imports` (imported mix with source service, terms, contained studio exports and detected marks; **owner act**) · `POST /api/v1/risk-acceptances` (**owner act**; only engine, conditioning, separation, edit or conversion input) |
| Registry and evidence | `GET /api/v1/registry?audience=product\|lab` (published claims and local results in separate fields) · `POST /api/v1/evidence` (EvidenceRecord; the Registry applies the gate rules) · `POST /api/v1/licenses/{component}/accept` (**owner act**, `license-acceptance/1`, before any weights download, gated or not) |
| v1-studio additions | Timeline revisions (`timeline/1`), edit operations (`edit-operation/1`: propose → candidates → audition → accept with preservation report → keeper revision; undo by hash), isolate-original jobs, DSP-finishing jobs. Same conventions: immutable revisions on a named base, 409 on a stale base, everything a job. |

- **Problem responses** are typed and carry a plain explanation: `profile_not_promoted`, `lane_forbidden`,
  `use_forbidden`, `insufficient_space{volume, free, needed, margin}`, `worker_refused{code}`, `stale_base`,
  `ineligible{reasons}`, `budget_refused{month_to_date, ceiling, cap}`, `quote_expired`, `owner_act_required` (403),
  `store_unavailable`.
- **Auth and local hardening** (ADR-0031). Binds 127.0.0.1 with a Host allowlist (DNS-rebinding defence) and an Origin
  check on every state change; tailnet binding is opt-in and token-gated. `studioctl serve` prints a one-time launch
  token that the browser exchanges for a `SameSite=Strict` cookie in the **owner-ui** scope. The CLI, eval harness and
  agents use an **automation** token from a local token file; that scope can do everything except owner acts.
- **Owner acts** (403 for automation): approve a quote, change the monthly cap, acknowledge an overrun or a
  reconciliation adjustment, change a project's operator lane, submit a verdict (including a smoke gate's "not garbled"
  check), accept a risk, accept a model license, record a reference permission, attest an import. A paid approval also
  needs the challenge nonce rendered in the dialog. `studioctl serve` prints the launch token only to an interactive
  terminal; test mode mints owner-ui sessions only on a temporary `test_store` with FakeBurstProvider and no keyring.
- **Secrets** (RunPod API key, HF token for gated models, tailnet pairing secrets) live in the OS keychain. Secrets,
  worker tokens and burst URLs never cross the API.
- **Events.** One SSE stream with a monotonically increasing `seq`, resumable by `Last-Event-ID`: job state and steps,
  artifacts committed, quotes, approvals, ledger entries, audition opened, verdict and reveal, registry status changes,
  mount state, session switches. Tests wait on `seq`, never on sleeps.

### ProjectStore (the durable truth)

- **Interface.** `ingest(stream, AssetMeta) -> Artifact` (verifies a declared hash) · `path(sha) -> Path` (read-only) ·
  `with unit_of_work() as uow: uow.put(record); uow.emit(Event)` (atomic) · `head(project_id, kind)` and
  `set_head(project_id, kind, rev, expected_rev)` (optimistic concurrency) · `closure(sha, edges={derived_from,
  converted_from}) -> ProvenanceGraph` · `reserve(bytes_by_volume) -> Reservation | InsufficientSpace(volume, free,
  needed, margin)` · `events(after_seq)` · `recover()`, `reindex()`, `fsck()`, `backup(dest)`, `restore(src)`, each
  returning a typed report.
- **Content-addressed blobs**, SHA-256, staged on the same volume, fsynced, renamed, then made read-only. Native-rate
  originals are always kept; conversions point to their source.
- **Content-addressed records.** Every immutable domain record (MelodySpec and SongSpec revisions, correction logs,
  verdicts, keepers, export manifests, evidence, reference permissions, risk acceptances, license acceptances) is also
  written as **canonical JSON** in the same unit of work as its row: UTF-8, sorted keys, no insignificant whitespace,
  **integers only**; non-integer quantities (LUFS, dBTP, cents, confidences, prices) are decimal strings with declared
  precision, so Python and TypeScript hash identically.
- **Provenance sidecar** beside every blob. An artifact without complete provenance is refused (ADR-0009).
- **SQLite is the system of record** (ADR-0028): WAL, numbered migrations, `synchronous=FULL`, `fullfsync` and
  `checkpoint_fullfsync` on macOS; projects, revision heads, the artifact index, jobs, events, sessions, quotes,
  approvals, burst runs, the ledger, verdicts and evidence. A `.backup` snapshot nightly and after every keeper.
  `reindex` rebuilds artifact and record rows and revision heads from sidecars and records; operational state (jobs,
  ledger, sessions) lives only in SQLite, and ledger lines can be rebuilt from provider billing.
- **Unit of work.** Blob, then sidecar or record, then rows and events, committed atomically; a crash leaves at most
  unreferenced blobs, which the startup recovery scan quarantines.
- **Write-path rules.** A commit into a project whose lane is not in the artifact's eligible lanes is refused; records
  must be schema-valid and provenance-complete; an artifact derived from an input by a use that input does not allow is
  refused (Suno boundary, ADR-0036).
- **Hides** the CAS layout, canonical JSON, crash safety on APFS, NTFS, ext4 and exFAT, migrations, the sparse-bundle
  free-space trap, the mount watch and recovery. **Internal seam:** `StoreVolume` with two adapters, the macOS sparse
  bundle and a plain directory (Linux, Windows, CI). macOS-only code lives only in that adapter and its helper scripts.

### Conductor (durable jobs)

- **Interface.** `submit(JobSpec) -> Job` (calls `Registry.admit`, then `ProjectStore.reserve`, then
  `Placement.resolve`; a paid placement returns the job in `awaiting_approval` with a Quote) · `on_approved(job_id,
  approval) -> Job` (called by Placement after the reservation is written) · `cancel(job_id) -> Job` · `run()` (the
  asyncio lifecycle owned by `serve`). State is observed only through store events.
- Every product feature is a JobSpec: `transcribe`, `guide`, `assemble-audio`, `generate`, `measure`, `adherence`,
  `separate`, `export`, `probe`, and in v1-studio `repaint`, `isolate`, `dsp-finish`, `dsp-edit`, `offline-render` (the
  contract ticket adds the kinds the schema still lacks, and a reserved `tts` kind so the later narration service fits).
  `generate` spawns child `measure` and, where the lane allows, `adherence` jobs.
- **Dispatch.** The job is submitted first (`job_id` is the idempotency key) and the worker admits or refuses it before
  any asset moves; inputs then move by hash (HEAD, then PUT only if missing), accepted only for that admitted job; worker steps are
  mirrored into events without invented percentages; outputs are pulled by hash into the store.
- **Residency.** One heavy profile resident per device, enforced with a device semaphore and `/v1/unload`; light
  profiles (analysis) run beside it.
- **Retries** only for retryable errors on free placements, bounded. A paid job never auto-retries.
- **Restart reconciliation.** Local workers die with the control service (parent-death watchdog), so their in-flight
  jobs become `failed(worker_lost)`. Remote and burst jobs are re-queried by `job_id` and resume or fail. A lost job is
  never `ready`.
- **Egress record** for every job that leaves the studio host: the asset hashes and the destination.

### Registry (what may run, in which lane, at what evidenced status)

- **Declarations only** (D-01): tasks (`text_to_song`, `cover`, `score_to_song`, `repaint`, `extend`, `extract`, `lego`,
  `complete`, `instrumental`, `reference_timbre`), limits (duration, sample rate, channels, lyric languages), backend and
  host OS, components, pins, gates (`smoke`, `benchmark`), allowed lanes, `claims_published` (each VENDOR, COMMUNITY or
  COMPETITOR-RUN; a schema rule rejects MEASURED-LOCAL there), `results_local` (each citing an `evidence_id`) and a
  `test_only` flag. No status field. Capabilities (`studio.playback`, `capture.mic` and `capture.midi-live` per OS, and `adherence.real-separator`) are declared the same way, each check with its measurement definition. Weights come from a Hugging Face revision, a pinned URL or a file in a pinned package, always behind a license acceptance.
- **Interface.** `admit(JobSpec, project) -> Admission | Refusal` · `view(audience) -> [ProfileCard]` (the product view
  omits anything below smoke-passed, shows unproven routes as "needs smoke" and never shows a published claim as
  measured) · `status(profile_id, host_class)` · `record(EvidenceRecord) -> StatusChange | Rejected` (the only write) ·
  `eligible_lanes(chain)`.
- **Component register** generated byte-for-byte from the evidence register (131 rows: 122 from the evidence register plus 9 supplement rows), with code, weights and
  output terms, obligations, allowed lanes, a process-boundary flag and verification status.
- **Use policy** lives here: reference permissions (`listening_only` is never engine input) and the Suno boundary.
- **Unregistered listening.** Product verdicts are evidence of kind `listening-unregistered`, shown per route ("kept n of
  m") and never changing a status.

Admission and status, trimmed from the architecture (§4.4) and ADR-0027:

```
Registry.admit(job, project) -> Admission | Refusal
  checks, in order, before anything loads:
    1. status(profile, target host_class) >= smoke-passed      (test_only counts only when STUDIO_ENV is dev|test)
    2. task, duration, language, channels within the declaration
    3. every component of the profile allows project.lane
    4. every derived_from / converted_from input has project.lane in eligible_lanes
    5. every input's allowed_uses include the task
    6. intent -> actual parameters (turbo hides guidance)
    7. prompt conflicts flagged
  Admission { profile_revision, actual_params, license_chain, eligible_lanes, obligations }
  Refusal   { reasons: [profile_not_promoted | over_limit | language_unsupported | lane_forbidden | use_forbidden | ...] }

profile_revision = sha256(code_commit ‖ weights_manifest ‖ env_lock_or_image_digest ‖ worker_sdk_version)
status(revision, host_class) = fold over EvidenceRecords for exactly that pair:
  declared     -> installed     : install record + conformance pass
  installed    -> smoke-passed  : the profile's declared smoke gate, its record listing every declared check passing and
                                  owner_not_garbled answered by an owner-ui verdict on that revision's smoke candidates
                                  (synthetic evidence only where the gate allows it)
  smoke-passed -> benchmarked   : a preregistered benchmark gate (never synthetic)
  any later failing record      -> disabled ; a pin change is a new revision, which computes to declared until its own
                                  install and conformance records exist
record() rejects: an unknown preregistration hash, a listening gate without owner verdicts, synthetic evidence aimed at a
  benchmark gate, a smoke record missing a declared check or its owner verdict
```

### Placement (where it runs and what it costs)

- **Interface.** `detect() -> HardwareSnapshot` · `recommend(snapshots) -> Recommendation{tier, reasons, warnings,
  per_tier_evidence}` (pure, golden-tested) · `select(session_id, tier | ComputeProfile) -> Session` · `resolve(profile_id,
  session) -> Ready(endpoint) | Paid(Quote) | Unavailable(reason, remedy)` · `challenge(quote_id) -> Nonce` ·
  `approve(quote_id, nonce, quote_sha256) -> Approval` (owner act; writes the reservation, then provisions) ·
  `release(endpoint, outcome) -> Settlement` · `reap() -> ReapReport`.
- **Worker supervisor** spawns each profile's environment on a random loopback port with a per-spawn token, health-checks
  it, and unloads idle workers.
- **Internal seams, each with two adapters:** `BurstProvider` (RunPod and FakeBurstProvider) and `HardwareProbe` (real
  commands and recorded-output fixtures).
- **BudgetLedger**, append-only: reserve, settle (basis `provider_reported` or `settled_at_ceiling`), release, overrun,
  fixed line, reconcile adjustment, cap change, overrun acknowledged.

### Score (pure composition semantics, no I/O)

- `apply(melody, ops) -> melody'` (move, resize, transpose, split, merge, add, delete, set tempo, meter or key, mark
  phrase, quantize as a reversible layer; every op set is a new revision plus correction-log entries) ·
  `assemble(melody, form) -> melody(kind=assembled)` · `from_midi(bytes)`, `from_midi_events(events)`, `to_midi(melody,
  form)` (via `mido`, once its license row is recorded) · `to_abc(assembled, song) -> Abc | Ineligible(reasons)` ·
  `validate(song, profiles) -> Validation` · `plan(song, lane, choices, compute) -> CandidatePlan` · `manifest(closure,
  chain, files) -> ExportManifest`.
- **TimeModel** (ADR-0033): 960 PPQ, tempo as integer microseconds per quarter, meter segments, and one half-up rounding
  function for tick↔frame, twinned in TypeScript; both pass the same tempo vectors.
- **YuE2 ABC dialect**: fixed header, one integer tempo, full bars, two voices, no tuplets or pickups (pickups padded with
  rests, tuplets re-quantized), lyrics bound by section tags and order with the syllable plan as a sidecar, `cot='melody'`
  (chord symbols stripped) or `cot='full'`. Typed ineligibility covers anything unrepresentable, lyrics in a language
  other than `zh` or `en`, and lengths over about six minutes. Output is validated in its fixtures with the YuE skill's ABC
  validator (`abc_tools`, Apache-2.0).
- **Candidate plan**: route × profile × seed for a lane, compute profile and set of eligible choices; the default is one
  candidate from each of the first two eligible routes in the plan-rules order (R1 only without a burst or with Jon's
  opt-in, then R2-synth, R2-raw, text), adjusted only by route-standing records from concluded preregistered sets; each
  reason says "first in the default order (unbenchmarked)", never "best"; the plan is labelled "unbenchmarked routes"
  until a benchmark record exists; one eligible route gives two seeds of it. `render_mode` is `whole_form` by default;
  `per_section` renders each SongForm section with one profile and seed and stitches them at the markers.

```
MelodySpec {                                   // melody-spec/1, trimmed
  melody_id, rev, base_rev?, spec_kind: melody | assembled, ppq: 960,
  tempo_map: {rev, tempo: [{tick, us_per_quarter: int}], meter: [{tick, numerator, denominator}]}, key,
  phrases: [{id, name, start_tick, end_tick}],
  notes: [{id, pitch: int, start_tick: int, duration_ticks: int, velocity: int,
           confidence: "0.00".."1.00" | null,
           origin: transcribed | corrected | midi_file | midi_live | manual | assembled}],
  source: {seed_kind: hum | midi_file | midi_live | assembled, capture_sha256?,
           transcription?: {method, profile_id, job_id, eligible_lanes, license_chain, note}, assembled_from?},
  quantize?, content_sha256 }
```

### Audition (blind, level-matched)

- **Interface.** `open(request_ids | candidate_ids | brief_id, mode) -> Audition` · `audio(id, label) -> Stream` ·
  `verdict(id, Verdict) -> Verdict` · `reveal(id) -> Reveal` · `keep(candidate_id, verdict_id) -> Keeper` (the preferred
  arm; after a tie either arm; after neither, none).
- Opens over two or more candidates **only when every arm is ready**. Labels come from a CSPRNG at open time; only
  `sha256(mapping ‖ nonce)` is published. Arms are 48 kHz/24-bit previews made by `measure`. Gains are **attenuation-only**
  down to the quietest arm's BS.1770-4 integrated loudness, with true-peak headroom from AURA's ≥4× oversampled meter and
  a residual mismatch of at most 0.1 LU. Audio is served by label with identical headers, no file name and no-store
  caching. Before the verdict the jobs drawer shows ordinals only and only "unplayable" shows.
- **Eval mode** adds reference-standard anchors (identity not blind, acknowledged), about 10% hidden repeat pairs and
  preregistered quotas; a short quota concludes `inconclusive`. A Suno import is never an arm.

```
Verdict { audition_id, preferred: A | B | … | tie | neither,     // verdict/1, an immutable owner act
          axes: [{axis: melody | vocal | lyrics | arrangement | mix | overall, preferred: label | tie | neither}],
          problem_intervals: [{label, start_ms, end_ms, note}],
          seconds_listened: [{label, seconds: int}], act: {give_verdict, owner-ui, at},
          evidence_kind: listening-unregistered | listening-preregistered }
Reveal  { audition_id, verdict_id, mapping: [{label, candidate_id}], nonce, revealed_at }
                                     // valid only if sha256(canonical(mapping sorted by label) + "|" + nonce) == commitment
"neither" re-rolls new seeds; the re-roll counts toward keeper cost
```

### Worker SDK and worker protocol v1

- **SDK** (`studio_worker`): stdlib-only on Python ≥3.10, so it installs into every pinned environment (Basic Pitch's
  3.10 included). It validates messages with the bundled schema checker, keeps an asset cache and crash journal, reports
  honest steps, honours cancel within 5 s, runs a parent-death watchdog for local spawns, hashes outputs with their audio
  metadata, and **measures timings and peak memory itself**, so a speed number is MEASURED-LOCAL by construction. An
  engine author writes four methods: `describe() -> [ProfileDescription]`, `prepare(profile_id, ctx)`, `run(task, ctx)`
  (where `ctx` offers `input(role)`, `step(name, index?, total?)`, `check_cancel()`, `emit(role, path, meta)` and
  `actual(params)`), and `unload()`.
- **Routes** (complete; anything else is 404): `GET /v1/describe` (worker id, protocol and SDK versions, host facts,
  env lock or image digest, code commit, per-profile tasks, limits, lanes, `weights_present` and weights manifest hash) ·
  `GET /v1/health` (`idle | loading | busy`, resident profile, memory) · `PUT | HEAD | GET /v1/assets/{sha256}` ·
  `POST /v1/jobs {job_id, profile_id, task, lane, inputs[{role, sha256, media_type, bytes}], params, seed, deadline_s}`
  → 202 or `422 Refused{code}` before anything loads · `GET /v1/jobs/{id}` (state, steps, outputs with audio metadata,
  `params_actual`, SDK-measured timings and peak memory, error; used for burst polling) · `GET /v1/jobs/{id}/events` (SSE)
  · `GET /v1/jobs/{id}/outputs/{role}` · `POST /v1/jobs/{id}/cancel` · `POST /v1/unload`.
- **Refusal codes:** `unsupported_task`, `lane_forbidden`, `over_limit`, `language_unsupported`, `weights_missing`,
  `insufficient_memory`, `insufficient_disk`, `busy`.
- **Auth:** bearer token per spawn (local), per pairing (tailnet), per lease (burst); never in the browser. Workers bind
  loopback or the tailnet interface or sit behind the provider's HTTPS proxy, and never call the control service.
- **Safety:** no shell; parameters validated per task and never interpolated into command lines; workers write only in
  their scratch directory; the only network fetch is the profile's pinned weights.

### Analysis worker and NeutralVoice

- One CPU-only Python 3.12 worker on every OS: `transcribe` (pYIN + AURA's HMM via librosa, ISC, no weights),
  `measure` (decode, duration, non-silence, clipping, integrated loudness labelled "BS.1770-4 (pyloudnorm)", true peak by
  AURA's ≥4× oversampled meter, the 48 kHz/24-bit audition preview), `guide` (NeutralVoice), `assemble-audio` (R2-raw hum
  slices along the SongForm), `adherence` (separated vocal → SwiftF0 with a pYIN cross-check → DTW → median cents error,
  octave-error rate, onset F1, contour correlation), `export` (bit-exact native copy, seeded-TPDF 48 kHz/24-bit only when
  the native rate differs, MIDI and specs from Score, then re-decode and re-hash), and `probe` (Metal working set on
  darwin-arm64).
- **NeutralVoice** (ADR-0032) is AURA's deterministic additive voice with formants; vowel, vibrato and drift are
  parameters. It does four jobs: the R2-synth input; ground-truth fixtures for transcription and adherence (±30 cents
  drift, onset jitter, vibrato, breath noise, rubato, and a line under an accompaniment bed), generated at test time and
  never committed; FakeEngine's sound; and the Playwright fake microphone. If it fails Jon's ear as a cover input, a
  license-verified MIDI synth becomes an alternative renderer behind the same `guide` task.
- **Separator worker** (individual and research lanes only until an LLC separator passes review): Demucs 4.1.0 or
  demucs-mlx on the Mac, chosen by smoke, with the MLX cache limit set. Its outputs are analysis artifacts for adherence
  and lyric error rate; they are never exported as stems.

### Engines and first profiles

| Profile | Engine / task | Host | Lanes | Notes |
|---|---|---|---|---|
| `fake-route-a`, `fake-route-b`, `fake-burst`, `fake-nc`, `fake-separate`, and the pre-seeded `fake-repaint`, `fake-isolate`, `fake-reference-timbre`, `fake-tts`, `fake-asr`, `fake-diagnostic` | FakeEngine (all tasks needed by the tests) | dev and CI, every OS | `fake-nc`: individual + research; others all | `test_only`; NeutralVoice guide plus a key-derived pad; fault knobs only when `STUDIO_ENV=test`; outputs carry `synthetic_test=true` |
| `ace-2b-turbo-mlx` | ACE-Step 1.5 2B turbo: `cover`, `text_to_song` | Mac (MLX/MPS) | all | quick iterations; guidance hidden, `shift=3.0` |
| `ace-2b-sft-mlx` | ACE-Step 1.5 2B SFT: `cover`, `text_to_song` (then `repaint` in P5) | Mac | all | full-quality candidates; pinned main ≥ `ca1e85fe9` |
| `ace-xl-sft-mlx` | ACE-Step 1.5 XL SFT | Mac | all | only after its own smoke, preflight and the diffusers bf16 loader check |
| `ace-*-cuda` | CUDA twins | tiers 1–3 worker hosts | all | per tier preset |
| `yue2-3b-score` | YuE2-3B: `score_to_song` (`abc=`, `cot`) | CUDA: burst in tier 4, local in tiers 1–3 after smoke | individual + research | OCI image (CUDA 12.8, torch 2.10.0, pinned commit, no weights), digest pinned; en/zh only; ≤ about 6 min |
| `separate-demucs` / `separate-demucs-mlx` | internal vocal separation (analysis) | Mac | individual + research | never exported as a stem; Demucs weights from a pinned URL behind a license acceptance |
| `isolate-demucs` / `isolate-demucs-mlx` (v1-studio) | Isolate original (`separated_source`, exportable) | Mac | individual + research | lanes and release blockers propagate to every stem; release-blocked until Jon decides |
| `transcribe-basic-pitch` | Basic Pitch, Python 3.10 env | Mac | individual + research until its provenance review | hum-benchmark challenger only; its model ships in the package, installed after a license acceptance |
| `ace-2b-base-mlx` | ACE-Step 1.5 2B base: adds `extend`, `extract`, `lego`, `complete`, `instrumental`, `reference_timbre` | Mac | all | the only profile with `reference_timbre` (O-07's global style reference); its own smoke ticket |
| HeartMuLa 3B, MiniMax Music 3 (P6) | LLC challengers | CUDA | LLC-eligible per register | MiniMax AUP #11 disclosure into the manifest |
| Stable Audio 3 Medium (v1-studio, optional) | `instrumental` | Mac (MLX) | per register | gated download, license registration, attribution, no training on outputs |

Install order is one challenger at a time (ADR-0002): ACE 2B turbo, then 2B SFT, then XL SFT on the Mac; YuE2 on an
approved burst; LLC challengers when a CUDA host or burst can run them.

### Web app and StudioEngine

- Listening-first and thin; it consumes only the generated typed client and holds no secrets and no edit logic beyond
  the TimeModel twin. Screens: **Session** (snapshot, recommended tier with reasons, all four tiers, per-tier evidence),
  **Capture** (AudioWorklet recorder with level meter, MIDI file drop, Web MIDI), **Melody** (piano roll over revisions,
  pitch curve, phrase marks, oscillator playback, note list view), **Song** (lyrics, SongForm, style, references, inline
  conflicts and R1 eligibility), **Generate** (plan with reasons and declined routes; the approval card), **Jobs drawer**
  (SSE-driven), **Audition** (synced switching with a short crossfade, loop span, keyboard control, no label leak in the
  DOM or accessibility tree), **Reveal / Keeper**, **Projects** and project page, **Export**, **Registry & Budget**
  (published and measured figures in separate columns; the ledger), **Settings** (cap, roots, reminders), and in
  v1-studio **Studio** (timeline).
- **Capture** records raw float32 PCM at the device rate through an AudioWorklet with `echoCancellation`,
  `noiseSuppression` and `autoGainControl` off, verified with `getSettings()`; it hashes with SubtleCrypto and uploads WAV,
  keeping the unverified m4a/AAC decoder off the core path.
- **Audition playback** uses GainNodes with server-computed attenuation-only gains.
- **StudioEngine** (v1-studio, P5): AudioWorklet playback with a SharedArrayBuffer ring per track, fed by a decode Web
  Worker that reads blob byte ranges; nothing blocking runs on the render thread; offline export never uses it. If a
  per-OS playback gate fails, only this module is replaced, by a CPAL native engine behind the same timeline contract.
- **Copy and design.** Plain, standard names (Cover, Extend, Replace) where they help; no imitation of Suno's branding or
  look; a large audition area and progressive disclosure; controls only where a profile implements them. The footer shows
  the public contact `hello@islanddevcrew.com` as text, read from the product record. Exact strings the tests assert:
  "Synthetic test output", "unbenchmarked routes" (the plan label), "unbenchmarked route" (the candidate badge), "needs
  smoke", "ACE-only: burst declined", "melody not kept", "adherence unmeasured (no LLC separator yet)", "unverified on
  real hums", "unplayable", "duration off", "BS.1770-4 (pyloudnorm)", `settled_at_ceiling`, "global timbre/style
  reference", "Not for release (research lane)", "separated · unreviewed". Badge strings are the `candidate/1` enum values;
  the UI renders them in sentence case.

### Eval harness and CLI

- **Eval harness** (P4): a Studio API client that commits preregistrations, runs briefs, opens eval-mode auditions and
  posts EvidenceRecords. It can request quotes but never approve them.
- **`studioctl`**: `setup` · `doctor` · `serve` · `env` · `store {create, attach, detach, compact, backup, restore, fsck,
  reindex}` · `worker add <url>` (pairing token) · `quote` (never approve). It never runs `sudo`; commands that need
  administrator rights are printed for Jon.

### Contracts

Every record is JSON Schema 2020-12 with `kind` and `schemaVersion`. Minor versions are additive; a major version is
upcast on read and stored objects are never rewritten; frozen legacy fixtures must load at HEAD forever; hashed records
hold integers only and every other quantity is a decimal string; schemas have no `$id` and use relative references.

| Contract | Purpose |
|---|---|
| `product/1` | The single rename constant and the public contact text. |
| `store/1` | Store identity, layout version, band size, last clean detach; with the format document, enough to open a store without AURA. |
| `melody-spec/1`, `correction-log/1` | The owned, editable melody (shape above) and its timestamped correction ops. |
| `song-spec/1` | Approved lyrics (BCP-47 language, kept apart from any transcript), style and exclusions, vocal mode, SongForm sections (vocal or instrumental, phrase refs, bars, repeats), duration, references, candidate count (2); each field requested / supported / observed. |
| `project/1` | Kind (`song`; `narration` reserved), operator lane (default `individual`), heads, requests, keepers, exports. |
| `artifact/1`, `provenance-sidecar/1` | Every stored blob with full provenance (shape below). |
| `job/1`, `event/1` | The durable unit of work (id is the idempotency key) with honest states, steps, placement, outputs, typed error, cost and egress; the resumable event stream. |
| `generation-request/1`, `candidate/1` | Plan with reasons, declined routes, jobs and quotes; two candidates, each with route, profile revision, seed, placement, measures and badges, never hidden. |
| `engine-profile/1`, `capability/1` | Declarations only (no status). |
| `component/1`, `lane-policy/1` | One license-register row; lane semantics as data (forbidden classes per lane, propagation rule). |
| `hardware-snapshot/1`, `compute-profile/1`, `session/1` | Detected facts with raw command output; the chosen tier preset and placement per profile; the session that pins the choice and logs switches. |
| `quote/1`, `approval/1`, `burst-run/1`, `ledger-entry/1` | The paid-run contracts (shape below). |
| `reference/1`, `import-terms/1`, `risk-acceptance/1`, `license-acceptance/1` | Reference standards and style references with permission records (an owner act); an imported mix's source service, attested terms, contained studio exports and detected marks (an owner act); Jon's signed acceptance of a named risk; his acceptance of a component's license documents before any weights download. |
| `audition/1`, `verdict/1`, `reveal/1` | Blind, level-matched comparison committed before reveal (the audition). |
| `eval-brief/1`, `prereg/1` | Smoke-12 and benchmark-48 briefs mapped to the four feels; the preregistration hashed before any run. |
| `evidence/1` | The only thing that changes a status or passes a gate (shape below). |
| `export-manifest/1` | The self-describing record inside an export bundle, with its release blockers and whether it is release-clear. |
| `edit-operation/1`, `timeline/1` (v1-studio) | A scoped generative edit with its preservation report; tracks, clips in project frames, artifact source frames at native rate, MIDI clips in ticks, markers. |
| `worker-describe/1`, `task-request/1`, `task-status/1`, `refusal/1` | The worker protocol. |

```
Artifact {                                                   // artifact/1 + provenance sidecar, trimmed
  sha256, bytes, media_type, audio: {sample_rate, channels, frames, sample_format},
  origin: generated_mix | separated_source | regenerated_part | new_part | human_recording | rendered_guide
        | rendered_midi | tts_render | conversion | imported_mix | analysis | preview,
  parents: [{edge: derived_from | converted_from | analyzed_by, sha256}],
  producing_job_id, engine: {profile_id, profile_revision, code_commit, env, sdk_version, weights, seed,
  params: {intent, actual}}, record_inputs, host (with host_class), compute,
  timings: {cold: bool, load_wall_ms, run_wall_ms, total_wall_ms, peak_rss_bytes, label, measured_by},
  operator_lane, eligible_lanes, license_chain, allowed_uses, capture?, import_terms_id?,
  retention_class: irreplaceable | derived | reproducible, synthetic_test: bool }
eligible_lanes(a) = (⋂ allowed_lanes(c) for c in license_chain(a))
                    ∩ (⋂ eligible_lanes(p) for p in parents(a) where edge ∈ {derived_from, converted_from})
                    ∩ import_terms(a).eligible_lanes, when a is an import

EvidenceRecord {                                             // evidence/1, trimmed
  id, check, subject: {subject_type, subject_id}, profile_revision?, host_class?, gate_id?,
  result: pass | fail | inconclusive, measured: [{metric, value: "decimal", unit, label: MEASURED-LOCAL}],
  checks: [{check, result, verdict_id?, measured}],          // every check the gate declares, for a smoke pass
  synthetic: bool, attachments: [{name, sha256}], prereg_sha256?, verdict_ids, recorded_at }
// the store is the system of record; docs/evidence holds hash-checked exports with the verdicts and preregistrations they cite
```

### Job lifecycle

```
queued ──▶ awaiting_approval ──(owner approval + reservation written)──▶ preparing
   │            │  (quote expired / declined / re-quoted on a compute-profile switch: old approval void)
   └────────────┴────────────────────────────────────────────────────────▶ preparing ──▶ loading ──▶ generating ──▶ analyzing ──▶ ready
                                                       any non-terminal state ──▶ failed{code, retryable} | cancelled
failure codes: worker_lost | worker_refused(code) | hash_mismatch | decode_failed | media_mismatch | timeout
             | disk_low | store_unavailable | budget_refused | quote_expired | cancelled_by_owner | internal
```

- `preparing`: assets pushed by hash. `loading`: model loading, cold or warm recorded. `generating`: engine running.
  `analyzing`: child `measure` and, where the lane allows, `adherence`. `ready`: outputs committed atomically.
- **Submit order**: `Registry.admit` → `ProjectStore.reserve` (preflight) → `Placement.resolve` → (paid: quote →
  `awaiting_approval`) → dispatch. Every refusal happens before any load or spend.
- **Atomic commit**: outputs pulled to the staging area and hash-verified; `measure` confirms they decode and their
  declared media facts (rate, channels, frames) match; one unit of work commits all artifacts, sidecars and events.
- **Cancel** must take effect within 5 s; otherwise a local worker is killed and a burst machine terminated; the job ends
  `cancelled` with no partial output.

### Compute profiles

- **Detection.** macOS: `sysctl`, `system_profiler` and the Metal `recommendedMaxWorkingSetSize` via the analysis worker
  (37.44 GiB on this M5 Pro, MEASURED-LOCAL). Linux, Windows and WSL2: `nvidia-smi` (name, memory, driver, compute
  capability), RAM, `/proc/version`; on Windows also `wsl.exe -l -v` and the `.wslconfig` memory. Remote hosts report the
  same facts in `/v1/describe`. Store facts: APFS free, exFAT host free, sequential MB/s, random 4K IOPS. Raw outputs are
  kept. An unreachable host has no snapshot and cannot qualify for a tier.
- **Recommendation** (pure, golden-tested over recorded snapshots for an M5 Pro 48 GB, a 3090, a 4090, a 5090, a 16 GB
  card and a no-GPU host):

| Hardware | Tier |
|---|---|
| Apple Silicon | 4 |
| NVIDIA ≥23.5 GiB, compute capability ≥8.9 (4090/5090 class) | 1 |
| NVIDIA ≥23.5 GiB, compute capability 8.0–8.6 (3090/A5000) | 2 |
| NVIDIA 11.5–23.5 GiB, compute capability ≥8.0 | 3 (O-02 names 12–16 GB; 16–23.5 GiB cards are placed in tier 3 as a deliberate extension, with a warning, pending Jon's confirmation) |
| Any NVIDIA card below compute capability 8.0 (no BF16), or no accelerator | burst only: tier-4 placements for CUDA profiles, MLX profiles unavailable off the Mac, with a warning |

  Warnings: host RAM under 24 GiB for YuE2; driver below 570.26 (Linux) or 570.65 (Windows) for cu128; Blackwell with
  cu126; WSL2 memory under 24 GiB. Each tier lists which profiles have evidence on a matching host class; the rest "need
  smoke". A 16 GB card never gets YuE2 until its own smoke record exists.

- **Tier presets:**

| Tier | ACE | YuE2 (individual lane) | Burst | Analysis and separation |
|---|---|---|---|---|
| 1 | `ace-xl-sft-cuda` local | local | overflow, per-run approval | studio host (separation on the Mac only, until a CUDA separator profile exists) |
| 2 | `ace-2b-sft-cuda`; XL with offload after a smoke run | local | overflow | studio host |
| 3 | `ace-2b-sft-cuda`; XL only with offload after a smoke run | local only after a smoke run on that card; otherwise burst | fallback | studio host |
| 4 | `ace-*-mlx` on the Mac | burst | per-run approval | the Mac |

- **Selection and switching.** `setup` writes the default compute profile from the recommendation. Every session start
  (each `serve` start or the first UI load after an idle gap) shows the snapshot, changes since last time, the
  recommendation with reasons, warnings and per-tier evidence, and all four tiers; one click keeps the profile. Any tier,
  host or OS may be chosen; unsatisfiable profiles resolve to burst or `Unavailable(reason, remedy)` in the plan before
  submit. A switch is logged: undispatched jobs are re-planned, jobs awaiting approval are re-quoted (old approval void),
  running jobs finish where they are unless cancelled; projects never change.

### Burst runs, the cap and cost (O-09)

```
max_minutes  = boot + weights_download + Σ job_estimate + teardown_margin
job_estimate = MEASURED-LOCAL history on that GPU class, else VENDOR figure × 3 labelled "unmeasured"
ceiling      = max_minutes × max(rate over the GPU-class fallback list) + fixed lines
month_to_date (UTC calendar month, shown in local time)
             = Σ settled actuals + Σ open reservations at ceiling + Σ fixed monthly lines + Σ reconcile adjustments
refuse the quote if month_to_date + ceiling > cap            // cap = 25.00; no override in the flow
Quote    { quote_sha256, provider, gpu_class, rate, rate_read_at, rate_source: live | snapshot(date), jobs[],
           ceiling, month_to_date, cap, egress: [{sha256, role}], lane_check, expires_at = created_at + 15 min }
Approval { quote_sha256, nonce (single use), approved_at }   // owner-ui only; void on any job-list change or profile switch
LedgerEntry = reserve | settle{basis: provider_reported | settled_at_ceiling} | release | overrun | fixed_line
            | reconcile_adjustment | cap_change | overrun_acknowledged                      // append-only
```

1. **Quote** from the live provider rate (dated snapshot only as a labelled fallback), with the egress list by hash (for
   R1: the ABC, the lyrics plan and job parameters; never Suno audio, never reference standards) and the lane check.
2. **Cap check** as above.
3. **Approval** in the UI only: the dialog fetches a challenge and shows provider, GPU class, rate and timestamp, job
   list, ceiling, month-to-date, cap, remainder and egress. One approval covers one generation request's burst jobs.
4. **Reservation before provisioning**, fsynced in the same transaction as the cap check.
5. **Provision**: RunPod secure cloud first, from the pinned yue2 image digest in a private registry (the pull credential
   lives at the provider), tagged `studio-burst` plus the run id, one-run 256-bit bearer token (only its hash stored), hard
   maximum duration, in-image `shutdown -h` deadline, container disk sized for weights, outputs and margin; weights
   downloaded at boot at the pinned revision under the recorded license acceptance; a conformance ping before the first job.
6. **Run**: the Conductor polls through the provider's HTTPS proxy with short requests; no long-lived streams.
7. **Settle**: terminate and confirm through the provider API; settle at the provider-reported cost or at the ceiling as
   `settled_at_ceiling`; reconciliation may lower only an amount settled at the ceiling, and books any invoice charge the
   ledger never saw (a missed machine, stopped-machine storage, a revised cost, network-volume fees) as a reconcile
   adjustment that counts toward the cap and blocks new leases until acknowledged; a cost above the reservation writes an
   overrun that does the same.
8. **Reaper** at startup and every 5 minutes. **No automatic paid retry.** Declining labels the plan "ACE-only: burst
   declined".

- **Backstops:** the in-image deadline (a second lock until the billing spike proves it), a provider-side spend limit Jon
  sets by hand, a prepaid balance kept at or below the remaining cap with auto top-up off, and monthly invoice
  reconciliation. The RunPod key sits in a presence-gated keychain item that the self-hosted runner's user cannot read. A network volume for weights is adopted only when measured
  boot-plus-download time across settled runs shows it is cheaper; its fee then becomes a fixed line. A Vast adapter
  behind the same port is considered only on ledger evidence.
- **Cost accounting** (ADR-0023): every job records compute cost (zero locally), SDK-measured cold and warm wall time,
  placement and host class. **Keeper cost** (candidates per keeper with re-rolls, compute cost, cold and warm time,
  listening time) is the only reported denominator; "cost per song" never appears without it.

### Storage

- **The volume** (ADR-0015): `setup` creates an APFS sparse bundle on the Backup Plus drive (`-size 900g` logical cap,
  Jon's to change; band size chosen from the P0 measurement of 8 MiB versus 64 MiB) and attaches it at STUDIO with
  `-owners on -nobrowse`. Setup probes ownership, symlinks, chmod, hardlinks and `clonefile`; writes the Spotlight
  marker and prints `mdutil -i off` as an owner action; adds a sticky Time Machine exclusion. An unclean-detach marker
  triggers a volume verify on the next attach. Compaction runs offline. An optional login item attaches at login.
- **Layout** (documented in the store's format document, readable without AURA): an identity file and a single-writer
  lock at the root; the project store (database with WAL and snapshots; content-addressed blobs in a two-level hex fan-out
  with provenance sidecars beside them; canonical records in a parallel tree; a same-volume staging area; quarantine;
  exports as clones of blobs plus their manifest); models (the HF home with its xet cache, other downloads with pin files,
  license acceptance records, per-profile weights manifests); environments (Python installs, the uv cache and per-worker
  environments keyed by lock hash); caches (pnpm, pip, torch, MLX, XDG, Playwright); ticket worktrees; per-job scratch
  (deleted at job end); logs; and evidence captures awaiting commit. The internal disk holds only the OS, the browser,
  the canonical docs checkout, a few KB of config and keychain entries.
- **One-volume rule and environment routing** (ADR-0034): `studioctl env` writes one env file that sets `HF_HOME`,
  `HF_XET_CACHE`, `UV_CACHE_DIR`, `UV_PYTHON_INSTALL_DIR`, `UV_PROJECT_ENVIRONMENT`, `PIP_CACHE_DIR`, `TORCH_HOME`,
  `XDG_CACHE_HOME`, `XDG_DATA_HOME`, `XDG_STATE_HOME`, `UV_TOOL_DIR`, `UV_TOOL_BIN_DIR`, `npm_config_cache`,
  `COREPACK_HOME`, `TMPDIR`, `PLAYWRIGHT_BROWSERS_PATH`, the MLX cache limit and the pnpm store (pnpm 11 reads `storeDir`
  and `cacheDir` from `pnpm-workspace.yaml`, not `.npmrc`; MEASURED-LOCAL); it exports nothing and fails when the volume
  is not mounted; the control service sets them per spawn. Ticket worktrees come from a bare clone on the volume, so their
  git objects never land in the canonical checkout's `.git`. Roots are configurable; environments and the uv cache always move together.
- **Disk preflight** (every download, install, environment build, job and export declares bytes per volume): STUDIO
  effective free = min(APFS free, exFAT host free) − band overhead, refused below a **10 GiB** margin (configurable);
  internal disk: no planned writes, heavy jobs blocked under **2 GiB**; remote hosts from the free space in `describe`;
  burst disks sized at quote time; a running job fails `disk_low` below half the margin. Estimates: ACE turbo + encoder +
  VAE ≈ 6.34 GB, LM 1.7B ≈ 3.76 GB, XL only as diffusers bf16 ≈ 11.1–11.5 GB once its loader is verified, YuE2 7.30 +
  0.53 GB on CUDA hosts and bursts only (VENDOR sizes); outputs at 92,160,000 bytes per 4-minute stereo float32 stem.
  Install verifies bytes against the manifest and every LFS sha256.
- **HDD consequence** (INFERRED from the measured ~125 MB/s): about 50 s to cold-load ACE turbo and 90 s for XL bf16, so
  workers keep one heavy model resident and report cold and warm times separately.
- **Retention and backup:** irreplaceable (human recordings, imported MIDI and mixes, MelodySpec and SongSpec revisions
  with correction logs, verdicts, keepers and their audio closures, references with permissions, risk acceptances,
  evidence, export manifests, the latest database snapshot) is always mirrored; derived (other candidates, analyses) only
  with `--include-derived`; reproducible (weights, environments, caches, previews, scratch, export renders) never.
  `backup` copies in the same CAS layout and re-hashes at the destination; `restore` rebuilds a fresh root; `fsck`
  re-hashes; a weekly reminder prompts both.
- **Other operating systems:** a plain directory (`STUDIO_ROOT`) with the same layout, no symlinks or xattrs, short
  lowercase-hex paths; projects move between hosts only by backup and restore in v1.

### Operator lanes (O-06, ADR-0011, ADR-0029)

Every project has a lane: `individual` (default), `llc` (Sabbath Echo and every IDC venture) or `research`. Every
artifact carries `eligible_lanes` (shape above); `analyzed_by` never propagates, but analysis jobs are still admitted in
the project's lane.

| # | Enforcement point | Check | Negative test |
|---|---|---|---|
| 1 | Project lane change (owner act) | Re-check every artifact and every lane-carrying record (a MelodySpec drafted by a lane-restricted transcriber) in the project | Moving an individual project holding a YuE2 artifact, or a melody drafted by an individual-only transcriber, to `llc` is refused |
| 2 | Admission (`Registry.admit` in `Conductor.submit`) | Components allow the lane; audio-ancestry inputs allow it; inputs' allowed uses include the task | An LLC request for `yue2-3b-score` returns `lane_forbidden` with no `loading` event; an LLC adherence job on `separate-demucs` is refused and the badge reads "adherence unmeasured (no LLC separator yet)" |
| 3 | Worker refuse-before-load | Request lane is in the profile's lanes | A direct `lane: llc` call to the yue2 or `fake-nc` worker gets `422 lane_forbidden` and loads nothing |
| 4 | Store write path | No artifact or melody record enters a project whose lane is not in its eligible lanes; an import's lanes come from its attested terms (a DAW bounce inherits the exports it contains) | A forced commit of an individual-only artifact into an LLC project is rejected; a DAW bounce of an individual-only export is refused in an LLC project |
| 5 | Export (closure over audio edges) | Manifest's eligible lanes contain the project lane; license chain, release blockers and disclosure from audio ancestry only; research exports are never release-clear | An LLC export of a closure containing `fake-nc` is refused; an LLC export of an ACE keeper `analyzed_by` an individual-only separator is allowed |
| 6 | Evaluation preregistration | Each brief runs in its own lane | An LLC brief plan naming YuE2 fails preregistration validation |
| 7 | Burst egress | The quote shows the lane check and egress list | A quote for an LLC project's YuE2 job is never created (refused at point 2) |

- **Use policy at the same points.** A `listening_only` reference is never engine input and never a product audition arm.
  Every import is an owner act whose allowed uses follow its source: Suno `[listen, loudness_measure, dsp_finish]` (Pro or
  Premier only, llc only with the LLC's account or a written license); owned purchase `[listen, loudness_measure,
  eval_anchor]`; licensed, only what its license grant names; never training. An owner-signed risk acceptance can add
  only engine, conditioning, separation, edit or conversion input; a Suno import is never an audition arm, an evaluation
  reference or anchor, a reference, training data or test material, whatever is signed, and DSP finishing preserves its
  embedded provenance. Ingest detects Suno's embedded marks and AURA's own export tags.
- **Lane-aware components in v1:** pYIN + HMM, NeutralVoice and ACE in every lane; SwiftF0 and Basic Pitch individual
  and research until their provenance review (LLC adherence would use pYIN only, once an LLC separator exists); Kim
  Mel-Band-RoFormer individual and research until its training-data review; Demucs and demucs-mlx individual and
  research; YuE2 individual and research; the non-commercial scorers individual and research (O-06), SongBench research
  only; HeartMuLa and MiniMax LLC-eligible (P6); a component whose license is still UNVERIFIED research only.
- **Licensing doctrine** (ADR-0011): weights never vendored (downloaded at runtime from a pinned repo and revision after
  an owner-act license acceptance, gated or not); copyleft and non-commercial components only as separate worker
  processes; a CI license allowlist over the control environment and web bundle (anything unknown fails; LGPL, GPL,
  AGPL, NC, CC-BY-SA, SSPL and BUSL are denied there); a release-blocker list kept current in the
  register; every component must pass the open-source-readiness register before the repo goes public.
- **Rule 07** (ADR-0037): the only contact anywhere is `hello@islanddevcrew.com` as text from the product record; no
  mailto link and no personal address in code, copy, contracts, manifests, package metadata, docs or commit metadata;
  noreply commit identity; a CI lint with planted violations.

### Evaluation design (ADR-0010)

- **Reference standards**: four human-made songs Jon owns or has licensed, one per feel (worship or acoustic ballad;
  cinematic or orchestral; R&B, soul or pop ballad; broad mix), imported `listening_only` with permission records; eval
  anchors only. Suno output is excluded from the harness.
- **Smoke set** (12 preregistered briefs): hummed melody; MIDI chord seed; guide vocal with corrected lyrics; explicit
  no-vocal instrumental; three-reference role task; one-word replace; chorus-only replace with protected verses; a piece
  over 4 minutes; sparse acoustic worship; dense pop; rhythm-heavy; cinematic instrumental bed. Briefs whose operations
  belong to v1-studio (one-word and chorus-only replace) run once their operations exist; until then they are recorded as
  not yet runnable, never as passed. The three-reference role task is not runnable in v1, because role-bound
  multi-reference conditioning [B11] is v2. The MIDI chord seed runs once chord symbols exist: the MIDI file's chord track
  becomes the SongForm's chord symbols, R1 uses `cot='full'`, and the R2 guide stays melody-only. Smoke-12 preregisters
  lyric error rate once its validation exists (its ticket blocks the smoke run).
- **Benchmark set**: 48 briefs, 6 in each of 8 categories mapped to the four feels; the only route to `benchmarked` for
  engine profiles (transcribers reach it through the hum benchmark). Completing it is post-v1.
- **Route standing**: only a concluded preregistered set changes a lane's default pair, through a route-standing record
  that `Score.plan` reads; a preregistered route comparison (R1, R2-raw and R2-synth at equal candidate count on the hum
  fixtures against the committed adherence thresholds) alone decides ADR-0004's reverse-if.
- **Protocol**: preregistration hash committed before any run (CI checks commit order); equal-candidate and
  equal-compute tracks; uncertainty clustered by brief; about 10% hidden repeat pairs; rejects retained; each brief in its
  own lane; a short quota concludes `inconclusive`; any route may lose. Operational gates sit beside listening: melody
  adherence, lyric error rate, edit preservation, export alignment, playback stability.
- **Hum benchmark** (TB6, a P2 parallel track): Jon records N hums plus the same melodies on MIDI as ground truth, N fixed
  at preregistration; Basic Pitch, SwiftF0 `segment_notes` and pYIN + HMM scored with mir_eval COn/COnP/COnPOff plus blind
  correction effort from the correction log; "manual entry wins" allowed.
- **Lyric error rate**: phonemes from a G2P whose license is verified first (an espeak-ng-backed G2P only behind a process
  boundary), ASR by Whisper or Qwen3-ASR on the internal separator's vocal; shown only after validation on NeutralVoice
  and fixture vocals.

### Studio scope (v1-studio, P5)

- **Timeline** (`timeline/1`): integer sample positions in project frames, artifacts referenced at native rate, MIDI in
  ticks, a versioned tempo map, section markers. Base: evaluate waveform-playlist v16 (MIT) against AURA's own timeline;
  never wavesurfer-multitrack; wavesurfer 8 core may draw single waveforms. Time and pitch: Signalsmith Stretch (MIT)
  first, SoundTouch (LGPL) only in a separate worker process, never in the web bundle, as fallback; Rubber Band never
  bundled. Speed changes appear only after objective criteria and Jon's blind verdict both pass.
- **Playback gate** per OS (the `studio.playback` capability): 8 tracks × 30 minutes with zero underruns by Chrome's
  `playbackStats`, UI p95 under 100 ms during a generation (Event Timing durations over a versioned scripted interaction
  set, at least 200 samples); 16 tracks as a stretch gate. Computed smoke-passed per OS.
- **Edit operations** (ADR-0017): mask, crossfades, locked context, candidates, the accepted one; ACE repaint with main's
  chunk mask for section, line and word edits; repaint at the start or end to extend; AURA composites each candidate
  (the original outside the mask and crossfades, ACE's output inside) and the preservation check compares PCM samples
  (not headers) of the composite outside the mask and crossfades in a declared rate, channel and sample-type domain, while
  ACE's raw deviation outside the mask is recorded separately as chunk-mask evidence; undo restores
  by hash; approved lyrics, ASR transcript and alignment are separate assets.
- **Stems** (ADR-0006): Isolate original stores mixture, stems and residual; bleed and residual energy against
  thresholds committed before the Mac run, sum-to-mixture as an integrity check on stored and exported files, and Jon's
  listening verdict (until then stems read "separated · unreviewed"); separators lane-aware; RoFormer checkpoints only from a verified allow-list. Re-perform and Create a new part
  are v2; their origins are reserved now. Replacing a part rebuilds the mix.
- **DSP finishing** (ADR-0019, ADR-0021, O-08): non-generative mixing and mastering (gain, fades, EQ, trimming, loudness
  to an explicitly chosen target with the dry export kept) and format and rate conversion; the only processing a Suno
  import, or a set of Jon's own Suno stems, may receive. Placing a Suno import on a timeline beside AURA audio is refused
  unless a risk acceptance names edit input.
- **Aligned stem export**: a common rate, zero start, equal frame counts; a DAW import checked with screenshots.

### Delivery order

Tracer bullets, each a narrow but complete path through contracts, store, jobs, workers, UI and tests (architecture §11):
**TB0** store, doctor, session → **TB1a** MIDI → measured fake pair → **TB1b** blind audition → keeper → verified export →
**TB1c** capture → ingest → **TB1d** transcribe → piano roll → **TB2** paid-run gate on FakeBurstProvider → **TB3** first
real pair: ACE on the Mac (R2-synth + R2-raw) → **TB4** MIDI in and out, live included → **TB5** adherence → **TB6** hum
benchmark (parallel, not blocking TB3) → **TB7** YuE2 on an approved burst (R1) → **TB8** reference standards and
preregistered smoke-12 → **TB9** first studio slice: section replace and the Mac playback gate. Phases: **P0** ground
(TB0), **P1** walking skeleton (TB1a–d, TB2), **P2** first real pair (TB3–TB6), **P3** not ACE-only (TB7), **P4**
measurement (TB8), **P5** v1-studio (TB9 onward), **P6** lanes and hosts beyond the Mac (pulled forward the day a CUDA
host is reachable). Each phase's exit criteria are checks that could fail, recorded as evidence records or CI run ids
(architecture §11, "Phase plan and exit evidence"); `/to-tickets` turns each into acceptance criteria.

## Testing Decisions

- **What a good test is here.** It exercises behaviour through one of the two seams (the Studio API, or the worker
  protocol) or through the contract gate, and it would fail if the behaviour broke, whatever the internal structure. It
  reads like the user story it proves ("an LLC request for YuE2 is refused before anything loads"). Expected values come
  from an independent source: the stdlib reference implementations, NeutralVoice ground truth generated from a golden
  MelodySpec, a worked example in an ADR, or a hand-checked literal. Never from the code under test (no tautological
  oracles), and never a snapshot produced by the same path. **No test mocks an internal collaborator.** Fakes exist only
  at real boundaries.
- **The seams, confirmed by the architecture (§6) and kept to the minimum.**

| Seam | What it proves | Runs |
|---|---|---|
| **1. Studio API** via **StudioHarness** (pytest against the real control app on an ephemeral port) | Every product behaviour as Jon would observe it: compute detect, recommend, select and switch (re-plan, re-quote, approval voided); store preflight on every volume, mount loss, the lock, recovery, `reindex` (delete the database, reindex, diff the durable rows and heads), backup, restore, `fsck` with a flipped byte; capture ingest and hash verification; transcription to a MelodySpec; correction ops, stale-base 409 and the growing correction log; MIDI round trip; SongForm assembly; ABC emission with typed ineligibility; guide rendering; SongSpec conflicts; candidate plans per lane and tier; `profile_not_promoted` before any load, pin change resetting status, promotion without evidence rejected, synthetic evidence never reaching benchmarked; honest job state sequences, SSE resume, cancel, SIGKILL during `generating` giving `failed(worker_lost)` with no partial artifact; the whole paid gate; blinding, gains and reveal; keeper and verified, deterministic export; every lane enforcement point's negative test; the Suno boundary; Rule-07 copy | Linux on every PR (≤10 min budget); macOS and Windows on integration and nightly |
| **Browser entry to seam 1** (Playwright; not a new seam) | The UI drives the API correctly; no blind label, hash, route, profile or file name in the DOM, the accessibility tree or any network response before the verdict; the approval card's copy; "Synthetic test output" and "ACE-only: burst declined" shown; accessibility audit and keyboard-only operation on every screen | Chromium headless on Linux per PR (fake microphone fed a NeutralVoice hum); macOS Chromium nightly with screenshots attached as evidence |
| **2. Worker protocol conformance** (a pytest suite run as `--worker URL --token`) | `describe` is schema-valid and matches the registry declaration; refuse-before-load for an unsupported task, forbidden lane, over-limit duration, unsupported language, missing weights and insufficient memory, with no `loading` step and no model import; hash mismatch rejected; submit idempotent on `job_id`; steps honest; cancel within 5 s; outputs hash-match and carry complete provenance; a restart reports the job lost, never ready; one heavy model resident and `/v1/unload` frees it; auth required; every undeclared route 404 | FakeEngine and the analysis worker on every PR; ACE on the self-hosted M5 Pro runner (producing an evidence record); YuE2 on a burst only through the `--paid` marker, which goes through the real quote → UI approval → reservation flow |
| **Contract gate** (data, not behaviour) | Schemas use only keywords the bundled checker implements; every fixture and registry file validates; the stdlib reference re-run matches every golden exactly; hand-written assertions hold (guarding against tautological fixtures); seeded-bad fixtures fail; the component register regenerates byte-identically; every frozen legacy fixture loads; `claims_published` never contains MEASURED-LOCAL; the TypeScript TimeModel twin passes the tempo vectors; the codegen drift check is clean | Every PR |

- **Mutant workers the conformance suite must fail** (CI asserts each failure, which proves the suite is not vacuous):
  one that loads before its refuse check, one that misdeclares its sample rate, one that returns a wrong output hash, one
  that ignores cancel, one that fabricates a percentage, one that goes silent on heartbeat or health, and one that answers
  an undeclared route.
- **Fakes, only at real boundaries.**
  - **FakeEngine worker**: a real subprocess speaking the real protocol, launched by the real supervisor. Profiles
    `fake-route-a`, `fake-route-b`, `fake-burst`, `fake-nc` (declares a non-commercial component, lanes individual and
    research) and `fake-separate` (returns exactly the vocal it embedded). Output: the NeutralVoice guide plus a pad
    derived from the key, seeded and deterministic within one operating system, architecture and SDK version. Fault
    knobs, available only when `STUDIO_ENV=test`:
    `driftCents`, `octaveErrorRate`, `onsetJitterMs`, `clipDb`, `silence`, `failAtStep`, `crashAt`, `wrongOutputHash`,
    `slowLoadMs`, `ignoreCancel`, `refuse`. Every output carries `synthetic_test=true`. It also impersonates a burst machine
    for FakeBurstProvider.
  - **The analysis worker** runs for real, as a subprocess, in every harness run.
  - **FakeBurstProvider**: in-process at the `BurstProvider` port, with programmable rates, provisioning latency,
    billing data (present, missing, above the reservation), lost machines and terminate failures. Every TB2 case runs
    for $0: over cap; reservation event before provision event; automation-token approve → 403; reused or expired nonce;
    job-list change needs a new quote; SIGKILL mid-run (the reaper settles at ceiling, the job fails `worker_lost`, no
    retry); overrun block.
  - **HardwareProbe fixtures**: recorded `sysctl`, `system_profiler`, `nvidia-smi` and `wsl.exe` output for an M5 Pro
    48 GB, a 3090, a 4090, a 5090, a 16 GB card and a host with no GPU.
  - **Temporary stores**: a plain directory on Linux and Windows; on macOS a 2 GB temporary APFS sparse bundle for the
    preflight and mount cases (including a fixture where APFS free exceeds exFAT host free).
  - **An injectable clock** (quote expiry, the 5-minute reaper, the UTC month boundary, weekly reminders) and a registry
    overlay that enables the `fake-*` profiles.
- **Golden fixtures and tolerance rules.** Golden fixtures are JSON (no audio is ever committed). Audio needed by a test
  is generated at test time from a golden MelodySpec by NeutralVoice or FakeEngine. Every comparison falls into exactly
  one class, declared in the fixture:
  1. **Bit-exact**: canonical JSON records and their hashes (identical across Python and TypeScript); the export's native
     copy; the seeded-TPDF 48 kHz deliverable on a given operating system and architecture; the preservation check
     (PCM samples, not headers, in a declared rate, channel and sample-type domain); tick↔frame vectors; ledger arithmetic; lane closure; audition gains
     as decimal strings.
  2. **Environment-exact**: FakeEngine and NeutralVoice audio is deterministic within one operating system, architecture
     and SDK version, so its hashes are compared only within that environment; across environments a fixture compares
     measured features instead.
  3. **Toleranced**: measurements whose fixture states the tolerance and the reason. Examples: residual level mismatch
     ≤ 0.1 LU; adherence metrics on the NeutralVoice-line-under-bed golden within the tolerances fixed in the fixture;
     loudness of a generated test tone against its analytic value; the transcriber's COnP F1 at or above its
     preregistered floor.

  A tolerance is never loosened in the same change that makes a failing test pass; widening one is its own fixture
  change with a written reason. Floats appear only where a fixture states a tolerance. Every fixture listed in the
  fixture manifest must be consumed, or a manifest test fails.
- **Per-OS CI** (ADR-0024, as noted 2026-11-07): the control service and StudioHarness on Linux, macOS and Windows for
  every PR (since PR #12; the `integration` ruleset requires all three), every integration push and nightly, from the
  first tickets; Playwright Chromium on Linux per PR and macOS nightly. A
  self-hosted Mac runner produces hardware evidence (ACE conformance and smoke, store throughput, the playback gate) and
  never runs paid jobs. Lints on every PR, each proven by a planted violation: a mailto link, a personal address, a
  non-noreply author, a 50 MB dummy weight file, a GPL dependency in the control environment, a secret in the web bundle.
  CI minute rates on a private repo are UNVERIFIED. The repository is public for the build so hosted CI stays free (Jon's
  reason, OWNER-DECISIONS-2026-11-07.md), and the rates matter again before it returns to private.
- **Evidence gates (real checks, not test seams).** What no fake can show, each producing an evidence record: ACE and
  YuE2 install, conformance and smoke on real host classes with cold and warm timings; Jon's recorded "not garbled"
  checks; store throughput, IOPS and band size on Backup Plus; Jon's blind verdicts; the per-OS Chrome `playbackStats`
  gate; the ledger reconciled against provider billing; the hum benchmark on Jon's hums; the burst spikes.
- **Evidence capture conventions (the analogue of JOVRA's rule 9: evidence, not claims).**
  - A ticket is done when a check that could fail has passed. The PR names the check and links its CI run id or evidence
    record id.
  - Five kinds of evidence are **reported separately and never merged into one "works"**: (1) CI on fakes; (2) hardware
    evidence on a named host class (for example `mlx/m5pro`); (3) listening evidence (Jon's verdicts, owner acts that no
    agent can produce); (4) paid evidence (ledger entries reconciled with the provider); (5) per-OS evidence (a real host
    running that OS). A claim with only the first kind says so.
  - An evidence record holds the check, subject (profile revision or capability, and host class), result, measurements
    labelled MEASURED-LOCAL, the synthetic flag, hashed attachments (logs, screenshots, raw command output) and, where a
    gate needs one, the preregistration hash. Records are committed to the repository as JSON with hashes; audio is never
    committed.
  - Synthetic evidence is labelled synthetic everywhere and can satisfy a smoke gate only where that gate allows it,
    never a benchmark gate.
  - Unverified work is labelled UNVERIFIED in the PR, the registry and the UI. A vendor figure is never copied into a
    measured field.
  - Playwright screenshots are attached as evidence on macOS nightly runs; DAW-import checks attach screenshots too.
- **Which modules are tested where.**

| Module | Seam |
|---|---|
| Studio API, ProjectStore, Conductor, Registry, Placement, Audition | Studio API (StudioHarness), plus Playwright for UI-visible behaviour |
| Score (pure) | Golden JSON fixtures reached through the Studio API's render and what-if endpoints, re-run against the stdlib reference by the contract gate; no second test seam |
| Worker SDK, FakeEngine, analysis worker, separator, ACE, YuE2, Basic Pitch adapters | Worker protocol conformance (+ mutants); analysis metrics also validated on NeutralVoice ground truth before they are shown |
| Web app (TimeModel twin) | Tempo vectors in vitest; everything else through Playwright against the real API |
| StudioEngine (v1-studio) | The per-OS playback gate (evidence), plus Playwright for transport behaviour |
| Contracts, registry data, component register | Contract gate |

- **Prior art.** AURA has no code yet. The patterns come from JOVRA: its `spec/` contract folder (JSON Schemas without
  `$id`, a stdlib reference engine that regenerates golden fixtures deterministically, a bundled JSON-Schema subset
  checker that refuses unknown keywords, a validator that re-runs the engine and fails on seeded-bad fixtures, and
  platform conformance tests that read fixtures in place and compare canonical JSON byte for byte); JOVRA ADR-0004
  (capability statuses promoted only by recorded benchmark runs, with synthetic benchmarks as a floor that never reaches
  `validated`); JOVRA ADR-0019 (quote, consent, cap and reservation for paid cloud work); and JOVRA's practice of one PR
  per ticket with evidence attached.

## Out of Scope

- **The narration service** (Sabbath Echo first). It gets its own spec and tickets later (ADR-0008, Q9). Music v1 only
  keeps the shared contracts open: `tts_render` is an artifact origin, `narration` is a reserved project kind, the store,
  Conductor, Placement, Registry and worker SDK stay domain-agnostic, and P6 dry-runs a `tts_render` artifact through the
  store, jobs and export manifest with no schema change.
- **Own-voice conversion and the voice registry** (v2, O-07, ADR-0007) [G1, G3, G4, G7]: no voice cloning or conversion
  in v1, no RVC, Applio or rmvpe weights, and every manifest carries `converted_vocal: false`. Seed-VC is rejected and
  live voice conversion is out of scope [G6]. Score-to-singing with DiffSinger stays research [A10, G5].
- **Training and personalization beyond the doctrine** (ADR-0020) [K1–K5]: no foundation training, no training job type,
  no LoRA or LoKr adapters, no DPO, no continued fine-tuning, and no non-ML taste memory in v1. MTG-Jamendo and FMA are
  excluded for anything shareable; Suno outputs and ElevenLabs renders are never training data. The codec round-trip
  ceiling study [J13] is research and must precede any enhancement or training claim.
- **A desktop shell** (ADR-0014) [J17]: no installer, auto-update or code signing; Electron is preferred if one is ever
  needed, and Tauri 2 is rejected for the Studio. No mobile companion [J18].
- **Hosted music services** (ADR-0022) [L11]: no Mureka, Lyria, Stability API or ElevenLabs Music in v1-core, no
  third-party "Suno API", and never a silent hosted fallback. A hosted service may later join only as an optional,
  model-pinned profile outside the listening harness unless a preregistration names it.
- **Suno as harness input** (O-08, ADR-0010, ADR-0021, ADR-0036): Suno output is never an audition arm, an evaluation
  reference or anchor, a reference, training data, or material used to develop or test AURA, whatever risk acceptance is
  signed (the schema refuses one naming those uses). Only the DSP finishing of Jon's own permitted downloads is in scope
  (v1-studio); a signed risk acceptance can add only engine, conditioning, separation, edit or conversion input, and a
  Suno arm in the harness would need O-08 revisited and ADR-0010 amended first.
- **Multi-user anything**: accounts, sign-in, sharing, share links, comments, publishing, credits, plans, Explore,
  self-hosted share servers [I11, J15], and any server store (ADR-0009's reverse condition). AURA is single-user and
  local.
- **Stems beyond Isolate original** (v2, ADR-0006): Re-perform this part [E5, E7] and Create a new part [E6] (their
  origins are reserved now); lead versus backing vocal splits [E8]; 12-stem or 100-instrument taxonomies and
  prompt-selected separation [E9, E10] (research).
- **Studio features after the v1-studio gates**: recording into tracks [F10] (v2; latency-compensated, never live
  monitoring); clip transpose, speed halving or doubling and follow-tempo [F4]; wavetable synth [F7]; automation curves
  [F8]; effects beyond gain and EQ (compressor, limiter, sends, sidechain, convolution reverb) until offline and real-time
  output are shown equivalent [F9]; native plugin hosting [F11]; chat-directed production and generated DSP code [F12,
  F13].
- **Generation and brief features deferred** (feature inventory tiers): random "dice" concepts [B2]; PerformanceSpec [B9];
  auto titles and style expansion [B10]; role-bound multi-reference conditioning [B11] (v2, labelled an approximation
  where an engine lacks it, so the smoke set's three-reference role task is not runnable in v1); time-indexed reference sampling [B12]; image or video to brief [B13]; personas [B14]; sounds
  and loops [C12]; "Remaster" [C13]; LLM lyric writing [B6], which the inventory lists as optional v1-core but the v1
  architecture does not design (see Further Notes).
- **Mastering and enhancement**: automatic reference-matched mastering through Matchering [I6] (v2, separate GPL process,
  only after a blind audition shows it helps without hiding defects); generative super-resolution [I7]; DeepFilterNet on
  music, ever.
- **Delivery extras**: destination eligibility checklists [I8] (v2); music video and lip-sync guide buses [I9]
  (research); client delivery packages [I10]; cover art and avatars [J14]; forced watermarks [J16].
- **Engines and components rejected or held** (RECONCILIATION §4): LeVo 2, DiffRhythm 2, MusicGen and JASCO, StepAudio 3
  Music, HeartMuLa 7B, Stable Audio Open 1.0, the MiniMax hosted API, ACE-Step-DAW and other AGPL code; YuE1 and the
  MiniMax MLX ports are on watch; Shao, MuLaCover, SongEcho and SheetSage2 run only in research-lane jobs, never in
  product code. The non-commercial scorers (SongEval, MuQ, CMI-RM, TuneJury) may run as diagnostics in individual and
  research projects (O-06), never selecting, ranking or filtering; SongBench stays research-only (academic terms).
- **Comparators the owner has not confirmed**: Logic Pro is not a comparator until Jon says he owns it (Q11).

## Further Notes

### Owner decisions applied

| ID | Decision | Where it lands |
|---|---|---|
| O-01 | Private `Navigata1/aura`; one issue, one branch and one PR per ticket into an integration branch; native blocking edges (amended 2026-11-07: public for the build phase, private again at production level) | `/to-tickets` and `/implement-spec` workflow; evidence conventions; `docs/research/OWNER-DECISIONS-2026-11-07.md` |
| O-02 | Four compute tiers, recommended from detected hardware, chosen at install and every session, switchable; tier 4 on this Mac; a rented burst is approved | Install and compute profile stories; Placement; compute profile decisions; YuE2 via burst (R1) |
| O-03 | Weights and the store on Backup Plus in an APFS sparse bundle; preflight on every volume | Store and disk stories; Storage decisions |
| O-04 | Hum or sing into a mic, and MIDI (file or live), both becoming an editable MelodySpec | Capture and transcription stories; Score |
| O-05 | Four feels with one reference standard each | Evaluation stories and design; `reference/1` |
| O-06 | Lane per project, default individual; IDC ventures and Sabbath Echo are `llc`; YuE2, Demucs and NC scorers only in individual and research | Lanes stories; seven enforcement points; register rows (NC scorers individual and research, SongBench research only) |
| O-07 | Own voice is v2; v1 uses engine vocals and ACE reference timbre labelled as a global style reference | Out of Scope; `converted_vocal: false`; story on reference timbre |
| O-08 | Reference standards only, listening-only; Suno excluded from the harness; Jon's Suno downloads may be DSP-finished | Evaluation and DSP-finishing stories; Suno boundary enforcement |
| O-09 | $25 monthly cap; every paid run needs Jon's explicit yes; logged against the cap before it starts | Burst stories; quote → approval → reservation → settle |
| O-10 | "AURA" in one constant | `product/1`; neutral identifiers |
| O-11 | Platform and compute selectable; control service and UI portable; Studio playback gated per OS | Cross-platform stories; per-OS CI and gates |

### Owner-pending items and the defaults this spec uses

- **Q1, Linux and Windows hardware** (GPU, VRAM, RAM, WSL2, tailnet reachability). Default: tier 4 on the Mac; tiers 1–3
  designed and tested only against recorded `nvidia-smi` output, labelled unverified until a host is reachable (P6).
- **Q4, release plans for the first song.** Default: personal; every export carries an AI-disclosure-ready manifest.
- **Q5, AURA's code license.** Default: all rights reserved until Jon chooses MIT or Apache-2.0 before the repo goes
  public; every component must already pass the open-source-readiness register. The repository became public for the
  build on 2026-11-07 without a license grant, so the default still holds: public visibility is not a license, and Q5
  stays open (Jon may later choose an open-core or open-source strategy; that is not yet a decision).
- **Q6, the melody and lyric language.** Default: English lyrics; Jon records his melody as the first hum fixture (it
  becomes an irreplaceable capture and seeds the hum benchmark).
- **Q8, the listening gate owner.** Default: Jon is the named gate owner and the only voter.
- **Q9, Sabbath Echo narration.** Out of scope for this spec; only the shared contracts must not preclude it.
- **Q10, Chromium for the Studio.** Default: yes; Safari and WKWebView are not supported for Studio playback.
- **Q11, Logic Pro.** Default: unknown, so not a comparator.
- **From the 2026-10-09 design review** (defaults applied until Jon answers): whether Demucs-isolated stems may appear in
  a released individual song (default: release-blocked); placing 16–23.5 GiB NVIDIA cards in tier 3 (default: yes, with a
  warning); the default route order in the plan rules (screens Q10: R1 only without a burst or with his per-request
  opt-in, then R2-synth, R2-raw, text); and his acceptance of this spec and of ADR-0025…0037, without which the ticket set
  stays a draft.
- **From the architecture:** the bundle's logical size (900g) is Jon's to change; the backup destination device is
  owner-pending (backup and restore are built and drilled against a second directory until Jon names a device); the
  provider-side spend limit and the Spotlight `mdutil` command are owner actions AURA prints and reminds about; the
  internal disk's stray caches are deleted only by Jon.

### Unverified capabilities and the tickets that gate them

Each row is a ticket node for `/to-tickets` (a spike, an `evaluate` ticket or a license-verification ticket). Until its
gate passes, the capability is labelled as shown and nothing depends on it silently.

| Capability or fact | Status today | Gating ticket / exit check | Until then |
|---|---|---|---|
| Hum transcription quality on Jon's voice | No clean transcriber benchmarked on humming (GAP-01) | Synthetic floor (P1-10), then the hum benchmark (TB6, P2-8): `transcriber-floor`, `hum-benchmark-on-jon` | pYIN + HMM labelled "unverified on real hums"; correction mandatory |
| Analysis profiles on the Mac's host class | Proven only on Linux CI host classes | `analysis-on-mac` (install, conformance and smoke on `cpu/m5pro`) | Measure, guide, export and transcription refused on the Mac |
| Any route keeping a hummed melody | UNVERIFIED; ACE Hit@1 2.4% (COMPETITOR-RUN), YuE2 71.3% (VENDOR, not on hums) | Adherence validated with a real separator (TB5, P2-4), the preregistered route comparison, smoke-12 (P4): `adherence`, `separator-on-mac`, `route-comparison`, `smoke-12` | Plan labelled "unbenchmarked routes"; "melody not kept" badge when adherence fails |
| Adherence on real candidates (real separator in the chain) | Validated only against fake-separate, which returns the line exactly | `separator-on-mac` (the `adherence.real-separator.darwin` capability, under a NeutralVoice bed and an ACE bed with reverb and doubling) | Adherence and its badges hidden on real candidates |
| Default melody route (screens Q10) | Plan-rules default, unbenchmarked | `route-comparison` | First two eligible routes in the plan-rules order, labelled "first in the default order (unbenchmarked)" |
| YuE2 on hand-written ABC | 84% exact pitch only on edited model scores (VENDOR) | ABC converter goldens validated by `abc_tools.py` (P3-1); R1 candidates on a burst (TB7): `abc-emission`, `r1-first-burst` | R1 conditioning, never claimed exact |
| YuE2 on a burst (runtime against the hard maximum, VRAM on the 24 GB class, in-image weight verification) | UNVERIFIED | `yue2-smoke-on-burst` | No product R1 candidate; burst fallback list only names smoke-passed GPU classes |
| ACE timings and output on the M5 Pro | No official Mac figures (C3) | ACE conformance and smoke on `mlx/m5pro` (P2-1, P2-2): `ace-on-mac` | ACE profiles absent from the product view |
| ACE base and the global style reference (O-07, reference timbre) | UNVERIFIED; only the base checkpoint declares `reference_timbre` | `ace-base-on-mac` | No style-reference candidates on a real engine |
| ACE XL via the diffusers bf16 loader | UNVERIFIED | XL loader check plus its own smoke: `ace-xl` | XL hidden |
| ACE repaint chunk mask (main only, #1292) | UNVERIFIED on the pinned commit | TB9 section replace with the composite preservation check and the raw-deviation record (P5-2): `repaint-on-mac` | No real edit operations |
| Isolate-original quality (bleed, residual energy) | UNVERIFIED | Thresholds committed before the Mac run, then Jon's listening verdict: `stems-listening` | Stems read "separated · unreviewed" |
| m4a/AAC decoder license (ffmpeg build, PyAV) | UNVERIFIED | Decoder license ticket: `codec-checks` | Hums arrive as WAV only |
| G2P or phonemizer license (lyric error rate) | UNVERIFIED (an espeak-ng path is GPL, allowed only inside the ASR/PER worker) | G2P license, then PER validation on human-verified sung words (P4-5): `lyric-per`, `lyric-per-on-mac` | No lyric-error badge |
| MIDI synth and soundfont licenses | UNVERIFIED (some soundfonts restrict rendered audio) | `midi-synth-eval` (T-14) | No instrument rendering; NeutralVoice is the only guide |
| mir_eval, mido, pyloudnorm, librosa, FastAPI, uv, React, Vite, codegen tools, SQLite, keyring | Licenses not re-verified (§4.9, §8) | License-verification nodes closed or explicitly left open (P0-9): `foundation`, `license-verification` | Research-lane only in the register; not adopted beyond the ticket that verifies them |
| BS.1770-4 versus -5 for stereo integrated loudness | UNVERIFIED (X-47) | Diff ticket (P4-6): `loudness-standard-diff` | Every figure labelled "BS.1770-4 (pyloudnorm)" |
| librosa DTW adequacy for adherence | UNVERIFIED | NeutralVoice-under-bed golden within committed thresholds (TB5, P2-4): `adherence`, `separator-on-mac` | Adherence not shown on real candidates |
| SwiftF0 and Basic Pitch training-data provenance for LLC use | Permissive labels over training data that is NC (SwiftF0) or unchecked (Basic Pitch) | `training-data-provenance` | Both individual and research only; LLC transcription uses pYIN + HMM or manual entry |
| An LLC-clean separator (Kim Mel-Band-RoFormer training data) | UNVERIFIED (register row narrowed to individual and research) | Training-data check, then the allow-list (P6-3): `llc-separator` | LLC adherence "unmeasured"; LLC isolation refused |
| demucs-mlx speed and output on the M5 Pro | VENDOR figure from an M4 Max | Separator smoke on the Mac: `separator-on-mac` | Demucs on MPS as the fallback choice |
| Microphone and live-MIDI capture per OS | Unverified on every host | `first-real-pair` (the microphone check), `hum-benchmark-on-jon` (Jon's keyboard), `os-hosts` | Record replaced by "Check this microphone"; live MIDI labelled unverified |
| Backup Plus band size, random IOPS, Spotlight marker honoured | Band size and IOPS unmeasured; marker behaviour UNVERIFIED | P0-4 measurement; setup probe: `store-facts-and-mount-watch`, `studio-volume-on-backup-plus` | 8 MiB default not assumed optimal; `mdutil` printed as an owner action |
| RunPod pod rates, HTTPS proxy reachability and limits, live-rate API, in-container shutdown stopping billing, provider spend limit, private-registry pulls | UNVERIFIED (only serverless rates were verified) | One spike each, pass or fail (P3-3): `runpod-spikes` | No real burst; FakeBurstProvider only; in-image deadline treated as a second lock, not a guarantee |
| Network volume fee and region lock | UNVERIFIED | Ledger evidence across settled runs (§7.6): `budget-screen` | Weights downloaded per lease |
| YuE2 on a 16 GB card (A4); YuE2 under WSL2 on Jon's box; WSL2 localhost forwarding | OPEN / UNVERIFIED | Smoke on that card; P6 host conformance: `cuda-host` | 16 GB cards resolve YuE2 to burst |
| Metal ports of YuE2 or HeartMuLa (GAP-04) | No parity data | Metal-against-reference parity plus smoke: `worker-hosts` | Watch only; YuE2 stays on burst in tier 4 |
| Studio playback per OS; browser latency on the M5 Pro, Windows and Linux (X-49) | Only a 2021 MacBook Pro measured | Playback gate on the Mac (P5-1), then each OS (P6-2): `playback-gate-mac`, `os-hosts` | Studio "unverified" on that OS |
| waveform-playlist fit; Signalsmith Stretch quality | UNVERIFIED | Scored evaluation in P5, and Jon's blind verdict for stretching: `timeline`, `extend-dsp-edits`, `time-stretch-listening` | Own timeline; no speed changes |
| Lyric word alignment on singing (WhisperX evaluated on speech only) | UNVERIFIED | Alignment evaluation in P5: `lyric-alignment` | No line or word replace |
| Whisper and Qwen3-ASR accuracy on sung vocals | UNVERIFIED | PER validation (P4-5): `lyric-per-on-mac` | No lyric-error badge |
| HeartMuLa and MiniMax on consumer cards (VRAM, one or two GPUs, 32 or 44.1 kHz) | CONTESTED / UNVERIFIED | LLC smoke with license-chain checks (P6-3): `llc-smoke` | LLC pairs are ACE-only |
| Real diagnostic scorers (audiobox-aesthetics, LAION-CLAP) | Licenses and smoke pending | `diagnostic-scores` (named contract-fix PRs, then smoke) | Fake diagnostics in CI only |
| An MP3 encoder | No candidate in the register [I1 lists MP3] | Encoder license ticket: `codec-checks` | Export bundles carry WAV and MIDI only |
| CI minute rates on a private repo | UNVERIFIED; the repository is public for the build from 2026-11-07, so Jon can keep hosted CI free (OWNER-DECISIONS-2026-11-07.md) | Observed billing, reported in the release-readiness pass before the return to private: `final-qa` | Three-OS checks on every pull request while the repository is public |
| GAME and SheetSage2 on one-note, fixed-boundary, melisma and noisy separated-vocal hums | UNVERIFIED; their October fixes are code fixes, not accuracy evidence (GAME's released ONNX graphs predate both, so the trial runs its PyTorch path), and their weights are non-commercial | Research-lane trial with Jon's license acceptances: `transcription-trial` | Not installed; research projects only once they are |
| A compatible alternate ACE decoder (ScragVAE) improving fidelity | UNVERIFIED; the card's figures are VENDOR, it has no LICENSE file and names no training data | Rights review, then Jon's blind, level-matched verdicts on identical latents: `decoder-trial` | The official decoder only |
| Magenta RealTime 2 streaming in real time with low control latency on the M5 Pro | VENDOR only, for the C++ runner: the README lists no M5 Pro and says base needs a Pro Max chip, while the introduction says M3 Pro or higher | Smoke gate with latency checks measured on `mlx/m5pro`: `magenta-realtime-trial` | Not installed; no instrument control in the Studio |

### Interpretations to confirm

1. **MIDI export is v1-core.** The feature inventory files MIDI and tempo-map export under v1-studio [I5], but the
   architecture puts MIDI with its tempo map and section markers in every export bundle (TB4, P2-7). This spec follows the
   architecture; aligned stem and track export stays v1-studio [I4].
2. **Chord symbols for R1's `cot='full'`.** The design emits chord symbols in YuE2's ABC, but no SongSpec or MelodySpec
   field holds chords yet, and the smoke set has a "MIDI chord seed" brief. Default: the contract ticket adds an optional
   chord-symbol field to the SongForm sections (an additive minor version); the chord-symbols ticket gives it an editor and
   reads a MIDI file's chord track into it; R1 uses `cot='full'` when it is filled and `cot='melody'` otherwise [A9].
3. **The "not garbled" check is an owner verdict.** Smoke gates need Jon's listening check, and listening gates need owner
   verdicts, so this spec records it through the owner-ui verdict path and an automation token cannot supply it.
4. **Count-in and metronome during capture** are a small addition not named in the architecture. They play only to the
   output device, never into the capture, and the capture screen recommends headphones.
5. **LLM lyric help** [B6] is listed as optional v1-core in the inventory but has no design (no local model or provider
   decision). It is out of scope here; a later ticket could add it as a worker task with visible, reversible suggestions.
6. **Smoke briefs that need v1-studio operations** (one-word replace, chorus-only replace) are recorded as not yet runnable
   in P4 rather than passed or failed, and run once TB9's edit operations exist.
7. **The cross-machine CUDA worker** [J8] is v1-core in the inventory, but in tier 4 the approved burst carries the second
   engine; a tailnet worker host arrives in P6, or earlier the day one is reachable.
8. **The tracker workflow.** Resolved: `docs/agents/issue-tracker.md` now sends every ticket PR into `integration`, per
   O-01; `main` advances only by Jon's release merge.

### Domain language

This spec uses `GLOSSARY.md` as written. Terms it relies on that the glossary does not yet define, offered as input for
`/domain-modeling`: **owner-ui scope** and **automation token** (ADR-0031), **challenge nonce**, **StudioHarness**,
**FakeEngine** and **FakeBurstProvider**, **mutant worker**, **declined route**, **egress list**, **figure label** (already
defined) applied to the registry's two columns, and **next useful action**. Group 21 (2026-11-07) adds **security
advisory** (a published vulnerability with its package, vulnerable range and patched version), **decoder** and **latents**
(an engine's VAE and the representation it decodes), and **control latency** (from a MIDI change to the changed audio).

Contact for the project, as text only: `hello@islanddevcrew.com`.
