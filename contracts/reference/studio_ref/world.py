"""A loaded set of registries and records, indexed for the cross-file reference rules (rules.py).

A "world" is what the store plus the registry would hold at one moment: the shipped registries, any test overlays,
and a set of records. Fixture scenarios build a world from the valid fixture world plus an overlay that adds or
replaces records by identity (identity()).
"""

from __future__ import annotations

from .canonical import self_hash

REGISTRY_KINDS = {"engine-profile-registry", "component-register", "capability-registry", "lane-policy", "compute-tiers",
                  "product"}
LANES = ("individual", "llc", "research")
PROPAGATING = ("derived_from", "converted_from")
GENERATIVE_ORIGINS = {"generated_mix", "regenerated_part", "new_part", "tts_render"}
CANDIDATE_ORIGINS = {"generated_mix", "regenerated_part", "new_part"}
SELF_HASH_FIELDS = {"melody-spec": "content_sha256", "song-spec": "content_sha256"}


def identity(doc: dict) -> tuple:
    kind = doc["kind"]
    if kind == "artifact":
        return (kind, doc["sha256"])
    if kind == "melody-spec":
        return (kind, doc["melody_id"], doc["rev"])
    if kind == "song-spec":
        return (kind, doc["song_id"], doc["rev"])
    if kind in ("ledger-entry", "event"):
        return (kind, doc["seq"])
    if kind == "provenance-sidecar":
        return (kind, doc["blob_sha256"])
    if kind == "correction-log":
        return (kind, doc["melody_id"])
    if kind in ("task-request", "task-status", "refusal"):
        return (kind, doc["job_id"])
    if kind in ("worker-describe", "worker-health"):
        return (kind, doc["worker_id"])
    if kind in ("engine-profile-registry", "capability-registry"):
        return (kind, doc["registry_id"])
    if kind == "component-register":
        return (kind, doc["register_id"])
    if kind in ("product", "store", "lane-policy", "compute-tiers"):
        return (kind,)
    return (kind, doc["id"])


def apply_overlay(base: list[dict], overlay: list[dict], remove: list[list] | None = None) -> list[dict]:
    docs = {identity(d): d for d in base}
    for key in remove or []:
        docs.pop(tuple(key), None)
    for d in overlay:
        docs[identity(d)] = d
    return list(docs.values())


