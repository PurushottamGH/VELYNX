# ENGINEERING ACCEPTANCE TESTS

**[FACT]** These are the exact pytest-implementable acceptance tests that verify the engineering framework strictly conforms to the scientific specification.

## Test 1: EXP-0 State Isolation
- **Purpose:** Verify the system wipes all states between trials.
- **Inputs:** Two distinct queries.
- **Expected outputs:** The semantic graph and episodic memory matrix must assert empty/zeros at the start of trial 2.
- **Failure conditions:** Non-zero elements in memory matrices prior to processing query 2.
- **Automated verification:** `assert np.all(memory_matrix == 0)` at `trial_start` hook.
- **Definition of Done:** Test passes 100% reliably.

## Test 2: E0 Hardcoded MDL Threshold
- **Purpose:** Verify $\lambda$ cannot be injected via config.
- **Inputs:** `experiment_config.json` containing an illegal `"lambda": 0.5` key.
- **Expected outputs:** The system MUST raise a `ConfigurationError` and halt.
- **Failure conditions:** The system executes using the config-provided lambda.
- **Automated verification:** Pytest `with pytest.raises(ConfigurationError):` block.
- **Definition of Done:** The mathematical derivation $\lambda_{model} = k \cdot b + n \cdot \log_2 N$ is the only execution path.

## Test 3: EXP-2 Circularity Guard
- **Purpose:** Prevent soul graph concept injection into EXP-2.
- **Inputs:** Initialization of the EXP-2 pipeline.
- **Expected outputs:** System boots successfully without loading `concepts.json`.
- **Failure conditions:** The module imports or parses `program_b/soul_graph` or `concepts.json`.
- **Automated verification:** Mock the file system to make `concepts.json` unreadable. If EXP-2 crashes with `FileNotFoundError`, the test fails.
- **Definition of Done:** EXP-2 runs entirely isolated from Program B's structural data.

## Test 4: E0 Emergence Statistic Calculation
- **Purpose:** Verify the $M$ statistic computes correctly and safely.
- **Inputs:** A predicted uniform state array, and a highly structured ground truth array.
- **Expected outputs:** $M$ evaluates to exactly 0.0 (no division by zero errors).
- **Failure conditions:** `NaN`, `Inf`, or exceptions thrown.
- **Automated verification:** Unit test feeding edge-case arrays into the metric function.
- **Definition of Done:** Metric function handles zero-entropy partitions securely.

## Test 5: E0 Random Seed Isolation
- **Purpose:** Prevent the agent from predicting the synthetic environment via PRNG synchronization.
- **Inputs:** Agent PRNG state and Environment PRNG state.
- **Expected outputs:** `agent.seed != env.seed`.
- **Failure conditions:** Both initialized from the same global `np.random.seed(42)`.
- **Automated verification:** Introspect the random state tuples of both objects.
- **Definition of Done:** Strictly separate local random instances (`np.random.RandomState`) are utilized.
