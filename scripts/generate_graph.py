import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

# ─── N O D E S ───────────────────────────────────────────────────────────────

LAWS = [
    (
        "L1",
        "HebbianLearning",
        "Fire together, wire together — coactivation count increments, edge at count>=2, asymptotic weight updates",
    ),
    (
        "L2",
        "FreeEnergyProxy",
        "Cognitive energy E = λ·H + μ·S + ν·A (λ=1.0, μ=2.0, ν=0.5) — stand-in for variational free energy",
    ),
    (
        "L3",
        "DirichletMarkovModel",
        "P(s|c) = (n(c,s)+α)/(N(c)+α·|support|) — additive smoothing with symmetric Dirichlet prior",
    ),
    (
        "L4",
        "ShannonSurprise",
        "I(s) = -log₂ P(s|c) — surprisal in bits, the universal cognitive currency",
    ),
    (
        "L5",
        "PrecisionWeightedAttention",
        "a(s) = 1−P(s|c) ∈ [0,1]; attention = precision of the prediction residual",
    ),
    ("L6", "KLDivergence", "KL(P‖Q) = Σ P(s) log₂(P(s)/Q(s)) — confidence delta per tick"),
    (
        "L7",
        "InertiaLaw",
        "effective_rate = base_rate × (1−stability); mature rules barely move at an anomaly",
    ),
    (
        "L8",
        "ExceptionQuarantine",
        "Contradictions filed as BeliefExceptions inside parent belief, never overwrite the rule",
    ),
    (
        "L9",
        "FractureMechanics",
        "Rule fractures when contradiction_count / support_count ≥ 0.85; dominant exception promoted",
    ),
    (
        "L10",
        "StabilityCurve",
        "stability(n) = ln(1+n) / (ln(1+n)+ln(1+4)) — logarithmic confidence-in-history measure",
    ),
    (
        "L11",
        "SynapticPruning",
        "asymptotic_weight ×= (1.0−decay_rate); edges below prune_threshold deleted",
    ),
    ("L12", "BayesianSurprise", "KL(Beta(1+s,1+f) ‖ Beta(1,1)) — divergence from uniform prior"),
    ("L13", "ExpectedInfoGain", "EIG = H(H)−Eₐ[H(H|A=a)] = I(H;A) for curiosity-driven inquiry"),
    (
        "L14",
        "NPMIClustering",
        "Normalised Pointwise Mutual Information (−1,1) for co-occurrence matrices",
    ),
    ("L15", "SpectralClustering", "Eigengap heuristic + K-Means++ on Laplacian for concept birth"),
    (
        "L16",
        "BayesianEdgeEvaluation",
        "Living edges tracked with Beta posterior: quality, reinforced_count, challenged_count → confidence state",
    ),
    (
        "L17",
        "ThermodynamicState",
        "Scalar parameter controlling strictness vs. exploration in reasoning, from conflict state",
    ),
    (
        "L18",
        "ResonancePropagation",
        "Multi-hop semantic wave propagation: compound resonance = 1−(1−curr)×(1−new_energy)",
    ),
    (
        "L19",
        "CognitiveProgressIndex",
        "CPI = weighted composite of accuracy (0.4), decay (0.3), compression (0.2), resolution (0.1)",
    ),
    ("L20", "FreeEnergyMinimization", "C8 merge policy: accept iff E_after ≤ E_before (ΔE ≥ 0)"),
    (
        "L21",
        "ParetoDominance",
        "C8 merge: reject only if all four vitals (H,S,A,E) worsen simultaneously",
    ),
]

ASSUMPTIONS = [
    (
        "A1",
        "SymbolAsAtom",
        "Cognition operates on discrete symbols each with positive probability via Dirichlet smoothing",
    ),
    (
        "A2",
        "FlatMarkovSufficient",
        "A single-level Markov chain captures enough predictive structure; hierarchy unnecessary",
    ),
    (
        "A3",
        "StabilitySolvesForgetting",
        "Inertia Law + Exception Quarantine prevents catastrophic forgetting without Fisher info",
    ),
    (
        "A4",
        "SurpriseEqualsDissonance",
        "Shannon surprisal captures all forms of cognitive dissonance (no valence/signed errors)",
    ),
    (
        "A5",
        "AttentionIsPrecisionResidual",
        "Attention = 1−P(obs|context); no biased competition, spatial, or overt/covert attention",
    ),
    (
        "A6",
        "LocalRulesSufficient",
        "Rate-based Hebbian coactivation suffices; no STDP, three-factor, or backprop needed",
    ),
    (
        "A7",
        "FreeEnergyProxyIsAdequate",
        "E = λH+μS+νA is a sufficient stand-in for variational free energy",
    ),
    (
        "A8",
        "ConceptBirthWorksFromStats",
        "Spectral clustering on NPMI-thresholded co-occurrence suffices for concept formation",
    ),
    (
        "A9",
        "SingleLevelPredictionWorks",
        "Flat predict/collide/adapt loop is enough; no hierarchical predictive coding needed",
    ),
    (
        "A10",
        "HandAuthoredScaffoldingOk",
        "Seeded curriculum and pre-authored ontology acceptable; emergence not required",
    ),
    (
        "A11",
        "CPIMeasuresLearning",
        "Four-component CPI (accuracy, decay, compression, resolution) captures genuine becoming",
    ),
    (
        "A12",
        "ProbationaryTestingWorks",
        "Probation over N deviation trials with coverage threshold validates latent abstractions",
    ),
    (
        "A13",
        "MetaphoricalNeuroscienceOk",
        "Terms like resonance, thermodynamic state, sleep cycle need no literal biological mechanism",
    ),
    (
        "A14",
        "RateBasedHebbianSufficient",
        "Rate-based coactivation counts capture Hebbian learning without spike-timing",
    ),
    (
        "A15",
        "EdgeWeightAsConfidence",
        "Asymptotic weight + Bayesian state fully capture edge reliability",
    ),
    (
        "A16",
        "ConjugatePriorsTractable",
        "Beta and Dirichlet conjugate priors keep Bayesian computations tractable",
    ),
]

