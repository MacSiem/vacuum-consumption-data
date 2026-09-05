"""Expand the frozen MIoT index into auditable, deliberately incomplete dispositions."""
import json

from tools.validate import ROOT


def report():
    raw = json.loads((ROOT / "data" / "inventory" / "miot-specifications.json").read_text())
    records = []
    for model in raw["models"]:
        status = model["status"]
        records.append({
            "protocol_id": model["model_id"],
            "spec_urn": model["spec_urn"],
            "source_url": model["url"],
            "source_sha256": model["source_sha256"],
            "retail_sku": model["marketing_model"],
            "disposition": "unknown_retail_and_mopping" if status == "spec_extracted_not_hardware_verified" else "needs_review",
            "confidence": "unknown",
            "owner": "manufacturer/region researcher",
            "next_step": "Verify a public regional retail SKU and independent mopping capability; protocol presence alone is insufficient.",
            "unknowns": model["unknowns"],
        })
    return {
        "schema_version": 2,
        "source": raw["source"],
        "cutoff_date": raw["cutoff_date"],
        "protocol_id_denominator": len(records),
        "retail_denominator": "unknown",
        "global_inventory_complete": False,
        "records": records,
    }


if __name__ == "__main__":
    payload = report()
    path = ROOT / "reports" / "miot-inventory-dispositions.json"
    path.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"protocol_id_denominator": payload["protocol_id_denominator"], "global_inventory_complete": False}))
