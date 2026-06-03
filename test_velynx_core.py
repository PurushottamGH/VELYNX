"""
VELYNX CORE v2 — integration test.
Verifies all 4 subsystems are working before deployment.
Run: python test_velynx_core.py
"""

import sys
import time
import tempfile
import os
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent))

RESET = "\033[0m"; GREEN = "\033[32m"; RED = "\033[31m"; CYAN = "\033[36m"; BOLD = "\033[1m"; DIM = "\033[2m"

def ok(msg): print(f"  {GREEN}✓{RESET} {msg}")
def fail(msg): print(f"  {RED}✗{RESET} {msg}")
def section(msg): print(f"\n{CYAN}{BOLD}{msg}{RESET}")

passed = failed_count = 0

def check(label, condition, detail=""):
    global passed, failed_count
    if condition:
        ok(label + (f" — {detail}" if detail else ""))
        passed += 1
    else:
        fail(label + (f" — {detail}" if detail else ""))
        failed_count += 1


# ──────────────────────────────────────────────────────────────────────────────
section("TEST 1: Memory (VelynxMemory)")
# ──────────────────────────────────────────────────────────────────────────────

with tempfile.TemporaryDirectory() as tmpdir:
    db = os.path.join(tmpdir, "test.db")

    from velynx_core.memory import VelynxMemory, Concept, Relation

    mem = VelynxMemory(db_path=db)
    check("Memory initializes", mem is not None)

    # Store a concept
    c1 = Concept(
        id=Concept.make_id("quantum mechanics", "physics"),
        name="quantum mechanics",
        domain="physics",
        what="A branch of physics governing subatomic particles.",
        why="Explains phenomena classical physics cannot — like electron orbitals.",
        how="Uses wave functions and the Schrödinger equation to predict particle states.",
        so_what="Enables technologies like semiconductors, MRI, and lasers.",
        confidence=0.9,
        sources=["https://en.wikipedia.org/wiki/Quantum_mechanics"]
    )
    is_new = mem.store_concept(c1)
    check("store_concept returns True for new concept", is_new is True)

    # Retrieve it
    retrieved = mem.get_concept(c1.id)
    check("get_concept returns correct name", retrieved and retrieved.name == "quantum mechanics")
    check("get_concept returns correct what", retrieved and "subatomic" in retrieved.what)

    # Store a second concept
    c2 = Concept(
        id=Concept.make_id("Schrödinger equation", "physics"),
        name="Schrödinger equation",
        domain="physics",
        what="The fundamental equation governing quantum mechanical wave functions.",
        why="Without it we cannot calculate how quantum systems evolve over time.",
        how="Applies differential operators to wave functions to determine energy eigenstates.",
        so_what="Every quantum chemistry and physics calculation relies on it.",
        confidence=0.88
    )
    mem.store_concept(c2)

    # Add a relation
    rel = Relation(
        from_id=c1.id, to_id=c2.id,
        relation_type="REQUIRES",
        weight=1.0,
        evidence="Quantum mechanics requires the Schrödinger equation"
    )
    rel_ok = mem.add_relation(rel)
    check("add_relation succeeds", rel_ok)

    # Test search
    results = mem.search_concepts("quantum", top_k=5)
    check("search_concepts finds relevant concepts", len(results) >= 1)

    # Test graph traversal
    neighbors = mem.get_neighbors(c1.id, relation_types=["REQUIRES"], max_hops=1)
    check("get_neighbors traverses REQUIRES relation",
          any(n.concept.name == "Schrödinger equation" for n in neighbors))

    # Test stats
    stats = mem.stats()
    check("stats reports 2 concepts", stats["concepts"] == 2)
    check("stats reports 1 relation", stats["relations"] == 1)

    # Update concept (upsert)
    c1.confidence = 0.95
    is_new2 = mem.store_concept(c1)
    check("upsert returns False for existing concept", is_new2 is False)
    updated = mem.get_concept(c1.id)
    check("confidence updated after upsert", updated and updated.confidence == 0.95)

    # find_concept by name
    found = mem.find_concept("quantum mechanics", "physics")
    check("find_concept by name+domain works", found and found.id == c1.id)

    mem.log_event("test", {"status": "ok"})
    check("log_event does not crash", True)