VARIABLES = [
    (
        "V1",
        "SurpriseBits",
        "prediction_error = -log₂ P(obs|context); the universal cognitive signal (bits)",
    ),
    ("V2", "AttentionWeight", "1−P(obs|context) ∈ [0,1]; precision of the residual, drives focus"),
    ("V3", "ConfidenceDelta", "KL(posterior‖prior) in bits; magnitude of belief shift per tick"),
    ("V4", "Stability", "ln(1+n)/(ln(1+n)+ln(5)) → [0,1); resistance to change"),
    (
        "V5",
        "FractureRatio",
        "contradiction_count / support_count; approaches 1.0 when rule is candidate for revision",
    ),
    ("V6", "SupportCount", "Raw episodic tally of confirmations of a rule"),
    ("V7", "ContradictionCount", "Raw episodic tally of anomalies quarantined against a rule"),
    (
        "V8",
        "EffectiveLearningRate",
        "base_rate × (1−stability); Inertia Law governs belief movement",
    ),
    ("V9", "H_Entropy", "Conditional Shannon entropy of cluster-transition Markov chain (bits)"),
    (
        "V10",
        "S_SurpriseSpatial",
        "Euclidean distance between predicted centroid and observed vector",
    ),
    ("V11", "A_ActiveLoad", "Live K-Means clusters + spatial volume of quarantined anomaly cloud"),
    ("V12", "E_CognitiveEnergy", "λH + μS + νA (λ=1.0, μ=2.0, ν=0.5); headline free-energy proxy"),
    (
        "V13",
        "PredictionAccuracyTrend",
        "EWMA of 1−normalized(surprise); ∈ [0,1]; CPI accuracy component",
    ),
    (
        "V14",
        "AverageSurpriseDecay",
        "EWMA of recovery fraction after novelty spike; CPI decay component",
    ),
    (
        "V15",
        "ConceptCompressionRatio",
        "experiences / consolidated concepts; ≥ 1; CPI compression component",
    ),
    (
        "V16",
        "ContradictionsResolved",
        "Monotone counter of reified contradictions; CPI resolution component",
    ),
    (
        "V17",
        "ThermodynamicStateValue",
        "Scalar controlling reasoning strictness vs. exploration (from conflict)",
    ),
    ("V18", "ResonanceScore", "Multi-hop activation propagation value; compound resonance formula"),
    (
        "V19",
        "EdgeAsymptoticWeight",
        "Living edge strength after Hebbian reinforcement; decays over time",
    ),
    ("V20", "ProbationCoverage", "hits / trials for a probationary concept; ≥ 0.60 to confirm"),
    (
        "V21",
        "PromisedBits",
        "Predictive bits a concept birth promises to save (H_before − H_after)",
    ),
    ("V22", "BayesianSurpriseKL", "KL(Beta(1+s,1+f)‖Beta(1,1)); surprise at concept reliability"),
    ("V23", "Regime", "Cognitive state: OPTIMAL / LEARNING / EXHAUSTION"),
    (
        "V24",
        "EnergyExhaustionThreshold",
        "E ≥ 18.0 signals fragmentation and triggers concept birth",
    ),
    ("V25", "NPMIScore", "Normalised Pointwise Mutual Information between features"),
]

EXPERIMENTS = [
    (
        "E1",
        "C1_PredictiveUnderstanding",
        "Engine holds a standing prediction; reality collides to produce surprise, driving attention/learning/concept formation",
    ),
    (
        "E2",
        "C2_ExplainPrediction",
        "Every forecast carries a rationale and localized world model (rule + exceptions)",
    ),
    (
        "E3",
        "C3_PredictionFailureAnalysis",
        "When surprise breaches threshold, engine authors causal_hypothesis positing missing intermediate cause",
    ),
    (
        "E4",
        "C5_CuriosityEngine",
        "Curiosity selects inquiry maximizing EIG over structural hypotheses about concept-trait relations",
    ),
    (
        "E5",
        "C6_StableBeliefRevision",
        "Multidimensional beliefs with Inertia Law, Exception Quarantine, and Fracture mechanics",
    ),
    (
        "E6",
        "C7_SensoriumMonitor",
        "Continuous loop: world→SensorArray→VectorPredictionCore→FreeEnergy vitals→on EXHAUSTION mine quarantine",
    ),
    (
        "E7",
        "C8_DecisionPolicy",
        "Staged memory restructuring: ReplayEngine sandbox-simulates merges, DecisionPolicy judges",
    ),
    (
        "E8",
        "SleepCycleExperiment",
        "run_sleep_cycle(): decay weights, prune edges, delete orphans, run gap scanner",
    ),
    (
        "E9",
        "AttentionModulatorDemo",
        "Compare cluster assignments with/without attention; same stream, different cluster geometry",
    ),
    (
        "E10",
        "CPILiveFireSimulation",
        "100-experience simulation with GenerativeWorld + PredictiveAgent + ReflectionEngine",
    ),
    (
        "E11",
        "ProbationaryConceptPipeline",
        "Candidate birth when EXHAUSTED, watch over PROBATION_MIN_TRIALS, confirm if ≥ 0.60 coverage",
    ),
    (
        "E12",
        "ConceptBirthEngine",
        "Emergent clustering: NPMI thresholding, spectral eigengap, greedy seed-growth, LatentConcept spawning",
    ),
    (
        "E13",
        "ReplayEngineSandbox",
        "Clone substrate, apply proposed merge, measure H/S/A, produce DecisionScore",
    ),
]

