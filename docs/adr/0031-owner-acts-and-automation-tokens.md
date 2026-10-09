# Owner acts need Jon in the Studio UI; automation tokens can do everything else

Status: accepted (2026-10-09) with the v1 architecture. It implements O-09's "every paid run still needs Jon's explicit
yes".

AURA spends money, records verdicts that gate quality, and changes lanes that gate licenses. Agents and scripts drive
most of its work, and a service on localhost is exposed to CSRF and DNS rebinding.

**Decision.**

- **Owner acts** are: approving a quote, changing the monthly cap, acknowledging an overrun or a reconciliation
  adjustment, changing a project's operator lane, submitting a verdict, accepting a risk, accepting a model license,
  recording a reference permission, and attesting an import.
- `studioctl serve` prints a one-time launch token, only to an interactive terminal and never to a log; `serve --open`
  hands it to the browser directly, and without a terminal serve starts automation-only. The browser exchanges it for a `SameSite=Strict` cookie with the
  **owner-ui** scope. The CLI, the eval harness and agents use an **automation** token from a local token file. That
  scope can do everything except owner acts, and gets 403 on each of them. A paid approval also needs the challenge
  nonce rendered in the dialog.
- The service binds 127.0.0.1, with a Host allowlist and an Origin check on every state change. Binding to the tailnet
  is opt-in and token-gated.
- Secrets (the RunPod API key, the HF token for gated models, tailnet pairing secrets) live in the OS keychain through
  `keyring`. They never appear in client code, the web bundle or API responses, and CI scans the built bundle for
  secrets.

**Why.** The paid-run rule (O-09), the integrity of blind auditions, and the lane doctrine (O-06) all depend on an
action that an agent cannot fake.

## Considered Options

- **A terminal y/N approval in the CLI.** Rejected: one approval path, the UI, keeps the owner-act surface minimal.
- **Approval open to any authenticated client.** Rejected for the same reason.

## Consequences

A workflow agent can prepare everything up to an owner act, and must then wait for Jon. The design does not claim to
defeat a compromised local machine.

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). Test mode mints owner-ui sessions only on a temporary store marked `test_store`, with FakeBurstProvider forced and keyring reads off; startup fails otherwise, so test mode can never approve a real quote, accept a real license or read a real secret.

**Reverse if:** nothing foreseen reverses this.

Evidence: [architecture.md](../spec/architecture.md) §3.1, §4.1, §7.5, §12 (localhost exposure), §13.2, §13.3,
§13.4 (T-08). [OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-06, O-08, O-09.
