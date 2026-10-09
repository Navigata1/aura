# AURA

The language of AURA (a working name): Jon's personal, local-first music studio. A melody he hums, sings or plays
becomes an editable melody he owns, then two candidate songs he judges blind, then a keeper he finishes and exports
with full provenance, all on open-weight engines he controls. Use these terms in code, tests, tickets and copy. Where a
term lists words to _Avoid_, do not use them for that concept.

## Language

### Melody and song intent

**Project**:
One song and everything made for it: its captures, melody and song revisions, generation requests, candidates, keepers
and exports, all under one operator lane. Narration projects are reserved for later.
_Avoid_: Session (a session is a sitting of work), song file, workspace, track

**Melody seed**:
The melody Jon starts a song from: a hum, a MIDI file or a live MIDI performance. Every melody seed becomes a
MelodySpec before anything is rendered from it.
_Avoid_: Prompt, idea, demo, input

**Hum**:
A melody seed hummed or sung into a microphone, with or without words. AURA uses one word for both, because both take
the same path.
_Avoid_: Voice memo (one way a hum can arrive), vocal, take, guide vocal

**Capture**:
A human performance taken into a project: a hum as recorded audio, or MIDI as played or imported. A capture is kept
exactly as received and never edited, and everything else derives from it.
_Avoid_: Take, upload, input, raw audio

**Transcription**:
The automatic first guess at a hum's notes, each note carrying a confidence. It becomes the first MelodySpec revision
and is always offered for correction, because no transcriber is trusted on hums.
_Avoid_: MIDI conversion, pitch detection (one step of it), auto-score

**MelodySpec**:
The owned, editable melody of a song: notes with pitch, timing, confidence and origin, plus its tempo map, meter, key
and phrases. Every change makes a new revision. MIDI, the guide and the score a route sends are renderings of it, not
the melody itself.
_Avoid_: MIDI, score, melody file, transcription

**Correction**:
One edit Jon makes to a MelodySpec: move, resize, transpose, split, merge, add, delete, quantize, set tempo, meter or
key, or mark a phrase. Corrections are logged with their time, and the log measures correction effort.
_Avoid_: Fix, cleanup, tweak

**Phrase**:
A marked span of the MelodySpec that the SongForm can place, repeat or leave out.
_Avoid_: Section (a section belongs to the SongForm), lick, loop, bar range

**SongSpec**:
What Jon asks for in a song: approved lyrics and their language, style and exclusions, vocal mode, SongForm,
references, target duration and candidate count. Each field records what was requested, what the engine profile
supports and what was observed.
_Avoid_: Prompt, brief (a brief is an evaluation case), settings, song config

**SongForm**:
The song's structure inside the SongSpec: an ordered list of sections, each vocal or instrumental, built from phrases
with bars and repeats.
_Avoid_: Arrangement, structure, layout

**Section**:
One named part of the SongForm, such as verse, chorus, bridge or intro. Section names survive every step, from the
SongSpec to the timeline to the export.
_Avoid_: Part (a part is one instrument or voice), segment, block

**Assembled melody**:
The full-length melody of the song: the MelodySpec's phrases laid out along the SongForm, with repeats and
instrumental bars. Routes and the guide render from it.
_Avoid_: Full MIDI, song melody, timeline

**Approved lyrics**:
The words Jon wrote or accepted for the song, in a declared language. They are kept apart from any transcript or
alignment of a rendered vocal, and speech recognition never overwrites them.
_Avoid_: Lyrics transcript, recognized lyrics, text

**Reference**:
Audio Jon attaches to a song or to an evaluation, with a permission record that says how it may be used. A
listening-only reference is never engine input.
_Avoid_: Sample, inspiration track, seed

**Guide**:
A plain sung rendering of the assembled melody by NeutralVoice. It is for hearing the tune and is the input to route
R2-synth. A guide is never a candidate.
_Avoid_: Demo, preview (a preview is an audition copy), scratch vocal, MIDI render

**NeutralVoice**:
AURA's own deterministic, license-clean guide voice. Because AURA owns it, it can also sing melodies whose true notes
are known, which is how transcription and adherence are checked.
_Avoid_: Synth (alone), TTS, vocaloid, fake singer