STAGES = [
    (
        "S1",
        "PreC1_DirichletMarkov",
        "Flat variable-order Markov model with symmetric Dirichlet prior (pre-C6 substrate)",
    ),
    (
        "S2",
        "C1_PredictiveLoop",
        "Continuous predict/collide/adapt loop; engine always holds a standing prediction",
    ),
    (
        "S3",
        "C2_ExplainPrediction",
        "Rationale generation per prediction; localized world model with rule + exceptions",
    ),
    (
        "S4",
        "C3_HypothesisGeneration",
        "Causal hypothesis triggered when surprise exceeds threshold",
    ),
    (
        "S5",
        "C5_CuriosityInquiry",
        "Curiosity engine selects highest-EIG question about concept-trait relationships",
    ),
    (
        "S6",
        "C6_StableBelief",
        "Multidimensional beliefs with stability, quarantine, fracture; replaces flat substrate",
    ),
    (
        "S7",
        "C7_SensoriumProcessing",
        "Continuous vector-based processing; prediction core + latent cause discovery",
    ),
    (
        "S8",
        "C8_MergeGovernance",
        "Replay sandbox simulates memory restructurings; DecisionPolicy accepts/rejects",
    ),
    (
        "S9",
        "Stage0_Probation",
        "Probationary concept as temporary overlay (not committed); watched over deviation trials",
    ),
    ("S10", "SleepCycle", "Synaptic decay, edge pruning, orphan deletion, gap scanning"),
    (
        "S11",
        "LivingGraphPhase",
        "Hebbian coactivation → edge creation → asymptotic weight reinforcement",
    ),
    ("S12", "ResonancePhase", "Multi-hop semantic wave propagation through Bayesian living graph"),
    (
        "S13",
        "DreamState",
        "Subconscious metaphorical linking of charged but unlinked concepts via FAISS",
    ),
    (
        "S14",
        "MetacognitivePenalty",
        "Bayesian penalty on edges that led to rejected/hallucinated responses",
    ),
    (
        "S15",
        "OntologyIntegration",
        "Birth concepts passed into World Model Registry and soul graph for reasoning",
    ),
]

RISKS = [
    (
        "R1",
        "FEPProxyNotFEP",
        "E=λH+μS+νA is NOT variational free energy; no generative likelihood, no posterior approximation; coefficients hand-tuned",
    ),
    (
        "R2",
        "NoHierarchicalPredCoding",
        "Single-level flat Markov; no hierarchy, canonical microcircuit, or multi-level precision weighting",
    ),
    (
        "R3",
        "CatastrophicForgettingRisk",
        "C6 Inertia Law + quarantine may not generalize; fracture mechanic invented, not biologically validated",
    ),
    (
        "R4",
        "OverclaimedNeuroscience",
        "PI review: zero contact with neuroscience; no STDP, neuromodulation, LTP/LTD mechanisms",
    ),
    (
        "R5",
        "NothingDevelops",
        "Scaffolding is hand-authored; nothing develops — PI review core finding",
    ),
    ("R6", "NoSTDP", "Rate-based Hebbian only; no spike-timing dependence, no temporal asymmetry"),
    (
        "R7",
        "NoDopamineNeuromodulation",
        "No reward prediction error, no ACh/NE/5-HT/DA modulation, no three-factor learning",
    ),
    (
        "R8",
        "NoHomeostasis",
        "No synaptic scaling, firing rate homeostasis, E/I balance, or BCM sliding threshold",
    ),
    (
        "R9",
        "ActiveInferenceOverclaim",
        "Only learning-rate modulation implemented; no policy selection, no expected free energy",
    ),
    (
        "R10",
        "ThermodynamicMetaphor",
        "Thermodynamic state has no connection to statistical mechanics; could mislead",
    ),
    (
        "R11",
        "CuriosityLimited",
        "Only structural hypothesis testing; no learning-progress or competence-based exploration",
    ),
    (
        "R12",
        "NoSensorimotorGrounding",
        "Piagetian sensorimotor bootstrapping absent; static embeddings lack sensory grounding",
    ),
    (
        "R13",
        "ConstitutionConflicts",
        "Science (methodology), Uncertainty (honest reporting), Epistemology (traceable sources) at risk",
    ),
    (
        "R14",
        "ScaffoldingNotEmergent",
        "Fixed curriculum with pre-answered questions; no autonomous learning progress",
    ),
    (
        "R15",
        "MetaphoricalLanguageMisleads",
        "Resonance, thermodynamic state, sleep cycle are metaphors, not literal neuroscience",
    ),
    (
        "R16",
        "EpisodicMemoryNotNeural",
        "Episodic memory is a causal event log / SQLite store, not auto-associative network",
    ),
    (
        "R17",
        "WorkingMemorySimplistic",
        "Simple FIFO key-value store; no central executive, phonological loop, visuospatial sketchpad",
    ),
]

