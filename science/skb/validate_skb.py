from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "SKB_RECORDS_v1.0.yaml"

COLLECTIONS = {
    "hypotheses": "HYP",
    "experiments": "EXP",
    "mechanisms": "MEC",
    "assumptions": "ASM",
    "unknowns": "UNK",
    "scientific_debt": "SDEBT",
    "negative_results": "NEG",
    "observations": "OBS",
    "evidence": "EVD",
    "decisions": "DEC",
    "theories": "THY",
}

ID_PATTERN = re.compile(r"^(HYP|EXP|MEC|ASM|UNK|SDEBT|NEG|OBS|EVD|DEC|THY)-2026-\d{4}(?:-R\d{4})?$")
REFERENCE_KEYS = {
    "hypotheses",
    "experiments",
    "mechanisms",
    "assumptions",
    "unknowns",
    "scientific_debt",
    "negative_results",
    "observations",
    "evidence",
    "decisions",
    "theories",
    "evidence_for",
    "evidence_against",
    "unresolved_evidence",
    "needed_by",
    "affects",
    "source_observations",
    "target",
    "affected_objects",
    "superseded_by",
    "source",
    "observation",
}


def iter_refs(value):
    if isinstance(value, str):
        if ID_PATTERN.match(value):
            yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_refs(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_refs(item)


def main() -> None:
    data = yaml.safe_load(RECORDS.read_text(encoding="utf-8"))
    errors: list[str] = []
    all_ids: dict[str, str] = {}

    for collection, prefix in COLLECTIONS.items():
        records = data.get(collection, [])
        if not isinstance(records, list):
            errors.append(f"{collection} is not a list")
            continue
        for record in records:
            record_id = record.get("id")
            if not isinstance(record_id, str) or not ID_PATTERN.match(record_id):
                errors.append(f"invalid id in {collection}: {record_id!r}")
                continue
            if not record_id.startswith(prefix + "-"):
                errors.append(f"wrong prefix for {record_id} in {collection}")
            if record_id in all_ids:
                errors.append(f"duplicate id {record_id} in {collection} and {all_ids[record_id]}")
            all_ids[record_id] = collection

    execution_ids = set()
    for experiment in data.get("experiments", []):
        for execution_id in experiment.get("executions", []):
            if not re.match(r"^EXP-2026-\d{4}-R\d{4}$", execution_id):
                errors.append(f"invalid execution id {execution_id}")
            if execution_id in execution_ids:
                errors.append(f"duplicate execution id {execution_id}")
            execution_ids.add(execution_id)

    known_ids = set(all_ids) | execution_ids

    def walk(node, path="root"):
        if isinstance(node, dict):
            for key, value in node.items():
                next_path = f"{path}.{key}"
                if key in REFERENCE_KEYS:
                    for ref in iter_refs(value):
                        if ref not in known_ids:
                            errors.append(f"unresolved reference {ref} at {next_path}")
                walk(value, next_path)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]")

    walk(data)

    for evidence in data.get("evidence", []):
        if not evidence.get("source_observations"):
            errors.append(f"evidence without source observations: {evidence['id']}")

    for relation in data.get("relations", []):
        for endpoint in ("from", "to"):
            ref = relation.get(endpoint)
            if ref not in known_ids:
                errors.append(f"relation has unknown {endpoint}: {ref}")

    if data.get("theories"):
        errors.append("SKB v1.0 declares theories despite living-model no-theory state")

    if errors:
        print("SKB VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    counts = {name: len(data.get(name, [])) for name in COLLECTIONS}
    counts["relations"] = len(data.get("relations", []))
    print("SKB VALIDATION PASSED")
    for name, count in counts.items():
        print(f"{name}: {count}")
    print(f"execution_ids: {len(execution_ids)}")
    print(f"total_unique_record_ids: {len(all_ids)}")


if __name__ == "__main__":
    main()
