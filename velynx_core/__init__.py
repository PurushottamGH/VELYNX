"""
VELYNX CORE v2
Self-reasoning AI — graph-native, self-learning, self-improving.
"""

from .memory import VelynxMemory, Concept, Relation, RetrievedConcept
from .brain import VelynxBrain, VelynxAnswer
from .learner import VelynxLearner, LearningItem
from .self_coder import VelynxSelfCoder

__version__ = "2.0.0"
__all__ = [
    "VelynxMemory", "Concept", "Relation", "RetrievedConcept",
    "VelynxBrain", "VelynxAnswer",
    "VelynxLearner", "LearningItem",
    "VelynxSelfCoder",
]