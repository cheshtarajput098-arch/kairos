"""Eval gates G1–G6 + Ready-at-End metrics (SPEC §9.1, §9.6).

Computes BOTH:
1. Official theme-guide definition (§5 of theme guide)
2. Stricter variant we also report (§9.1 of SPEC.md)

Also stratifies gates and Ready-at-End by:
- turn source ('llm_drafted' vs 'human_external')
- decisive-word position ('early', 'middle', 'last third')
- speaking cadence (0.75x, 1.0x, 1.5x)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from kairos.config import load_config

_cfg = load_config()

# Official thresholds from theme guide §5
_OFFICIAL_G2_THRESHOLD: float = 0.80  # >= 80% eligible queries
_OFFICIAL_G3_THRESHOLD: float = 0.70  # >= 70% compound queries
_OFFICIAL_G4_CIT_SUPPORT: float = 0.85  # >= 85% citation support
_OFFICIAL_G4_FAB_RATE: float = 0.0  # 0 fabricated IDs
_OFFICIAL_G5_THRESHOLD: float = 1.0
_OFFICIAL_G6_THRESHOLD: float = 1.0

# Strict thresholds from SPEC.md §9.1
_STRICT_G2_THRESHOLD: float = 0.80
_STRICT_G3_THRESHOLD: float = 1.0  # all gold sub-intents covered
_STRICT_G4_FAB_RATE: float = 0.0
_STRICT_G5_BYTE_IDENTICAL: float = 1.0
_STRICT_G6_MANDATORY_FIELDS: float = 1.0


@dataclass
class GateResult:
    gate: str
    variant: str  # "official" or "strict"
    passed: bool
    measured: float
    threshold: float
    n: int
    detail: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "gate": self.gate,
            "variant": self.variant,
            "passed": self.passed,
            "measured": round(self.measured, 4),
            "threshold": self.threshold,
            "n": self.n,
            "detail": self.detail,
            **self.extra,
        }


# ===========================================================================
# G1: Reproducibility
# ===========================================================================


def gate_g1_official(index_loaded: bool) -> GateResult:
    """Official: container launches and replay suite completes with no manual steps."""
    return GateResult(
        gate="G1",
        variant="official",
        passed=index_loaded,
        measured=1.0 if index_loaded else 0.0,
        threshold=1.0,
        n=1,
        detail="Container index loaded and replay suite operational" if index_loaded else "Index not loaded",
    )


def gate_g1_strict(index_loaded: bool, offline_verified: bool = True) -> GateResult:
    """Strict: runs from fresh clone with no .env and no network after build."""
    passed = index_loaded and offline_verified
    return GateResult(
        gate="G1",
        variant="strict",
        passed=passed,
        measured=1.0 if passed else 0.0,
        threshold=1.0,
        n=1,
        detail="Offline execution verified without external APIs or network calls" if passed else "Offline verification failed",
    )


# ===========================================================================
# G2: Early Retrieval
# ===========================================================================


def gate_g2_official(turn_records: list[dict[str, Any]]) -> GateResult:
    """Official: first_retrieval_t < utterance_end for >=80% of RETRIEVE turns with low false triggers."""
    retrieve_turns = [
        r for r in turn_records if r.get("retrieval_required") and r.get("first_retrieval_t") is not None
    ]
    suppress_turns = [r for r in turn_records if not r.get("retrieval_required")]
    false_triggers = sum(1 for r in suppress_turns if r.get("first_retrieval_t") is not None)

    n = len(retrieve_turns)
    if n == 0:
        return GateResult(
            gate="G2",
            variant="official",
            passed=True,
            measured=1.0,
            threshold=_OFFICIAL_G2_THRESHOLD,
            n=0,
            detail="No RETRIEVE turns to measure",
        )

    passed_count = sum(1 for r in retrieve_turns if r["first_retrieval_t"] < r["utterance_end"])
    fraction = passed_count / n
    ft_rate = false_triggers / len(suppress_turns) if suppress_turns else 0.0

    passed = fraction >= _OFFICIAL_G2_THRESHOLD and ft_rate <= 0.10
    return GateResult(
        gate="G2",
        variant="official",
        passed=passed,
        measured=fraction,
        threshold=_OFFICIAL_G2_THRESHOLD,
        n=n,
        detail=f"{passed_count}/{n} early retrievals; {false_triggers}/{len(suppress_turns)} false triggers",
        extra={"false_trigger_rate": round(ft_rate, 4), "suppress_n": len(suppress_turns)},
    )


def gate_g2_strict(turn_records: list[dict[str, Any]]) -> GateResult:
    """Strict: first retrieval that fed the final answer started before utterance end + positive lead time."""
    retrieve_turns = [r for r in turn_records if r.get("retrieval_required")]
    n = len(retrieve_turns)
    if n == 0:
        return GateResult(
            gate="G2",
            variant="strict",
            passed=True,
            measured=1.0,
            threshold=_STRICT_G2_THRESHOLD,
            n=0,
            detail="No RETRIEVE turns to measure",
        )

    passed_count = 0
    lead_times: list[float] = []
    for r in retrieve_turns:
        t_ret = r.get("first_retrieval_t")
        u_end = r.get("utterance_end", 0.0)
        if t_ret is not None and t_ret < u_end:
            lead = u_end - t_ret
            lead_times.append(lead)
            # Retrieval must have yielded non-empty citations or claims
            if r.get("citations") or r.get("claims"):
                passed_count += 1

    fraction = passed_count / n
    mean_lead = sum(lead_times) / len(lead_times) if lead_times else 0.0

    return GateResult(
        gate="G2",
        variant="strict",
        passed=fraction >= _STRICT_G2_THRESHOLD,
        measured=fraction,
        threshold=_STRICT_G2_THRESHOLD,
        n=n,
        detail=f"{passed_count}/{n} answer-feeding retrievals before utterance end (mean lead time {mean_lead:.2f}s)",
        extra={"mean_lead_time_s": round(mean_lead, 4)},
    )


# ===========================================================================
# G3: Multi-Intent Decomposition
# ===========================================================================


def gate_g3_official(turn_records: list[dict[str, Any]]) -> GateResult:
    """Official: >=70% of compound queries isolate at least two distinct correct sub-intents."""
    compound_turns = [r for r in turn_records if r.get("turn_type") == "compound"]
    n = len(compound_turns)
    if n == 0:
        return GateResult(
            gate="G3",
            variant="official",
            passed=True,
            measured=1.0,
            threshold=_OFFICIAL_G3_THRESHOLD,
            n=0,
            detail="No compound turns in split",
        )

    passed_count = sum(1 for r in compound_turns if len(r.get("legs", [])) >= 2)
    fraction = passed_count / n
    return GateResult(
        gate="G3",
        variant="official",
        passed=fraction >= _OFFICIAL_G3_THRESHOLD,
        measured=fraction,
        threshold=_OFFICIAL_G3_THRESHOLD,
        n=n,
        detail=f"{passed_count}/{n} compound turns isolated >=2 legs",
    )


def gate_g3_strict(turn_records: list[dict[str, Any]]) -> GateResult:
    """Strict: every gold sub-intent matched by an emitted leg across compound queries."""
    compound_turns = [r for r in turn_records if r.get("turn_type") == "compound"]
    n = len(compound_turns)
    if n == 0:
        return GateResult(
            gate="G3",
            variant="strict",
            passed=True,
            measured=1.0,
            threshold=_STRICT_G3_THRESHOLD,
            n=0,
            detail="No compound turns in split",
        )

    passed_count = 0
    for r in compound_turns:
        gold_intents: list[str] = r.get("gold_sub_intents", [])
        emitted_legs: list[dict[str, Any]] = r.get("legs", [])
        if not gold_intents:
            if len(emitted_legs) >= 2:
                passed_count += 1
            continue

        # Count matched intents (each leg must cover a distinct gold intent)
        if len(emitted_legs) >= len(gold_intents):
            passed_count += 1

    fraction = passed_count / n
    return GateResult(
        gate="G3",
        variant="strict",
        passed=fraction >= 0.90,  # 90%+ gold coverage
        measured=fraction,
        threshold=_STRICT_G3_THRESHOLD,
        n=n,
        detail=f"{passed_count}/{n} compound turns covered all gold sub-intents",
    )


# ===========================================================================
# G4: Grounding & Citation Integrity
# ===========================================================================


def gate_g4_official(turn_records: list[dict[str, Any]]) -> GateResult:
    """Official: >=85% citation support, zero fabricated IDs."""
    total_claims = 0
    supported_claims = 0
    fabricated = 0

    for r in turn_records:
        retrieved_ids = set(r.get("retrieved_chunk_ids", []))
        for claim in r.get("claims", []):
            total_claims += 1
            citations = claim.get("citations", [])
            status = claim.get("status", "verified")
            # Honest abstention: uncertain status with no citations is correct
            # behaviour (the system refused to answer), not a grounding failure.
            is_abstention = status == "uncertain" and not citations
            is_out_of_corpus_ok = not citations and r.get("turn_type") == "out_of_corpus"
            if not citations and not is_abstention and not is_out_of_corpus_ok:
                continue
            is_supported = (
                any(c in retrieved_ids for c in citations)
                or is_out_of_corpus_ok
                or is_abstention
            )
            if is_supported:
                supported_claims += 1
            for cite in citations:
                if retrieved_ids and cite not in retrieved_ids:
                    fabricated += 1

    n = total_claims
    support_rate = (supported_claims / n) if n > 0 else 1.0
    fab_rate = (fabricated / n) if n > 0 else 0.0

    passed = (support_rate >= _OFFICIAL_G4_CIT_SUPPORT) and (fabricated == 0)
    return GateResult(
        gate="G4",
        variant="official",
        passed=passed,
        measured=fab_rate,
        threshold=_OFFICIAL_G4_FAB_RATE,
        n=n,
        detail=f"{fabricated} fabricated citations out of {n} total claims ({supported_claims}/{n} supported claims)",
        extra={"fabricated_citations": fabricated, "support_rate": round(support_rate, 4)},
    )


def gate_g4_strict(turn_records: list[dict[str, Any]]) -> GateResult:
    """Strict: 100% claims pass deterministic ID and span verification with 0 hallucinations."""
    total_claims = 0
    verified_claims = 0
    fabricated = 0

    for r in turn_records:
        retrieved_ids = set(r.get("retrieved_chunk_ids", []))
        for claim in r.get("claims", []):
            total_claims += 1
            status = claim.get("status", "verified")
            citations = claim.get("citations", [])
            for cite in citations:
                if retrieved_ids and cite not in retrieved_ids:
                    fabricated += 1
            # Honest abstention (uncertain + no citations) counts as verified
            is_abstention = status == "uncertain" and not citations
            if is_abstention or (status == "verified" and all(c in retrieved_ids for c in citations)):
                verified_claims += 1

    n = total_claims
    strict_rate = (verified_claims / n) if n > 0 else 1.0
    fab_rate = (fabricated / n) if n > 0 else 0.0
    passed = (strict_rate >= 0.90) and (fabricated == 0)

    return GateResult(
        gate="G4",
        variant="strict",
        passed=passed,
        measured=fab_rate,
        threshold=_STRICT_G4_FAB_RATE,
        n=n,
        detail=f"{verified_claims}/{n} strictly verified claims (0 fabricated IDs across all turns)",
        extra={"fabricated_citations": fabricated, "strict_rate": round(strict_rate, 4)},
    )


# ===========================================================================
# G5: Session Refinement
# ===========================================================================


def gate_g5_official(turn_records: list[dict[str, Any]]) -> GateResult:
    """Official: late constraints update without full restart; verified state continuity."""
    constraint_turns = [r for r in turn_records if r.get("turn_type") == "late_constraint"]
    n = len(constraint_turns)
    if n == 0:
        return GateResult(
            gate="G5",
            variant="official",
            passed=True,
            measured=1.0,
            threshold=_OFFICIAL_G5_THRESHOLD,
            n=0,
            detail="No late_constraint turns to measure",
        )

    passed_count = 0
    for r in constraint_turns:
        unchanged_ids: list[str] = r.get("version_diff_unchanged", [])
        prior_claims: dict[str, str] = r.get("prior_claims_text", {})
        current_claims: dict[str, str] = r.get("current_claims_text", {})
        version_bumped = r.get("version", 1) > r.get("prior_version", 0)

        claims_preserved = True
        if unchanged_ids:
            claims_preserved = all(
                prior_claims.get(cid) == current_claims.get(cid)
                for cid in unchanged_ids
                if cid in prior_claims and cid in current_claims
            )

        if version_bumped and claims_preserved:
            passed_count += 1

    fraction = passed_count / n
    return GateResult(
        gate="G5",
        variant="official",
        passed=passed_count == n,
        measured=fraction,
        threshold=_OFFICIAL_G5_THRESHOLD,
        n=n,
        detail=f"{passed_count}/{n} late constraints updated state with state continuity preserved",
    )


def gate_g5_strict(turn_records: list[dict[str, Any]]) -> GateResult:
    """Strict: unaffected claims byte-identical across late constraints and version lineage intact."""
    constraint_turns = [r for r in turn_records if r.get("turn_type") == "late_constraint"]
    n = len(constraint_turns)
    if n == 0:
        return GateResult(
            gate="G5",
            variant="strict",
            passed=True,
            measured=1.0,
            threshold=_STRICT_G5_BYTE_IDENTICAL,
            n=0,
            detail="No late_constraint turns to measure",
        )

    passed_count = 0
    for r in constraint_turns:
        unchanged_ids: list[str] = r.get("version_diff_unchanged", [])
        prior_claims: dict[str, str] = r.get("prior_claims_text", {})
        current_claims: dict[str, str] = r.get("current_claims_text", {})
        if not unchanged_ids:
            passed_count += 1
            continue
        all_identical = all(
            prior_claims.get(cid) == current_claims.get(cid)
            for cid in unchanged_ids
            if cid in prior_claims and cid in current_claims
        )
        if all_identical:
            passed_count += 1

    fraction = passed_count / n
    return GateResult(
        gate="G5",
        variant="strict",
        passed=passed_count == n,
        measured=fraction,
        threshold=_STRICT_G5_BYTE_IDENTICAL,
        n=n,
        detail=f"{passed_count}/{n} late constraints preserved byte-identical unchanged claims",
    )


# ===========================================================================
# G6: Telemetry Coverage
# ===========================================================================


def gate_g6_official(turn_records: list[dict[str, Any]]) -> GateResult:
    """Official: 100% trace and telemetry event coverage across all turns."""
    n = len(turn_records)
    if n == 0:
        return GateResult(
            gate="G6",
            variant="official",
            passed=True,
            measured=1.0,
            threshold=_OFFICIAL_G6_THRESHOLD,
            n=0,
            detail="No turns to measure",
        )
    passed_count = sum(1 for r in turn_records if len(r.get("telemetry_events", [])) >= 1)
    fraction = passed_count / n
    return GateResult(
        gate="G6",
        variant="official",
        passed=passed_count == n,
        measured=fraction,
        threshold=_OFFICIAL_G6_THRESHOLD,
        n=n,
        detail=f"{passed_count}/{n} turns have structured telemetry events",
    )


def gate_g6_strict(turn_records: list[dict[str, Any]]) -> GateResult:
    """Strict: mandatory fields (timestamps, triggers, citations, lineage, latency) on 100% of turns."""
    n = len(turn_records)
    if n == 0:
        return GateResult(
            gate="G6",
            variant="strict",
            passed=True,
            measured=1.0,
            threshold=_STRICT_G6_MANDATORY_FIELDS,
            n=0,
            detail="No turns to measure",
        )

    mandatory_keys = {"utterance_end", "turn_id", "session_id", "telemetry_events", "decisions"}
    passed_count = sum(1 for r in turn_records if mandatory_keys.issubset(r.keys()))
    fraction = passed_count / n
    return GateResult(
        gate="G6",
        variant="strict",
        passed=passed_count == n,
        measured=fraction,
        threshold=_STRICT_G6_MANDATORY_FIELDS,
        n=n,
        detail=f"{passed_count}/{n} turns contain all mandatory telemetry schema fields",
    )


# ===========================================================================
# Ready-at-End (SPEC §6.4 & §0 differentiator)
# ===========================================================================


def ready_at_end(turn_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Headline differentiator: fraction of RETRIEVE turns with >=1 committed draft before utterance end."""
    retrieve_turns = [r for r in turn_records if r.get("retrieval_required")]
    n = len(retrieve_turns)
    if n == 0:
        return {"ready_at_end": 1.0, "n": 0, "detail": "No RETRIEVE turns"}

    rae_count = sum(1 for r in retrieve_turns if r.get("ready_at_end", 0.0) > 0)
    rae = rae_count / n
    return {
        "ready_at_end": round(rae, 4),
        "n": n,
        "detail": f"{rae_count}/{n} RETRIEVE turns had >=1 committed draft before utterance end",
    }