METRICS = [
    (
        "M1",
        "CPI_Composite",
        "Cognitive Progress Index = weighted blend of accuracy (0.4), decay (0.3), compression (0.2), resolution (0.1); ∈ [0,1]",
    ),
    (
        "M2",
        "TransitionEntropy_H",
        "Conditional Shannon entropy H(next|current) of cluster-transition Markov chain (bits)",
    ),
    (
        "M3",
        "SpatialSurprise_S",
        "Euclidean distance between predicted centroid and observed vector",
    ),
    ("M4", "ActiveLoad_A", "Cluster count + anomaly spatial volume"),
    (
        "M5",
        "CognitiveEnergy_E",
        "λH + μS + νA; headline free-energy proxy; threshold at 18.0 for exhaustion",
    ),
    (
        "M6",
        "PredictionAccuracy",
        "EWMA of 1−normalized(surprise); ∈ [0,1]; rising = converging on world",
    ),
    (
        "M7",
        "SurpriseDecayRate",
        "EWMA of recovery fraction after novelty spike; 1 = instant recovery",
    ),
    ("M8", "CompressionRatio", "experiences / consolidated concepts; higher = more abstraction"),
    ("M9", "ContradictionsResolvedCount", "Monotone integer; each reified concept increments it"),
    ("M10", "FractureRatio", "contradiction_count / support_count; ≥ 0.85 triggers fracture"),
    (
        "M11",
        "ProbationCoverage",
        "hits / trials for probationary concept; must be ≥ 0.60 to confirm",
    ),
    ("M12", "ExpectedInfoGain", "I(H;A) in bits; curiosity engine uses this to select inquiry"),
    ("M13", "BayesianSurpriseValue", "KL(Beta(1+s,1+f) ‖ Beta(1,1)); concept reliability surprise"),
    (
        "M14",
        "EdgeConfidence",
        "Bayesian state: ACTIVE / CONTESTED / INFERRED / UNCERTAIN / VERIFIED",
    ),
    ("M15", "EdgeAsymptoticWeight", "Living edge strength after decay and reinforcement"),
    ("M16", "ResonanceFieldScore", "Compound activation score after multi-hop propagation"),
    (
        "M17",
        "BottleneckMeanAccuracy",
        "Per-concept mean accuracy; chronic if consolidated but < 0.55",
    ),
    (
        "M18",
        "PromisedBitsDelta",
        "H_before − H_after at concept birth; predictive uncertainty reduction",
    ),
    (
        "M19",
        "SurpriseSlope",
        "OLS slope of recent average_surprise; |slope|<ε + level>threshold = plateau",
    ),
]

KILL_CRITERIA = [
    ("K1", "CPIDeclining", "CPI consistently drops across runs — learning stagnates or reverses"),
    (
        "K2",
        "CatastrophicForgettingPersists",
        "C6 Inertia Law + quarantine fails to protect mature rules in long-running regimes",
    ),
    ("K3", "ConstitutionViolation", "Science/Uncertainty/Epistemology constitutions breached"),
    (
        "K4",
        "NothingDevelopsPersists",
        "Scaffolding remains entirely hand-authored; PI review verdict never addressed",
    ),
    (
        "K5",
        "SurprisePlateauUnresolved",
        "Average surprise plateaus above stuck_threshold (1.5 bits) with bottleneck < 0.55",
    ),
    (
        "K6",
        "ExhaustionSustained",
        "Cognitive energy E ≥ 18.0 sustained; fragmentation signal without discovery",
    ),
    (
        "K7",
        "FractureSupersaturation",
        "fracture_ratio ≥ 1.0 sustained across multiple contexts; rules cannot stabilize",
    ),
    ("K8", "NoGenuineLearning", "CPI near 0.5 with flat trajectory while surprise stays high"),
    (
        "K9",
        "FEPMisrepresentation",
        "FEP proxy presented as Friston free energy without qualification fails Science constitution",
    ),
    (
        "K10",
        "ProbationNeverConfirms",
        "All probationary candidates rejected; hypothesis testing pipeline fails to find valid structures",
    ),
]

# ─── E D G E S ───────────────────────────────────────────────────────────────