print()


# ──────────────────────────────────────────────────────────────────────────────
section("TEST 2: Brain (VelynxBrain)")
# ──────────────────────────────────────────────────────────────────────────────

with tempfile.TemporaryDirectory() as tmpdir:
    db = os.path.join(tmpdir, "brain_test.db")
    mem = VelynxMemory(db_path=db)

    # Seed some knowledge
    concepts = [
        Concept(
            id=Concept.make_id("photosynthesis", "biology"),
            name="photosynthesis",
            domain="biology",
            what="The process by which plants convert light energy into chemical energy stored as glucose.",
            why="It is the primary source of organic compounds and oxygen on Earth.",
            how="Chlorophyll absorbs sunlight, splits water molecules, and uses CO2 to produce glucose via the Calvin cycle.",
            so_what="Without photosynthesis, nearly all life on Earth would cease to exist.",
            confidence=0.92
        ),
        Concept(
            id=Concept.make_id("chlorophyll", "biology"),
            name="chlorophyll",
            domain="biology",
            what="Green pigment in plant cells that captures light energy for photosynthesis.",
            why="It enables plants to use solar energy as their power source.",
            how="Its molecular structure absorbs red and blue light while reflecting green light.",
            so_what="Chlorophyll is why plants are green and why they can feed themselves from sunlight.",
            confidence=0.88
        ),
    ]
    for c in concepts:
        mem.store_concept(c)

    # Add a relation
    mem.add_relation(Relation(
        from_id=concepts[0].id, to_id=concepts[1].id,
        relation_type="REQUIRES", weight=1.0, evidence="photosynthesis requires chlorophyll"
    ))

    from velynx_core.brain import VelynxBrain, detect_intent, extract_concepts

    brain = VelynxBrain(mem)
    check("Brain initializes", brain is not None)

    # Test intent detection
    check("detect_intent 'what is'",   "what" in detect_intent("what is quantum mechanics"))
    check("detect_intent 'how does'",  "how" in detect_intent("how does this work"))
    check("detect_intent 'why is'",    "why" in detect_intent("why is gravity important"))
    check("detect_intent 'difference'","compare" in detect_intent("difference between A and B"))

    # Test concept extraction
    kws = extract_concepts("what is photosynthesis in plants")
    check("extract_concepts finds 'photosynthesis'", "photosynthesis" in kws)

    # Test reasoning with known concept
    answer = brain.reason("what is photosynthesis")
    check("reasoning returns VelynxAnswer", answer is not None)
    check("answer has confidence > 0",     answer.confidence > 0)
    check("answer has what field",         bool(answer.what))
    check("answer has why field",          bool(answer.why))
    check("answer has how field",          bool(answer.how))
    check("answer mentions photosynthesis",
          "photosynthesis" in answer.answer.lower() or "light" in answer.answer.lower())
    check("answer comes from graph",       answer.from_graph)
    check("latency < 5000ms",             answer.latency_ms < 5000)
    check("reasoning chain non-empty",    len(answer.reasoning_chain) > 0)

    # Test with unknown concept — should return low confidence
    unknown = brain.reason("what is xyzquantumblorp")
    check("unknown query returns low confidence", unknown.confidence < 0.1)
    check("unknown query is not from graph",      not unknown.from_graph)

    # Test WHY query specifically
    why_answer = brain.reason("why is photosynthesis important")
    check("WHY query returns answer",     why_answer is not None)
    check("WHY answer has content",       len(why_answer.answer) > 20)

    # Test graph traversal enrichment
    how_answer = brain.reason("how does chlorophyll work")
    check("HOW query returns answer",   how_answer is not None)
    check("HOW answer uses graph path", how_answer.from_graph)

    print()


# ──────────────────────────────────────────────────────────────────────────────
section("TEST 3: Learner (VelynxLearner)")
# ──────────────────────────────────────────────────────────────────────────────

