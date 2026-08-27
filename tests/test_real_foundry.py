from __future__ import annotations

import os
import unittest

from rag.pipeline import RAGPipeline, UNKNOWN_ANSWER


RUN_REAL = os.environ.get("RUN_REAL_FOUNDRY_TESTS") == "1"


@unittest.skipUnless(RUN_REAL, "yerel model testleri için RUN_REAL_FOUNDRY_TESTS=1 ayarlayın")
class RealFoundryIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pipeline = RAGPipeline()
        cls.pipeline.load()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.pipeline.close()

    def test_answerable_query_uses_expected_source(self) -> None:
        result = self.pipeline.answer_query("TCP ile UDP arasındaki farklar nelerdir?")
        self.assertFalse(result.used_fallback)
        self.assertIn("networking.md", result.sources)
        self.assertTrue(
            any(term in result.answer.lower() for term in ("güvenilir", "sıralı", "teslim"))
        )

    def test_unanswerable_query_is_rejected(self) -> None:
        result = self.pipeline.answer_query("Tiramisu yapmak için hangi malzemeler gerekir?")
        self.assertTrue(result.used_fallback)
        self.assertEqual(result.answer, UNKNOWN_ANSWER)
        self.assertEqual(result.sources, [])


if __name__ == "__main__":
    unittest.main()
