from __future__ import annotations

import subprocess
import sys
import unittest


class FoundryRuntimeImportTests(unittest.TestCase):
    def test_sdk_is_not_loaded_until_manager_is_requested(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys; import rag.foundry_runtime; "
                    "print('foundry_local_sdk' in sys.modules)"
                ),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.strip(), "False")


if __name__ == "__main__":
    unittest.main()
