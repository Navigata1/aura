# C03 — Git text decoding independent of the host locale

Issue #11 repairs a software validation failure, not a product/audio capability. The original integration run
[42342742232](https://github.com/Navigata1/aura/actions/runs/42342742232) at `d008639` failed Windows job128313805325:
`scripts/ci/check.py` decoded UTF-8 diff text using cp1252 and encountered undefined byte `0x9d`. Linux/macOS passed.
The original run and its failure remain recorded in the mission evidence; it was not retried to replace the result.

The policy scanner now explicitly decodes Git diff, log and zero-delimited filenames as UTF-8 with `surrogateescape`,
preserving otherwise undecodable bytes instead of dropping them. Git log output is explicitly configured UTF-8.
The clean-contract-copy inventory uses the same filename decoding. The product JSON reader declares UTF-8, and
policy diagnostics escape non-ASCII characters so an ASCII console can report a violation without a second crash.
The other subprocess reads in these two CI entry points were inspected; none remain locale-dependent. The developer
worktree helper's bare-repository boolean and run.py's Node version read only ASCII protocol values and are unchanged.

The public policy CLI regression uses real Git repositories and subprocesses with Python's supported
`PYTHONUTF8=0`, `PYTHONCOERCECLOCALE=0` and `LC_ALL=C` settings. On macOS/Linux this produces an ASCII default;
on Windows it exercises the native legacy code page when present. It also forces ASCII stdout. This is deterministic
legacy-default coverage on Linux, not a claim that a Mac emulates Windows cp1252. The original hosted failure is the
cp1252 evidence. The unchanged baseline checker fails under pinned Python 3.12 separately for UTF-8 diff content,
Unicode filenames and Unicode commit messages. The repaired checker passes all three and still rejects planted
credential-shaped content, including an ASCII token beside invalid UTF-8 bytes, without printing the token.

Local full gate: 46 Python tests, 12 subtests, two Vitest tests, two Node tests, clean tracked-contract checks, build,
policy and license inventory pass. Existing contract fixture bytes are unchanged. Red/green logs live under
`/Volumes/STUDIO/evidence/C03/`; the initial exploratory Python 3.14 red is retained separately from the pinned 3.12
red/green proof. No environment was installed on the internal disk.

PR checks now run the same gates on Linux, macOS and Windows for every ticket. The observed Linux-green PR followed
by a Windows-failing integration push justifies replacing the old foundation-only exception. This adds hosted CI
matrix work, not paid model computation, and changes no assertions or retry policy. Fresh hosted checks and independent current-head/current-base review remain pending
at preparation time. Full T02, C02, scheduled-nightly acceptance and real playback/quality remain open. No merge or
main release is conferred by this local validation.
