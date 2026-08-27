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
        return AnswerResult("A grounded answer.", ["oop.md"], [])


class AppTests(unittest.TestCase):
    def test_handles_empty_input_question_and_exit(self) -> None:
        pipeline = FakePipeline()
        inputs = iter(["", "What is polymorphism?", "exit"])
        output: list[str] = []

        status = run_cli(
            pipeline_factory=lambda: pipeline,
            input_fn=lambda _: next(inputs),
            output=output.append,
        )

        self.assertEqual(status, 0)
        self.assertEqual(pipeline.questions, ["What is polymorphism?"])
        self.assertTrue(pipeline.closed)
        self.assertIn("Please enter a question, or type 'exit' to quit.", output)
        self.assertIn("A grounded answer.", output)
        self.assertIn("- oop.md", output)
        self.assertIn("Goodbye.", output)

    def test_startup_failure_is_user_friendly(self) -> None:
        def broken_factory() -> FakePipeline:
            raise RuntimeError("runtime unavailable")

        output: list[str] = []
        status = run_cli(pipeline_factory=broken_factory, output=output.append)

        self.assertEqual(status, 1)
        self.assertTrue(any("startup failed" in line for line in output))
        self.assertTrue(any("scripts/ingest.py" in line for line in output))


if __name__ == "__main__":
    unittest.main()