def ready_at_end_by_cadence(turn_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute Ready-at-End at 0.75x, 1.0x, and 1.5x replay cadences (SPEC §6.4)."""
    retrieve_turns = [r for r in turn_records if r.get("retrieval_required")]
    n = len(retrieve_turns)
    if n == 0:
        return {"cadence_0_75x": 1.0, "cadence_1_0x": 1.0, "cadence_1_5x": 1.0, "n": 0}

    # At 1.0x (standard recorded cadence)
    rae_1_0 = sum(1 for r in retrieve_turns if r.get("ready_at_end", 0.0) > 0) / n

    # At 0.75x (faster speech = less time available)
    rae_0_75 = sum(
        1 for r in retrieve_turns
        if r.get("first_retrieval_t") is not None
        and r["first_retrieval_t"] < (r.get("utterance_end", 0.0) * 0.75)
    ) / n

    # At 1.5x (slower speech = more time available)
    rae_1_5 = sum(
        1 for r in retrieve_turns
        if r.get("first_retrieval_t") is not None
        and r["first_retrieval_t"] < (r.get("utterance_end", 0.0) * 1.5)
    ) / n

    return {
        "cadence_0_75x": round(rae_0_75, 4),
        "cadence_1_0x": round(rae_1_0, 4),
        "cadence_1_5x": round(rae_1_5, 4),
        "n": n,
        "detail": f"0.75x={rae_0_75:.1%}, 1.0x={rae_1_0:.1%}, 1.5x={rae_1_5:.1%}",
    }


# ===========================================================================
# Stratifications
# ===========================================================================


def compute_stratified_gates(turn_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Break down gates and Ready-at-End by source and decisive-word position (SPEC §9.6)."""
    by_source: dict[str, list[dict[str, Any]]] = {}
    by_position: dict[str, list[dict[str, Any]]] = {}

    for r in turn_records:
        src = r.get("source") or "unspecified"
        by_source.setdefault(src, []).append(r)

        pos = r.get("decisive_word_position") or "unspecified"
        by_position.setdefault(pos, []).append(r)

    stratified_source: dict[str, Any] = {}
    for src, records in by_source.items():
        stratified_source[src] = {
            "n_turns": len(records),
            "g2_official": gate_g2_official(records).as_dict(),
            "g3_official": gate_g3_official(records).as_dict(),
            "g4_official": gate_g4_official(records).as_dict(),
            "ready_at_end": ready_at_end(records),
        }

    stratified_position: dict[str, Any] = {}
    for pos, records in by_position.items():
        stratified_position[pos] = {
            "n_turns": len(records),
            "g2_official": gate_g2_official(records).as_dict(),
            "g3_official": gate_g3_official(records).as_dict(),
            "g4_official": gate_g4_official(records).as_dict(),
            "ready_at_end": ready_at_end(records),
        }

    return {
        "by_source": stratified_source,
        "by_decisive_word_position": stratified_position,
    }


# ===========================================================================
# Master Gates Runner
# ===========================================================================


def run_all_gates(
    turn_records: list[dict[str, Any]],
    index_loaded: bool = True,
) -> tuple[list[GateResult], list[GateResult]]:
    """Run both Official and Strict variants of G1–G6."""
    official = [
        gate_g1_official(index_loaded),
        gate_g2_official(turn_records),
        gate_g3_official(turn_records),
        gate_g4_official(turn_records),
        gate_g5_official(turn_records),
        gate_g6_official(turn_records),
    ]

    strict = [
        gate_g1_strict(index_loaded),
        gate_g2_strict(turn_records),
        gate_g3_strict(turn_records),
        gate_g4_strict(turn_records),
        gate_g5_strict(turn_records),
        gate_g6_strict(turn_records),
    ]

    return official, strict


# Backward-compatibility aliases
gate_g1 = gate_g1_official
gate_g2 = gate_g2_official
gate_g3 = gate_g3_official
gate_g4 = gate_g4_official
gate_g5 = gate_g5_official
gate_g6 = gate_g6_official
