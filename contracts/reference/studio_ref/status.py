"""Computed profile and capability status (ADR-0027): a pure fold over evidence records for one
(profile_revision, host_class). Never stored, never set by hand.

    declared -> installed      install pass AND conformance pass at this revision and host class
    installed -> smoke-passed  a smoke pass aimed at the profile's smoke gate whose checks list every check the gate
                               declares, each passing, with owner_not_garbled answered by a verdict id; synthetic only
                               where the gate allows
    benchmarked                 unavailable until concluded benchmark results have a binding contract (C01)
    any failing install/conformance/smoke record once at installed or above -> disabled (terminal)

Benchmark and hum-benchmark records are currently unsupported as conclusions. The admission rule rejects their
pass/fail results, and this fold ignores both kinds entirely: an unsupported conclusion neither promotes nor disables.
A preregistration hash (even one in known_preregs) and a verdict id do not prove quotas, thresholds or result binding.
See contracts/README.md and docs/spec/contract-fixes/C01-benchmark-conclusions.md before enabling either transition.

A failing attempt while still declared changes nothing. listening-unregistered records never change status. A pin
change is a new revision: with no records at that revision it computes to declared, and it reaches installed only after
its own install and conformance records. A smoke record whose checks omit a gate check, fail one, or answer
owner_not_garbled without a verdict does not promote (whether that verdict resolves to an owner-ui verdict on this
revision's smoke candidates is the evidence.gates rule's job, since this fold sees no verdicts).
"""

from __future__ import annotations

ORDER = ["declared", "installed", "smoke-passed", "benchmarked"]
GATED_CHECKS = {"install", "conformance", "smoke"}
VERDICT_CHECKS = {"owner_not_garbled", "preregistered_listening"}


def gate_checks_met(record: dict, gate: dict) -> bool:
    """Every check the gate declares is present in the record and passing; listening checks carry a verdict id."""
    results = {c["check"]: c for c in record.get("checks", [])}
    for name in gate.get("checks", []):
        c = results.get(name)
        if c is None or c["result"] != "pass":
            return False
        if name in VERDICT_CHECKS and not c.get("verdict_id"):
            return False
    return True


def compute_status(subject: dict, evidence: list[dict], revision: str | None, host_class: str,
                   known_preregs: set[str] | None = None) -> str:
    """subject is an engine profile (gates.smoke) or capability (gate).

    known_preregs is retained for call compatibility; it confers no authority to conclude a benchmark.
    """
    smoke_gate = subject["gates"]["smoke"] if "gates" in subject else subject["gate"]
    test_only = subject.get("test_only", False)
    records = [e for e in evidence
               if e["subject"]["subject_id"] == subject["id"] and e["host_class"] == host_class
               and (revision is None or e["profile_revision"] == revision)]
    records.sort(key=lambda e: (e["recorded_at"], e["id"]))
    state = "declared"
    install_ok = conformance_ok = False
    for e in records:
        check, result = e["check"], e["result"]
        if check not in GATED_CHECKS or result == "inconclusive":
            continue
        if result == "fail":
            if state != "declared":
                return "disabled"
            continue
        if check == "install":
            install_ok = True
        elif check == "conformance":
            conformance_ok = True
        elif check == "smoke" and state == "installed" and e["gate_id"] == smoke_gate["gate_id"] \
                and gate_checks_met(e, smoke_gate):
            if not e["synthetic"] or smoke_gate["synthetic_allowed"] or test_only:
                state = "smoke-passed"
        if state == "declared" and install_ok and conformance_ok:
            state = "installed"
    return state