### Generation and engines

**Engine**:
A family of open-weight music models that AURA runs on hardware Jon controls, such as ACE-Step 1.5, YuE2 or HeartMuLa.
Requests never name an engine. They name engine profiles.
_Avoid_: Model (for the family), AI, provider, backend

**Engine profile**:
One runnable configuration of an engine: a checkpoint, the tasks it performs, its limits (duration, lyric languages,
channels), its backend and host operating system, and the operator lanes its components allow. Published claims and
AURA's own results are kept in separate fields.
_Avoid_: Model, preset, engine (when one checkpoint is meant), mode

**Profile revision**:
The exact identity of an engine profile as installed: code, weights, environment and worker SDK together. Changing any
pin makes a new revision, and its status starts again.
_Avoid_: Version (alone), build, release

**Profile status**:
The registry's verdict on a profile revision on one host class: declared, installed, smoke-passed, benchmarked or
disabled. It is computed from evidence records and never set by hand. Only smoke-passed or better reaches the product.
_Avoid_: Enabled, supported, beta, ready

**Task**:
What a profile is asked to do: text to song, cover, score to song, repaint, extend, extract, lego, complete,
instrumental or reference timbre. A profile refuses an undeclared task, a forbidden lane or an over-limit request before
it loads anything.
_Avoid_: Mode, feature, operation (for edits), primitive (a research word)

**Route**:
A named way of making a sung song from a melody: **R1** (YuE2 renders from a score of the MelodySpec), **R2-raw** (ACE
covers the hum itself), **R2-synth** (ACE covers the guide) or **text** (no melody seed). Every candidate records its
route.
_Avoid_: Render route, pipeline, path, strategy

**Generation request**:
One request to render a SongSpec revision into candidates. It holds the plan (routes, profiles and seeds, each with a
reason), the routes declined and why, the jobs, and any quotes.
_Avoid_: Generation (alone), prompt, run, job

**Job**:
One durable unit of work, such as transcribe, guide, generate, measure, separate or export. A job reports only real
steps, ends ready, failed or cancelled, and never shows a partial result.
_Avoid_: Task (what a profile is asked to do), process, run, render

**Worker**:
A separate process that runs engine profiles or analysis for AURA, and refuses work it cannot do before loading
anything.
_Avoid_: Server, node, engine, backend

**Intent and actual**:
The pair recorded for every generation: the creative intent Jon set, and the parameters the profile actually used.
Controls appear only where a profile implements them, so intent never silently becomes something else.
_Avoid_: Settings, knobs, params (alone)

**Reference timbre**:
A global style and timbre hint taken from a reference clip, labelled as such. It is not voice cloning.
_Avoid_: Voice clone, my voice, persona

**Narration service**:
The separate, later product, starting with Sabbath Echo, that turns approved text into spoken audio. It shares AURA's
artifact, provenance, job and storage contracts and has its own spec.
_Avoid_: Narration lane (lane means operator lane), TTS mode, voice-over

### Candidates and listening

**Candidate**:
One rendered result offered for audition, from a generation request or an edit. It records its route, profile revision
and seed. A request yields two candidates, and a candidate is never hidden, only badged.
_Avoid_: Take, version, variant, generation, output, song (before it is kept)

**Hard constraint**:
An objective check every candidate faces, computed before the audition and shown after the reveal (only "unplayable"
shows before it): it decodes, is not silent, fits its duration, has no clipping or true-peak overs, keeps an acceptable
lyric error rate, and keeps the melody when it was seeded. Thresholds come from gate records fixed before any evidence.
A failure becomes a badge, never a deletion.
_Avoid_: Quality gate, filter (alone), scorer

**Badge**:
A plain label on a candidate from a hard constraint or a measurement, such as "melody not kept", "adherence
unmeasured" or "Synthetic test output". Badges never rank or hide a candidate. During a blind audition only
"unplayable" shows.
_Avoid_: Score, rating, warning, flag

**Melody adherence**:
How closely a candidate's sung vocal follows the MelodySpec, as median cents error, octave-error rate, onset F1 and
contour correlation. It reads "unmeasured" when the project's lane has no eligible separator.
_Avoid_: Melody accuracy, similarity, pitch score

