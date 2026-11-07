# C03 independent Standards review — final filesystem-safe revision

Reviewed head: `322fdb724fa37bac3de11b3f5a4d064a4bb8411c`.
Integration base: `d008639ac6e133b91521dfbb290c5b01f81f9815`.
Reviewer: foundation_standards_nov06; no implementation edits.

## Standards

No blocking findings at this final head. UTF-8 decoding with surrogate escape is confined to Git diff/log text, and Git log output encoding is pinned. Raw zero-delimited filename bytes use os.fsdecode in both the policy scanner and clean-copy inventory, matching Python's native filesystem representation. Non-ASCII diagnostics use ASCII escaping. No bytes are silently ignored; commit identity, source, diff and bundle scanning remain in force.

The real-Git CLI regression now requires the Unicode-named planted file to produce its own tracked-file finding as well as a diff finding, so the latter cannot mask a skipped path. Invalid UTF-8 beside an ASCII credential still yields a rejecting diff finding without leaking the credential. The initial UTF-8-only filename revision was held and its review withdrawn before merge. A native Mac probe cannot reproduce the POSIX ASCII-filesystem mismatch because macOS keeps UTF-8 filesystem encoding; that exploratory failed assertion is preserved and is not represented as product red evidence. The Spec review's separately labelled OS-boundary simulation is distinct from hosted hardware proof.

All PRs now run the existing gates on Linux, macOS and Windows, addressing the observed Linux-green/Windows-red integration gap. No retries, assertion weakening, main release or paid model execution is added. Mission state preserves the actual failed R01 integration run and does not claim it green based on local checks.

Fresh final-head checks:
- External preflight passed; 21 focused policy/encoding tests and three subtests passed.
- Independent files-only Unicode-filename secret probe rejects on the repaired checker without relying on diff scanning or exposing the token.
- Commit-aware built-bundle policy: 603 tracked files, zero violations.
- Fresh tracked-copy contract/registry/ticket checks passed.
- All 310 prior fixture hashes remain unchanged; final worktree clean.

Disposition: Standards approval at this exact head/base. Separate final-head Spec approval, green current-head checks on all three hosted OS and unchanged head/base verification are required before merge. This is software validation only; it establishes no audio quality, playback, listening, model runtime or release acceptance.

Evidence SHA-256:
- `standards-fixed-tests.log`: `1af613fc92d5344b6654a8e2507e073c470968645c1b8deb88361eba3d05a3e6`.
- `standards-filesystem-fixed.log`: `eafc1fe5605eb7e8297b54c9c3f80d77ee957c3204f5e17483c381cd35d3fe3d`.
- `standards-fixed-policy.log`: `dd03220e8ccd6da6313e1e27daa2b0691836a7e8d5d14f5f65ac7a249cc5a008`.
- `standards-fixed-clean-contracts.log`: `73b91b8518e0782b4e5d32105cdd47a6930d822223dbd06fd5fd1410243046ab`.
- `standards-fixture-hashes.json`: `f9649aba6e2fb07f7cc2b75f576f479720d741a85e07754f50898bea03ba1799`.
