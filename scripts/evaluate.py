#!/usr/bin/env python3
"""Belgelenmiş Türkçe değerlendirme matrisini gerçek yerel modellerle çalıştır."""

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
        return bool(result.answer.strip()), "boş olmayan kontrollü bir sonuç döndü"
    if case["should_answer"]:
        source_ok = case["expected_source"] in result.sources
        terms = [term.lower() for term in case.get("required_terms_any", [])]
        term_ok = not terms or any(term in result.answer.lower() for term in terms)
        passed = not result.used_fallback and source_ok and term_ok
        return passed, f"kaynak_doğru={source_ok}, terim_doğru={term_ok}"
    passed = result.used_fallback and result.answer == UNKNOWN_ANSWER and not result.sources
    return passed, f"kontrollü_cevap={result.used_fallback}, kaynaklar={result.sources}"


def main() -> int:
    cases: list[dict[str, Any]] = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    print(f"Değerlendirme vakası: {len(cases)}", flush=True)
    load_start = time.perf_counter()
    pipeline = RAGPipeline()
    pipeline.load()
    cold_load_seconds = time.perf_counter() - load_start
    print(f"Soğuk model yükleme: {cold_load_seconds:.3f} sn", flush=True)

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
                top_score = "uygulanamaz"
                sources = []
                answer = "<hata>"
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
            print(f"  soru: {case['question'] or '<boş>'}")
            print(f"  en_yüksek_skor: {top_score}")
            print(f"  kaynaklar: {sources}")
            print(f"  cevap: {answer}")
            print(f"  kontroller: {note}", flush=True)
    finally:
        pipeline.close()

    print("\nSüre özeti")
    print(f"  soğuk_yükleme_saniye: {cold_load_seconds:.3f}")
    print(f"  sıcak_sorgu_min_saniye: {min(warm_times):.3f}")
    print(f"  sıcak_sorgu_medyan_saniye: {statistics.median(warm_times):.3f}")
    print(f"  sıcak_sorgu_maks_saniye: {max(warm_times):.3f}")
    print(f"Değerlendirme sonucu: {len(cases) - failures}/{len(cases)} PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