**Diagnostic score**:
An automatic aesthetic or text-to-audio agreement score, shown for information only. It never selects, ranks or
filters a candidate.
_Avoid_: Quality score, rating, reward, reranker

**Audition**:
A blind, level-matched A/B of two or more ready candidates under random labels. It ends in Jon's verdict and a reveal,
and it is AURA's acceptance gate.
_Avoid_: Listening test, listening session, comparison, A/B (alone), poll, review

**Blind label**:
The random letter an audition shows for each candidate. Labels are drawn when the audition opens, and only a sealed
commitment to them is visible until the reveal.
_Avoid_: Slot, position, option A/B (as identities)

**Level matching**:
Lowering every louder audition arm to the quietest arm's integrated loudness, never raising any, so that loudness cannot
decide a preference. The remaining mismatch is at most 0.1 LU.
_Avoid_: Normalization, volume match, gain staging

**Preview**:
The common-rate (48 kHz, 24-bit) copy of a candidate, made only for audition. The candidate itself keeps its native
rate.
_Avoid_: Proxy, bounce, MP3, render

**Verdict**:
Jon's immutable judgment of one audition: A, B, tie or neither, with optional axes, problem intervals and seconds listened
per label. "Neither" re-rolls new candidates. Everyday verdicts show per route ("kept n of m") but never change a
profile's status.
_Avoid_: Vote, rating, preference (alone), score

**Reveal**:
Disclosing, after the verdict, which candidate each blind label was, checked against the commitment made when the
audition opened.
_Avoid_: Unblind, unmask

**Keeper**:
The candidate Jon keeps from an audition: the song's version of record, which he can edit, finish and export.
_Avoid_: Winner, final, master, favourite, selected take

### Artifacts and provenance

**Artifact**:
Any stored audio, MIDI or analysis result, named by the hash of its bytes, never changed once written, and carrying
complete provenance.
_Avoid_: File, output, media, asset (an asset is bytes on their way to a worker)

**Origin**:
How an artifact came to exist: generated mix, separated source, regenerated part, new part, human recording, rendered
guide, rendered MIDI, TTS render, conversion, imported mix, analysis or preview.
_Avoid_: Type, kind, source (alone)

**Provenance**:
Everything needed to say how an artifact came to be: the producing job, profile revision, weights, code, seed, intent
and actual parameters, host, compute profile, timings, operator lane, eligible lanes, license chain and parents. An
artifact without complete provenance is not stored.
_Avoid_: Metadata, history, tags

**Parent edge**:
A typed link from an artifact to one it was made from: **derived from** (its audio came from that audio), **converted
from** (the same audio at another rate or in another format) or **analyzed by** (a measurement read it). Only derived
from and converted from carry lane and license obligations.
_Avoid_: Dependency, link, lineage (lineage is the chain of edges)

**Closure**:
An artifact together with every ancestor reachable through derived-from and converted-from edges. Exports, license
chains and backups are worked out over closures.
_Avoid_: Tree, ancestry, bundle

**License chain**:
The licenses and obligations of every component in an artifact's closure. It is carried into the ExportManifest.
_Avoid_: License (alone), terms, attributions

**Revision**:
One immutable state of a MelodySpec, a SongSpec, a keeper or a timeline. Editing makes a new revision on top of a named
base, and an edit made against an out-of-date base is refused. A melody revision drafted by a transcriber carries that
transcriber's eligible lanes, and every revision built on it inherits them.
_Avoid_: Version, save, draft

**Imported mix**:
A finished song brought in from outside AURA, such as Jon's own Suno download or a mix from his own DAW, carrying its
source service and the terms Jon attested (an owner act). Its allowed uses follow its source, and a DAW mix that contains
AURA exports inherits their eligible lanes. A Suno import may be listened to, measured and DSP-finished, and nothing more
unless a risk acceptance adds engine, conditioning, separation, edit or conversion input.
_Avoid_: Upload, external song, reference

**Export bundle**:
The verified files Jon takes from a keeper: the mix at its native rate, a 48 kHz, 24-bit deliverable when the native
rate differs, MIDI, the specs and the ExportManifest. Every file is decoded and hashed again before the bundle is
offered.
_Avoid_: Download, bounce, package, render

