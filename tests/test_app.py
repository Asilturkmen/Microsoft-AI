from __future__ import annotations

import unittest

from app import run_cli
from rag.pipeline import AnswerResult


class FakePipeline:
    def __init__(self) -> None:
        self.questions: list[str] = []
        self.closed = False

    def __enter__(self) -> "FakePipeline":
        return self

    def __exit__(self, *args: object) -> None:
        self.closed = True

    def answer_query(self, question: str) -> AnswerResult:
        self.questions.append(question)
        return AnswerResult("Belgeye dayalı bir cevap.", ["oop.md"], [])


class AppTests(unittest.TestCase):
    def test_handles_empty_input_question_and_exit(self) -> None:
        pipeline = FakePipeline()
        inputs = iter(["", "Polimorfizm nedir?", "çıkış"])
        output: list[str] = []

        status = run_cli(
            pipeline_factory=lambda: pipeline,
            input_fn=lambda _: next(inputs),
            output=output.append,
        )

        self.assertEqual(status, 0)
        self.assertEqual(pipeline.questions, ["Polimorfizm nedir?"])
        self.assertTrue(pipeline.closed)
        self.assertIn("Lütfen bir soru girin veya çıkmak için 'çıkış' yazın.", output)
        self.assertIn("Belgeye dayalı bir cevap.", output)
        self.assertIn("- oop.md", output)
        self.assertIn("Görüşmek üzere.", output)

    def test_startup_failure_is_user_friendly(self) -> None:
        def broken_factory() -> FakePipeline:
            raise RuntimeError("runtime unavailable")

        output: list[str] = []
        status = run_cli(pipeline_factory=broken_factory, output=output.append)

        self.assertEqual(status, 1)
        self.assertTrue(any("başlatılamadı" in line for line in output))
        self.assertTrue(any("scripts/ingest.py" in line for line in output))


if __name__ == "__main__":
    unittest.main()
