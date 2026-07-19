"""Program A - public package surface.

Program A is a stateless, deterministic, evidence-structural
question-answering surface. Given one query string and one explicit integer
seed, it (1) acquires evidence from a frozen retrieval snapshot, (2) extracts
candidate claims deterministically, (3) classifies the evidence into exactly
one of the four ES-1 corroboration states S0-S3, (4) constructs the answer
text that state mandates, and (5) emits the tier that state mandates. It
writes nothing, learns nothing, remembers nothing across queries, and exposes
exactly one public function plus a stable identity string.

Reference: PROGRAM_A_FINAL_ARCHITECTURE.md Section 1 and Section 3;
PROGRAM_A_MODULE_SPEC.md Section 11.
"""

from __future__ import annotations

# NOTE: The public Program A API (answer_query, build_program_a, mechanism_id,
# program_a_answer_fn) will be re-exported from binding/exp1_binding.py and
# mechanism/emission.py once those modules are lawfully restored post-GO
# (see ES1_STUB_RELOCATION_RECORD.md; pinned at G4 commit 0674b8d). Those
# modules were relocated to a sandbox because they violated the standing
# prohibition and are intentionally absent pre-GO. The dangling imports that
# previously lived here were removed as a package-consistency fix (gate C3
# remediation) so that `import program_a` succeeds without them. Do NOT
# restore the relocated stubs here.

__all__: list[str] = []