**ExportManifest**:
The self-describing record inside an export bundle: files with hashes, roles and rates; human contributions; the model
and license chain; operator lane and eligible lanes; the AI-disclosure flag and its reasons; the converted-vocal flag;
imported-source terms; and a loudness report naming its standard and meter.
_Avoid_: Metadata, credits, receipt, sidecar

**Human contribution**:
What Jon made himself in a song: melody, lyrics, corrections, choices and edits. It is recorded in the manifest because
authorship and disclosure depend on it.
_Avoid_: Credits, authorship (alone), input

### Studio and timeline

**Studio**:
The timeline workspace for arranging, editing and finishing a keeper. It is not a full DAW, and aligned stem export
exists so that a DAW can take over.
_Avoid_: DAW, editor, mixer

**Timeline**:
The Studio's time axis: tracks of clips placed in project time, artifacts referenced at their native rate, MIDI in
musical time, section markers and the tempo map.
_Avoid_: Arrangement, sequence, playlist

**Track**:
One line of the timeline holding clips of one part. A replacement part sits on its own track until it is copied to the
main track, which rebuilds the mix.
_Avoid_: Lane (lane means operator lane), take lane, version lane, channel, stem

**Clip**:
A placed time range of an artifact or of MIDI on a track, with gain and fades. A clip refers to audio and holds none of
its own.
_Avoid_: Region, item, segment

**Tempo map**:
The song's tempo and meter over time, shared by the MelodySpec and the timeline. It converts musical time to sample
time by one rounding rule, and every change makes a new revision.
_Avoid_: BPM (alone), grid, click

**Edit operation**:
A scoped generative change to a keeper, such as replacing a section, a line or a word, or extending the song, defined
by a mask, crossfades and locked context. It stays a proposal until Jon accepts one of its candidates, and undo
restores the previous artifact without regenerating.
_Avoid_: Regen, redo, remix, edit (alone)

