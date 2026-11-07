# C03 independent Spec review — final corrected head

Head: `322fdb724fa37bac3de11b3f5a4d064a4bb8411c`.
Base: `d008639ac6e133b91521dfbb290c5b01f81f9815`.
Review date: November 6, 2026. No repository edits by reviewer; worktree clean. This supersedes the withdrawn approval at `9e49156`, retained separately.

## Spec

No blocking finding remains. UTF-8 diff/log decoding with reversible `surrogateescape` repairs the preserved Windows cp1252 failure without discarding input. Git log output is explicitly UTF-8. Crucially, raw zero-delimited filenames now use `os.fsdecode` in both the scanner and clean-copy inventory, matching the host filesystem representation instead of assuming that filenames use the content decoder. Product JSON declares UTF-8; diagnostics escape characters only when reporting and never print token values.

Independent public-CLI probes at the final head establish:
- Original baseline reproduces the cp1252 content-decoding failure under a labelled locale-boundary simulation; the fix accepts identical real Git Unicode content and commit messages.
- A removed synthetic secret remains rejected by the diff scan, and non-noreply commit identity remains rejected.
- A separate ASCII POSIX filesystem-boundary simulation reproduces the intermediate `9e49156` source-only Unicode-filename skip; the final head rejects that tracked-file secret without relying on the diff. Native macOS retains UTF-8 filesystem encoding and did not reproduce this Linux-class issue; that unsuccessful native attempt is preserved.
- The committed public regression passes with pinned managed Python. It now separately requires both tracked-file and diff findings, preventing one path from masking the other. Invalid UTF-8 content beside an ASCII synthetic token still fails without token disclosure.

The PR matrix requires the unchanged gate on all three hosted OS before merge; no retries or relaxed checks were introduced. Original Windows-red integration evidence remains recorded. No contracts, fixture bytes, owner-act rules, model behavior or audio capability changed.

Disposition: Spec review passes for this exact head/base, conditional on all three current-head hosted jobs plus separate Standards review. Simulated boundary tests are not native Linux/Windows proof. Full T02/C02, scheduled-nightly acceptance and real music/playback quality remain open.

## Evidence hashes

- `spec-probes.py`: `fc97aab2953b68bc8ec4c4d058ae3c7218f6213e2c845260b939d23f4ecd9a01`
- `spec-probes-final.log`: `69ea6eff33b69b6fc5a6200a891d4c4c4086810f0814943f7c8ef085be9e88c7`
- `spec-filename-simulated.py`: `f7860848c1deae683584af6d4994084c3ee8f90204cdc9c3711d818c643f3004`
- `spec-filename-simulated-final.log`: `f2f7b6cf2110c3d56eac306a5ac79993d072891b4efb2c81e20f80b9eae27b71`
- `spec-supported-locale-tests-final.log`: `782a2bfa5d75b4c14ab3d6556f3f39d67f6b86e18415c4933cd866b765ee9909`
- `spec-filename-reproduction.log`: `403bb9ea2357b07d27b64fff8803798469b39076fd1c0c5bd2dcb50e3ed47625`
