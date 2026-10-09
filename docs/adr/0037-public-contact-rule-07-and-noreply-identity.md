# The only public contact is `hello@islanddevcrew.com` as text, and every commit uses a noreply identity (IDC Rule 07)

Status: accepted (2026-10-09). IDC Domain Doctrine Rule 07, binding on every Island Development Crew project. AURA is
personal today, but every surface it has already follows the rule.

Island Development Crew runs lean, often on a single human seat. A public founder address becomes a spam magnet and
burns that seat. Rule 07 gives every domain one public role address, `hello@<domain>`. Personal addresses never appear
on a public surface, and a `mailto:` link is a scraping target.

**Decision.**

- The only contact address anywhere in AURA (UI, docs, README, contracts, schemas, export manifests, package metadata)
  is `hello@islanddevcrew.com`, shown as **text** and never as a `mailto:` link. AURA uses the IDC corporate address
  because it owns no domain.
- It is stored once, as `publicContactText` in `contracts/product.json` (ADR-0035), and the UI footer reads it from
  there.
- **No personal address** of Jon or anyone else appears in code, copy, manifests, package metadata, OG or schema
  fields, docs or commit metadata.
- **Commits use a noreply identity**: the GitHub account's `users.noreply.github.com` address.
- **CI enforces it** (`scripts/ci/`). A Rule-07 lint fails on any `mailto:` link, on any address other than the public
  contact, and on any commit author that is not a noreply identity. Planted violations must fail (P0-7).

**Why.** IDC Rule 07 and its sub-rules. JOVRA's hard rule 7 applies the same pattern.

## Consequences

Some Markdown renderers, GitHub's among them, turn a bare email address into a link, so docs write the address in code
formatting. If a contact form is ever needed, it posts structured fields to the IDC ingestion endpoint rather than
exposing a `mailto:`.

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). The Rule-07 lint is exact: tracked files, excluding the archived `docs/research/sources/`; `hello@islanddevcrew.com` is the only address in text; the account's GitHub noreply address and GitHub's own noreply identity appear only as commit author or committer, and Anthropic's noreply identity only in Co-Authored-By trailers (the lint matches those patterns, so no doc needs to spell them out); a bare address in Markdown prose outside code formatting fails; package manifests carry no author email. It runs on every PR and every push to `integration`, because GitHub authors a squash merge after PR CI.

**Reverse if:** AURA graduates to its own domain. The public contact then becomes that domain's `hello@` address,
changed in the one constant.

Evidence: IDC Domain Doctrine v1.2, Rule 07. [architecture.md](../spec/architecture.md) §2 (`CLAUDE.md`,
`contracts/product.json`, `scripts/ci/`), §4.11, §11 (P0-7). JOVRA `CLAUDE.md`, hard rule 7.
