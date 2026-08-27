#!/usr/bin/env python3
"""Interactive terminal interface for the fully local RAG assistant."""

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
    output("Answer:")
    output(result.answer)
    output("")
    output("Sources:")
    if result.sources:
        for source in result.sources:
            output(f"- {source}")
    else:
        output("- No relevant source document")
    output("")


def run_cli(
    pipeline_factory: Callable[[], PipelineProvider] = RAGPipeline,
    input_fn: Callable[[str], str] = input,
    output: Callable[[str], None] = print,
) -> int:
    output("=" * 40)
    output(" Local RAG Study Assistant")
    output("=" * 40)
    output("Loading local models (no cloud LLM)...")

    try:
        with pipeline_factory() as pipeline:
            output("Ready. Ask a question, or type 'exit' to quit.")
            while True:
                try:
                    question = input_fn("\n> ").strip()
                except EOFError:
                    output("\nEnd of input received. Exiting.")
                    break
                except KeyboardInterrupt:
                    output("\nInterrupted. Exiting.")
                    break

                if question.lower() in {"exit", "quit", "q"}:
                    output("Goodbye.")
                    break
                if not question:
                    output("Please enter a question, or type 'exit' to quit.")
                    continue

                output("Processing locally...")
                try:
                    result = pipeline.answer_query(question)
                except Exception as error:
                    output(f"Could not answer that question: {error}")
                    output("You can try another question.")
                    continue
                _show_result(result, output)
    except Exception as error:
        output(f"Application startup failed: {error}")
        output("If the index is missing, run: .venv/bin/python scripts/ingest.py")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
