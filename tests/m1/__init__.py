"""M1 platform acceptance tests.

Scope: the engineering platform — protocols, registry, config system, engine,
metrics, artifacts, scheduler. Scientific claims are out of scope by construction:
these tests establish implementation conformance only, which per the Scientific
Operating System (section 11) is not evidence for any mechanism.

The one test that carries scientific weight is
`test_frozen_v0_equivalence.py`: it shows the platform reproduces the reviewed M0
artifact exactly, so M1 results remain comparable with M0.
"""
