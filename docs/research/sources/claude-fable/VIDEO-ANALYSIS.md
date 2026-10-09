# Suno Teardown — Flagship Report

**Source:** "Suno AI Tutorial For Beginners (2026) – Everything You NEED to KNOW!" — Simon Crowe, YouTube, uploaded 2026-08-25, 20:19, ~35k views. https://youtu.be/MI6vwl_ZHN8
**Method:** two channels — YouTube auto-captions (`reference/transcript.txt`, 474 timestamped lines, 3,292 words) and 150 informative frames sampled across the full runtime with near-duplicate frames dropped (`reference/sheet_1..6.jpg`, 25 per sheet, numbered #001–#150). Every claim below is cited to a transcript timestamp `[mm:ss]` or a frame `#NNN`. Auto-captions render "Suno" as "Sunno" and "electro-pop" as "electroop"; UI labels are taken from frames, never from audio. Frames are a sample: a one-second flash of UI could be missed.
**Purpose:** ground truth for building a personal, single-user Suno-style app (see `SPEC.md`).

---

## 1. Thesis

Suno in late 2026 is three products wearing one nav: (a) a **prompt-to-song generator** with a Simple and an Advanced form, (b) a **voice layer** that clones the user's own voice and applies it via "Cover", and (c) **Studio**, a browser DAW built around stems, per-stem AI regeneration, and audio-to-audio ("hum → instrument"). The tutorial's arc is literally that order: generate [01:29–07:39] → your voice [07:39–11:31] → Studio/stems [11:31–18:50] → export [18:50–19:43].

## 2. Section-by-section (spine from transcript, detail from frames)

### 2.1 Onboarding & shell — [00:34–01:29], #006–#012
- Sign-up modal "Ready to make music?" with Continue with Google / Apple / Phone (#006); birthday, username, display name [00:45]; onboarding survey "Which describes you best?" — Content creator, Total beginner, Creative pro, Pro musician or producer, Hobbyist, Songwriter or lyricist (#007). Narrator: skippable, "won't affect anything" [00:52].
- Left nav (consistent across every screen): **Home, Explore, Create, Studio, Library**, then user, **Earn Credits, Labs** (#017), and **Hooks** appears in later frames (#046). Bottom: persistent player bar with shuffle / prev / play / next / repeat, volume, queue (#017, #046).
- Explore: grid of community songs + "Made in Suno Studio" row + "Best Of" (#009–#011); any song can be opened and remixed [01:18].

### 2.2 Simple mode — [01:29–03:25], #013–#025
- Home hero: "Hear your vision like never before", a single text box "Describe the song you want to make", a **dice button** that fills a random concept, and a pink **Create** button (#013–#016). Dice examples captured: "Live country rock song about a BBQ with friends" (#014), "Melodic bailable song about missed calls" (#015).
- One click yields **four results**: 2× v4.5 (free model) and 2× v5.5 (paid), titled e.g. "Missed call loop (V.1)/(V.2)" and "Missed call dancin'" (#021–#024); the free-plan results carry an "Upgrade for full song" chip (#018, #023).
- Narrator's judgment: v5.5 "just sounds like a proper song… vocals more natural, everything fuller" [03:15–03:22].

### 2.3 Pricing (shown, barely said) — [03:37–04:21], #028–#032
Frame #028 is the only place the full plan matrix is legible:

| Plan | Price | Credits | Notable |
|---|---|---|---|
| Free | $0 | 50/day (~10 songs) | v4.5-all, no downloads, no commercial use, upload ≤8 min audio, shared queue |
| Pro | $10/mo ($8 annual) | 2,500/mo (~500 songs) | v5.5, 20 downloads/mo (from 9/3/26), commercial rights, personas + advanced editing, stems [04:01] |
| Premier | $30/mo | 10,000/mo (~2,000 songs) | Studio access, 60 downloads/mo |

A normal generation costs ~5 credits [04:08]. **For a personal clone, none of this exists** — no credits, no plans, no download caps.

### 2.4 Advanced mode — [04:21–07:39], #033–#057
Full control surface, legible in #017 and #046 (`reference/create-panel-and-more-options.jpg`):
- Tabs: **Simple | Advanced | Sounds** (#046); model dropdown **v4.5-all / v5.5** (#017/#046).
- Attach row: **+ Audio, + Voice, + Inspo** (#017).
- **Song Description** textarea with an enhance/edit icon; **+ Lyrics** button; **Instrumental** toggle; **Suggestions** tag chips (eurovision, chillsynth, emocore, sweet voice, russian ch…) (#017).
- **More Options** (#046): Lyrics = **Write | Prompt | Instrumental**; **Exclude styles**; **Vocal Gender** Male/Female; **Weirdness** slider (default 50%); **Style Influence** slider (50%); **Duration** Custom | Auto. Narrator sets Prompt + Male and leaves the rest at defaults [05:56–06:12].
- Sample prompts on screen (#036–#038): "Upbeat indie-pop song about moving to New York." / "Dark cinematic instrumental with piano, strings and a slow dramatic build." / "Funny 80s rock anthem about a guy who takes his fantasy football team way too seriously."
- Narrator's real prompt, visible in full in #042–#044 (Lyrics pane): *"A high-energy modern electro-pop and dance-pop anthem called 'The Algorithm Hates Me' about a YouTuber getting almost no views but refusing to quit. Funny, self-deprecating verses about refreshing analytics, talking to an empty comment section and blaming the thumbnail. Build through a rising pre-chorus into a huge festival-style singalong chorus with layered gang vocals chanting 'The algorithm hates me'. Energetic male lead vocals, punchy electronic drums, driving bass, bright synths, rhythmic guitars, dramatic builds, an explosive final chorus and polished chart-ready production."*
- Every generation returns **two versions** of the same prompt + lyrics [06:34]; results appear in the right-hand **Workspaces › My Workspace** list with Filters / Newest / List view, thumbnail, title, model chip, like/dislike/share (#046).
- Session credit counter: "50 credits used this session · You're on a roll" (#046); onboarding quest widget "Unlock Your Sound 4 of 6 completed" with a countdown (#046).

### 2.5 Voice cloning — [07:39–11:31], #058–#086
- Entry: Create → **Voice → Create voice** [07:59]. Modal **"Create a Voice" (Beta)**: "Add your voice to the mix. Record or upload a sample and we'll use this content to influence how your generated songs sound." Buttons **Record / Upload Audio / Select from library**; tips: "Sing in the style and language you want", "A good microphone helps — your built-in mic works just fine", "Record at least 10 seconds" (#060).
- Recording flow: "Record your Voice — Sing something in your natural voice" with a big red button (#061–#065); live waveform with Restart / Pause / Done (#066–#067); **Trim your recording** with a pink selection region and **Start over / Use Voice** (#068–#069).
- **Verification**: "One more piece of content we need — read this out loud: 'Sing a gentle melody to calm the busy listening crowd'" (#070) [09:22–09:28]. This is a liveness/consent gate; the clone should keep an equivalent.
- **Voice details**: name ("My Voice – Aug 20"), style tags, description, avatar upload or "Prompt Suno to create an image", Save (#071–#072). Narrator names his "Simon" [09:33].
- Guidance from narrator: 15 s–4 min accepted, ~2 min is the sweet spot, quiet room, some range and energy, phone mic is fine [08:10–08:44].
- Applying it: Library → ⋯ → **Remix → Cover** (#076 shows the full context menu: Remix, Edit, Publish, Share, Download, Manage, Add to Queue, Add to Playlist, Move to Trash) → in the Create panel the source song appears as an **Audio** attachment with a **Cover** mode pill, and the voice "Simon" appears as a chip (#077–#080, #085). Cover keeps the song; regenerate would produce a different song [10:20–10:31]. Result is titled "The algorithm hates me (cover)" (#083–#084).

### 2.6 Song Editor → Studio — [11:31–14:13], #087–#105
- Library ⋯ → **Edit → Open in editor** [11:47]. The second-level menu in #088 lists: Extend, Crop, Remove Section, Reverse, Adjust Speed, Fade In, Fade Out, Replace Section, Remaster, Open in Studio, Open in Editor.
- **Song Editor (Beta)** (#089–#091, `reference/create-voice-and-song-editor.jpg`): header actions Legacy Editor, Reset All, undo/redo, My Workspace, **Save as New Song, Get Stems, Edit in Studio**; left pane **Edit | My Edits** with the lyrics; main pane a **section-labelled, colour-coded timeline** (VERSE, PRE, CHORUS, VERSE 2, BRIDGE, CHO…) with a FADE handle; transport shows **133** BPM. Narrator's reason to go via Editor rather than straight to Studio: it segments the song into sections [11:54–12:11].
- **Suno Studio** (#092, `reference/pricing-and-studio.jpg`): top bar SUNO Studio / Learn / Layout / credits; project header with song name, undo/redo, **Export**; **Clip | Track** inspector toggle. Track lane with S/M, "No Input" source, and the colour-coded section clips. Right inspector for a selected clip: **Remix**, like/dislike, **Clip Settings** (Tempo: On Beat; Transpose ±; Speed ½ / ×2; Clip Volume dB), **Stems → Extract**, Version 1 carousel, Styles ("electro-pop, dance-pop"). Bottom prompt bar: **Song ▾ | Styles | Lyrics | Replace ▾**. Footer transport: Upload, 4/4, 133 BPM, timecode, bar position.
- Lyric edit workflow [12:17–14:13]: select section title → inspector set to Clip → copy lyrics → paste into Lyrics box → change line (narrator swaps "Seven views, two are mine / That's a pretty rough splash" to "…my mum clicked, then she dashed" — #097–#098) → bottom bar **Song → Vocals** and **Replace → Cover** (#100–#101) → Generate → two versions appear as **Version 1 / Version 2** sub-lanes (#102–#103) → pick one → **Copy to Main Track** (#103 button).

### 2.7 Stems & per-stem regeneration — [14:13–17:22], #106–#128
- Select whole song → inspector **Extract Stems → All detected stems** [14:44–14:53]. Panel lists **Vocals, B Vocals, Drums, Bass, Guitar, Percussion, Synth, FX** each with an insert arrow and ⋯, plus **Insert All / Download** (#113, #116, `reference/stems-panel.jpg`).
- Insert All drops every stem as its own coloured track on the timeline (#113) — narrator calls it "a bit much" and undoes [15:16–15:21]. Preferred flow: insert one stem via the arrow or drag ("Drop Here" target, #115) [15:27–15:37].
- Per-stem regeneration: stem selected → prompt bar text ("more epic") → **Cover** → two versions → audition against original → Copy to Main Track (#117–#122). Repeated for drums with "bigger and more energetic" (#124–#128). Narrator's claim: this replaces one instrument "without changing the rest of the song" [16:31–16:36].

### 2.8 Hum-to-instrument — [17:22–18:50], #129–#139
- **Add Track → No Input → select mic** ("1 | External Microphone" picker, #132–#133) → arm track → transport record (#135) → hum → stop → choose instrument (Electric guitar) → prompt "Energetic electric rock guitar" → **Cover** (#137) → result lands on an Audio Track lane with its own EQ (Flat/Reset) and Follow Track Tempo controls in the inspector (#136–#138).

### 2.9 Export & share — [18:50–19:43], #140–#146
- Studio **Export → Full Song** (menu also shows Multitrack, #141) → toast "Song Saved! … was saved to your Library — Go to Song" (#142).
- Song page: cover art, title, author, caption, date, reactions row, like/share/⋯, lyrics, **Remix** button, "Similar" sidebar, comments (#143). ⋯ → **Download → MP3 Audio / WAV Audio / Get Stems / MIDI / Video** (#144); "Download WAV Audio — Preparing your download…" (#145).

### 2.10 What the frames add that the audio never said
- The **Sounds** tab, **Hooks** and **Labs** nav items, the **Inspo** attachment, and the "Unlock Your Sound" quest timer (#017, #046).
- The exact **More Options** control set and defaults (#046).
- Studio's per-clip **Tempo / Transpose / Speed / Volume** and per-track **EQ** (#092, #136).
- The **Multitrack** export option (#141) and **MIDI / Video** download options (#144).
- The full right-click menus (#076, #088) — the clone's command surface.
- Credits renew/download caps "starting 9/3/26" (#028) — Suno was mid-policy-change when recorded.

## 3. Claims worth verifying before you rely on them
- "~5 credits per song" [04:08] — narrator's figure, not on screen.
- "Cover keeps the song" [10:20] — true in the demo but the fidelity of a cover is model-dependent; test on your own engine.
- Per-stem Cover leaves the rest untouched [16:31] — in the frames the new stem is a *separate lane copied to main*, i.e. the mix is rebuilt, not the original regenerated. Model it that way.
- v5.5 vs v4.5 quality gap [03:15] — subjective, one listener.

## 4. So-what for the build
1. The UI is fully specified by #017, #046, #076, #088, #089, #092, #113, #143, #144. Nothing requires guessing.
2. The product is **two generation primitives** — *text→song* and *audio+text→song (cover)* — plus **source separation**. Every feature in the video is a composition of those three.
3. Personal use deletes credits, plans, download caps, Explore, publishing, comments, and verification-by-liveness (keep a lightweight consent note).
4. Engine reality: open models now claim both primitives (ACE-Step 1.5: cover, repaint, stems, timbre cloning; self-reported style/lyric alignment 39.1/26.3 vs Suno v5 46.8/34.2). Quality will be "good", not v5.5. See `SPEC.md` §Engine.

## 5. Reference files
- `reference/transcript.txt` — timestamped captions.
- `reference/sheet_1..6.jpg` — all 150 frames, 25 per sheet, numbered.
- `reference/create-panel-and-more-options.jpg` (#017 + #046), `reference/pricing-and-studio.jpg` (#028 + #092), `reference/stems-panel.jpg` (#113 + #116), `reference/create-voice-and-song-editor.jpg` (#060 + #089).
- Engine sources: ACE-Step 1.5 paper https://arxiv.org/html/2602.00744v1 · ACE-Step v1 https://arxiv.org/html/2506.00045v1 · deployment survey https://www.spheron.network/blog/deploy-open-source-ai-music-generation-gpu-cloud-2026/ · ACE-Step on Mac https://lilting.ch/en/articles/ace-step-music-generation-mac
