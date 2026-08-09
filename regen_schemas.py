"""Regenerate schemas/lske/*.schema.json from the canonical dicts (R9-2 reviewable diff)."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from v2.lske.schema import COLLECTION_SPECS, all_schemas  # noqa: E402

SCHEMA_DIR = ROOT / "schemas" / "lske"


def _serialized(schema):
    return (json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main() -> int:
    schemas = all_schemas()
    assert len(schemas) == 23, len(schemas)
    assert list(schemas) == ["record", *(s.key for s in COLLECTION_SPECS), "relation", "obs2"]
    changed = []
    for name, schema in schemas.items():
        filename = "record.schema.json" if name == "record" else f"{name}.schema.json"
        path = SCHEMA_DIR / filename
        payload = _serialized(schema)
        if not path.exists() or path.read_bytes() != payload:
            path.write_bytes(payload)
            changed.append(filename)
    print(f"regenerated {len(changed)} of {len(schemas)} schema files")
    for filename in changed:
        print("  ", filename)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
