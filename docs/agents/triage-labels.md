# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Needs Jon for an owner act or an input only he can supply; an agent prepares everything up to it |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

Edit the right-hand column to match whatever vocabulary you actually use.

In this repo `ready-for-human` never means "a human writes the code". A ticket that needs Jon (its JSON field is
`owner_gate`) is still prepared end to end by an agent: environment, preflight, the quote, the dialog, the evidence
capture. The agent stops only at the owner act (a license acceptance, a paid-run approval, a verdict, a 'not garbled'
check, a risk acceptance, an import or reference permission) or at an input only Jon can supply (his hums, his
reference songs, his hardware, his go-ahead), and resumes after it. Work-stream labels are `stream:*`, never `lane:*`.