EDGES_DEPENDS_ON = [
    ("L1", "A14", "Rate-based Hebbian depends on coactivation being sufficient"),
    ("L2", "A7", "Proxy depends on 3-term sum approximating variational free energy"),
    ("L3", "A1", "Dirichlet-Markov depends on symbols as atomic units with positive probability"),
    ("L4", "A4", "Shannon surprisal depends on capturing all cognitive dissonance"),
    ("L5", "A5", "Attention depends on precision-of-residual being sufficient"),
    ("L7", "A3", "Inertia Law depends on stability preventing catastrophe"),
    ("L8", "A3", "Quarantine depends on filing anomalies without rewriting being sufficient"),
    ("L9", "A3", "Fracture depends on promotion-of-dominant-exception strategy"),
    ("L11", "A1", "Pruning depends on weight-threshold model being sufficient"),
    ("L12", "A16", "Bayesian surprise depends on Beta conjugate posteriors being tractable"),
    ("L13", "A4", "EIG depends on information-theoretic curiosity being sufficient"),
    ("L14", "A8", "NPMI depends on co-occurrence stats being sufficient for concept formation"),
    ("L15", "A8", "Spectral clustering depends on eigengap heuristic being adequate"),
    ("L16", "A15", "Bayesian edge eval depends on Beta posteriors capturing reliability"),
    ("L17", "A13", "Thermodynamic state depends on metaphor being acceptable"),
    ("L18", "A13", "Resonance depends on wave metaphor being acceptable"),
    ("L19", "A11", "CPI depends on four components genuinely measuring becoming"),
    ("L20", "L2", "Free energy minimization depends on the energy proxy"),
    ("L21", "L2", "Pareto depends on the vitals which derive from the proxy"),
    ("E1", "S2", "C1 experiment depends on predictive loop stage"),
    ("E2", "S3", "C2 experiment depends on explain prediction stage"),
    ("E3", "S4", "C3 experiment depends on hypothesis generation stage"),
    ("E4", "S5", "C5 experiment depends on curiosity inquiry stage"),
    ("E5", "S6", "C6 experiment depends on stable belief stage"),
    ("E6", "S7", "C7 experiment depends on sensorium processing stage"),
    ("E7", "S8", "C8 experiment depends on merge governance stage"),
    ("E8", "S10", "Sleep experiment depends on sleep cycle stage"),
    ("E11", "S9", "Probationary pipeline depends on Stage 0 probation"),
    ("E12", "S15", "Concept birth depends on ontology integration stage"),
    ("E13", "S8", "Replay sandbox depends on C8 merge governance stage"),
    ("V1", "L4", "Surprise variable instantiates Shannon surprise law"),
    ("V2", "L5", "Attention weight instantiates precision-weighted attention"),
    ("V4", "L10", "Stability variable instantiates stability curve"),
    ("V5", "L9", "Fracture ratio instantiates fracture mechanics"),
    ("V8", "L7", "Effective learning rate instantiates Inertia Law"),
    ("V9", "L2", "H is the first term of the free energy proxy"),
    ("V10", "L2", "S is the second term of the free energy proxy"),
    ("V11", "L2", "A is the third term of the free energy proxy"),
    ("V12", "L2", "E is the weighted sum of H, S, A"),
    ("M1", "L19", "CPI composite instantiates the CPI formula"),
    ("M2", "V9", "Entropy metric measures variable H"),
    ("M3", "V10", "Surprise metric measures variable S"),
    ("M4", "V11", "Active load metric measures variable A"),
    ("M5", "V12", "Energy metric measures variable E"),
    ("M10", "V5", "Fracture ratio metric measures variable fracture ratio"),
    ("M11", "V20", "Coverage metric measures probation coverage"),
    ("M14", "L16", "Edge confidence depends on Bayesian edge evaluation"),
    ("S6", "L7", "Stable belief depends on Inertia Law"),
    ("S6", "L8", "Stable belief depends on Exception Quarantine"),
    ("S6", "L9", "Stable belief depends on Fracture Mechanics"),
    ("S11", "L1", "Living graph depends on Hebbian learning"),
    ("R1", "L2", "Risk arises because proxy used as free energy stand-in"),
    ("R2", "A2", "Risk from assumption that flat Markov is sufficient"),
    ("R3", "L7", "Risk that Inertia Law may not generalize"),
    ("R3", "L8", "Risk that quarantine may not generalize"),
    ("R4", "A13", "Risk from metaphorical neuroscience language"),
    ("R5", "A10", "Risk from hand-authored scaffolding assumption"),
    ("R9", "A13", "Risk from overclaiming active inference"),
    ("K1", "M1", "Kill criterion depends on CPI metric"),
    ("K5", "M19", "Kill criterion depends on surprise slope metric"),
    ("K6", "V24", "Kill criterion depends on exhaustion threshold"),
    ("K7", "V5", "Kill criterion depends on fracture ratio variable"),
]

EDGES_CONTRADICTS = [
    (
        "L5",
        "L7",
        "C6 replaces precision-weighted learning with Inertia Law; attention no longer modulates learning rate",
    ),
    ("A4", "R2", "Single-level surprise contradicts true predictive coding which needs hierarchy"),
    ("A7", "R1", "Claim of adequacy contradicts formal FEP requirements"),
    ("A2", "L3", "Flat Markov contradicts the need for hierarchical structure in real brains"),
    ("A6", "R6", "Local rules sufficient contradicts known STDP mechanisms"),
    ("A5", "R2", "Single-level attention contradicts hierarchical attention models"),
    ("S6", "S2", "C6 stable beliefs contradict C1 flat probability model; C6 replaces it"),
    (
        "L7",
        "L5",
        "Inertia (inverse-stability scaling) directly contradicts precision-weighting (surprise-amplified learning)",
    ),
    ("A10", "K4", "Hand-authored scaffolding contradicts claim of developmental emergence"),
    ("S9", "S15", "Stage 0 does NOT commit to ontology; contradicts integration claim"),
    (
        "L19",
        "K8",
        "CPI could show improvement while system not genuinely learning (gaming the metric)",
    ),
    ("A9", "R2", "Flat loop contradicts hierarchical predictive coding claim"),
]

