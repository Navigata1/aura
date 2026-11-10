# T03 merge notes (lead), 2026-11-07

- Fixture coupling accepted as for T01 (review NB-2): `IR-COMPONENT-NC-IN-PROCESS` and `IR-COMPONENT-NC-IN-LLC` embed the register overlay's `generated_from` hash, so T03's overlay edit moved one generated line in each. 308 of 310 fixtures are byte-identical, and no legacy fixture changed. Every later overlay edit will hit the same coupling: the second-merged PR regenerates.
- The non-blocking findings NB-4, NB-5, NB-7 and NB-11 (register sync hardening) go to a follow-up contract-fix issue.
- Evidence hygiene for checkpoint PRs (NB-14): this ticket's raw/ and licenses/ evidence holds third-party addresses copied from license, NOTICE and registry metadata. Commit only the review and merge records to `ops/mission/evidence/`, never raw fetched license material.
