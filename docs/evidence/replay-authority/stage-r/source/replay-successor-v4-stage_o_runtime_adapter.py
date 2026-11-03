"""Hypothetical v4 runtime adapter status for an uninstalled store."""

from typing import Any, Dict, Optional


def candidate_observation() -> dict:
    return {
        "schema_version": 1,
        "record_type": "replay-successor-runtime-observation-v1",
        "source": "repository-hypothetical",
        "active_binding_version": 3,
        "installed": False,
        "installer_sha256": None,
        "review_sha256": None,
        "authorization_sha256": None,
        "store_device": None,
        "store_inode": None,
        "budget_amendment_sha256": None,
        "operator_per_run_approval_sha256": None,
        "execution_requested": False,
    }


def adapter_status(observation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    value = candidate_observation() if observation is None else observation
    if value != candidate_observation():
        raise ValueError("runtime observation must remain uninstalled")
    return {
        "schema_version": 1,
        "record_type": "replay-successor-runtime-adapter-status-v1",
        "implementation_status": "source-prepared-unissued",
        "gates": {
            "source_prepared": "pass",
            "independent_review": "not-run",
            "operator_authorization": "not-run",
            "protected_installation": "not-run",
            "replay_execution": "blocked",
        },
        "execution_authorized": False,
        "allowed_mutations": [],
    }