with tempfile.TemporaryDirectory() as tmpdir:
    db = os.path.join(tmpdir, "learner_test.db")
    cp = os.path.join(tmpdir, "checkpoint.json")
    mem = VelynxMemory(db_path=db)

    from velynx_core.learner import (
        VelynxLearner, LearningItem, LearnerCheckpoint,
        extract_concept_from_source, fetch_wikipedia
    )

    # Test checkpoint crash safety
    ckpt = LearnerCheckpoint(cp)
    items = [
        LearningItem("gravity", "physics", priority=1.5),
        LearningItem("entropy", "physics", priority=1.0),
    ]
    stats_data = {"total_learned": 5}
    ckpt.save(items, stats_data)
    check("Checkpoint saves", Path(cp).exists())

    loaded_q, loaded_s = ckpt.load()
    check("Checkpoint loads queue",  len(loaded_q) == 2)
    check("Checkpoint loads stats",  loaded_s.get("total_learned") == 5)
    check("Loaded item has correct topic", loaded_q[0].topic == "gravity")

    # Test concept extraction from source text
    mock_source = {
        "title": "Gravity",
        "text": (
            "Gravity is the fundamental force of nature that attracts objects with mass toward each other. "
            "It is important because it governs the motion of planets, stars, and galaxies. "
            "Gravity works by causing spacetime curvature as described by Einstein's general relativity. "
            "As a result, objects in free fall follow curved paths called geodesics. "
            "This results in phenomena like planetary orbits and black holes."
        ),
        "url": "https://en.wikipedia.org/wiki/Gravity"
    }
    concept = extract_concept_from_source("gravity", "physics", mock_source)
    check("extract_concept_from_source returns Concept", concept is not None)
    check("Concept has what field",    concept and bool(concept.what))
    check("Concept has why field",     concept and bool(concept.why))
    check("Concept has how field",     concept and bool(concept.how))
    check("Concept has so_what field", concept and bool(concept.so_what))
    check("Confidence > 0.5",         concept and concept.confidence > 0.5)
    check("Domain correct",           concept and concept.domain == "physics")

    # Test learner queue management
    learner = VelynxLearner(mem, checkpoint_path=cp, batch_size=2)
    check("Learner initializes",       learner is not None)

    learner.enqueue("quantum entanglement", "physics", priority=2.0)
    learner.enqueue("black holes", "astronomy", priority=1.8)
    check("Queue size after 2 enqueues", learner.queue_size() >= 2)

    # Duplicate enqueue should be a no-op
    learner.enqueue("black holes", "astronomy")
    check("Duplicate enqueue is no-op", learner.queue_size() <= 4)  # no extra

    # Test bulk curriculum
    curriculum = [
        {"topic": "entropy",     "domain": "physics",  "priority": 1.0},
        {"topic": "evolution",   "domain": "biology",  "priority": 1.2},
    ]
    added = learner.enqueue_curriculum(curriculum)
    check("Curriculum enqueue adds topics", added >= 1)

    # Stats
    stats = learner.stats()
    check("Learner stats has queue_pending", "queue_pending" in stats)
    check("Learner is not running yet",      not stats["is_running"])

    # Test actual learning (Wikipedia fetch — needs internet)
    print(f"\n  {DIM}Testing live Wikipedia fetch (requires internet)...{RESET}")
    try:
        result = fetch_wikipedia("entropy")
        if result:
            ok(f"Wikipedia fetch works: '{result['title']}' ({len(result['text'])} chars)")
            passed += 1
            # Actually learn it
            from velynx_core.learner import extract_concept_from_source
            c = extract_concept_from_source("entropy", "physics", result)
            if c:
                mem.store_concept(c)
                ok(f"Learned from Wikipedia: confidence={c.confidence:.2f}")
                passed += 1
            else:
                fail("Concept extraction from Wikipedia failed")
                failed_count += 1
        else:
            print(f"  {DIM}Wikipedia not reachable (offline?) — skipping live test{RESET}")
    except Exception as e:
        print(f"  {DIM}Live fetch skipped: {e}{RESET}")

    print()


# ──────────────────────────────────────────────────────────────────────────────
section("TEST 4: Self-Coder (VelynxSelfCoder)")
# ──────────────────────────────────────────────────────────────────────────────

