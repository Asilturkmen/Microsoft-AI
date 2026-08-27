#!/usr/bin/env python3
"""Run the documented evaluation matrix against real local Foundry models."""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.pipeline import RAGPipeline, UNKNOWN_ANSWER  # noqa: E402


CASES_PATH = PROJECT_ROOT / "tests" / "evaluation_cases.json"


def _evaluate_result(case: dict[str, Any], result: Any) -> tuple[bool, str]:
    if case.get("expected_safe_result"):
        return bool(result.answer.strip()), "returned a non-empty controlled result"
    if case["should_answer"]:
        source_ok = case["expected_source"] in result.sources
        terms = [term.lower() for term in case.get("required_terms_any", [])]
        term_ok = not terms or any(term in result.answer.lower() for term in terms)
        passed = not result.used_fallback and source_ok and term_ok
        return passed, f"source_ok={source_ok}, term_ok={term_ok}"
    passed = result.used_fallback and result.answer == UNKNOWN_ANSWER and not result.sources
    return passed, f"fallback={result.used_fallback}, sources={result.sources}"


def main() -> int:
    cases: list[dict[str, Any]] = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    print(f"Evaluation cases: {len(cases)}", flush=True)
    load_start = time.perf_counter()
    pipeline = RAGPipeline()
    pipeline.load()
    cold_load_seconds = time.perf_counter() - load_start
    print(f"Cold model load: {cold_load_seconds:.3f}s", flush=True)

    failures = 0
    warm_times: list[float] = []
    try:
        for case in cases:
            start = time.perf_counter()
            try:
                result = pipeline.answer_query(case["question"])
            except Exception as error:
                elapsed = time.perf_counter() - start
                expected = case.get("expected_error")
                passed = expected == type(error).__name__
                note = f"{type(error).__name__}: {error}"
                top_score = "n/a"
                sources = []
                answer = "<error>"
            else:
                elapsed = time.perf_counter() - start
                passed, note = _evaluate_result(case, result)
                top_score = f"{result.retrieved_chunks[0].score:.6f}"
                sources = result.sources
                answer = result.answer.replace("\n", " ")
                warm_times.append(elapsed)

            status = "PASS" if passed else "FAIL"
            failures += int(not passed)
            print(f"\n[{status}] {case['id']} ({elapsed:.3f}s)")
            print(f"  question: {case['question'] or '<empty>'}")
            print(f"  top_score: {top_score}")
            print(f"  sources: {sources}")
            print(f"  answer: {answer}")
            print(f"  checks: {note}", flush=True)
    finally:
        pipeline.close()

    print("\nTiming summary")
    print(f"  cold_load_seconds: {cold_load_seconds:.3f}")
    print(f"  warm_query_min_seconds: {min(warm_times):.3f}")
    print(f"  warm_query_median_seconds: {statistics.median(warm_times):.3f}")
    print(f"  warm_query_max_seconds: {max(warm_times):.3f}")
    print(f"Evaluation result: {len(cases) - failures}/{len(cases)} PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
