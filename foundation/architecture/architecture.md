# VELYNX Architecture

## Layered Architecture

```
┌──────────────────────────────────────────────┐
│                  Program D                    │
│         Audit & Falsification Protocol        │
├──────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │Program A │  │Program B │  │ Program C  │  │
│  │Retrieval │  │Soul Graph│  │ Cognitive  │  │
│  │          │  │          │  │   Stack    │  │
│  └────┬─────┘  └────┬─────┘  └──────┬─────┘  │
│       │              │               │        │
│  ┌────┴──────────────┴───────────────┴─────┐  │
│  │           Core Primitives               │  │
│  │  Predictors │ MDL │ Emergence │ Metrics  │  │
│  └─────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────┐  │
│  │           Infrastructure                │  │
│  │  App │ DB │ Runtime │ Config │ Frontend │  │
│  └─────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

## Core Scientific Primitives

1. **Predictors** (`core/predictors/`): Dirichlet-Markov conjugate prior predictor
2. **MDL** (`core/mdl/`): Minimum Description Length growth trigger and concept birth
3. **Emergence** (`core/emergence/`): Emergence statistics and null-referenced tests
4. **Measurement** (`core/measurement/`): Proper scoring rules, metrics, observability

## Program Layer

- **Program A** (`program_a/`): Retrieval and NLP — live-truth calibration
- **Program B** (`program_b/`): Soul Graph — affective indexing
- **Program C** (`program_c/`): Cognitive stack — predictive processing core

## Infrastructure Layer

- **infra/app/**: FastAPI entry point, routes, middleware
- **infra/database/**: DB engine, models, migrations
- **infra/runtime/**: Event bus, monitoring, tracing
- **infra/ops/**: Circuit breakers, health, supervisor
- **infra/config/**: JSON configuration
- **infra/frontend/**: React/Vite UI
