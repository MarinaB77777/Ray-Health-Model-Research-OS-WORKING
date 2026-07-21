# assessment/prognosis/prognosis.py

from assessment.mappings.resource_level_maps import (
    NOT_ENOUGH_DATA,
    build_level_profiles,
)


def _empty_counter():
    return {}


def _add_evidence(bucket, key, evidence):
    if key not in bucket:
        bucket[key] = []

    bucket[key].append(evidence)


def build_prognosis_layer(domain_scores: dict) -> dict:
    level_profiles = build_level_profiles(domain_scores)

    vulnerable_functions = _empty_counter()
    preserved_functions = _empty_counter()
    candidate_mechanisms = _empty_counter()

    for domain, profile in level_profiles.items():
        if profile.get("status") == NOT_ENOUGH_DATA:
            continue

        evidence = {
            "domain": domain,
            "level": profile.get("level"),
            "score": profile.get("score"),
            "resource_state": profile.get("resource_state"),
        }

        for function_name in profile.get("vulnerable_functions", []):
            _add_evidence(
                vulnerable_functions,
                function_name,
                evidence,
            )

        for function_name in profile.get("preserved_functions", []):
            _add_evidence(
                preserved_functions,
                function_name,
                evidence,
            )

        for mechanism_name in profile.get("candidate_mechanisms", []):
            _add_evidence(
                candidate_mechanisms,
                mechanism_name,
                evidence,
            )

    active_candidate_mechanisms = {
        name: evidence
        for name, evidence in candidate_mechanisms.items()
        if len(evidence) >= 2
    }

    weak_candidate_mechanisms = {
        name: evidence
        for name, evidence in candidate_mechanisms.items()
        if len(evidence) == 1
    }

    return {
        "ok": True,
        "layer": "prognosis_layer_v1",
        "level_profiles": level_profiles,
        "vulnerable_functions": vulnerable_functions,
        "preserved_functions": preserved_functions,
        "candidate_mechanisms": candidate_mechanisms,
        "active_candidate_mechanisms": active_candidate_mechanisms,
        "weak_candidate_mechanisms": weak_candidate_mechanisms,
        "rules": {
            "mechanism_candidate_requires_level_map": True,
            "active_candidate_requires_two_evidence_sources": True,
            "weak_candidate_is_not_forecast": True,
            "missing_data_must_not_be_invented": True,
        },
    }