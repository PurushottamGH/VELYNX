"""The nine propagation obligations."""

from __future__ import annotations

import pytest

from ros.propagation import DISCHARGE_SITE, Obligation, audit, audit_all
from ros.store import load_default


def outstanding(report) -> set[Obligation]:
    return {r.obligation for r in report.outstanding}


# ------------------------------------------------------------ completeness


def test_every_obligation_has_a_discharge_site():
    """A report that says an obligation is outstanding but not where to
    discharge it moves work onto the reader."""
    assert set(DISCHARGE_SITE) == set(Obligation)
    assert all(DISCHARGE_SITE[o] for o in Obligation)


def test_nine_obligations_exactly():
    assert len(Obligation) == 9


# --------------------------------------------------- positive control (live)


def test_live_repository_has_all_due_propagation_complete():
    """A real assertion about the laboratory: every experiment that has executed
    has discharged all nine obligations."""
    reports = audit_all(load_default("."))
    assert reports, "no experiments are due; the audit would be vacuous"
    assert [r.experiment_id for r in reports if not r.complete] == []


def test_unexecuted_experiments_are_not_reported_as_defects():
    """Designed and blocked experiments have not executed, so no propagation is
    owed. Firing on a known negative disqualifies a measurement (Lock E2)."""
    store = load_default(".")
    every = audit_all(store, include_not_due=True)
    due = audit_all(store)
    assert len(every) > len(due)
    for report in every:
        if not report.due:
            assert report.outstanding == ()
            assert "NOT DUE" in report.render()


def test_miniature_lab_experiment_is_complete(lab):
    from ros.store import DEFAULT_STORE_PATH, Store

    store = Store.load(lab / DEFAULT_STORE_PATH)
    report = audit(store, "EXP-2026-0001")
    assert report.due
    assert report.complete, report.render()


# ------------------------------------------------------- negative controls


@pytest.mark.parametrize(
    "mutate,expected",
    [
        (lambda d: d["experiments"][0].pop("validity"), Obligation.EXECUTION_VALIDITY),
        (lambda d: d["experiments"][0].update({"observations": []}), Obligation.OBSERVATIONS),
        (lambda d: d["evidence"][0].pop("rationale"), Obligation.INTERPRETATION),
        (lambda d: d.update({"decisions": []}), Obligation.DECISION),
        (lambda d: d["hypotheses"][0].pop("status"), Obligation.DEPENDENT_STATUS),
        (lambda d: d["experiments"][0].pop("limitations"), Obligation.ROADMAP),
        (lambda d: d.update({"relations": []}), Obligation.LIVING_MODEL),
    ],
)
def test_each_obligation_can_fail(edit_store, mutate, expected):
    """One negative control per obligation. An obligation that cannot be
    reported missing is not being checked."""
    store = edit_store(mutate)
    report = audit(store, "EXP-2026-0001")
    assert expected in outstanding(report), report.render()
    assert not report.complete


def test_removing_all_supporting_records_removes_debt_linkage(edit_store):
    def mutate(document):
        document["assumptions"] = []
        document["unknowns"] = []
        document["scientific_debt"] = []

    store = edit_store(mutate)
    report = audit(store, "EXP-2026-0001")
    assert Obligation.ASSUMPTIONS_UNKNOWNS_DEBT in outstanding(report)


def test_dropping_evidence_reports_both_dependent_obligations(edit_store):
    """Evidence carries two obligations. Removing it must report both, not stop
    at the first."""
    store = edit_store(lambda d: d["experiments"][0].update({"evidence": []}))
    report = audit(store, "EXP-2026-0001")
    assert {Obligation.EVIDENCE_RELATIONS, Obligation.INTERPRETATION} <= outstanding(report)


def test_report_names_where_to_discharge(edit_store):
    store = edit_store(lambda d: d["experiments"][0].pop("validity"))
    rendered = audit(store, "EXP-2026-0001").render()
    assert DISCHARGE_SITE[Obligation.EXECUTION_VALIDITY] in rendered


def test_status_alone_makes_propagation_due(edit_store):
    """An experiment with no recorded executions but a closed status has run;
    the audit must not let a missing field excuse propagation."""

    def mutate(document):
        document["experiments"][0].pop("executions")
        document["experiments"][0]["status"] = "Closed"

    store = edit_store(mutate)
    assert audit(store, "EXP-2026-0001").due


def test_designed_experiment_is_not_due(edit_store):
    def mutate(document):
        document["experiments"][0]["status"] = "Designed"
        document["experiments"][0].pop("executions")

    store = edit_store(mutate)
    assert not audit(store, "EXP-2026-0001").due


def test_recorded_executions_outrank_a_stale_status(edit_store):
    """If a run happened, propagation is owed regardless of what the status
    field still says."""

    def mutate(document):
        document["experiments"][0]["status"] = "Designed"
        document["experiments"][0]["executions"] = ["run-a"]

    store = edit_store(mutate)
    assert audit(store, "EXP-2026-0001").due


def test_auditing_a_non_experiment_raises(lab):
    from ros.store import DEFAULT_STORE_PATH, Store

    store = Store.load(lab / DEFAULT_STORE_PATH)
    with pytest.raises(KeyError):
        audit(store, "HYP-2026-0001")
