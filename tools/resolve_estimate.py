"""Resolve only explicitly scoped, labeled estimates; never manufacture a rate."""

def _matches(estimate_context, request):
    if estimate_context["model_id"] != request.get("model_id"):
        return False
    for key in ("sku", "dock_variant", "firmware", "integration_id", "integration_version", "reservoir", "action"):
        value = estimate_context[key]
        if value is not None and request.get(key) != value:
            return False
    settings = request.get("settings", {})
    return all(value is None or settings.get(key) == value for key, value in estimate_context["settings"].items())


def resolve_estimate(records, context):
    """Return a displayable runtime estimate or explicit unknown.

    Callers must present ``label`` and ``limitations``; this result is never an
    approved profile, measurement, or completion-counter proof.
    """
    candidates = [r for r in records if r["kind"] == "estimate" and r["estimate_readiness"] == "labeled_runtime_estimate" and _matches(r["context"], context)]
    if not candidates:
        return {"status": "unknown", "reason": "no scoped, source-backed estimate"}
    candidate = sorted(candidates, key=lambda r: r["id"])[0]
    return {"status": "labeled_estimate", "id": candidate["id"], "quantity": candidate["quantity"], "source_type": candidate["source_type"], "confidence": candidate["confidence"], "label": candidate["label"], "limitations": candidate["limitations"], "basis_ids": candidate["basis_ids"]}
