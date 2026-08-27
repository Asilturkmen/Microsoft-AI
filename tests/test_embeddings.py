from __future__ import annotations

import math
import unittest

from rag.embeddings import validate_embedding


class EmbeddingValidationTests(unittest.TestCase):
    def test_accepts_finite_numeric_vector(self) -> None:
        self.assertEqual(validate_embedding([1, 2.5, -3]), [1.0, 2.5, -3.0])

    def test_rejects_empty_non_finite_and_wrong_dimension(self) -> None:
        with self.assertRaisesRegex(ValueError, "empty"):
            validate_embedding([])
        with self.assertRaisesRegex(ValueError, "NaN"):
            validate_embedding([1.0, math.nan])
        with self.assertRaisesRegex(ValueError, "dimension mismatch"):
            validate_embedding([1.0], expected_dimension=2)


if __name__ == "__main__":
    unittest.main()