class World:
    def __init__(self, docs: list[dict]):
        self.docs = docs
        self.registries = [d for d in docs if d["kind"] in REGISTRY_KINDS]
        self.records = [d for d in docs if d["kind"] not in REGISTRY_KINDS]
        self.by_kind: dict[str, list[dict]] = {}
        for d in self.records:
            self.by_kind.setdefault(d["kind"], []).append(d)
        self._index_registries()
        self._index_records()

    # ----- registries ----------------------------------------------------------------------------------------
    def _index_registries(self) -> None:
        self.components: dict[str, dict] = {}
        self.component_overlay: dict[str, bool] = {}
        self.duplicates: list[str] = []
        self.profiles: dict[str, dict] = {}
        self.profile_overlay: dict[str, bool] = {}
        self.capabilities: dict[str, dict] = {}
        self.lane_forbidden: dict[str, set] = {}
        self.lane_releasable: dict[str, bool] = {}
        self.tiers: dict | None = None
        for reg in sorted(self.registries, key=lambda r: (bool(r.get("overlay", False)), identity(r))):
            kind = reg["kind"]
            if kind == "component-register":
                for c in reg["components"]:
                    if c["id"] in self.components:
                        self.duplicates.append(f"component {c['id']}")
                        continue
                    self.components[c["id"]] = c
                    self.component_overlay[c["id"]] = reg["overlay"]
            elif kind == "engine-profile-registry":
                for p in reg["profiles"]:
                    if p["id"] in self.profiles:
                        self.duplicates.append(f"profile {p['id']}")
                        continue
                    self.profiles[p["id"]] = p
                    self.profile_overlay[p["id"]] = reg["overlay"]
            elif kind == "capability-registry":
                for c in reg["capabilities"]:
                    if c["id"] in self.capabilities:
                        self.duplicates.append(f"capability {c['id']}")
                        continue
                    self.capabilities[c["id"]] = c
            elif kind == "lane-policy":
                self.lane_forbidden = {lane["id"]: set(lane["forbidden_release_blockers"]) for lane in reg["lanes"]}
                self.lane_releasable = {lane["id"]: lane["releasable"] for lane in reg["lanes"]}
            elif kind == "compute-tiers":
                self.tiers = reg

    # ----- records ---------------------------------------------------------------------------------------------
    def _index_records(self) -> None:
        def by_id(kind: str) -> dict:
            return {d["id"]: d for d in self.by_kind.get(kind, [])}

        self.artifacts = {d["sha256"]: d for d in self.by_kind.get("artifact", [])}
        self.melodies = {(d["melody_id"], d["rev"]): d for d in self.by_kind.get("melody-spec", [])}
        self.songs = {(d["song_id"], d["rev"]): d for d in self.by_kind.get("song-spec", [])}
        self.ids: dict[str, dict] = {
            kind: by_id(kind)
            for kind in ("project", "job", "candidate", "generation-request", "keeper", "verdict", "reveal",
                         "audition", "quote", "approval", "burst-run", "reference", "import-terms", "license-acceptance",
                         "risk-acceptance", "evidence", "prereg", "eval-brief", "eval-set", "export-manifest",
                         "edit-operation", "timeline", "hardware-snapshot", "compute-profile", "session")
        }
        self.import_terms_by_artifact = {t["artifact_sha256"]: t for t in self.by_kind.get("import-terms", [])}
        self.ledger = sorted(self.by_kind.get("ledger-entry", []), key=lambda e: e["seq"])
        self.events = sorted(self.by_kind.get("event", []), key=lambda e: e["seq"])
        self.record_hashes: dict[str, tuple] = {}
        for kind, field in SELF_HASH_FIELDS.items():
            for d in self.by_kind.get(kind, []):
                self.record_hashes[d[field]] = identity(d)
        for d in self.by_kind.get("prereg", []):
            self.record_hashes[d["prereg_sha256"]] = identity(d)
        self.suno_imports = {t["artifact_sha256"] for t in self.by_kind.get("import-terms", []) if t["source_service"] == "suno"}

    # ----- helpers ---------------------------------------------------------------------------------------------
    def project_lane_at(self, project: dict, at: str) -> str:
        changes = sorted(project["lane_changes"], key=lambda c: c["act"]["at"])
        lane = changes[0]["from"] if changes else project["operator_lane"]
        for change in changes:
            if change["act"]["at"] <= at:
                lane = change["to"]
        return lane

    def component_lanes(self, component_ids) -> set:
        lanes = set(LANES)
        for cid in component_ids:
            comp = self.components.get(cid)
            if comp is not None:
                lanes &= set(comp["allowed_lanes"])
        return lanes

    def computed_eligible(self, artifact: dict) -> set:
        prov = artifact["provenance"]
        lanes = self.component_lanes(e["component_id"] for e in prov["license_chain"])
        terms = self.ids["import-terms"].get(prov.get("import_terms_id")) if prov.get("import_terms_id") else None
        if terms is not None:
            lanes &= set(terms["eligible_lanes"])
        for parent in prov["parents"]:
            if parent["edge"] in PROPAGATING and parent["sha256"] in self.artifacts:
                lanes &= set(self.artifacts[parent["sha256"]]["provenance"]["eligible_lanes"])
        return lanes

    def closure(self, sha: str) -> list[str]:
        """The artifact and every ancestor reachable through derived_from and converted_from edges."""
        seen: set[str] = set()
        stack = [sha]
        while stack:
            current = stack.pop()
            if current in seen or current not in self.artifacts:
                continue
            seen.add(current)
            for parent in self.artifacts[current]["provenance"]["parents"]:
                if parent["edge"] in PROPAGATING:
                    stack.append(parent["sha256"])
        return sorted(seen)

    def register_entry(self, component_id: str) -> dict | None:
        comp = self.components.get(component_id)
        if comp is None:
            return None
        return {"component_id": component_id, "code_license": comp["code_license"],
                "weights_license": comp["weights_license"], "obligations": comp["obligations"]}

    def self_hash_ok(self, doc: dict, field: str) -> bool:
        return doc[field] == self_hash(doc, field)