EDGES_VALIDATES = [
    ("E1", "S2", "C1 validates predictive loop works"),
    ("E2", "S3", "C2 validates explanation generation"),
    ("E3", "S4", "C3 validates hypothesis generation on surprise"),
    ("E4", "L13", "C5 validates EIG-driven curiosity works"),
    ("E5", "L7", "C6 validates Inertia Law prevents catastrophic forgetting"),
    ("E5", "L8", "C6 validates quarantine mechanics"),
    ("E5", "L9", "C6 validates fracture mechanics"),
    ("E6", "L18", "C7 validates attention feedback (discovery improves prediction)"),
    ("E7", "L20", "C8 validates free energy minimization for merge decisions"),
    ("E8", "L11", "Sleep validates synaptic pruning mechanics"),
    ("E9", "L5", "Demo validates attention warps cluster geometry"),
    ("E10", "L19", "CPI simulation validates the CPI measure"),
    ("E11", "A12", "Pipeline validates Stage 0 testing works"),
    ("E12", "L15", "Concept birth validates spectral clustering for emergence"),
    ("E13", "L20", "Replay sandbox validates free energy measurement"),
    ("M1", "E10", "CPI metric validated by live-fire simulation"),
    ("M14", "A15", "Edge confidence validates Bayesian edge evaluation"),
    ("S11", "L1", "Living graph validates Hebbian learning implementation"),
    ("S12", "L18", "Resonance phase validates resonance propagation"),
    ("S13", "L1", "Dream state validates Hebbian coactivation in subconscious linking"),
]

EDGES_FALSIFIES = [
    ("K1", "A11", "CPI declining falsifies that system is learning"),
    ("K2", "A3", "Forgetting falsifies that stability solves it"),
    ("K4", "A10", "Nothing develops falsifies hand-authored scaffolding is acceptable"),
    ("K5", "A12", "Unresolved plateau falsifies probation testing works"),
    ("K6", "L20", "Sustained exhaustion falsifies system self-regulates"),
    ("K7", "L9", "Supersaturation falsifies fracture mechanics"),
    ("K8", "A11", "No learning falsifies CPI captures genuine becoming"),
    ("K9", "A7", "FEP misrepresentation falsifies the proxy claim"),
    ("K10", "A12", "Never confirming falsifies hypothesis testing pipeline"),
    ("E10", "A11", "If CPI flatlines despite learning, the metric is falsified"),
    ("R1", "L2", "Formal gap falsifies proxy being free energy"),
    ("R2", "L3", "Absence of hierarchy falsifies predictive coding claims"),
    ("R9", "L2", "Only learning-rate modulation falsifies active inference claim"),
    ("R14", "A10", "Fixed curriculum falsifies claim of autonomous development"),
]

EDGES_DERIVES_FROM = [
    ("L1", "L3", "Hebbian count updates are compatible with Dirichlet-Markov count model"),
    ("L2", "L3", "Energy proxy entropy H derives from Markov chain of clusters"),
    ("L2", "L4", "Energy proxy surprise S derives from Shannon surprisal"),
    ("L2", "L18", "Energy proxy active load A influenced by resonance-based clustering"),
    (
        "L4",
        "L3",
        "Shannon surprise of symbol derives from Dirichlet-smoothed predictive distribution",
    ),
    ("L5", "L4", "Attention weight derives from probability that feeds into surprise"),
    ("L6", "L4", "KL divergence is expected value of log-ratio, related to surprise"),
    ("L7", "L10", "Inertia law derives from stability curve"),
    ("L9", "L10", "Fracture ratio compares to stability half-maturity constant"),
    ("L12", "L6", "Bayesian surprise is a specific KL divergence between Betas"),
    ("L13", "L4", "EIG = H(H)−Eₐ[H(H|A)] derives from Shannon entropy"),
    (
        "L14",
        "L4",
        "NPMI = log(p(x,y)/p(x)p(y)) / −log p(x,y) derives from pointwise mutual information",
    ),
    ("L15", "L14", "Spectral clustering operates on NPMI-derived graph"),
    ("L17", "L4", "Thermodynamic state from conflict state (surprise patterns)"),
    ("L19", "M6", "CPI accuracy component from prediction accuracy metric"),
    ("L19", "M7", "CPI decay component from surprise decay rate"),
    ("L19", "M8", "CPI compression component from compression ratio"),
    ("L19", "M9", "CPI resolution component from contradictions resolved"),
    ("L20", "L2", "Free energy minimization derives from the proxy"),
    ("V1", "L4", "Surprise bits derives from Shannon surprisal"),
    ("V3", "L6", "Confidence delta derives from KL divergence"),
    ("V4", "L10", "Stability derives from stability curve formula"),
    ("V8", "L7", "Effective learning rate derives from Inertia Law"),
    ("V9", "M2", "Entropy H derives from transition entropy metric"),
    ("V12", "V9", "E derives from H"),
    ("V12", "V10", "E derives from S"),
    ("V12", "V11", "E derives from A"),
    ("V23", "V12", "Regime derives from cognitive energy"),
    ("E7", "E13", "C8 policy consumes ReplayEngine sandbox simulations"),
    ("E11", "E12", "Probation pipeline uses concept birth for candidate generation"),
    ("M1", "M6", "CPI composes from accuracy metric"),
    ("M1", "M7", "CPI composes from decay metric"),
    ("M1", "M8", "CPI composes from compression metric"),
    ("M1", "M9", "CPI composes from resolution metric"),
    ("M5", "M2", "Energy metric derives from entropy metric"),
    ("M5", "M3", "Energy metric derives from surprise metric"),
    ("M5", "M4", "Energy metric derives from active load metric"),
]