with tempfile.TemporaryDirectory() as tmpdir:
    db = os.path.join(tmpdir, "sc_test.db")
    mem = VelynxMemory(db_path=db)

    from velynx_core.self_coder import (
        VelynxSelfCoder, SandboxExecutor, analyze_file, scan_codebase,
        generate_fix, CodeIssue
    )

    # Create a test Python file with known issues
    test_file = Path(tmpdir) / "bad_code.py"
    test_file.write_text("""
import logging
logger = logging.getLogger(__name__)

def compute_something(x, y):
    result = x + y
    extra = x * y
    diff = x - y
    ratio = x / y if y != 0 else 0
    squared = x ** 2
    cubed = x ** 3
    combined = result + extra + diff
    return combined + ratio + squared + cubed

def handle_data(data):
    try:
        return data.process()
    except:
        return None

def missing_docs(a, b):
    return a + b

def another_func():
    # TODO: fix this later
    return None
""")

    # Analyze
    issues = analyze_file(test_file)
    check("analyze_file finds issues", len(issues) > 0)

    bare_except_issues = [i for i in issues if i.issue_type == "bare_except"]
    check("Detects bare_except",     len(bare_except_issues) > 0)

    no_docstring_issues = [i for i in issues if i.issue_type == "no_docstring"]
    check("Detects no_docstring",    len(no_docstring_issues) > 0)

    todo_issues = [i for i in issues if i.issue_type == "todo_comment"]
    check("Detects TODO comments",   len(todo_issues) > 0)

    # Generate fix for bare_except
    if bare_except_issues:
        issue = bare_except_issues[0]
        fix = generate_fix(issue)
        check("generate_fix returns non-empty", bool(fix))
        check("Fix replaces bare except", "except Exception" in fix)

    # Test sandbox
    sandbox = SandboxExecutor(timeout=10)

    ok_code = "print('hello from velynx sandbox')"
    success, output = sandbox.run_code(ok_code)
    check("Sandbox runs valid code", success, output.strip()[:40])

    bad_code = "import os; os.remove('/nonexistent/file/that/doesnt/exist')"
    success2, output2 = sandbox.run_code(bad_code)
    check("Sandbox handles errors gracefully", True)  # shouldn't crash the test runner

    timeout_code = "while True: pass"
    success3, output3 = sandbox.run_code(timeout_code)
    check("Sandbox enforces timeout", not success3 and "timeout" in output3.lower())

    # Syntax check
    syn_ok, msg = sandbox.syntax_check("def f(): return 1")
    check("Syntax check passes valid code", syn_ok)

    syn_bad, msg2 = sandbox.syntax_check("def f(: return 1")
    check("Syntax check catches errors", not syn_bad)

    # Self-coder init
    sc = VelynxSelfCoder(
        mem,
        codebase_root=tmpdir,
        history_path=os.path.join(tmpdir, "history.json"),
        cycle_interval_seconds=9999
    )
    check("SelfCoder initializes", sc is not None)

    report = sc.report()
    check("SelfCoder report returns dict", isinstance(report, dict))
    check("Report has total_attempts",    "total_attempts" in report)

    # Run a real cycle on our bad_code.py
    attempts = sc.run_one_cycle()
    check("run_one_cycle returns list", isinstance(attempts, list))
    if attempts:
        check("Attempt has target_function", bool(attempts[0].target_function))
        check("Attempt has test_result",     attempts[0].test_result in
              ("passed", "failed", "error", "skipped"))

    print()


# ──────────────────────────────────────────────────────────────────────────────
section("TEST 5: Full pipeline integration")
# ──────────────────────────────────────────────────────────────────────────────

