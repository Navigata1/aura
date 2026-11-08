# T03 license verification of the v1-core plumbing — 2026-11-07

This records primary-source license checks for the components T03 (P0-9) names. Every reading is an engineering
interpretation of the license texts, not legal advice. It is not a model-license acceptance, an owner act, a complete
binary or transitive SBOM, or evidence of quality or compatibility. No weights were downloaded and nothing was
installed.

Method: each license text was fetched at a pinned tag and commit from the official repository twice (the raw URL and
the GitHub contents API), the bytes were compared, and the SHA-256 was recorded. Registry metadata (PyPI or npm) for
the same version corroborates it. For weights, the model card at a pinned revision and the author's own statements were
read; for training data, the paper and each dataset's terms. Copies are kept on the studio volume under
`evidence/T03`; [plumbing-sources-2026-11-07.json](plumbing-sources-2026-11-07.json) lists all 74 sources with their
pins and hashes. Repository files carry no upstream license text and no personal contact details.

## Rows closed from a primary source

Lanes and the process-boundary flag are the generated register's values
([components.v1.json](../../../contracts/registry/components.v1.json)).

| Component | Pin | License as read | Allowed lanes | Process boundary | Status |
|---|---|---|---|---|---|
| mido | 1.3.3 (commit 7313549) | MIT | individual, llc, research | no | confirmed |
| librosa (`librosa-pyin`) | 1.0.0 (3e4ff7b) | ISC | individual, llc, research | no | confirmed |
| pyloudnorm | 0.2.0 (b8d67bf) | MIT | individual, llc, research | no | corrected (kept) |
| mir_eval (`mir-eval`) | 0.8.2 (8db0b38) | MIT | individual, llc, research | no | confirmed |
| axe-core and @axe-core/playwright | 4.14.0 (e797173, 2375f7f) | MPL-2.0, development only | individual, llc, research | no | confirmed |
| Newsreader | google/fonts 8b0a1d0 | OFL-1.1, no Reserved Font Name | individual, llc, research | no | confirmed |
| IBM Plex Sans | 1.1.0 (1da12f0) | OFL-1.1, Reserved Font Name "Plex" | individual, llc, research | no | confirmed |
| IBM Plex Mono | 2.5.0 (2f9ba1b) | OFL-1.1, Reserved Font Name "Plex" | individual, llc, research | no | confirmed |
| Bravura Text | 1.482 (37b1943) | OFL-1.1, Reserved Font Name "Bravura" | individual, llc, research | no | confirmed |
| Lucide | 1.70.0 (b826f0c) | ISC, Feather-derived icons MIT | individual, llc, research | no | confirmed |
| YuE skill `abc_tools.py` (`yue-abc-tools`) | yue2-music-v1.2.0 (72272f9) | Apache-2.0 | individual, llc, research | no | confirmed |
| SwiftF0 package and bundled ONNX | 0.3.0 (d1ba77f) | MIT label; trained on CC BY-NC-SA 4.0 data | individual, research | no | confirmed |
| Basic Pitch | 0.4.0 (9991303) | Apache-2.0 with NOTICE; training data recorded for T54 | individual, research | no | confirmed |
| Demucs (`demucs-4.1.0`) | 4.1.0 (6a604bb) | code MIT; weights research and personal only (author) | individual, research | yes | corrected (kept) |
| demucs-mlx | 1.6.1 (9950c7d) | code MIT; converted weights keep the author's restriction | individual, research | yes | corrected (kept) |
| wavesurfer.js 8 core (`wavesurfer-core`) | 8.0.5 (b0ce881) | BSD-3-Clause | individual, llc, research | no | confirmed |
| waveform-playlist | @waveform-playlist/browser 16.0.1 (f1739ab) | MIT, but requires waveform-data 4.5.2 (LGPL-3.0) | individual, llc, research | yes | corrected |
| Signalsmith Stretch | 1.4.0 (a670068) | MIT, with Signalsmith Linear 0.6.4 MIT | individual, llc, research | no | confirmed |

The pyloudnorm and Demucs rows keep their earlier `corrected` status: the earlier corrections (BS.1770-4, the
non-commercial weights) still stand and this pass confirms the licenses under them.

## Rows that stay open

Each stays `unverified`, research-only (individual and llc forbid an unverified license, `lanes.v1.json`) and a release
blocker. The labels are the "Until then" column of the spec's Unverified capabilities table.

| Component | Blocking gate | Shown until it closes |
|---|---|---|
| m4a/AAC decoder (`audio-decoder`) | T102 codec-checks | "Hums arrive as WAV only" |
| MP3 encoder (`mp3-encoder`, new row) | T102 codec-checks | "Export bundles carry WAV and MIDI only" |
| G2P or phonemizer (`g2p-phonemizer`) | T72 lyric-per, then T73 lyric-per-on-mac | "No lyric-error badge" |
| MIDI synth and soundfont (`midi-synth-soundfont`) | T101 midi-synth-eval | "No instrument rendering; NeutralVoice is the only guide" |
| Lyric-alignment model (`lyric-aligner`, new row) | T84 lyric-alignment | "No line or word replace" |

## Findings (interpretations, not legal advice)