EDGES_SUPPORTS = [
    ("L1", "S11", "Hebbian learning supports living graph edge creation"),
    ("L3", "S2", "Dirichlet-Markov supports predictive loop"),
    ("L4", "E3", "Shannon surprise supports causal hypothesis triggers"),
    ("L5", "E9", "Precision-weighted attention supports attention modulator demo"),
    ("L7", "S6", "Inertia law supports stable belief revision"),
    ("L8", "S6", "Exception quarantine supports stable belief revision"),
    ("L9", "S6", "Fracture mechanics supports belief revision"),
    ("L11", "S10", "Synaptic pruning supports sleep cycle maintenance"),
    ("L13", "S5", "EIG supports curiosity-driven inquiry"),
    ("L14", "E12", "NPMI supports concept birth engine"),
    ("L15", "E12", "Spectral clustering supports concept birth engine"),
    ("L18", "S12", "Resonance supports multi-hop propagation phase"),
    ("L20", "E7", "Free energy minimization supports C8 decision policy"),
    ("A1", "L3", "Symbol assumption supports Dirichlet-Markov"),
    ("A3", "E5", "Stability assumption supports C6 experiment"),
    ("A7", "E7", "Proxy adequacy supports C8 decision policy"),
    ("A8", "E12", "Stats assumption supports concept birth engine"),
    ("A11", "E10", "CPI measures learning supports live-fire simulation"),
    ("A12", "E11", "Probation assumption supports pipeline"),
    ("V1", "E3", "Surprise supports hypothesis generation trigger"),
    ("V2", "E9", "Attention weight supports attention modulator"),
    ("V4", "E5", "Stability supports C6 belief revision"),
    ("V8", "S6", "Effective learning rate supports stable update dynamics"),
    ("V12", "V23", "Energy supports regime classification"),
    ("V23", "E11", "EXHAUSTION regime triggers concept birth pipeline"),
    ("M1", "K1", "CPI supports kill criterion on declining learning"),
    ("M5", "K6", "Energy metric supports exhaustion kill criterion"),
    ("M17", "K5", "Bottleneck accuracy supports plateau kill criterion"),
    ("S6", "E5", "Stable belief stage supports C6 experiment"),
    ("S7", "E6", "Sensorium stage supports C7 experiment"),
    ("S9", "E11", "Stage 0 probation supports probation pipeline"),
]

ALL_EDGES = [
    ("depends_on", EDGES_DEPENDS_ON),
    ("contradicts", EDGES_CONTRADICTS),
    ("validates", EDGES_VALIDATES),
    ("falsifies", EDGES_FALSIFIES),
    ("derives_from", EDGES_DERIVES_FROM),
    ("supports", EDGES_SUPPORTS),
]

ALL_NODES = LAWS + ASSUMPTIONS + VARIABLES + EXPERIMENTS + STAGES + RISKS + METRICS + KILL_CRITERIA

TYPE_MAP = {}
for nodes, typename in [
    (LAWS, "Laws"),
    (ASSUMPTIONS, "Assumptions"),
    (VARIABLES, "Variables"),
    (EXPERIMENTS, "Experiments"),
    (STAGES, "Stages"),
    (RISKS, "Risks"),
    (METRICS, "Metrics"),
    (KILL_CRITERIA, "KillCriteria"),
]:
    for nid, _, _ in nodes:
        TYPE_MAP[nid] = typename

LABEL_MAP = {nid: lbl for nid, lbl, _ in ALL_NODES}
DESC_MAP = {nid: desc for nid, _, desc in ALL_NODES}


# ─── G R A P H M L ──────────────────────────────────────────────────────────
def make_graphml():
    root = ET.Element("graphml", xmlns="http://graphml.graphdrawing.org/xmlns")
    # key definitions
    ET.SubElement(root, "key", id="type", for_="node", attrname="type", attrtype="string")
    ET.SubElement(root, "key", id="label", for_="node", attrname="label", attrtype="string")
    ET.SubElement(
        root, "key", id="description", for_="node", attrname="description", attrtype="string"
    )
    ET.SubElement(root, "key", id="edgetype", for_="edge", attrname="edgetype", attrtype="string")
    ET.SubElement(
        root, "key", id="edgedesc", for_="edge", attrname="description", attrtype="string"
    )

    graph = ET.SubElement(root, "graph", id="ProgramC", edgedefault="directed")
    for nid, lbl, desc in ALL_NODES:
        n = ET.SubElement(graph, "node", id=nid)
        ET.SubElement(n, "data", key="type").text = TYPE_MAP[nid]
        ET.SubElement(n, "data", key="label").text = lbl
        ET.SubElement(n, "data", key="description").text = desc

    for etype, edges in ALL_EDGES:
        for src, tgt, desc in edges:
            e = ET.SubElement(graph, "edge", id=f"{src}_{tgt}_{etype}", source=src, target=tgt)
            ET.SubElement(e, "data", key="edgetype").text = etype
            ET.SubElement(e, "data", key="edgedesc").text = desc

    return ET.tostring(root, encoding="unicode")


