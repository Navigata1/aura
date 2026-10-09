# Backup Plus throughput (MEASURED-LOCAL, 2026-10-09)

Closes the "external drive type and throughput" item in RECONCILIATION.md §8.

| Property | Value | How |
|---|---|---|
| Device | Seagate **BUP Slim** (Backup Plus Slim, a 2.5″ spinning HDD), 2.0 TB | `diskutil info disk4` |
| Filesystem / bus | exFAT, USB | `diskutil info "/Volumes/Backup Plus"` |
| Free | ~1.2 TiB | `df -h` |
| Cold sequential read | **~125 MB/s** (1 GiB in 8.57 s) | `dd if=<previously offloaded file> of=/dev/null bs=8m count=128` |
| Sequential write, synced | **~70 MB/s** (1 GiB in 15.35 s, including `sync`) | `dd if=/dev/zero of=<probe> bs=8m count=128 && sync`; the probe was deleted afterwards |

One run each, on a quiet machine, not a benchmark suite. Random-access performance was not measured, and HDD seeks will make many small files (HF caches, Python environments) slower than these sequential figures.

## Consequences (INFERRED)

- Cold-loading the ACE-Step turbo set (~6.34 GB) takes about 50 s, and XL bf16 (~11 GB) about 90 s. Workers should keep one heavy model resident and report cold and warm wall time separately (D-23).
- Python environments and package caches on the HDD will make imports and installs slower. If internal space allows, prefer the internal SSD for small, hot environments, and keep weights, model caches and the project store on the HDD-backed AURA store.
- A future USB/Thunderbolt SSD would cut cold loads by roughly 5–20×. That is optional, not required.
