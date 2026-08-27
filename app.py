#!/usr/bin/env python3
"""Tamamen yerel RAG asistanı için etkileşimli terminal arayüzü."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from rag.pipeline import AnswerResult, RAGPipeline


class PipelineProvider(Protocol):
    def __enter__(self) -> "PipelineProvider": ...

    def __exit__(self, *args: object) -> None: ...

    def answer_query(self, question: str) -> AnswerResult: ...


def _show_result(result: AnswerResult, output: Callable[[str], None]) -> None:
    output("")
    output("Cevap:")
    output(result.answer)
    output("")
    output("Kaynaklar:")
    if result.sources:
        for source in result.sources:
            output(f"- {source}")
    else:
        output("- İlgili kaynak belge bulunamadı")
    output("")


def run_cli(
    pipeline_factory: Callable[[], PipelineProvider] = RAGPipeline,
    input_fn: Callable[[str], str] = input,
    output: Callable[[str], None] = print,
) -> int:
    output("=" * 40)
    output(" Yerel RAG Çalışma Asistanı")
    output("=" * 40)
    output("Yerel modeller yükleniyor (bulut LLM kullanılmaz)...")

    try:
        with pipeline_factory() as pipeline:
            output("Hazır. Bir soru sorun veya çıkmak için 'çıkış' yazın.")
            while True:
                try:
                    question = input_fn("\n> ").strip()
                except EOFError:
                    output("\nGirdi sona erdi. Çıkılıyor.")
                    break
                except KeyboardInterrupt:
                    output("\nİşlem kesildi. Çıkılıyor.")
                    break

                if question.lower() in {"çıkış", "çık", "exit", "quit", "q"}:
                    output("Görüşmek üzere.")
                    break
                if not question:
                    output("Lütfen bir soru girin veya çıkmak için 'çıkış' yazın.")
                    continue

                output("Soru yerel olarak işleniyor...")
                try:
                    result = pipeline.answer_query(question)
                except Exception as error:
                    output(f"Bu soru cevaplanamadı: {error}")
                    output("Başka bir soru deneyebilirsiniz.")
                    continue
                _show_result(result, output)
    except Exception as error:
        output(f"Uygulama başlatılamadı: {error}")
        output("İndeks eksikse şu komutu çalıştırın: .venv/bin/python scripts/ingest.py")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
