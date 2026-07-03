VELYNX/
├── foundation/                          # Irreducible scientific substrate
│   ├── hypothesis/                      # Central hypothesis H*, sub-hypotheses H1/H2/H3
│   │   ├── central_hypothesis.md
│   │   ├── H1_calibration.md
│   │   ├── H2_affective_indexing.md
│   │   └── H3_emergent_development.md
│   ├── assumptions/                     # Three irreducible assumptions (I1/I2/I3)
│   │   ├── assumption_ledger.md
│   │   ├── assumption_coverage_matrix.csv
│   │   └── parameter_atlas.md
│   ├── kill_criteria/                   # Kill criteria K1–K10 (all wired)
│   │   ├── kill_criteria.md
│   │   └── kill_criteria_validation_report.md
│   ├── mathematics/                     # 5 primitives, provenance, variable graph
│   │   ├── mathematical_foundation.md
│   │   ├── variable_provenance.md
│   │   ├── variable_dependency_graph.graphml
│   │   └── variable_dependency_matrix.csv
│   ├── architecture/                    # Layer boundaries, module deps
│   │   ├── architecture.md
│   │   ├── dependency_graph.graphml
│   │   ├── dependency_matrix.csv
│   │   └── layer_diagram.mmd
│   └── novelty/                         # Novelty analysis vs 11 reference fields
│       ├── novelty_analysis.md
│       └── publication_test.md
│
├── core/                                # Reusable scientific machinery (5 primitives)
│   ├── predictors/                      # Growable predictor class
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── dirichlet_markov.py
│   ├── emergence/                       # Emergence statistics (NMI, held-out split)
│   │   ├── __init__.py
│   │   ├── emergence_statistic.py
│   │   └── null_referenced_test.py
│   ├── mdl/                             # MDL growth operator
│   │   ├── __init__.py
│   │   ├── mdl_growth.py
│   │   └── concept_birth_ledger.py
│   ├── measurement/                     # Log-loss, metrics, observability
│   │   ├── __init__.py
│   │   ├── proper_scoring.py
│   │   ├── metrics.py
│   │   └── observability.py
│   └── controls/                        # Null/baseline models
│       ├── __init__.py
│       ├── fixed_capacity.py
│       ├── random_growth.py
│       └── shuffled_input.py
│
├── experiments/                         # Self-contained experiments
│   ├── E0/                              # Emergence-vs-injection (decides H*)
│   │   ├── preregistration.md
│   │   ├── protocol.md
│   │   ├── run.py
│   │   ├── analysis.py
│   │   ├── detectors.py
│   │   ├── dataset.py
│   │   ├── leakage_check.py
│   │   └── paraphrases.json
│   ├── R1/                              # Free-energy ablation (72 exps, run)
│   │   ├── preregistration.md
│   │   ├── protocol.md
│   │   ├── run.py
│   │   └── analysis.py
│   ├── R3F/                             # Formal benchmark suite
│   │   ├── preregistration.md
│   │   ├── protocol.md
│   │   ├── run.py
│   │   └── analysis.py
│   ├── EXP1/                            # Calibration curve (H1)
│   │   ├── preregistration.md
│   │   ├── protocol.md
│   │   ├── run.py
│   │   └── analysis.py
│   ├── EXP2/                            # Affective indexing (H2)
│   │   ├── preregistration.md
│   │   ├── protocol.md
│   │   ├── run.py
│   │   └── analysis.py
│   ├── EXP3/                            # Minimal predictive organism (H3)
│   │   ├── preregistration.md
│   │   ├── protocol.md
│   │   ├── run.py
│   │   └── analysis.py
│   ├── EXP4/                            # Cycle bootstrapping
│   │   ├── preregistration.md
│   │   ├── protocol.md
│   │   ├── run.py
│   │   └── analysis.py
│   └── coverage/
│       └── experiment_coverage_matrix.csv
│
├── benchmarks/                          # Evaluation harnesses & shared benchmarks
│   ├── evaluation/
│   │   ├── benchmark_runner.py
│   │   ├── scenario_loader.py
│   │   ├── trial_runner.py
│   │   └── adversarial_tests.py
│   ├── cognition/
│   │   ├── cognition_benchmarks.py
│   │   ├── cognition_drift_monitor.py
│   │   ├── memory_retrieval_tests.py
│   │   └── planning_evaluator.py
│   ├── reflection/
│   │   ├── reflection_evaluator.py
│   │   └── reality_checks.py
│   ├── monitoring/
│   │   ├── runtime_profiler.py
│   │   ├── stability_monitor.py
│   │   └── session_replay.py
│   ├── hallucination/
│   │   └── hallucination_detector.py
│   └── failure/
│       └── failure_analysis.py
│
├── program_a/                           # Calibrated live-truth retrieval (product)
│   ├── retrieval/
│   │   ├── unified_retriever.py
│   │   ├── arxiv_client.py
│   │   ├── brave_client.py
│   │   ├── browser.py
│   │   ├── duckduckgo_client.py
│   │   ├── searxng_client.py
│   │   ├── tavily_client.py
│   │   ├── wiki_client.py
│   │   └── video_learner.py
│   └── nlp/
│       └── temporal_parser.py
│
├── program_b/                           # Soul Graph (authored artifact)
│   ├── soul_graph/
│   │   ├── soul_graph.py
│   │   └── soul_store.py
│   └── concepts/
│       └── concepts.json
│
├── program_c/                           # Symbolic-AGI stack (engineering-retained)
│   ├── cognition/
│   │   ├── perception.py
│   │   ├── reasoning_engine.py
│   │   ├── scenario_engine.py
│   │   ├── attention_modulator.py
│   │   ├── priority_router.py
│   │   ├── decision_policy.py
│   │   ├── concept_birth.py
│   │   ├── dream_state.py
│   │   ├── replay_engine.py
│   │   ├── sim_engine.py
│   │   ├── sim_detector.py
│   │   ├── viz_engine.py
│   │   ├── viz_detector.py
│   │   ├── predictive_core.py
│   │   ├── predictive_engine.py
│   │   ├── vector_prediction_core.py
│   │   └── unified_pipeline.py
│   ├── memory/
│   │   ├── knowledge_graph.py
│   │   ├── memory_graph.py
│   │   ├── episodic_memory.py
│   │   ├── episodic.py
│   │   ├── working_memory.py
│   │   ├── vector_store.py
│   │   ├── vector_backend.py
│   │   ├── embedding_service.py
│   │   ├── gpu_embedder.py
│   │   ├── concept_engine.py
│   │   ├── memory_manager.py
│   │   ├── memory_retriever.py
│   │   ├── memory_store.py
│   │   ├── memory_schemas.py
│   │   ├── crawler_index.py
│   │   ├── state_delta.py
│   │   ├── session.py
│   │   └── recall_logger.py
│   ├── learning/
│   │   ├── continuous_learner.py
│   │   ├── deep_learner.py
│   │   ├── online_learner.py
│   │   ├── night_learner.py
│   │   ├── curriculum.py
│   │   ├── feedback_loop.py
│   │   ├── gap_tracker.py
│   │   ├── knowledge_tutor.py
│   │   ├── living_constitution.py
│   │   ├── permanence.py
│   │   ├── source_trust.py
│   │   ├── strategy_optimizer.py
│   │   ├── rule_deriver.py
│   │   ├── proactive_cognition.py
│   │   └── failure_diagnosis.py
│   ├── knowledge/
│   │   ├── knowledge_engine.py
│   │   ├── consolidator.py
│   │   ├── epistemic_manager.py
│   │   ├── fact_extractor.py
│   │   ├── normalizer.py
│   │   ├── ontology_loader.py
│   │   ├── predicate_resolver.py
│   │   ├── schema_gatekeeper.py
│   │   ├── temporal_filter.py
│   │   ├── entity_bridge.py
│   │   ├── bridge.py
│   │   ├── voice_engine.py
│   │   ├── world_model_context.py
│   │   └── world_model_schema.py
│   ├── metacognition/
│   │   ├── meta_monitor.py
│   │   ├── adaptation_engine.py
│   │   ├── cognition_metrics.py
│   │   ├── confidence_calibrator.py
│   │   ├── pattern_analyzer.py
│   │   └── strategy_analyzer.py
│   ├── reflection/
│   │   ├── reflection_engine.py
│   │   ├── advanced_reflection.py
│   │   ├── confidence_estimator.py
│   │   ├── improvement_engine.py
│   │   └── reasoning_audit.py
│   ├── pipeline/
│   │   ├── agentic_loop.py
│   │   ├── inference_pipeline.py
│   │   ├── reasoning_core.py
│   │   ├── reasoning_wiring.py
│   │   ├── context_builder.py
│   │   ├── intent_engine.py
│   │   ├── query_rewriter.py
│   │   ├── knowledge_router.py
│   │   ├── retrieval_mesh.py
│   │   ├── synthesizer.py
│   │   ├── truth_filter.py
│   │   ├── contradiction.py
│   │   ├── resonance.py
│   │   ├── reflex.py
│   │   ├── constitution_loader.py
│   │   ├── seed_knowledge.py
│   │   ├── persistence.py
│   │   ├── self_router.py
│   │   ├── soul_router.py
│   │   └── reflection_router.py
│   ├── abstraction/
│   │   ├── belief_generator.py
│   │   ├── belief_models.py
│   │   ├── belief_store.py
│   │   ├── consolidation_runner.py
│   │   └── cross_seed_validator.py
│   ├── self_model/
│   │   ├── self_model.py
│   │   ├── identity_store.py
│   │   ├── health_monitor.py
│   │   ├── baseline_tracker.py
│   │   └── self_audit.py
│   ├── simulation/
│   │   ├── interface.py
│   │   ├── causal_evaluator.py
│   │   ├── logger.py
│   │   └── simulation_memory_context.py
│   ├── agency/
│   │   ├── action_log.py
│   │   ├── code_writer.py
│   │   ├── curiosity.py
│   │   ├── curiosity_executor.py
│   │   ├── dependency_manager.py
│   │   ├── health_sentinel.py
│   │   ├── quality_assurance.py
│   │   ├── system_bridge.py
│   │   ├── auto_fixer.py
│   │   └── context_recon.py
│   ├── conversation/
│   │   ├── dialogue_manager.py
│   │   ├── monologue.py
│   │   ├── context_compressor.py
│   │   ├── beliefs.py
│   │   ├── working_memory.py
│   │   └── reasoning_modes.py
│   └── models/
│       ├── answer.py
│       ├── source.py
│       ├── query.py
│       ├── predictive.py
│       └── llm_client.py
│
├── infra/                               # Operations, API, database, config
│   ├── app/
│   │   ├── main.py
│   │   ├── lifespan.py
│   │   ├── pipeline.py
│   │   ├── streaming.py
│   │   ├── routes_eval.py
│   │   ├── routes_ops.py
│   │   ├── routes_query.py
│   │   └── soul/
│   │       └── soul_store.py
│   ├── database/
│   │   ├── engine.py
│   │   ├── models.py
│   │   ├── repositories.py
│   │   ├── redis_cache.py
│   │   ├── runtime_state.py
│   │   └── alembic/
│   │       ├── env.py
│   │       ├── script.py.mako
│   │       └── versions/
│   ├── runtime/
│   │   ├── event_bus.py
│   │   ├── event_handlers.py
│   │   ├── event_models.py
│   │   ├── runtime_monitor.py
│   │   └── tracing.py
│   ├── ops/
│   │   ├── circuit_breakers.py
│   │   ├── failure_recovery.py
│   │   ├── health_monitor.py
│   │   ├── load_shedding.py
│   │   ├── observability.py
│   │   ├── resource_manager.py
│   │   ├── runtime_snapshots.py
│   │   ├── runtime_supervisor.py
│   │   └── token_budget_manager.py
│   ├── constitution/
│   │   ├── epistemology.md
│   │   ├── logic.md
│   │   ├── science.md
│   │   ├── uncertainty.md
│   │   ├── communication.md
│   │   └── curiosity.md
│   ├── config/
│   │   ├── baseline.json
│   │   ├── noisy.json
│   │   └── simple.json
│   ├── data/                             # Runtime data (not VCS for experiments)
│   │   ├── chroma_db/
│   │   ├── concepts.json
│   │   └── ... (generated at runtime)
│   └── frontend/
│       ├── src/
│       ├── dist/
│       ├── index.html
│       ├── package.json
│       ├── vite.config.js
│       ├── tailwind.config.js
│       └── postcss.config.js
│
├── docs/
│   ├── research/
│   │   ├── PROGRAM_D_RESEARCH_STATE_v0.1.md
│   │   └── VELYNX_v2_PI_Review.md
│   ├── architecture/
│   │   ├── ARCHITECTURE.md
│   │   ├── phase57_agentic_loop_architecture.md
│   │   └── phase60_self_model_architecture.md
│   ├── audits/
│   │   ├── VELYNX_AUDIT_2026-06-01.md
│   │   └── VELYNX_PHASE36_AUDIT.md
│   ├── requirements/
│   │   ├── requirements.md
│   │   └── requirements_raw.txt
│   ├── reviews/
│   │   ├── program_d_circular_dependencies.md
│   │   ├── program_d_dead_code_analysis.md
│   │   ├── program_d_duplicated_logic.md
│   │   └── program_d_hidden_coupling.md
│   ├── literature/
│   │   └── program_d_mathematical_provenance.md
│   └── plans/
│       ├── program_d_reduction_plan.md
│       ├── program_d_migration_plan.md
│       ├── program_c_reduction_plan.md
│       ├── program_c_safe_removal_order.md
│       └── program_c_archive_manifest.md
│
├── archive/
│   ├── code/
│   │   ├── velynx_core/                  # Duplicate stack, superseded
│   │   ├── orchestrator.py
│   │   ├── brain.py
│   │   ├── self_coder.py
│   │   ├── cognitive_core.py
│   │   ├── cognitive_health.py
│   │   ├── cognitive_telemetry.py
│   │   ├── backend/agents/               # Dead stubs
│   │   ├── backend/audio/
│   │   ├── backend/testing/
│   │   ├── backend/tools/
│   │   ├── backend/contracts/
│   │   ├── backend/integration/
│   │   ├── backend/self_coder.py
│   │   ├── backend/orchestrator.py
│   │   ├── configs/
│   │   └── frontend/                     # (If JS frontend is not the active product)
│   ├── experiments/
│   │   ├── experiments/calculator.py
│   │   ├── experiments/test_calc.py
│   │   └── experiments/generated_tool.py
│   ├── documents/
│   │   └── ... (superseded docs)
│   └── data/
│       └── ... (legacy data files)
│
├── artifacts/                            # Generated outputs (not VCS-tracked)
│   ├── benchmarks/
│   │   ├── R2A1_policy_benchmark_*/
│   │   ├── R3F1_report
│   │   └── attribution_*/
│   ├── experiments/
│   │   ├── exp_001/
│   │   ├── ...
│   │   └── exp_N/
│   └── output/
│       ├── sim_*.html
│       ├── chart_*.png
│       ├── plot_*.png
│       └── concept_map_*.png
│
├── tests/                                # Shared test infrastructure
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── scripts/                              # Build & dev scripts (thin)
│   ├── start-frontend.ps1
│   ├── test-api.ps1
│   ├── wipe_db.py
│   └── _fix_imports.py
│
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── Dockerfile
└── docker-compose.yml
