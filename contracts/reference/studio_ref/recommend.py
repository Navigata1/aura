"""recommend(snapshots) over compute-tiers.v1.json (architecture.md §7.2, ADR-0003). Pure; golden-tested.

Decisions taken where the docs left room (README, "Decisions"): every NVIDIA tier needs compute capability >= 8.0
(BF16), so a card below that qualifies for nothing and is warned about; with several reachable hosts the best (lowest)
tier wins, because a Mac studio host can drive a tailnet CUDA worker (option A); an unprobed host never qualifies.
"""

from __future__ import annotations

from decimal import Decimal

GIB = Decimal(2 ** 30)


def _version(text: str) -> tuple[int, ...]:
    return tuple(int(p) for p in text.split("."))


def recommend(snapshots: list[dict], tiers: dict) -> dict:
    t = tiers["thresholds"]
    tier12 = Decimal(t["nvidia_tier12_min_vram_gib"])
    tier3 = Decimal(t["nvidia_tier3_min_vram_gib"])
    cc1 = Decimal(t["tier1_min_compute_capability"])
    cc2 = Decimal(t["tier2_min_compute_capability"])
    ram_min = Decimal(t["yue2_min_host_ram_gib"]) * GIB
    wsl_min = Decimal(t["wsl2_min_memory_gib"]) * GIB
    blackwell = Decimal(t["blackwell_min_compute_capability"])
    candidates: list[tuple[int, str]] = []
    warnings: list[str] = []

    def warn(code: str) -> None:
        if code not in warnings:
            warnings.append(code)

    for snap in snapshots:
        nvidia_here = False
        for acc in snap["accelerators"]:
            if acc["vendor"] == "apple":
                candidates.append((4, "apple_silicon"))
                continue
            nvidia_here = True
            vram = Decimal(acc["vram_bytes"]) / GIB
            cc = Decimal(acc["compute_capability"])
            if cc < cc2:
                warn("compute_capability_below_8_0")
            elif vram >= tier12 and cc >= cc1:
                candidates.append((1, "nvidia_24gb_cc89"))
            elif vram >= tier12:
                candidates.append((2, "nvidia_24gb_cc80"))
            elif vram >= tier3:
                candidates.append((3, "nvidia_12_16gb"))
            else:
                warn("nvidia_vram_below_tier3")
            driver = acc["driver_version"]
            minimum = t["min_driver_windows"] if snap["os"]["family"] == "windows" else t["min_driver_linux"]
            if driver is not None and _version(driver)[:2] < _version(minimum):
                warn("driver_below_cu128_minimum")
            if cc >= blackwell and acc["cuda_runtime"] == t["blackwell_bad_cuda_runtime"]:
                warn("blackwell_with_cu126")
        if nvidia_here:
            if Decimal(snap["memory_bytes"]) < ram_min:
                warn("host_ram_below_24gib_for_yue2")
            if snap["wsl2"] is not None and snap["wsl2"]["memory_bytes"] is not None \
                    and Decimal(snap["wsl2"]["memory_bytes"]) < wsl_min:
                warn("wsl2_memory_below_24gib")
    if not candidates:
        warn("burst_only")
        return {"tier": 4, "reasons": ["no_qualifying_accelerator"], "warnings": warnings}
    best = min(c[0] for c in candidates)
    reasons = sorted({c[1] for c in candidates if c[0] == best})
    return {"tier": best, "reasons": reasons, "warnings": warnings}
