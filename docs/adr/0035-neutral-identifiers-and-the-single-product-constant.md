# "AURA" lives in one constant; code, the CLI, environment variables, the volume and the store format use neutral names

Status: accepted (2026-10-09). Owner decision O-10 ("AURA" is the working name, kept in one constant so a rename is
cheap).

"AURA" is a working name while the tool is personal. A name baked into paths, packages and on-disk formats would turn a
rename into a migration.

**Decision.** The product name appears only in `contracts/product.json`, which holds `productName` and the public
contact text (ADR-0037); the UI and any docs that need the name read it from there. Python packages are `studio_*`,
environment variables `STUDIO_*`, the CLI `studioctl`, the volume `/Volumes/STUDIO`, and the store format uses
`studio`. The CLI is not called `studio`, because Android Studio's JetBrains launcher installs a command with that
name, and Jon also builds for Android (JOVRA).

**Why.** O-10 asks for a cheap rename. Neutral identifiers make a rename touch one constant and no path.

## Consequences

A rename changes one file. `doctor` checks for a mount-point collision on `/Volumes/STUDIO`.

**Reverse if:** the name becomes permanent and public. Even then the identifiers can stay neutral.

Evidence: [OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-10.
[architecture.md](../spec/architecture.md) §2, §8.1, §13.4 (T-16).
