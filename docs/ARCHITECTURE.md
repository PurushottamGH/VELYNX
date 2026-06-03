# Architecture

## High-level flow

1. **Learning tutor** handles deterministic basics (math, grammar, definitions).
2. **Curriculum** resolves staged lessons and tracks mastery via permanence.
3. **Seed knowledge** handles lightweight deterministic answers.
4. **Associative memory** recalls confident prior answers.
5. **Retrieval pipeline** runs intent decomposition, multi-source retrieval, truth filtering, contradiction analysis, reasoning, and synthesis.

## Staged curriculum

The staged curriculum is stored in JSON for easy iteration and loaded at runtime with a Python fallback:

- Curriculum data: [data/curriculum.json](data/curriculum.json)
- Loader + fallback: [backend/learning/curriculum.py](backend/learning/curriculum.py)

Each lesson includes:

- `id`, `title`, `prompt`, `expected_answer`, `teaching_answer`
- `answer_type`, `aliases`, `prerequisites`, `mastery_threshold`
- `cognitive_layer` (symbols, quantity, grammar, logic, abstract, emotion, metacognition)
- `domains` (math, language, etc.)

Stages are advisory groupings used to track the learning order and describe system intent.

## Cognitive layer threading

The system derives a `cognitive_layer` signal and threads it through the pipeline:

- Lesson matching returns `cognitive_layers` for deterministic answers.
- Intent decomposition derives `cognitive_layer` and loads learned rules filtered to that layer.
- Reasoning output exposes the layer for debug and memory tagging.

Key files:

- [backend/pipeline/intent_engine.py](backend/pipeline/intent_engine.py)
- [backend/pipeline/constitution_loader.py](backend/pipeline/constitution_loader.py)
- [backend/pipeline/reasoning_core.py](backend/pipeline/reasoning_core.py)
- [backend/app/main.py](backend/app/main.py)

## Permanence and strategy learning

Permanence records confidence and strategy preference scores. Both are now layer-aware using composite keys:

- Confidence: `layer::fact`
- Strategy scores: `layer::query_type`

See [backend/learning/permanence.py](backend/learning/permanence.py) and
[backend/learning/strategy_optimizer.py](backend/learning/strategy_optimizer.py).

## Living constitution

Rules learned from feedback carry `cognitive_layer` and `status` metadata. Rendering can filter by layer
so the reasoning layer only applies relevant rules.

- Rule storage: [backend/learning/living_constitution.py](backend/learning/living_constitution.py)
- Rule derivation: [backend/learning/rule_deriver.py](backend/learning/rule_deriver.py)

## Feedback loop

Feedback strengthens or weakens permanence and learns strategy preferences with layer context.

- [backend/learning/online_learner.py](backend/learning/online_learner.py)