# ─── M E R M A I D ──────────────────────────────────────────────────────────
def make_mermaid():
    lines = ["graph TD"]
    lines.append("")
    lines.append("%% ==================== L A W S ====================")
    for nid, lbl, _ in LAWS:
        lines.append(f'    {nid}["<b>{lbl}</b><br/>Laws"]:::law')
    lines.append("")
    lines.append("%% ==================== A S S U M P T I O N S ====================")
    for nid, lbl, _ in ASSUMPTIONS:
        lines.append(f'    {nid}["<b>{lbl}</b><br/>Assumptions"]:::assumption')
    lines.append("")
    lines.append("%% ==================== V A R I A B L E S ====================")
    for nid, lbl, _ in VARIABLES:
        lines.append(f'    {nid}["<b>{lbl}</b><br/>Variables"]:::variable')
    lines.append("")
    lines.append("%% ==================== E X P E R I M E N T S ====================")
    for nid, lbl, _ in EXPERIMENTS:
        lines.append(f'    {nid}["<b>{lbl}</b><br/>Experiments"]:::experiment')
    lines.append("")
    lines.append("%% ==================== S T A G E S ====================")
    for nid, lbl, _ in STAGES:
        lines.append(f'    {nid}["<b>{lbl}</b><br/>Stages"]:::stage')
    lines.append("")
    lines.append("%% ==================== R I S K S ====================")
    for nid, lbl, _ in RISKS:
        lines.append(f'    {nid}["<b>{lbl}</b><br/>Risks"]:::risk')
    lines.append("")
    lines.append("%% ==================== M E T R I C S ====================")
    for nid, lbl, _ in METRICS:
        lines.append(f'    {nid}["<b>{lbl}</b><br/>Metrics"]:::metric')
    lines.append("")
    lines.append("%% ==================== K I L L  C R I T E R I A ====================")
    for nid, lbl, _ in KILL_CRITERIA:
        lines.append(f'    {nid}["<b>{lbl}</b><br/>KillCriteria"]:::kill')
    lines.append("")

    # Style definitions with distinct colors
    lines.append("%% ==================== S T Y L E S ====================")
    lines.append("    classDef law fill:#1a237e,color:#fff,stroke:#0d47a1,stroke-width:2px")
    lines.append("    classDef assumption fill:#4a148c,color:#fff,stroke:#7b1fa2,stroke-width:2px")
    lines.append("    classDef variable fill:#004d40,color:#fff,stroke:#00695c,stroke-width:2px")
    lines.append("    classDef experiment fill:#b71c1c,color:#fff,stroke:#d32f2f,stroke-width:2px")
    lines.append("    classDef stage fill:#e65100,color:#fff,stroke:#f57c00,stroke-width:2px")
    lines.append("    classDef risk fill:#3e2723,color:#fff,stroke:#5d4037,stroke-width:2px")
    lines.append("    classDef metric fill:#1b5e20,color:#fff,stroke:#2e7d32,stroke-width:2px")
    lines.append(
        "    classDef kill fill:#b71c1c,color:#fff,stroke:#f44336,stroke-width:3px,stroke-dasharray: 5 5"
    )
    lines.append("")

    lines.append("%% ==================== E D G E S ====================")

    # Per connection type subgraphs for readability, then edges
    etype_styles = {
        "depends_on": "-->|depends_on|",
        "contradicts": "-.->|contradicts|",
        "validates": "==>|validates|",
        "falsifies": "-.->|falsifies|",
        "derives_from": "-->|derives|",
        "supports": "==>|supports|",
    }
    for etype, edges in ALL_EDGES:
        arrow = etype_styles[etype]
        lines.append(f"    %% {etype}")
        for src, tgt, _ in edges:
            lines.append(f"    {src} {arrow} {tgt}")
        lines.append("")

    return "\n".join(lines)


# ─── W R I T E   F I L E S ──────────────────────────────────────────────────
if __name__ == "__main__":
    import os

    outdir = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(outdir, "program_c_graph.graphml"), "w", encoding="utf-8") as f:
        f.write(make_graphml())
    print("[OK] program_c_graph.graphml written")

    with open(os.path.join(outdir, "program_c_diagram.mmd"), "w", encoding="utf-8") as f:
        f.write(make_mermaid())
    print("[OK] program_c_diagram.mmd written")

    # Stats
    print(f"\nNodes: {len(ALL_NODES)}")
    print(f"  Laws: {len(LAWS)}")
    print(f"  Assumptions: {len(ASSUMPTIONS)}")
    print(f"  Variables: {len(VARIABLES)}")
    print(f"  Experiments: {len(EXPERIMENTS)}")
    print(f"  Stages: {len(STAGES)}")
    print(f"  Risks: {len(RISKS)}")
    print(f"  Metrics: {len(METRICS)}")
    print(f"  Kill Criteria: {len(KILL_CRITERIA)}")
    print(f"Edges: {sum(len(es) for _, es in ALL_EDGES)}")
    for etype, edges in ALL_EDGES:
        print(f"  {etype}: {len(edges)}")
