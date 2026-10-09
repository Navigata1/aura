# No desktop shell in v1; when one is needed, Electron rather than Tauri 2

Status: accepted (2026-10-09). From D-14. It rests on the Chromium-browser default (Q10, owner-pending).

The Studio needs Chromium's audio stack. Tauri 2 uses WKWebView on macOS, which ignores `latencyHint`, pins a 128-frame
buffer and has no `setSinkId`. The often-quoted "Tauri 42 MB against Electron 168 MB" compares RAM from a blog post,
not bundle sizes: a minimal Tauri app can be under 600 KB, and Electron's arm64 runtime zip is 124 MB.

**Decision.** v1 runs in Jon's Chromium-based browser against localhost. When an installable app is needed (v2),
prefer **Electron** (MIT, Chromium audio). Re-evaluate Tauri v3's CEF runtime when it leaves alpha. **Tauri 2 is
rejected for the Studio.**

**Why.** C39 and C40. A shell adds packaging, signing and update work, and nothing in v1 pays for it.

## Consequences

v1 has no installer, auto-update or code signing. The control service already owns everything a shell would host, so
adding one later wraps the same origin.

**Reverse if:** Tauri's CEF runtime ships stable, WebKit gains `latencyHint` and `setSinkId`, or Jon rejects the
Chromium requirement (Q10).

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §2 C39, C40; §4.7; §6 D-14.
[evidence-register.json](../research/evidence-register.json) V-ui-4.
[feature-inventory.md](../research/feature-inventory.md) J17.