1. **waveform-playlist v16 brings an LGPL-3.0 dependency.** `@waveform-playlist/browser` 16.0.1 and
   `@waveform-playlist/ui-components` 14.0.1 require `waveform-data` ^4.5.2, whose LICENSE at v4.5.2 is LGPL-3.0. The
   web bundle's deny-list refuses LGPL, so the row joins the `copyleft` release-blocker class, and T77 can adopt it only
   with that dependency removed or replaced. Tone.js 15.1.22 is MIT.
2. **Reserved Font Names.** IBM Plex ("Plex") and Bravura ("Bravura") declare one; Newsreader declares none. The
   OFL-FAQ shipped with Bravura (1.1-update6, section 2.6) treats subsetting a web font as modification, and OFL-1.1
   condition 3 bars a Modified Version from using a Reserved Font Name, as the primary font name presented to users,
   without written permission. The planned subsets therefore need new names, or the fonts ship unmodified.
3. **IBM's npm font packages run telemetry.** `@ibm/plex-sans` 1.1.0 and `@ibm/plex-mono` 2.5.0 declare an
   `ibmtelemetry` postinstall script and depend on `@ibm/telemetry-js`. Take the files from the pinned tags, or install
   with scripts disabled.
4. **axe-core is MPL-2.0.** It is file-level copyleft, which binds only modified axe-core files; as an unmodified test
   tool it binds none of the studio's code. The web-bundle allowlist does not admit MPL-2.0, so it must stay a
   development dependency.
5. **Basic Pitch's training data, the input to T54.** Table 1 of the paper (arXiv 2203.09893v2) trains on GuitarSet (CC
   BY 4.0), MAESTRO (CC BY-NC-SA 4.0), Slakh2100 redux (CC BY 4.0), iKala (an end-user agreement for academic purposes
   only, with no profit; its official host no longer resolves, so an archived copy is cited) and the MedleyDB
   pitch-tracking subset (CC BY-NC-SA 4.0, non-commercial research only); Molina and Phenicx were test-only. The v0.4.0
   data scripts cover the same five, and their README calls them "a selection of" the training datasets. On these terms
   the row looks like SwiftF0's case, but the classification is T54's verdict, so the row keeps
   `unverified_training_data` until then.
6. **Demucs weights.** The Hugging Face cards at the pinned revisions state no license. The author's statements in
   facebookresearch/demucs #327, #384 and #508 (hashed in the manifest) restrict the weights to research and personal
   use. The demucs-mlx card's MIT tag on the converted weights does not change that.
7. **SwiftF0.** The MIT-labelled wheel bundles `swift_f0/model.onnx`. Its training README and the
   `lars1234/pitch-benchmark` dataset card state CC BY-NC-SA 4.0 for research use, so the
   `permissive_label_nc_data` caveat stands until T54.
8. **Transitive copyleft stays in workers.** librosa 1.0.0 requires soundfile (libsndfile, LGPL-2.1-or-later) and soxr
   (LGPL-2.1-or-later). Demucs 4.1.0 requires lameenc (LGPL-3.0-or-later). Both already run only in worker processes,
   and their adopting tickets audit the resolved dependency licenses.
9. **Signalsmith Stretch's web build lags.** The WASM/AudioWorklet release at tag 1.4.0 is package version 1.3.2 (npm
   `signalsmith-stretch` 1.3.2, MIT). The adopting ticket pins the build it uses.
10. **`abc_tools.py` is Apache-2.0 code.** It sits under the YuE2 skill's own Apache-2.0 LICENSE; the YuE2 weights'
    MODEL_LICENSE covers the weights, not this file.

## Register mechanics

`scripts/registry/register_overlay.json` gains two sections, both read by `scripts/registry/sync.py`.
`license_verification` replaces named fields of an evidence-register row from its pinned sources.
`open_rows` gives a still-open row its gate and label, which the generator writes into the row's `verdict_condition`.
The generator now fails when any row whose status is not `unverified` cites no primary source, and when an open row
is not unverified, research-only and release-blocking. It also writes the
[open-source-readiness register](open-source-readiness.md) from the same rows. `sync.py --check` and
`tests/foundation/test_open_source_readiness.py` fail when a release-blocking row is missing from it.

## Still open after this pass

- Obligations of rows that engine profiles and fixtures copy (`basic-pitch`, `librosa-pyin`, `pyloudnorm`, `swiftf0`,
  `demucs-4.1.0`, `demucs-mlx`) are unchanged. Basic Pitch's NOTICE arguably calls for `apache_notice`, and the MIT,
  BSD and ISC rows for `attribution`. Adding them changes the profiles' license records and the fixture world
  together, so it belongs to a contract-fix PR.
- Transitive and distribution audits of exact installed environments belong to each adopting ticket. T54 records the
  SwiftF0 and Basic Pitch provenance verdicts, T95 the Kim Mel-Band-RoFormer training-data check. The grouped
  `codegen-tools` stack row stays with T01 and T04.
- The `contracts/fixtures/invalid/component-nc-in-process.json` and `component-nc-in-llc.json` fixtures embed the
  register's `generated_from` hashes, as the T01 note recorded. They were regenerated by
  `contracts/reference/generate_fixtures.py`, and only the overlay hash line changed.
