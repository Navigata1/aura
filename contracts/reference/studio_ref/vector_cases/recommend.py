"""Recommend hand-derived golden cases and public reference evaluator."""
from studio_ref import recommend
from studio_ref.fixture_support import SV

KIND = "fixture.recommend"

def build(profiles):
    GIB = 2 ** 30
    MIB = 2 ** 20

    def snap(sid, osf, cpu, mem, accs, wsl=None):
        return {"kind": "hardware-snapshot", "schemaVersion": SV, "id": sid, "host_id": "host_" + sid[3:], "taken_at": "2026-10-09T10:00:00Z",
                "os": {"family": osf, "version": "fixture", "arch": "arm64" if osf == "darwin" else "x86_64"}, "cpu": cpu, "memory_bytes": mem,
                "accelerators": accs, "wsl2": None if wsl is None else {"memory_bytes": wsl}, "volumes": [], "raw_outputs": []}

    def nv(name, mib, cc, driver, cuda):
        return {"vendor": "nvidia", "name": name, "vram_bytes": mib * MIB, "unified_memory": False, "compute_capability": cc,
                "driver_version": driver, "cuda_runtime": cuda, "metal_recommended_max_working_set_bytes": None}
    mac = snap("hw_m5pro", "darwin", "Apple M5 Pro", 48 * GIB,
               [{"vendor": "apple", "name": "Apple M5 Pro GPU", "vram_bytes": None, "unified_memory": True, "compute_capability": None,
                 "driver_version": None, "cuda_runtime": None, "metal_recommended_max_working_set_bytes": None}])
    r4090 = snap("hw_4090", "linux", "x86", 64 * GIB, [nv("RTX 4090", 24564, "8.9", "570.86", "12.8")])
    r5090 = snap("hw_5090", "linux", "x86", 64 * GIB, [nv("RTX 5090", 32607, "12.0", "575.51", "12.6")])
    r3090 = snap("hw_3090", "windows", "x86", 32 * GIB, [nv("RTX 3090", 24576, "8.6", "566.03", "12.8")], wsl=16 * GIB)
    r16 = snap("hw_4060ti", "linux", "x86", 16 * GIB, [nv("RTX 4060 Ti 16GB", 16380, "8.9", "570.26", "12.8")])
    titan = snap("hw_titanrtx", "linux", "x86", 64 * GIB, [nv("TITAN RTX", 24576, "7.5", "570.86", "12.8")])
    none = snap("hw_cpuonly", "linux", "x86", 32 * GIB, [])

    def rc(name, snaps, tier, reasons, warnings, why):
        return {"name": name, "derivation": why, "snapshots": snaps, "expected": {"tier": tier, "reasons": reasons, "warnings": warnings}}
    recommend = {"kind": "fixture.recommend", "schemaVersion": SV, "cases": [
        rc("this Mac", [mac], 4, ["apple_silicon"], [], "Apple Silicon recommends tier 4 (ADR-0003)."),
        rc("4090", [r4090], 1, ["nvidia_24gb_cc89"], [], "24564 MiB = 23.99 GiB >= 23.5 and cc 8.9 >= 8.9; driver 570.86 >= 570.26."),
        rc("5090 with cu126", [r5090], 1, ["nvidia_24gb_cc89"], ["blackwell_with_cu126"], "31.84 GiB, cc 12.0; a Blackwell card on cu126 is warned."),
        rc("3090 on Windows", [r3090], 2, ["nvidia_24gb_cc80"], ["driver_below_cu128_minimum", "wsl2_memory_below_24gib"],
           "24 GiB at cc 8.6 is tier 2; 566.03 < 570.65 on Windows; WSL2 16 GiB < 24."),
        rc("16 GB card", [r16], 3, ["nvidia_12_16gb"], ["host_ram_below_24gib_for_yue2"],
           "15.996 GiB is in 11.5-23.5; driver 570.26 meets the Linux minimum exactly; 16 GiB RAM < 24."),
        rc("pre-BF16 card", [titan], 4, ["no_qualifying_accelerator"], ["compute_capability_below_8_0", "burst_only"],
           "cc 7.5 < 8.0 qualifies for no NVIDIA tier (decision 1 in the README); burst only."),
        rc("no accelerator", [none], 4, ["no_qualifying_accelerator"], ["burst_only"], "No accelerator: tier 4, burst only, with a warning."),
        rc("Mac plus a reachable 4090", [mac, r4090], 1, ["nvidia_24gb_cc89"], [], "The best tier wins (option A: Mac studio host, CUDA worker)."),
    ]}
    return recommend

def evaluate(case, world):
    return recommend.recommend(case["snapshots"], world.tiers), case["expected"]
