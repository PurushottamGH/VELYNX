"""Planning and goal evaluation."""
from __future__ import annotations

import logging
from typing import Any

from evaluation import MetricEvaluation

logger = logging.getLogger("uvicorn")


class PlanningEvaluator:
    """Evaluates planning and goal management quality."""

    def evaluate_plan(self, plan: dict[str, Any]) -> list[MetricEvaluation]:
        """Evaluate a plan's structure and quality."""
        evaluations: list[MetricEvaluation] = []

        tasks = plan.get("tasks", [])
        edges = plan.get("edges", [])

        # Task count
        evaluations.append(MetricEvaluation(
            name="task_count",
            value=float(len(tasks)),
            threshold=1.0,
            passed=len(tasks) >= 1,
            description=f"Plan has {len(tasks)} tasks",
        ))

        if not tasks:
            return evaluations

        # DAG validity (no tasks depend on themselves)
        self_loops = sum(1 for f, t in edges if f == t)
        evaluations.append(MetricEvaluation(
            name="dag_validity",
            value=float(self_loops),
            threshold=0.0,
            passed=self_loops == 0,
            description=f"Self-loops: {self_loops}",
        ))

        # Dependency depth
        task_ids = {t.get("id", "") for t in tasks}
        max_depth = self._compute_max_depth(tasks, edges)
        evaluations.append(MetricEvaluation(
            name="dependency_depth",
            value=float(max_depth),
            threshold=5.0,
            passed=max_depth <= 5,
            description=f"Max dependency depth: {max_depth}",
        ))

        # Task description quality
        descriptions = [t.get("description", "") for t in tasks]
        avg_desc_len = sum(len(d) for d in descriptions) / len(descriptions) if descriptions else 0
        evaluations.append(MetricEvaluation(
            name="description_quality",
            value=avg_desc_len,
            threshold=10.0,
            passed=avg_desc_len >= 10,
            description=f"Avg description length: {avg_desc_len:.0f} chars",
        ))

        # Strategy presence
        strategy = plan.get("strategy", "")
        evaluations.append(MetricEvaluation(
            name="strategy_present",
            value=1.0 if strategy else 0.0,
            threshold=0.5,
            passed=bool(strategy),
            description=f"Strategy: {strategy or 'none'}",
        ))

        return evaluations

    def evaluate_goal_progress(
        self, progress: dict[str, Any]
    ) -> list[MetricEvaluation]:
        """Evaluate goal progress."""
        evaluations: list[MetricEvaluation] = []

        total = progress.get("total_sub_goals", 0)
        completed = progress.get("completed", 0)
        ratio = progress.get("completion_ratio", 0.0)

        if total > 0:
            evaluations.append(MetricEvaluation(
                name="goal_completion",
                value=ratio,
                threshold=0.0,
                passed=True,
                description=f"Completed {completed}/{total} sub-goals ({ratio:.0%})",
            ))

        return evaluations

    def evaluate_plan_execution(
        self, report: dict[str, Any]
    ) -> list[MetricEvaluation]:
        """Evaluate plan execution report."""
        evaluations: list[MetricEvaluation] = []

        total = report.get("total_tasks", 0)
        completed = report.get("completed", 0)
        failed = report.get("failed", 0)
        progress = report.get("overall_progress", 0.0)

        if total > 0:
            fail_rate = failed / total
            evaluations.append(MetricEvaluation(
                name="execution_fail_rate",
                value=fail_rate,
                threshold=0.3,
                passed=fail_rate < 0.3,
                description=f"Fail rate: {fail_rate:.0%} ({failed}/{total})",
            ))

            evaluations.append(MetricEvaluation(
                name="execution_progress",
                value=progress,
                threshold=0.0,
                passed=True,
                description=f"Progress: {progress:.0%}",
            ))

        return evaluations

    def _compute_max_depth(
        self, tasks: list[dict], edges: list[tuple[str, str]]
    ) -> int:
        """Compute maximum dependency depth in a task DAG."""
        task_map = {t.get("id", ""): t for t in tasks}
        depends_on: dict[str, set[str]] = {tid: set() for tid in task_map}
        for from_id, to_id in edges:
            if to_id in depends_on:
                depends_on[to_id].add(from_id)

        memo: dict[str, int] = {}

        def depth(tid: str, visited: set[str]) -> int:
            if tid in memo:
                return memo[tid]
            if tid in visited:
                return 0  # cycle protection
            visited.add(tid)
            deps = depends_on.get(tid, set())
            if not deps:
                memo[tid] = 0
                return 0
            d = 1 + max(depth(d, visited) for d in deps if d in task_map)
            memo[tid] = d
            return d

        return max((depth(tid, set()) for tid in task_map), default=0)


# Module-level singleton
planning_evaluator = PlanningEvaluator()