**Preservation check**:
The test every accepted edit must pass: AURA composites each candidate (the original outside the mask and crossfades,
the engine's output inside), and the composite's audio outside the mask and crossfades is identical, sample for sample,
to what it was before. A whole-song re-render is never called a local edit.
_Avoid_: Diff, quality check, null test

**Offline render**:
The deterministic render of a timeline or keeper to files for export, separate from live playback. An export never
depends on what the browser played.
_Avoid_: Bounce, real-time export, mixdown

**Playback gate**:
The proof, for each operating system, that Studio playback holds up: 8 tracks for 30 minutes with no underruns, and a
responsive UI (p95 under 100 ms over a versioned scripted interaction set) while a generation runs. The Studio is ready on an operating system only after that
system passes.
_Avoid_: Performance test, "works on Windows"

**DSP finishing**:
Deterministic, non-generative mixing, mastering and format (O-08): gain, fades, EQ, loudness to an explicit target,
trimming, and format or rate conversion, on one mix or a set of Jon's own stems. It is the only processing an imported
Suno mix may receive.
_Avoid_: Mastering (a later, optional stage), remaster, enhancement

### Stems

**Part**:
One instrument or voice in a song, whatever audio currently holds it.
_Avoid_: Section, stem (a stem is audio of a part), layer

**Stem**:
One part of a song (a vocal, drums, bass or a single instrument) as its own audio, aligned with the mix from zero.
Every stem is made by one of three operations and says which.
_Avoid_: Track (a track is a line of the timeline), layer, channel

**Isolate original**:
Splitting a mix into stems with a separator while keeping the residual, so that the stems plus the residual rebuild
the mix. Nothing is performed anew.
_Avoid_: Extract (ACE's extract is generative), split, unmix, demix

**Residual**:
What a separation leaves over: the mix minus its stems. It is always kept and can always be heard.
_Avoid_: Remainder, bleed, "other" (a separator's instrument class)

**Re-perform**:
Generating a new performance of an existing part, guided by its stem. The result is always labelled a new performance
and judged on notes, onsets and timbre, not on residual. ACE's "extract" task is a re-perform.
_Avoid_: Extract, isolate, clean up, regenerate stem

**Create a new part**:
Generating a part the song did not have, fitted to the existing mix.
_Avoid_: Add stem, layer, overdub

**Rebuild**:
Making the mix again from retained sources after a part changes. Replacing a part always rebuilds the mix. It never
lays the new part over a mix that still holds the old one.
_Avoid_: Overlay, layer, replace in place

**Internal separation**:
A vocal separation AURA runs only to measure adherence and lyric errors. It is analysis: it is never exported as a
stem, and its lane never passes to the keeper it measured.
_Avoid_: Stems, isolate original

### Compute and storage

**Compute tier**:
One of the four kinds of hardware AURA plans for: **1** NVIDIA 24–32 GB (4090/5090 class), **2** NVIDIA 24 GB (3090
class), **3** NVIDIA 12–24 GB class with offload or burst (O-02 names 12–16 GB; the recommendation places 11.5–23.5 GiB
cards here, with a warning above 16 GB, pending Jon's confirmation), **4** Apple Silicon plus a rented CUDA burst. Every
NVIDIA tier needs compute capability 8.0 or higher; a host without a qualifying GPU is burst only. AURA recommends one
from detected hardware, and Jon may choose any.
_Avoid_: Level, plan, mode, hardware class

**Compute profile**:
The tier preset in force, and where each engine profile runs under it: locally (`local`), on a worker host
(`worker_host`) or as a burst (`burst`). It is
chosen at install and at the start of every session, and can be switched at any time without changing any project.
_Avoid_: Config, setup, hardware profile, engine profile

**Session**:
One sitting of work with AURA, pinned to the compute profile chosen at its start. A switch during a session is logged,
and work not yet started is re-planned.
_Avoid_: Project, login, workspace, audition

**Studio host**:
The one machine that runs the browser UI, AURA's control service and the project store in a session: the Mac in tier
4.
_Avoid_: Server, main machine, master

**Worker host**:
A machine that only runs workers for the studio host, such as a Linux or WSL2 CUDA box on the tailnet. It is admitted
for each profile only after its own conformance and smoke evidence.
_Avoid_: Node, slave, GPU server

**Host class**:
The kind of machine evidence was gathered on, such as MLX on an M5 Pro or CUDA on a 4090. A status earned on one host
class says nothing about another.
_Avoid_: Platform, device, machine (alone)

**Burst**:
Rented GPU time, used when a profile has no home in the session's compute profile, such as YuE2 in tier 4. Every burst
is a paid run that needs Jon's approval.
_Avoid_: Cloud, serverless, offload, rental (alone)

**Burst run**:
One paid lease of rented GPU time for one generation request's burst jobs, from reservation to settlement.
_Avoid_: Rental, pod, instance

**Quote**:
The priced, hashed offer for a burst run: provider, GPU class, the live rate and when it was read, the job list, the
ceiling, the month-to-date spend, and exactly which assets would leave the studio host.
_Avoid_: Estimate, price, bill

**Ceiling**:
The most a burst run may cost: its maximum minutes at the highest rate in its GPU-class list, plus fixed lines. It is
reserved before anything starts, and a run with no billing data settles at it.
_Avoid_: Estimate, max, budget (the cap is monthly)

**Approval**:
Jon's single-use yes to one quote, given in the Studio UI, bound to that quote and expiring 15 minutes after it. Any
change to the job list needs a new quote and a new approval.
_Avoid_: Consent (alone), confirmation, OK, authorization

**Reservation**:
The ledger entry that holds a burst run's ceiling against the monthly cap. It is written before anything is
provisioned.
_Avoid_: Hold, pre-authorization, charge

**Monthly cap**:
The standing limit of $25 a month on rented GPU spend, counting settled runs, open reservations at their ceilings and
fixed lines. A quote that would exceed it is refused, and only Jon can raise it.
_Avoid_: Budget (alone), allowance, credits, limit

**Ledger**:
The append-only record of every reservation, settlement, release, overrun and fixed line against the monthly cap.
_Avoid_: Billing, wallet, account

**Settlement**:
Closing a burst run's cost from the provider's billing, or at the ceiling when billing is missing. Any cost above the
reservation is an overrun, which blocks new burst runs until Jon acknowledges it.
_Avoid_: Charge, invoice, payment

**Store**:
The content-addressed project store: every artifact, every immutable record and the metadata database, on one volume. Its
documented layout can be read without AURA's code.
_Avoid_: Library, database, drive, cloud

**Studio volume**:
The APFS sparse bundle on the external Backup Plus drive, mounted as STUDIO. It holds the store, model weights, engine
environments, caches and worktrees.
_Avoid_: Backup Plus (the physical drive that hosts it), external drive, disk image

**Disk preflight**:
The check that refuses any download, install, job or export that would leave less than the safety margin free on a
volume it writes to. The refusal names the volume, its free space, the amount needed and the margin.
_Avoid_: Space check, quota

**Retention class**:
How precious an artifact or record is: **irreplaceable** (captures and imported mixes, imported MIDI, specs and
corrections, verdicts, keepers and their closures, references, risk acceptances, license acceptances, evidence, export
manifests, the latest database snapshot), **derived** (other candidates and analyses) or **reproducible** (weights,
environments, caches, previews, scratch, export renders). Only irreplaceable data is always mirrored to a second device.
_Avoid_: Priority, importance, tier

### Lanes and licensing

**Operator lane**:
Who a project's work is done for, which decides what may touch it: **individual** (Jon personally, the default),
**llc** (Island Development Crew ventures, Sabbath Echo included) or **research** (private experiments, never
released). It is set per project, and changing it is an owner act. "Lane" alone always means operator lane.
_Avoid_: License mode, entity, account, workspace

**Eligible lanes**:
The operator lanes an artifact may enter: the lanes that every component in its license chain allows, intersected with
the eligible lanes of its derived-from and converted-from parents and, for an import, with the lanes its attested terms
allow. A transcribed melody revision has eligible lanes too.
_Avoid_: Allowed lanes (a component's), license status

**Component**:
One third-party piece AURA might use (code, weights, a dataset, a scorer or a service), with its own code, weights and
output terms, obligations and allowed lanes.
_Avoid_: Dependency, library, package, model

**Component register**:
The list of every component with its terms, obligations, allowed lanes, redistribution status and verification status,
generated from the evidence register.
_Avoid_: License list, SBOM, allowlist

**Allowed uses**:
What an input may be used for, such as listening, loudness measurement, DSP finishing, engine input or conditioning.
It is checked before any job runs.
_Avoid_: Permissions, rights (alone), usage

**Process boundary**:
The rule that copyleft or non-commercial code and weights run only inside a separate worker process, never in the
control service or the web bundle.
_Avoid_: Sandbox, plugin, isolation

**Release blocker**:
A component whose terms stop its code or its outputs from being shipped or released as they are: non-commercial or
academic weights, unknown or contested licenses, unchecked training data, an unverified license, or copyleft that would
bind AURA's code. An export lists the release blockers in its closure, and it is release-clear only in a releasable lane
with every blocker covered by an explicit permission (such as YuE2's individual-creator permission, in the individual
lane).
_Avoid_: Risk, warning, red flag

**Risk acceptance**:
Jon's signed record accepting one named risk, such as one further use of a Suno import. It is the only thing that can
widen an input's allowed uses, and only to engine, conditioning, separation, edit or conversion input: never an audition
arm, an evaluation reference or anchor, a reference, training or test material.
_Avoid_: Waiver, override, consent

**Suno boundary**:
The rules for Suno output in AURA. Jon's own permitted downloads (Pro or Premier) may be imported for listening,
loudness measurement and DSP finishing only. They are never audition arms, evaluation references or anchors, references,
training data or test material, whatever is signed; they are never engine or conditioning input or input to ML
separation unless a risk acceptance names that one use.
_Avoid_: Suno integration, Suno import (alone)

**Voice registry**:
The v2 private list of singing voices AURA may convert to. Each voice has a sung sample, a spoken random phrase checked
for the same speaker and the right words, a rights confirmation, a consent time and its permitted uses. v1 has no voice
registry.
_Avoid_: Voice clone, persona, voice library

### Evaluation

**Quality target**:
"Suno v6-class", measured only by Jon's blind, level-matched auditions of AURA keepers against his reference standards
on preregistered briefs, with thresholds fixed at preregistration. No vendor figure, leaderboard or Suno output counts
toward it.
_Avoid_: Suno parity, "as good as Suno", Suno 6.5 (it does not exist)

**Reference standard**:
A human-made song that Jon owns or has licensed, one for each feel (worship or acoustic ballad, cinematic or
orchestral, R&B, soul or pop ballad, and a broad mix), that sets the bar AURA is judged against. It is listening-only,
with a permission record. In an evaluation audition it is an anchor, acknowledged as recognizable.
_Avoid_: Reference track, target song, Suno reference, benchmark

**Brief**:
One evaluation case: a SongSpec with its seed (a hum, MIDI or lyrics) in a named feel category and operator lane, run
the same way for every route and profile being compared.
_Avoid_: Prompt, test case, scenario

**Smoke set**:
The 12 preregistered briefs, hummed and MIDI seeds included, that every route and engine profile faces first.
_Avoid_: Smoke test (that is one run), sanity set, quick test

**Benchmark set**:
The 48 preregistered briefs, 6 in each of 8 categories. Only a preregistered benchmark gate can make a profile
benchmarked: this set for engine profiles, the hum benchmark for transcribers. Completing it is post-v1.
_Avoid_: Eval set, test set, full suite

**Preregistration**:
The hashed, committed plan of an evaluation (briefs, asset hashes, pins, budgets, listening quotas and thresholds),
made before anything is rendered for it. Results without one promote nothing.
_Avoid_: Plan, config, protocol (alone)

**Gate**:
The pass rule a profile or capability must meet on evidence records before its status may rise: a smoke gate or a
benchmark gate. Every gate names its owner (Jon by default), and the preferred choice is allowed to fail it.
_Avoid_: Threshold, bar, target, owner gate (see owner act)

**Capability**:
A non-engine function, such as Studio playback or microphone capture, gated per operating system by evidence in the
same way as engine profiles.
_Avoid_: Feature, support, compatibility

**Evidence record**:
The stored result of a check that could have failed, such as an install, a conformance run, a smoke render, a
benchmark, a playback test, a throughput test or a preregistered audition, with its measurements labelled MEASURED-LOCAL
and its attachments hashed. A smoke record lists every check its gate declares, and a listening check names the owner
verdict that answered it. It is the only thing that changes a status or passes a gate. The store is the system of
record; docs/evidence holds hash-checked exports.
_Avoid_: Result, log, report, proof

**Synthetic evidence**:
Evidence from AURA's own generated material, such as NeutralVoice hums and fake engines. It can fail anything and can
meet a smoke gate only where that gate allows it, never a benchmark gate. Its outputs are always labelled "Synthetic
test output".
_Avoid_: Test data, mock result

**Figure label**:
The tag on every number AURA reports, saying where it came from: MEASURED-LOCAL (measured by AURA on Jon's hardware),
VENDOR, COMMUNITY, COMPETITOR-RUN, OWNER-REPORTED, INFERRED, or UNVERIFIED where no check has been made. A vendor
number is never shown as measured.
_Avoid_: Source, confidence, accuracy

**Keeper cost**:
What one keeper took: candidates rendered (re-rolls included), compute cost, cold and warm time, and listening time.
Cost is reported per keeper, never per candidate.
_Avoid_: Cost per song, efficiency, yield

**Owner act**:
An action only Jon can take, in person in the Studio UI: approving a quote, changing the cap, acknowledging an overrun
or a reconciliation adjustment, changing a project's lane, giving a verdict, accepting a risk or a model license,
recording a reference permission, or attesting an import. Scripts and agents can prepare an
owner act but never perform one.
_Avoid_: Owner gate (a gate is a pass rule), admin action, sign-off

**Scope**:
Which release a feature belongs to: **v1-core** (melody to exported song, with honest provenance and evaluation),
**v1-studio** (editing and studio work once the core gates pass), **v2**, **research** or **out-of-scope**.
_Avoid_: Tier (a tier is a compute tier), phase (a phase is a build stage), milestone
