import sys
from pathlib import Path
import importlib

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.learning import permanence


def test_permanence_persistence(tmp_path, monkeypatch) -> None:
    # Use a temp data path to avoid clobbering real state
    test_file = tmp_path / "permanence.json"
    # reload module with custom path by creating a new PermanenceLayer
    layer = permanence.PermanenceLayer(path=test_file)

    fact = "unit test: persistence survives restart"
    # initial confidence
    initial = layer.confidence(fact)
    assert initial == 0.5

    # reinforce and persist
    layer.reinforce(fact, source="unittest", delta=0.2)
    after = layer.confidence(fact)
    assert after > initial

    # Simulate restart by reloading permanence module and creating new layer
    importlib.reload(permanence)
    new_layer = permanence.PermanenceLayer(path=test_file)
    assert new_layer.confidence(fact) == after