with tempfile.TemporaryDirectory() as tmpdir:
    db = os.path.join(tmpdir, "full_test.db")
    cp = os.path.join(tmpdir, "ckpt.json")

    from velynx_core.memory import VelynxMemory, Concept, Relation
    from velynx_core.brain import VelynxBrain

    mem = VelynxMemory(db_path=db)
    brain = VelynxBrain(mem)

    # Simulate a full learn-then-reason cycle

    # Step 1: Inject knowledge directly (simulating learned knowledge)
    concepts_to_inject = [
        Concept(
            id=Concept.make_id("neural network", "AI"),
            name="neural network",
            domain="AI",
            what="A computational model inspired by biological neurons that learns patterns from data.",
            why="Neural networks can approximate any continuous function, making them universal learners.",
            how="Layers of weighted connections pass signals forward; backpropagation adjusts weights to minimize error.",
            so_what="They power image recognition, language models, and most modern AI systems.",
            confidence=0.91,
            sources=["https://en.wikipedia.org/wiki/Neural_network"]
        ),
        Concept(
            id=Concept.make_id("backpropagation", "AI"),
            name="backpropagation",
            domain="AI",
            what="Algorithm for training neural networks by computing gradients of the loss function.",
            why="Without backpropagation, neural networks cannot be trained efficiently on large datasets.",
            how="Applies the chain rule of calculus to propagate error gradients from output to input layers.",
            so_what="It is the core training mechanism behind all deep learning systems today.",
            confidence=0.89,
            sources=["https://en.wikipedia.org/wiki/Backpropagation"]
        ),
        Concept(
            id=Concept.make_id("gradient descent", "AI"),
            name="gradient descent",
            domain="AI",
            what="Optimization algorithm that iteratively moves parameters toward the minimum of a loss function.",
            why="Most machine learning problems reduce to finding the minimum of a loss function.",
            how="Computes the gradient of the loss, then updates parameters in the opposite direction.",
            so_what="Without gradient descent, training large models would be computationally infeasible.",
            confidence=0.90
        ),
    ]

    for c in concepts_to_inject:
        mem.store_concept(c)

    # Add semantic relations
    nn_id  = concepts_to_inject[0].id
    bp_id  = concepts_to_inject[1].id
    gd_id  = concepts_to_inject[2].id

    mem.add_relation(Relation(nn_id, bp_id, "REQUIRES", 1.0, "training neural networks requires backpropagation"))
    mem.add_relation(Relation(bp_id, gd_id, "ENABLES",  1.0, "backpropagation enables gradient descent updates"))
    mem.add_relation(Relation(nn_id, gd_id, "REQUIRES", 0.9, "neural networks require gradient descent for learning"))

    # Step 2: Query — should reason via graph traversal
    ans = brain.reason("how does a neural network learn")
    check("Full pipeline: returns answer",       ans is not None)
    check("Full pipeline: confidence > 0.5",     ans.confidence > 0.5)
    check("Full pipeline: from graph",           ans.from_graph)
    check("Full pipeline: concepts used > 1",    len(ans.concepts_used) > 1)
    check("Full pipeline: answer non-empty",     len(ans.answer) > 50)
    check("Full pipeline: WHY layer present",    bool(ans.why))
    check("Full pipeline: HOW layer present",    bool(ans.how))
    check("Full pipeline: SO WHAT layer present",bool(ans.so_what))
    check("Full pipeline: latency < 1000ms",     ans.latency_ms < 1000)
    check("Full pipeline: sources tracked",      len(ans.sources) >= 1)

    # Stats
    stats = mem.stats()
    check("Memory has 3 concepts",     stats["concepts"] == 3)
    check("Memory has 3 relations",    stats["relations"] == 3)

    # Query for related concept (graph traversal)
    bp_ans = brain.reason("what is backpropagation")
    check("Backpropagation query answered", bp_ans and bp_ans.confidence > 0.5)

    print()


# ──────────────────────────────────────────────────────────────────────────────
section("RESULTS")
# ──────────────────────────────────────────────────────────────────────────────

total = passed + failed_count
print(f"\n  Passed:  {GREEN}{passed}{RESET} / {total}")
print(f"  Failed:  {RED}{failed_count}{RESET} / {total}")
print(f"  Score:   {round(passed/total*100) if total else 0}%")

if failed_count == 0:
    print(f"\n  {GREEN}{BOLD}All tests passed. VELYNX Core v2 is ready.{RESET}\n")
    sys.exit(0)
else:
    print(f"\n  {RED}Some tests failed. Review above before deploying.{RESET}\n")
    sys.exit(1)